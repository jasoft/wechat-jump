from ultralytics import YOLO
import numpy as np
import os
import glob

model = YOLO("./runs/detect/humen/weights/best.pt")

def get_boxes(filename: str):
    results = model.predict(filename, imgsz=640, conf=0.7, iou=0.1, verbose=False)
    results[0].show()
    boxes = results[0].boxes
    boxes_xywhn = boxes.xywhn.cpu().numpy()
    # 转为字符串
    boxes_xywhn_str = boxes_xywhn.astype(str)
    boxes_label = boxes.cls.cpu().numpy().astype(int).astype(str)

    res = ""

    for xywhn, label in zip(boxes_xywhn_str, boxes_label):
        res += label + " " + " ".join(xywhn) + "\n"
    return res

if __name__ == '__main__':
    folder_path = './dataset/recoder'

    # 使用glob获取所有png文件
    png_files = glob.glob(os.path.join(folder_path, '*.png'))

    # 打印结果
    for png_file in png_files:
        predict_result = get_boxes(png_file)
        label_name = png_file.split("/")[-1].split(".")[0]
        with open(f"./dataset/recoder_label/{label_name}.txt", "w") as f:
            f.write(predict_result)
