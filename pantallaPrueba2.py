import cv2
import numpy as np
import pygame
import mss
import mss.tools
import win32api

# Inicializar pygame y configurar el sonido
pygame.mixer.init()
sound = pygame.mixer.Sound('e:/contador/deteccion de movimiento/sound.wav')  # Reemplaza 'beep.wav' con la ruta de tu archivo de sonido

# Obtener la resolución de la pantalla principal
screen_info = win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[0][0])
screen_size = (screen_info['Work'][2] - screen_info['Work'][0], screen_info['Work'][3] - screen_info['Work'][1])

# Obtener la mitad superior de la pantalla
upper_half_rect = (0, 0, screen_size[0], screen_size[1] // 2)

# Configurar los parámetros del algoritmo de detección de movimiento
sensitivity_threshold = 70  # Ajusta este valor según tu necesidad (valor más bajo = más sensible)

# Variables para el bucle principal
motion_detected = False
previous_frame = None

with mss.mss() as sct:
    monitor = {"top": 0, "left": 0, "width": screen_size[0], "height": screen_size[1]}

    while True:
        # Capturar el fotograma actual de la pantalla
        frame = np.array(sct.grab(monitor))

        # Obtener la mitad superior del fotograma
        upper_half_frame = frame[upper_half_rect[1]:upper_half_rect[1]+upper_half_rect[3],
                                 upper_half_rect[0]:upper_half_rect[0]+upper_half_rect[2]]

        # Convertir el fotograma a escala de grises
        gray_frame = cv2.cvtColor(upper_half_frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

        # Si es el primer fotograma, guárdalo como referencia y continúa al siguiente fotograma
        if previous_frame is None:
            previous_frame = gray_frame
            continue

        # Calcula la diferencia absoluta entre el fotograma actual y el anterior
        frame_delta = cv2.absdiff(previous_frame, gray_frame)

        # Aplica un umbral a la diferencia y dilata la imagen resultante
        _, thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Encuentra los contornos de la imagen umbralizada
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = False

        # Itera sobre los contornos y verifica si son lo suficientemente grandes
        for contour in contours:
            if cv2.contourArea(contour) > sensitivity_threshold:
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(upper_half_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                motion_detected = True

        # Reproducir el sonido si se detecta movimiento
        if motion_detected:
            sound.play()

        # Mostrar la imagen resultante
        cv2.imshow("Motion Detection", upper_half_frame)

        # Salir si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Actualizar el fotograma anterior
        previous_frame = gray_frame

# Liberar los recursos
cv2.destroyAllWindows()
