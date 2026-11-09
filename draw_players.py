# Importamos los paquetes
import numpy as np
import cv2

# Etiquetas que usamos para el balon
BALL_LABELS = ['Basketball (Ball)', 'Basketball', 'Ball', 'Sports Ball']

def draw_players(buffer, response):
    # Leer imagen desde el buffer
    nparr = np.frombuffer(buffer, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    height, width, _ = img.shape

    players = []
    ball = None
    ball_confidence = 0

    # 1. Recoger las cajas de personas y del balon
    for label in response['Labels']:
        for instance in label['Instances']:
            # Rekognition da la posicion de 0 a 1, la pasamos a pixeles
            box = instance['BoundingBox']
            x = int(width * box['Left'])
            y = int(height * box['Top'])
            w = int(width * box['Width'])
            h = int(height * box['Height'])

            # Jugadores: solo con buena confianza y que no sean muy pequenos (publico lejano)
            if label['Name'] == 'Person' and instance['Confidence'] >= 50 and box['Height'] >= 0.10:
                players.append((x, y, w, h))
            # Balon: nos quedamos con el que tenga mas confianza
            elif label['Name'] in BALL_LABELS and instance['Confidence'] > ball_confidence:
                ball = (x, y, w, h)
                ball_confidence = instance['Confidence']

    # 2. Distancia de cada jugador al balon (entre los centros de las cajas)
    distances = []
    if ball is not None:
        ball_x = ball[0] + ball[2] // 2
        ball_y = ball[1] + ball[3] // 2
        for (x, y, w, h) in players:
            distances.append(int(((x + w // 2 - ball_x) ** 2 + (y + h // 2 - ball_y) ** 2) ** 0.5))

    # 3. El jugador mas cercano al balon es el de menor distancia
    closest = None
    if len(distances) > 0:
        closest = distances.index(min(distances))

    # 4. Dibujar los jugadores (verde, el mas cercano en rojo) y su linea hasta el balon
    for i, (x, y, w, h) in enumerate(players):
        if i == closest:
            color = (0, 0, 255)    # rojo (BGR)
        else:
            color = (0, 255, 0)    # verde (BGR)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 3)
        cv2.putText(img, f"J{i + 1}", (x, max(y - 10, 25)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Linea de pase: del centro del jugador al centro del balon, con la distancia en pixeles
        if ball is not None:
            player_x = x + w // 2
            player_y = y + h // 2
            cv2.line(img, (player_x, player_y), (ball_x, ball_y), color, 2)
            cv2.putText(img, f"{distances[i]} px", ((player_x + ball_x) // 2, (player_y + ball_y) // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # 5. Dibujar el balon en naranja
    if ball is not None:
        x, y, w, h = ball
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 165, 255), 4)
        cv2.putText(img, "BALON", (x, max(y - 10, 25)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)

    print("Draw players task has been successfully run")

    # Codificar la imagen y devolver los datos
    _, res_buffer = cv2.imencode('.jpg', img)
    return res_buffer, len(players), ball is not None