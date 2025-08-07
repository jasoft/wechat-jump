from ultralytics import YOLO
import numpy as np

model = YOLO("./runs/detect/train2/weights/best.pt")

results = model.predict(
    "dataset\\screenshot_dataset\\screenshot_20250807_152924.png", imgsz=640, conf=0.5
)

for result in results:
    boxes = result.boxes  # Boxes object for bounding box outputs
    print(boxes.xywh.cpu().numpy())
    print(boxes.cls.cpu().numpy())
    result.show()
