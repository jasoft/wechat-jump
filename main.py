import numpy as np
from ultralytics import YOLO
import subprocess
import random
import time
import os
import numpy as np


class Jump:
    def __init__(self, model_path: str) -> None:
        self.model = YOLO(model_path)
        self.save_floder = f"./dataset/predict_{int(time.time())}"

    def filter_boxes(self, boxes, scores, iou_threshold=0.5):
        """
        过滤掉重叠的检测框
        :param boxes: 检测框列表，每个检测框为 [x, y, w, h]
        :param scores: 检测框的置信度分数列表
        :param iou_threshold: IOU 阈值，默认为 0.5
        :return: 过滤后的检测框索引列表
        """
        if len(boxes) == 0:
            return []

        # 将检测框转换为左上角和右下角坐标
        x1 = boxes[:, 0] - boxes[:, 2] / 2
        y1 = boxes[:, 1] - boxes[:, 3] / 2
        x2 = boxes[:, 0] + boxes[:, 2] / 2
        y2 = boxes[:, 1] + boxes[:, 3] / 2

        # 计算每个检测框的面积
        areas = (x2 - x1) * (y2 - y1)

        # 按照置信度分数从高到低排序
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)

            # 计算当前检测框与剩余检测框的 IOU
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            inter = w * h

            ovr = inter / (areas[i] + areas[order[1:]] - inter)

            # 保留 IOU 小于阈值的检测框
            inds = np.where(ovr <= iou_threshold)[0]
            order = order[inds + 1]

        return boxes[keep]

    def predict(self, image: str):
        results = self.model.predict(image, conf=0.3, iou=0.5, verbose=False)
        # 保存预测结果
        os.makedirs(self.save_floder, exist_ok=True)
        save_name = f"{self.save_floder}/results_{time.time()}.png"
        results[0].save(filename=save_name)

        # 获取检测框和置信度
        boxes = results[0].boxes.xywh.cpu().numpy()  # 转换为numpy数组
        scores = results[0].boxes.conf.cpu().numpy()  # 获取置信度分数
        
        # 使用filter_boxes过滤重叠的检测框
        filtered_boxes = self.filter_boxes(boxes, scores, iou_threshold=0.3)
        
        # 按y坐标排序过滤后的检测框
        boxes_xywh = sorted(filtered_boxes.tolist(), key=lambda x: x[1])
        
        # 确保至少有两个检测框
        if len(boxes_xywh) < 2:
            print(f"警告: 只检测到 {len(boxes_xywh)} 个目标，可能影响跳跃精度")
            if len(boxes_xywh) == 0:
                return 0
            # 如果只有一个框，返回一个默认距离
            return 100.0
            
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
    jump = Jump("./best.pt")
    # jump.adb_screenshot()
    # print(jump.predict("./iphone.png"))
    while True:
        jump.jump(k=1.2)
