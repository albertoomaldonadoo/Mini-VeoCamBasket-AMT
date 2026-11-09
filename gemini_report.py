# Importamos los paquetes
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Cargamos las variables de entorno del fichero .env
load_dotenv()

# Crear el cliente de Gemini con la clave del .env
client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

def gemini_report(players, ball, image_bytes, original_bytes):
    # Escribimos la peticion con los datos que ha sacado Rekognition
    prompt = f"""Eres un entrenador de baloncesto de la NBA super experto.
Te paso dos imagenes de la MISMA foto de una jugada:
- La primera es la foto original, sin marcas. Usala para entender la jugada.
- La segunda tiene las marcas de Amazon Rekognition: cajas con los jugadores (J1, J2...), caja naranja con el balon y lineas con la distancia en pixeles. Usala solo para saber que numero es cada jugador.
El jugador en rojo es solo el mas cercano al balon. Estar cerca NO significa tener el balon.
- Jugadores detectados: {players}
- Balon detectado: {'si' if ball else 'no'}

Reglas:
- Antes de nada mira donde esta el balon: en las manos de un jugador, en el aire (pase o tiro) o no se ve. Si esta en el aire, nadie lo tiene todavia.
- Describe solo lo que se ve en la foto. No inventes jugadores, equipos, marcador ni lo que paso antes o despues.
- Si no se ve claro quien ataca y quien defiende, no lo adivines.
- Si lo que marca Rekognition no coincide con lo que ves (por ejemplo una persona del publico), fiate de la foto original.
- Los consejos deben hablar de posiciones, espacios y movimientos que se ven en la foto.

Escribe en español:
**Balon:** donde esta (en manos de un jugador, en el aire o no se ve).
**Jugada:** que se ve en la foto (1 frase).
**Para anotar:** tres acciones concretas para conseguir canasta (lista numerada).
**Error a corregir:** un error que se vea en la imagen y como corregirlo para poder meter la canasta.
Maximo 130 palabras."""

    # Mandamos las dos imagenes y el texto juntos a Gemini
    original = types.Part.from_bytes(data=original_bytes, mime_type='image/jpeg')
    marked = types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')

    # temperature baja = respuestas mas estables y con menos invenciones
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[original, marked, prompt],
        config=types.GenerateContentConfig(temperature=0.3))

    # Devolvemos el texto del informe
    return response.text