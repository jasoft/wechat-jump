from ultralytics import YOLO

model = YOLO("./runs/detect/train/weights/best.pt")

results = model(["./dataset/screenshot_dataset/screenshot_20250622_204808.png"])

for result in results:
    boxes = result.boxes  # Boxes object for bounding box outputs
    print(boxes.xywh.tolist())

    print(sorted(boxes.xywh.tolist(), key=lambda x: x[1]))
    # masks = result.masks  # Masks object for segmentation masks outputs
    # keypoints = result.keypoints  # Keypoints object for pose outputs
    # probs = result.probs  # Probs object for classification outputs
    # obb = result.obb  # Oriented boxes object for OBB outputs