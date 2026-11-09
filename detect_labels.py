# Importamos los paquetes
import os
import boto3

from dotenv import load_dotenv

# Cargamos las variables de entorno del fichero .env
load_dotenv()

# Obtenemos las variables de entorno
accessKeyId = os.environ.get('ACCESS_KEY_ID')
secretKey = os.environ.get('ACCESS_SECRET_KEY')
bucket = os.environ.get('BUCKET_SOURCE')
region = os.environ.get('REGION')

# Creamos el cliente de Rekognition con las credenciales
rekognition_client = boto3.Session(
    aws_access_key_id=accessKeyId,
    aws_secret_access_key=secretKey,
    region_name=region).client('rekognition')

def detect_labels(img):
    # Llamamos al servicio y detecta objetos y personas con su posicion exacta en la imagen.
    # Bajamos MinConfidence a 40 para que no se le escapen objetos pequenos como el balon
    # (despues filtramos nosotros en draw_players.py)
    try:
        response = rekognition_client.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': img}},
            MaxLabels=100,
            MinConfidence=40)

        print("Image task recognition has been successfully run")
    except Exception as error:
        print(error)
        raise Exception("An unexpected error was raised recognizing an image")

    # Devolvemos la respuesta de Rekognition al main
    return response