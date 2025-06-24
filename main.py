import numpy as np
from ultralytics import YOLO
import subprocess
import random
import time
import os


class Jump:
    def __init__(self, model_path: str) -> None:
        self.model = YOLO(model_path)
        self.save_floder = f"./dataset/predict_{int(time.time())}"

    def predict(self, image: str):
        results = self.model.predict(image, conf=0.45, iou=0.01)
        # 保存预测结果
        os.makedirs(self.save_floder, exist_ok=True)
        save_name = f"{self.save_floder}/results_{time.time()}.png"
        results[0].save(filename=save_name)

        boxes_xywh = sorted(results[0].boxes.xywh.tolist(), key=lambda x: x[1])
        box1, box2 = boxes_xywh[0], boxes_xywh[1]

        # 计算两个框框中心点 欧氏距离
        center1_x, center1_y = box1[0], box1[1]
        center2_x, center2_y = box2[0], box2[1]

        # 计算欧氏距离
        distance = np.sqrt((center1_x - center2_x) ** 2 + (center1_y - center2_y) ** 2)

        return round(distance, 3)

    # 使用adb控制手机屏幕截图，并将截图传输到本机，同时删除手机目录的截图
    def adb_screenshot(self):
        # 截图并传输
        subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/temp_screenshot.png"], check=True)
        subprocess.run(["adb", "pull", "/sdcard/temp_screenshot.png", "./iphone.png"], check=True)
        subprocess.run(["adb", "shell", "rm", "/sdcard/temp_screenshot.png"], check=True)

    # 使用 adb 模拟按压
    def adb_tap(self, x: int, y: int, duration_ms: int = 100):
        """
        使用adb模拟手机屏幕按压
        :param x: 按压位置的x坐标
        :param y: 按压位置的y坐标  
        :param duration_ms: 按压持续时间，单位毫秒
        """
        subprocess.run(["adb", "shell", "input", "swipe", str(x), str(y), str(x), str(y), str(duration_ms)], check=True)
        print(f"模拟按压位置: ({x}, {y}), 持续时间: {duration_ms}ms")

    def jump(self, k: float = 7.0):
        self.adb_screenshot()
        distance = self.predict("./iphone.png")
        print(f"距离: {distance}")

        # 计算按压时间 根据手机分辨率不同按压时间不同（系数 k 不同）
        press_time = int(distance * k)

        # 模拟按压 位置随机按压
        x = random.randint(300, 700)
        y = random.randint(1000, 1200)
        self.adb_tap(x, y, duration_ms = press_time)
        # 等待1秒
        time.sleep(2)

    

if __name__ == "__main__":
    jump = Jump("./runs/detect/train/weights/best.pt")
    # jump.adb_screenshot()
    # print(jump.predict("./iphone.png"))
    while True:
        jump.jump(k=1.2)
