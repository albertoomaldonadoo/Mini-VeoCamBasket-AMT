# Importamos los paquetes
import boto3, os
from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv
from detect_labels import detect_labels
from draw_players import draw_players
from gemini_report import gemini_report

# Cargamos las variables de entorno del fichero .env
load_dotenv()

# Obtenemos las variables de entorno
accessKeyId = os.environ.get('ACCESS_KEY_ID')
secretKey = os.environ.get('ACCESS_SECRET_KEY')
bucket_source = os.environ.get('BUCKET_SOURCE')
bucket_dest = os.environ.get('BUCKET_DEST')
region = os.environ.get('REGION')

# Creamos la aplicacion Flask
application = Flask(__name__)

# Creamos el servicio S3 y le asignamos las credenciales
s3 = boto3.Session(
    aws_access_key_id=accessKeyId,
    aws_secret_access_key=secretKey,
    region_name=region).resource('s3')

# Endpoint api/analyze (solo acepta peticiones POST con JSON)
@application.route('/api/analyze', methods=['POST'])
def analyzeImage():
    # Sacamos del JSON el nombre de la imagen que esta en el bucket origen
    key = request.get_json().get('key')
    if key is None:
        abort(400)

    try:
        # 1. Llamada a Rekognition
        response = detect_labels(key)

        # 2. Leer la imagen original del bucket
        fileObject = s3.Object(bucket_source, key).get()
        fileContent = fileObject['Body'].read()

        # 3. Funcionalidad extra: dibujar jugadores, balon y lineas de pase
        buffer_img, players, ball = draw_players(fileContent, response)

        # 4. Guardar la imagen resultado en el bucket destino
        result_key = f"result_{key}"
        s3.Object(bucket_dest, result_key).put(Body=buffer_img.tobytes())

        # 5. IA extra: Gemini recibe la foto original y la foto con las marcas, y da consejos de entrenador
        report = gemini_report(players, ball, buffer_img.tobytes(), fileContent)
    except Exception as error:
        print(error)
        abort(500)

    # Devolvemos los datos en formato JSON
    return jsonify({
        'players': players,
        'ball': ball,
        'report': report,
        'result_key': result_key
    })

# Arrancamos la aplicacion
if __name__ == "__main__":
    application.debug = True
    application.run() # Se ejecuta en http://127.0.0.1:5000/