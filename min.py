import cv2
import numpy as np
from ultralytics import YOLO
import time

model = YOLO('yolov8n.pt')

def apply_gamma_correction(frame, gamma=1.5):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(256)]).astype("uint8")
    return cv2.LUT(frame, table)
cap = cv2.VideoCapture("rtsp://192.168.19.203:8554/live")

start_time = time.time()
frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (640, 480))
    gamma_corrected = apply_gamma_correction(frame, gamma=1.5)

    results = model(gamma_corrected, stream=False)[0]

    person_count = 0
    vehicle_count = 0
    traffic_count = 0

    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        conf = box.conf[0]
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        if label == 'person':
            person_count += 1
        elif label in ['car', 'bus', 'truck', 'motorbike']:
            vehicle_count += 1
        elif label in ['traffic light', 'stop sign']:
            traffic_count += 1

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    cv2.putText(frame, f'Persons: {person_count}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
    cv2.putText(frame, f'Vehicles: {vehicle_count}', (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    cv2.putText(frame, f'Traffic Objects: {traffic_count}', (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

    cv2.imshow("YOLOv8 CCTV Detection", frame)

    frame_count += 1
    elapsed_time = time.time() - start_time
    if elapsed_time > 1:
        fps = frame_count / elapsed_time
        cv2.putText(frame, f'FPS: {fps:.2f}', (10, 450),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
