import numpy as np
from ultralytics import YOLO


class Jump:
    def __init__(self, model_path: str) -> None:
        self.model = YOLO(model_path)

    def predict(self, image: str):
        results = self.model(image)
        boxes = sorted(results[0].boxes.xywh.tolist(), key=lambda x: x[1])
        box1, box2 = boxes[0], boxes[1]

        return box1[:2], box2[:2]

if __name__ == "__main__":
    jump = Jump("./runs/detect/train/weights/best.pt")
    print(jump.predict("./dataset/screenshot_dataset/screenshot_20250622_204808.png"))  