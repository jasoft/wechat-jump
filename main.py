from ultralytics import YOLO
import random
import time
import os
import numpy as np
import datetime
from device_controller import (
    DeviceController,
    AdbDeviceController,
    WindowsDeviceController,
)


class Jump:
    def __init__(
        self, model_path: str, device_controller: DeviceController = None
    ) -> None:
        self.model = YOLO(model_path)
        self.save_floder = f"./dataset/predict_{int(time.time())}"
        # 如果没有指定设备控制器，默认使用ADB控制器
        self.device_controller = (
            device_controller if device_controller else AdbDeviceController()
        )

    def predict(self, image: str):
        results = self.model.predict(image, conf=0.6, iou=0.9, verbose=False)
        # 保存预测结果
        os.makedirs(self.save_floder, exist_ok=True)
        save_name = f"{self.save_floder}/results_{time.time()}.png"
        results[0].save(filename=save_name)

        # 获取检测框和类别
        boxes = results[0].boxes.xywh.cpu().numpy()  # 转换为numpy数组
        cls = results[0].boxes.cls.cpu().numpy()  # 获取类别

        # 筛选出类别为0的检测框 cube
        cube_boxes = boxes[cls == 0]
        cube_boxes = sorted(cube_boxes, key=lambda x: x[1])
        # 筛选出类别为1的检测框
        humen_boxes = boxes[cls == 1]

        # 计算距离
        if len(cube_boxes) > 0 and len(humen_boxes) > 0:
            cube_box = cube_boxes[0]
            humen_box = humen_boxes[0]
            # 计算距离
            distance = np.sqrt(
                (cube_box[0] - humen_box[0]) ** 2
                + (cube_box[1] - (humen_box[1] + humen_box[3] * 0.5)) ** 2
            )
            return round(distance, 3)
        else:
            return 0

    def screenshot(self, save_path: str = "./iphone.png"):
        """
        截取设备屏幕

        Args:
            save_path: 截图保存路径
        """
        return self.device_controller.screenshot(save_path)

    def tap(self, x: int, y: int, duration_ms: int = 100):
        """
        在设备上进行点击操作

        Args:
            x: 点击位置的x坐标
            y: 点击位置的y坐标
            duration_ms: 按压持续时间，单位毫秒
        """
        return self.device_controller.tap(x, y, duration_ms)

    def jump(self, k: float = 7.0, screenshot_path: str = "./iphone.png"):
        # 截图
        self.screenshot(screenshot_path)
        distance = self.predict(screenshot_path)
        print(f"距离: {distance}")

        # 计算按压时间 根据设备分辨率不同按压时间不同（系数 k 不同）
        press_time = int(distance * k)

        # 获取屏幕尺寸用于随机点击位置
        screen_width, screen_height = self.device_controller.get_screen_size()

        # 模拟按压 位置随机按压（根据屏幕尺寸调整）
        x = random.randint(int(screen_width * 0.3), int(screen_width * 0.7))
        y = random.randint(int(screen_height * 0.6), int(screen_height * 0.8))
        self.tap(x, y, duration_ms=press_time)
        # 等待2秒
        time.sleep(2)


if __name__ == "__main__":
    # 可以选择使用ADB控制器或Windows控制器
    # device = AdbDeviceController()  # 使用ADB控制Android手机
    device = WindowsDeviceController("跳一跳")  # 使用Windows窗口控制

    # jump = Jump("./best.pt")  # 默认使用ADB控制器
    jump = Jump("./best.pt", WindowsDeviceController("跳一跳"))  # 使用Windows控制器

    # jump.screenshot()
    # print(jump.predict("./iphone.png"))
    while True:
        jump.jump(k=1.62)
