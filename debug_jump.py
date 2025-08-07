#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跳一跳调试版本
显示检测框、距离计算和按压时间等调试信息
"""

import cv2
import numpy as np
import time
import random
from main import Jump
from device_controller import WindowsDeviceController, AdbDeviceController
import os


class DebugJump(Jump):
    """带调试功能的Jump类"""

    def __init__(self, model_path: str, device_controller=None, debug=True):
        super().__init__(model_path, device_controller)
        self.debug = debug
        self.debug_window_name = "跳一跳调试窗口"
        self.last_screenshot_path = "./debug_screenshot.png"

        if self.debug:
            cv2.namedWindow(self.debug_window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.debug_window_name, 800, 600)

    def predict_with_debug(self, image_path: str):
        """
        带调试信息的预测函数

        Args:
            image_path: 图片路径

        Returns:
            tuple: (distance, debug_info)
        """
        # 使用原始预测方法
        results = self.model(image_path)

        # 读取图像用于调试显示
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ 无法读取图像: {image_path}")
            return 0, {}

        debug_info = {
            "player_detected": False,
            "platform_detected": False,
            "player_center": None,
            "platform_center": None,
            "distance": 0,
            "detections": [],
        }

        player_center = None
        platform_center = None
        best_platform = None
        best_platform_confidence = 0

        # 处理检测结果
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # 获取边界框坐标
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())

                    # 获取类别名称
                    class_name = self.model.names[class_id]

                    # 计算中心点
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)

                    # 记录检测信息
                    detection = {
                        "class": class_name,
                        "confidence": confidence,
                        "bbox": (int(x1), int(y1), int(x2), int(y2)),
                        "center": (center_x, center_y),
                    }
                    debug_info["detections"].append(detection)

                    # 在图像上绘制检测框
                    color = (0, 255, 0) if class_name == "humen" else (255, 0, 0)
                    cv2.rectangle(
                        image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2
                    )

                    # 绘制标签
                    label = f"{class_name}: {confidence:.2f}"
                    cv2.putText(
                        image,
                        label,
                        (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        2,
                    )

                    # 绘制中心点
                    cv2.circle(image, (center_x, center_y), 5, color, -1)

                    # 记录中心点位置
                    if class_name == "humen":  # 玩家
                        player_center = (center_x, center_y)
                        debug_info["player_detected"] = True
                        debug_info["player_center"] = player_center
                    elif class_name == "cube":  # 平台
                        # 选择置信度最高的平台作为目标
                        if confidence > best_platform_confidence:
                            best_platform_confidence = confidence
                            best_platform = (center_x, center_y)
                            platform_center = (center_x, center_y)
                            debug_info["platform_detected"] = True
                            debug_info["platform_center"] = platform_center

        # 计算距离
        distance = 0
        if player_center and platform_center:
            distance = np.sqrt(
                (platform_center[0] - player_center[0]) ** 2
                + (platform_center[1] - player_center[1]) ** 2
            )
            debug_info["distance"] = distance

            # 绘制距离线
            cv2.line(image, player_center, platform_center, (0, 255, 255), 2)

            # 在线的中点显示距离
            mid_x = (player_center[0] + platform_center[0]) // 2
            mid_y = (player_center[1] + platform_center[1]) // 2
            cv2.putText(
                image,
                f"Distance: {distance:.1f}",
                (mid_x, mid_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )

        # 显示调试信息
        if self.debug:
            self._display_debug_info(image, debug_info)

        return distance, debug_info

    def _display_debug_info(self, image, debug_info):
        """显示调试信息"""
        # 在图像上添加文本信息
        info_y = 30
        line_height = 25

        # 检测状态
        player_status = "✓" if debug_info["player_detected"] else "✗"
        platform_status = "✓" if debug_info["platform_detected"] else "✗"

        cv2.putText(
            image,
            f"Player: {player_status}",
            (10, info_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0) if debug_info["player_detected"] else (0, 0, 255),
            2,
        )
        info_y += line_height

        cv2.putText(
            image,
            f"Platform: {platform_status}",
            (10, info_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0) if debug_info["platform_detected"] else (0, 0, 255),
            2,
        )
        info_y += line_height

        # 距离信息
        cv2.putText(
            image,
            f"Distance: {debug_info['distance']:.1f}",
            (10, info_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        info_y += line_height

        # 检测数量
        cv2.putText(
            image,
            f"Detections: {len(debug_info['detections'])}",
            (10, info_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        # 显示图像
        cv2.imshow(self.debug_window_name, image)
        cv2.waitKey(1)  # 非阻塞显示

    def debug_jump(self, k: float = 7.0, screenshot_path: str = None):
        """
        带调试信息的跳跃函数

        Args:
            k: 跳跃系数
            screenshot_path: 截图保存路径
        """
        if screenshot_path is None:
            screenshot_path = self.last_screenshot_path

        print("\n" + "=" * 50)
        print("🎮 开始新一轮跳跃")

        # 截图
        print("📸 正在截图...")
        if not self.screenshot(screenshot_path):
            print("❌ 截图失败")
            return False

        # 预测并获取调试信息
        print("🔍 正在分析图像...")
        distance, debug_info = self.predict_with_debug(screenshot_path)

        # 显示详细调试信息
        print(f"📊 检测结果:")
        print(f"   玩家检测: {'✓' if debug_info['player_detected'] else '✗'}")
        print(f"   平台检测: {'✓' if debug_info['platform_detected'] else '✗'}")
        print(f"   检测数量: {len(debug_info['detections'])}")

        if debug_info["player_center"]:
            print(f"   玩家位置: {debug_info['player_center']}")
        if debug_info["platform_center"]:
            print(f"   平台位置: {debug_info['platform_center']}")

        print(f"   计算距离: {distance:.2f}")

        # 检查是否检测到必要的对象
        if not debug_info["player_detected"]:
            print("⚠️ 警告: 未检测到玩家")
        if not debug_info["platform_detected"]:
            print("⚠️ 警告: 未检测到目标平台")

        if distance == 0:
            print("❌ 无法计算距离，跳过本次跳跃")
            return False

        # 计算按压时间
        press_time = int(distance * k)
        print(f"⏱️ 按压时间计算: {distance:.2f} × {k} = {press_time}ms")

        # 获取屏幕尺寸用于随机点击位置
        screen_width, screen_height = self.device_controller.get_screen_size()

        # 生成随机点击位置
        x = random.randint(int(screen_width * 0.3), int(screen_width * 0.7))
        y = random.randint(int(screen_height * 0.6), int(screen_height * 0.8))

        print(f"🖱️ 点击位置: ({x}, {y})")
        print(f"⏰ 按压时长: {press_time}ms")

        # 执行点击
        if self.tap(x, y, duration_ms=press_time):
            print("✅ 跳跃执行成功")
        else:
            print("❌ 跳跃执行失败")

        print("⏳ 等待2秒...")
        time.sleep(2)

        return True

    def run_debug_mode(self, k: float = 1.18, max_jumps: int = 100):
        """
        运行调试模式

        Args:
            k: 跳跃系数
            max_jumps: 最大跳跃次数
        """
        print("🚀 启动跳一跳调试模式")
        print(f"📋 参数设置:")
        print(f"   跳跃系数: {k}")
        print(f"   最大跳跃次数: {max_jumps}")
        print(f"   调试窗口: {self.debug}")
        print("\n💡 操作提示:")
        print("   - 按 'q' 键退出")
        print("   - 按 's' 键保存当前截图")
        print("   - 按 'p' 键暂停/继续")
        print("   - 调试窗口会显示检测框和距离信息")

        jump_count = 0
        paused = False

        try:
            while jump_count < max_jumps:
                # 检查键盘输入
                if self.debug:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        print("👋 用户退出")
                        break
                    elif key == ord("s"):
                        # 保存当前截图
                        save_path = f"debug_save_{int(time.time())}.png"
                        if os.path.exists(self.last_screenshot_path):
                            import shutil

                            shutil.copy(self.last_screenshot_path, save_path)
                            print(f"💾 截图已保存: {save_path}")
                    elif key == ord("p"):
                        paused = not paused
                        print(f"⏸️ {'暂停' if paused else '继续'}")

                if paused:
                    time.sleep(0.1)
                    continue

                jump_count += 1
                print(f"\n🎯 第 {jump_count} 次跳跃")

                # 执行调试跳跃
                if not self.debug_jump(k):
                    print("⚠️ 跳跃失败，继续下一次")

        except KeyboardInterrupt:
            print("\n⏹️ 程序被中断")
        finally:
            if self.debug:
                cv2.destroyAllWindows()
            print(f"📈 总共执行了 {jump_count} 次跳跃")


def main():
    """主函数"""
    print("🎮 跳一跳调试工具")
    print("=" * 50)

    # 选择设备控制器
    print("📱 选择控制方式:")
    print("1. Windows窗口控制")
    print("2. ADB手机控制")

    choice = input("请选择 (1/2): ").strip()

    if choice == "1":
        device_controller = WindowsDeviceController("跳一跳")
        print("✅ 使用Windows窗口控制")
    elif choice == "2":
        device_controller = AdbDeviceController()
        print("✅ 使用ADB手机控制")
    else:
        print("❌ 无效选择，使用默认ADB控制")
        device_controller = AdbDeviceController()

    # 创建调试Jump实例
    debug_jump = DebugJump("./best.pt", device_controller, debug=True)

    # 设置参数
    k = float(input("请输入跳跃系数 (默认1.18): ").strip() or "1.18")
    max_jumps = int(input("请输入最大跳跃次数 (默认100): ").strip() or "100")

    # 运行调试模式
    debug_jump.run_debug_mode(k=k, max_jumps=max_jumps)


if __name__ == "__main__":
    main()
