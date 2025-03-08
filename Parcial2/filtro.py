import cv2
import mediapipe as mp
import numpy as np

# Cargar la imagen del filtro de payaso (PNG)
clown_nose = cv2.imread("clown_nose.png", cv2.IMREAD_UNCHANGED)

# Si la imagen no tiene canal alfa, se agrega
if clown_nose.shape[2] == 3:
    clown_nose = cv2.cvtColor(clown_nose, cv2.COLOR_BGR2BGRA)

# Inicializar MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
cap = cv2.VideoCapture(0)

with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(frame_rgb)

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                h, w, _ = frame.shape
                x, y, box_w, box_h = (int(bboxC.xmin * w), int(bboxC.ymin * h),
                                      int(bboxC.width * w), int(bboxC.height * h))

                # Calcular la posición de la nariz
                nose_x, nose_y = x + box_w // 2, y + int(box_h * 0.55)

                # Redimensionar la nariz
                nose_w, nose_h = box_w // 3, box_h // 5
                clown_nose_resized = cv2.resize(clown_nose, (nose_w, nose_h))

                # Obtener las dimensiones del filtro
                nh, nw, nc = clown_nose_resized.shape

                # Fusionar la imagen con transparencia
                for i in range(nh):
                    for j in range(nw):
                        if clown_nose_resized[i, j, 3] > 0:  # Solo aplicar si no es transparente
                            frame[nose_y + i, nose_x - nw // 2 + j] = clown_nose_resized[i, j, :3]

                # Tomar captura automática
                cv2.imwrite("captura_payaso.png", frame)
                print("📸 Captura guardada: captura_payaso.png")

        cv2.imshow("Filtro de Payaso 🎭", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

