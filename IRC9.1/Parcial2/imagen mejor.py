import cv2
import mediapipe as mp

# Inicializar MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Inicializar la captura de video
cap = cv2.VideoCapture(0)

with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar el fotograma")
            break

        # Convertir la imagen a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detectar rostros
        results = face_detection.process(frame_rgb)

        # Dibujar las detecciones en la imagen
        if results.detections:
            for detection in results.detections:
                mp_drawing.draw_detection(frame, detection)

        # Mostrar la imagen con detección de rostros
        cv2.imshow("Detector de Rostros - MediaPipe", frame)

        # Salir si se presiona 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Liberar la cámara y cerrar ventanas
cap.release()
cv2.destroyAllWindows()
