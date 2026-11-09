# Mini-VeoCamBasket-AMT

Aplicación que analiza una foto de baloncesto: detecta jugadores y balón con **Amazon Rekognition**, los dibuja con OpenCV y pide consejos de entrenador a **Gemini**. Interfaz hecha con **Gradio**.

Proyecto de la Unidad 5 del curso de IA y Big Data (IES Portada Alta) Alberto Maldonado Triana.

## Documentación (PDF)

La documentación de la tarea está en este repositorio: [Tarea5.1-AconlaplataformaAWS-AMT.pdf](https://github.com/albertoomaldonadoo/Mini-VeoCamBasket-AMT/blob/main/Tarea5.1-AconlaplataformaAWS-AMT.pdf)

## Cómo iniciar la aplicación

**1. Descargar el proyecto**

```
git clone https://github.com/albertoomaldonadoo/Mini-VeoCamBasket-AMT.git
cd Mini-VeoCamBasket-AMT
```

**2. Instalar las librerías**

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**3. Crear el fichero `.env`**

Copia `.env.example`, llámalo `.env` y rellena tus claves:

```
ACCESS_KEY_ID=
ACCESS_SECRET_KEY=
BUCKET_SOURCE=
BUCKET_DEST=
REGION=eu-west-2
GEMINI_API_KEY=
```

**4. Arrancar la API (terminal 1)**

```
python application.py
```

**5. Arrancar la interfaz (terminal 2, con el entorno activado)**

```
python app_gradio.py
```

**6. Usar la app**

Abre http://127.0.0.1:7860, sube una foto, pulsa **Analizar jugada** y, para otra prueba, **Nueva consulta**.

## Qué necesitas en AWS

- Dos buckets de S3 (origen y destino) en la región `eu-west-2`.
- Un usuario de IAM con los permisos `AmazonS3FullAccess` y `AmazonRekognitionFullAccess`.

## Ficheros

- `application.py`: API Flask y buckets de S3.
- `detect_labels.py`: llamada a Rekognition.
- `draw_players.py`: dibuja jugadores, balón y líneas de pase.
- `gemini_report.py`: consejos de entrenador con Gemini.
- `app_gradio.py`: interfaz web.

## Autor

Alberto Maldonado (AMT)
