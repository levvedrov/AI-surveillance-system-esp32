from ultralytics import YOLO
import cv2 as cv

smallModel = YOLO("server/weights/yolov8s.pt")
mediumModel = YOLO("server/weights/yolov8m.pt")
largeModel = YOLO("server/weights/yolov8l.pt")
gunModel = YOLO("server/weights/guns.pt") 


def people(frame, model=mediumModel):
    results = model(frame)
    boxes = results[0].boxes
    amount = 0
    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        if model.names[cls] == 'person' and conf>0.5:
            x1,y1,x2,y2=map(int,box.xyxy[0])
            cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv.putText(frame, f"Person {conf:.2f}", (x1, y1-10),
            cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            amount+=1
    return amount, frame


