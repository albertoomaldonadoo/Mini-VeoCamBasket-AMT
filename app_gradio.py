# Interfaz web con Gradio: subir una imagen, analizarla y descargar el resultado

# Importamos los paquetes
import os, uuid
import boto3
import requests
import gradio as gr
from dotenv import load_dotenv

# Cargamos las variables de entorno del fichero .env
load_dotenv()

# Obtenemos las variables de entorno
accessKeyId = os.environ.get('ACCESS_KEY_ID')
secretKey = os.environ.get('ACCESS_SECRET_KEY')
bucket_source = os.environ.get('BUCKET_SOURCE')
bucket_dest = os.environ.get('BUCKET_DEST')
region = os.environ.get('REGION')

# Creamos el servicio S3 y le asignamos las credenciales
s3 = boto3.Session(
    aws_access_key_id=accessKeyId,
    aws_secret_access_key=secretKey,
    region_name=region).resource('s3')

# Estilos CSS: fondo animado, tarjetas de cristal, numeros con degradado y boton con brillo
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

/* Fondo animado con degradado y dos luces de colores */
.gradio-container {
    --body-text-color: #f2f2f2;
    --block-background-fill: transparent;
    --block-label-text-color: #ff9d4d;
    --block-border-color: rgba(255, 255, 255, 0.08);
    font-family: 'Space Grotesk', sans-serif !important;
    background: linear-gradient(-45deg, #0b0b10, #1b1033, #2a1608, #0b0b10) !important;
    background-size: 400% 400% !important;
    animation: fondo 18s ease infinite;
    width: 100% !important;
    max-width: 1500px !important;
    margin: auto !important;
    isolation: isolate;
}
@keyframes fondo { 0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;} }
.gradio-container::before, .gradio-container::after {
    content: ''; position: fixed; z-index: -1; width: 500px; height: 500px;
    border-radius: 50%; filter: blur(90px); pointer-events: none;
}
.gradio-container::before { top: -150px; left: -100px; background: rgba(255, 122, 26, 0.35); }
.gradio-container::after { bottom: -200px; right: -100px; background: rgba(120, 70, 255, 0.30); }

/* Cabecera */
.cabecera { text-align: center; padding: 30px 0 10px 0; }
.cabecera h1 {
    font-size: 3.4rem; font-weight: 700; margin: 0; letter-spacing: -1px;
    background: linear-gradient(90deg, #ffb347, #ff5e1a, #ff3d7f);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.cabecera p { color: #b9b9c6; font-size: 1.1rem; margin: 8px 0 0 0; }

/* Las 3 columnas siempre en horizontal y del mismo ancho, desde el principio */
#fila { flex-wrap: nowrap !important; }
#fila > * { min-width: 0 !important; flex: 1 1 0 !important; }

/* Tarjetas de cristal */
.cristal {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 24px !important;
    padding: 18px !important;
    backdrop-filter: blur(14px);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35);
    transition: transform 0.25s, box-shadow 0.25s;
}
.cristal:hover { transform: translateY(-4px); box-shadow: 0 16px 50px rgba(255, 122, 26, 0.18); }
.cristal img { border-radius: 16px; }

/* Datos grandes con degradado */
.stats { display: flex; gap: 20px; margin: 18px 0; }
.stat {
    flex: 1; text-align: center; padding: 20px; border-radius: 24px;
    background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(14px);
}
.stat span { display: block; color: #b9b9c6; font-size: 0.85rem; letter-spacing: 3px; }
.stat b {
    font-size: 3rem; font-weight: 700;
    background: linear-gradient(90deg, #ffb347, #ff5e1a);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}

/* Boton con brillo */
#boton {
    background: linear-gradient(90deg, #ff7a1a, #ff3d7f, #ff7a1a) !important;
    background-size: 200% auto !important;
    color: white !important; font-size: 1.15rem !important; font-weight: 700 !important;
    border: none !important; border-radius: 40px !important; padding: 14px !important;
    box-shadow: 0 0 30px rgba(255, 94, 26, 0.5);
    animation: brillo 4s linear infinite;
}
@keyframes brillo { to { background-position: 200% center; } }
#boton:hover { transform: scale(1.04); box-shadow: 0 0 45px rgba(255, 94, 26, 0.8); }

/* Boton de nueva consulta (solo borde) */
#nuevo {
    background: transparent !important; color: #ffb347 !important;
    border: 1px solid #ff7a1a !important; border-radius: 40px !important; font-weight: 700 !important;
}
#nuevo:hover { background: rgba(255, 122, 26, 0.15) !important; }

/* Texto del informe */
.informe strong { color: #ffb347; }
.informe h3 { color: #ff7a1a; }
"""

# Texto que se ve en el informe antes de analizar nada
INFORME_INICIAL = "### Informe del entrenador\n\n*Aquí aparecerán los consejos de Gemini.*"

def tarjetas(jugadores, balon):
    # Crea las dos tarjetas con los datos (jugadores y balon)
    return f"""<div class="stats">
        <div class="stat"><span>JUGADORES</span><b>{jugadores}</b></div>
        <div class="stat"><span>BALÓN</span><b>{balon}</b></div>
    </div>"""

def analizar(image_path):
    # Si no hay imagen, avisamos al usuario
    if image_path is None:
        raise gr.Error("Sube una imagen primero")

    # 1. Subir la imagen al bucket origen con un nombre unico
    key = f"{uuid.uuid4().hex}.jpg"
    with open(image_path, 'rb') as f:
        s3.Object(bucket_source, key).put(Body=f.read())

    # 2. Llamar a la API Flask
    response = requests.post('http://127.0.0.1:5000/api/analyze', json={'key': key})
    if response.status_code != 200:
        raise gr.Error("Error al analizar la imagen")
    data = response.json()

    # 3. Descargar la imagen resultado del bucket destino
    result = s3.Object(bucket_dest, data['result_key']).get()['Body'].read()
    result_path = data['result_key']
    with open(result_path, 'wb') as f:
        f.write(result)

    # 4. Preparar los datos
    stats = tarjetas(data['players'], 'Sí' if data['ball'] else 'No')

    # Devolvemos: imagen analizada, datos, informe y fichero para descargar
    return result_path, stats, data['report'], result_path

def nueva_consulta():
    # Dejamos todas las casillas como al principio para poder hacer otra prueba
    return None, None, tarjetas('-', '-'), INFORME_INICIAL, None

# Interfaz Gradio
with gr.Blocks(title="Mini-Veo") as interface:
    # Estilos y cabecera
    gr.HTML(f"<style>{CSS}</style>")
    gr.HTML("""<div class="cabecera">
                 <h1>Mini-Veo-Basket-AMT</h1>
                 <p>Analiza una jugada de baloncesto y descubre cómo meter la canasta</p>
               </div>""")

    # Tarjetas con los datos (arriba del todo)
    stats = gr.HTML(tarjetas('-', '-'))

    # Fila principal: tres columnas en horizontal desde el principio
    with gr.Row(elem_id="fila"):
        # Columna 1: imagen de entrada y botones
        with gr.Column(elem_classes="cristal"):
            imagen = gr.Image(type="filepath", label="Fotograma del partido")
            boton = gr.Button("Analizar jugada", elem_id="boton")
            nuevo = gr.Button("Nueva consulta", elem_id="nuevo")
        # Columna 2: imagen analizada y descarga
        with gr.Column(elem_classes="cristal"):
            resultado = gr.Image(label="Imagen analizada")
            archivo = gr.File(label="Descargar resultado")
        # Columna 3: consejos del entrenador
        with gr.Column(elem_classes="cristal"):
            informe = gr.Markdown(INFORME_INICIAL, elem_classes="informe")

    # Al pulsar cada boton se ejecuta su funcion
    boton.click(fn=analizar, inputs=imagen, outputs=[resultado, stats, informe, archivo])
    nuevo.click(fn=nueva_consulta, inputs=None, outputs=[imagen, resultado, stats, informe, archivo])

# Arrancamos la interfaz
if __name__ == "__main__":
    interface.launch()