from ultralytics import YOLO

# Load a model
model = YOLO("yolov10n.pt")  # load a pretrained model (recommended for training)

# Train the model
results = model.train(data="./dataset/yolo_dataset/data.yaml", epochs=100, imgsz=640)