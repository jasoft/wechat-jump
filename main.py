from ultralytics import YOLO
import random
import time
import os
import numpy as np

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
        results = self.model.predict(image, conf=0.2, iou=0.9, verbose=False)
        # 保存预测结果
        os.makedirs(self.save_floder, exist_ok=True)
        save_name = f"{self.save_floder}/results_{time.time()}.png"
        results[0].save(filename=save_name)

        # 检查是否有检测结果
        if results[0].boxes is None or len(results[0].boxes) == 0:
            print("⚠️ 未检测到任何对象")
            return 0

        # 获取检测框、类别和置信度
        boxes = results[0].boxes.xywh.cpu().numpy()  # 转换为numpy数组
        cls = results[0].boxes.cls.cpu().numpy()  # 获取类别
        confidences = results[0].boxes.conf.cpu().numpy()  # 获取置信度

        # 筛选出类别为1的检测框 (humen/玩家)
        humen_mask = cls == 1
        humen_boxes = boxes[humen_mask]
        humen_confidences = confidences[humen_mask]

        if len(humen_boxes) == 0:
            print("⚠️ 未检测到玩家")
            return 0

        # 获取玩家位置（选择置信度最高的）
        best_humen_idx = np.argmax(humen_confidences)
        humen_box = humen_boxes[best_humen_idx]
        humen_bottom_y = humen_box[1] + humen_box[3]  # 玩家底部Y坐标

        # 筛选出类别为0的检测框 (cube/平台)
        cube_mask = cls == 0
        cube_boxes = boxes[cube_mask]
        cube_confidences = confidences[cube_mask]

        if len(cube_boxes) == 0:
            print("⚠️ 未检测到平台")
            return 0

        # 过滤掉Y坐标大于等于玩家的平台（已经跳过的或当前站立的平台）
        valid_cubes = []
        valid_confidences = []

        for i, cube_box in enumerate(cube_boxes):
            cube_center_y = cube_box[1] + cube_box[3] / 2
            print(
                f"cube_center_y: {cube_center_y}, humen_center_y: {humen_bottom_y}, cube_box:{cube_box}, cube_confidences[i]:{cube_confidences[i]}"
            )
            # 只保留Y坐标小于玩家的平台（在玩家前方的平台）
            if cube_center_y < humen_bottom_y:
                print(f"有效平台: {cube_box}, 置信度: {cube_confidences[i]}")
                valid_cubes.append(cube_box)
                valid_confidences.append(cube_confidences[i])

        if len(valid_cubes) == 0:
            print("⚠️ 未找到有效的目标平台（所有平台都在玩家后方）")
            return 0

        # 从有效平台中选择最近的一个（Y坐标最大的，即最接近玩家的前方平台）
        valid_cubes = np.array(valid_cubes)

        # 计算所有有效平台到玩家的距离
        distances = np.sqrt(
            (valid_cubes[:, 0] - humen_box[0]) ** 2
            + (valid_cubes[:, 1] - (humen_box[1] + humen_box[3] * 0.5)) ** 2
        )

        # 创建距离大于50的掩码
        valid_distance_mask = distances > 50

        # 如果没有距离大于50的平台，返回0
        if not np.any(valid_distance_mask):
            print("⚠️ 未找到合适距离的目标平台")
            return 0

        # 在距离有效的平台中选择宽度最大的
        valid_distance_cubes = valid_cubes[valid_distance_mask]
        valid_distances = distances[valid_distance_mask]
        target_cube_idx = np.argmax(valid_distance_cubes[:, 2])  # 选择宽度最大的平台
        target_cube = valid_distance_cubes[target_cube_idx]
        distance = valid_distances[target_cube_idx]

        print(
            f"🎯 目标选择: 玩家Y={humen_bottom_y:.1f}, 目标平台Y={target_cube[1]:.1f}, 距离={distance:.1f}"
        )

        return 0 if distance < 50 else round(distance, 3)  # 距离小于50返回0

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
        time.sleep(press_time / 1000 + 1)


if __name__ == "__main__":
    # 可以选择使用ADB控制器或Windows控制器
    # device = AdbDeviceController()  # 使用ADB控制Android手机
    device = WindowsDeviceController("跳一跳")  # 使用Windows窗口控制

    # jump = Jump("./best.pt")  # 默认使用ADB控制器
    jump = Jump("./best.pt", WindowsDeviceController("跳一跳"))  # 使用Windows控制器

    # jump.screenshot()
    # print(jump.predict("./iphone.png"))
    while True:
        jump.jump(k=1.61)
