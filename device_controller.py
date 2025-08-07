#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备控制器接口和实现
提供统一的截图和操作接口，支持ADB和Windows窗口两种方式
"""

from abc import ABC, abstractmethod
import subprocess
import time
from PIL import Image

# Windows相关导入（可选）
try:
    import win32gui
    import win32ui
    import win32con
    import win32api
    from ctypes import windll
    import mss

    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    print("⚠️ Windows相关模块未安装，WindowsDeviceController将不可用")


class DeviceController(ABC):
    """设备控制器抽象基类"""

    @abstractmethod
    def screenshot(self, save_path: str = "./screenshot.png") -> bool:
        """
        截取设备屏幕

        Args:
            save_path: 截图保存路径

        Returns:
            bool: 截图是否成功
        """
        pass

    @abstractmethod
    def tap(self, x: int, y: int, duration_ms: int = 100) -> bool:
        """
        在指定位置进行点击/按压操作

        Args:
            x: 点击位置的x坐标
            y: 点击位置的y坐标
            duration_ms: 按压持续时间，单位毫秒

        Returns:
            bool: 操作是否成功
        """
        pass

    @abstractmethod
    def get_screen_size(self) -> tuple:
        """
        获取屏幕尺寸

        Returns:
            tuple: (width, height)
        """
        pass


class AdbDeviceController(DeviceController):
    """ADB设备控制器，用于控制Android手机"""

    def __init__(self):
        """初始化ADB控制器"""
        self.temp_screenshot_path = "/sdcard/temp_screenshot.png"

    def screenshot(self, save_path: str = "./screenshot.png") -> bool:
        """
        使用ADB截取手机屏幕

        Args:
            save_path: 截图保存路径

        Returns:
            bool: 截图是否成功
        """
        try:
            # 截图并传输
            subprocess.run(
                ["adb", "shell", "screencap", "-p", self.temp_screenshot_path],
                check=True,
            )
            subprocess.run(
                ["adb", "pull", self.temp_screenshot_path, save_path], check=True
            )
            subprocess.run(
                ["adb", "shell", "rm", self.temp_screenshot_path], check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"ADB截图失败: {e}")
            return False

    def tap(self, x: int, y: int, duration_ms: int = 100) -> bool:
        """
        使用ADB模拟手机屏幕按压

        Args:
            x: 按压位置的x坐标
            y: 按压位置的y坐标
            duration_ms: 按压持续时间，单位毫秒

        Returns:
            bool: 操作是否成功
        """
        try:
            subprocess.run(
                [
                    "adb",
                    "shell",
                    "input",
                    "swipe",
                    str(x),
                    str(y),
                    str(x),
                    str(y),
                    str(duration_ms),
                ],
                check=True,
            )
            print(f"ADB模拟按压位置: ({x}, {y}), 持续时间: {duration_ms}ms")
            return True
        except subprocess.CalledProcessError as e:
            print(f"ADB点击失败: {e}")
            return False

    def get_screen_size(self) -> tuple:
        """
        获取手机屏幕尺寸

        Returns:
            tuple: (width, height)
        """
        try:
            result = subprocess.run(
                ["adb", "shell", "wm", "size"],
                capture_output=True,
                text=True,
                check=True,
            )
            # 解析输出，格式类似: Physical size: 1080x2340
            size_line = result.stdout.strip()
            if "Physical size:" in size_line:
                size_str = size_line.split("Physical size: ")[1]
                width, height = map(int, size_str.split("x"))
                return (width, height)
            return (1080, 1920)  # 默认尺寸
        except subprocess.CalledProcessError as e:
            print(f"获取屏幕尺寸失败: {e}")
            return (1080, 1920)  # 默认尺寸


class WindowsDeviceController(DeviceController):
    """Windows窗口控制器，用于控制Windows应用窗口"""

    def __init__(self, window_title: str = "跳一跳"):
        """
        初始化Windows控制器

        Args:
            window_title: 目标窗口标题
        """
        if not WINDOWS_AVAILABLE:
            raise ImportError(
                "Windows相关模块未安装，请安装pywin32: pip install pywin32"
            )

        self.window_title = window_title
        self.hwnd = None
        self.mss_instance = mss.mss()
        self._find_window()

    def _find_window(self) -> bool:
        """
        查找目标窗口

        Returns:
            bool: 是否找到窗口
        """

        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if self.window_title in window_text:
                    windows.append(hwnd)
            return True

        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)

        if windows:
            self.hwnd = windows[0]
            print(f"找到窗口: {win32gui.GetWindowText(self.hwnd)}")
            return True
        else:
            print(f"未找到包含'{self.window_title}'的窗口")
            return False

    def _activate_window(self) -> bool:
        """
        激活目标窗口，确保窗口在前台

        Returns:
            bool: 是否成功激活窗口
        """
        if not self.hwnd:
            if not self._find_window():
                return False

        try:
            # 检查窗口是否最小化，如果是则恢复
            if win32gui.IsIconic(self.hwnd):
                win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                time.sleep(0.1)

            # 显示窗口
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

            # 尝试多种方法激活窗口
            try:
                # 方法1: SetForegroundWindow
                win32gui.SetForegroundWindow(self.hwnd)
            except:
                try:
                    # 方法2: 使用ctypes调用
                    windll.user32.SetForegroundWindow(self.hwnd)
                except:
                    pass

            try:
                # 激活窗口
                win32gui.SetActiveWindow(self.hwnd)
            except:
                pass

            # 将窗口置顶
            try:
                win32gui.SetWindowPos(
                    self.hwnd,
                    win32con.HWND_TOP,
                    0,
                    0,
                    0,
                    0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
                )
            except:
                pass

            # 等待窗口激活
            time.sleep(0.1)

            return True
        except Exception as e:
            print(f"激活窗口失败: {e}")
            return False

    def _get_dpi_scale(self) -> float:
        """
        获取DPI缩放比例

        Returns:
            float: DPI缩放比例
        """
        try:
            # 获取系统DPI
            hdc = windll.user32.GetDC(0)
            dpi = windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
            windll.user32.ReleaseDC(0, hdc)

            # 标准DPI是96，计算缩放比例
            scale = dpi / 96.0
            return scale
        except:
            return 1.0  # 默认无缩放

    def _get_window_rect_with_dpi(self) -> tuple:
        """
        获取考虑DPI缩放的窗口位置和大小

        Returns:
            tuple: (left, top, width, height) 实际像素坐标
        """
        if not self.hwnd:
            return (0, 0, 0, 0)

        try:
            # 获取窗口矩形（逻辑坐标）
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)

            # 获取DPI缩放比例
            scale = self._get_dpi_scale()

            # 转换为实际像素坐标
            actual_left = int(left * scale)
            actual_top = int(top * scale)
            actual_width = int((right - left) * scale)
            actual_height = int((bottom - top) * scale)

            return (actual_left, actual_top, actual_width, actual_height)
        except Exception as e:
            print(f"获取窗口位置失败: {e}")
            return (0, 0, 0, 0)

    def screenshot(self, save_path: str = "./screenshot.png") -> bool:
        """
        截取Windows窗口屏幕（支持高DPI）

        Args:
            save_path: 截图保存路径

        Returns:
            bool: 截图是否成功
        """
        if not self.hwnd:
            if not self._find_window():
                return False

        # 激活窗口确保获取正确图像
        if not self._activate_window():
            print("警告: 无法激活窗口，截图可能不准确")

        try:
            # 获取窗口的客户区坐标（不包含标题栏和边框）
            client_rect = win32gui.GetClientRect(self.hwnd)
            client_width = client_rect[2]
            client_height = client_rect[3]

            # 将客户区坐标转换为屏幕坐标
            client_point = win32gui.ClientToScreen(self.hwnd, (0, 0))
            client_left = client_point[0]
            client_top = client_point[1]

            if client_width <= 0 or client_height <= 0:
                print("错误: 无效的客户区尺寸")
                return False

            print(
                f"客户区坐标: left={client_left}, top={client_top}, width={client_width}, height={client_height}"
            )

            # 使用mss截取客户区
            monitor = {
                "left": client_left,
                "top": client_top,
                "width": client_width,
                "height": client_height,
            }

            print(f"MSS monitor配置: {monitor}")

            # 截图
            screenshot = self.mss_instance.grab(monitor)
            print(f"MSS截图尺寸: {screenshot.size}")

            # 转换为PIL图像并保存
            img = Image.frombytes(
                "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX"
            )
            img.save(save_path)

            print(f"Windows窗口截图已保存 (MSS): {save_path}")

            return True

        except Exception as e:
            print(f"Windows截图失败: {e}")
            return False

    def tap(self, x: int, y: int, duration_ms: int = 100) -> bool:
        """
        在Windows窗口指定位置进行点击操作

        Args:
            x: 点击位置的x坐标（相对于窗口）
            y: 点击位置的y坐标（相对于窗口）
            duration_ms: 按压持续时间，单位毫秒

        Returns:
            bool: 操作是否成功
        """
        if not self.hwnd:
            if not self._find_window():
                return False

        # 激活窗口确保点击准确
        if not self._activate_window():
            print("警告: 无法激活窗口，点击可能不准确")

        try:
            # 将窗口坐标转换为屏幕坐标
            left, top, _, _ = win32gui.GetWindowRect(self.hwnd)
            screen_x = left + x
            screen_y = top + y

            # 获取当前鼠标位置
            original_pos = win32gui.GetCursorPos()

            # 移动鼠标到目标位置
            win32api.SetCursorPos((screen_x, screen_y))

            # 模拟鼠标按下
            win32api.mouse_event(
                win32con.MOUSEEVENTF_LEFTDOWN, screen_x, screen_y, 0, 0
            )

            # 等待指定时间
            time.sleep(duration_ms / 1000.0)

            # 模拟鼠标释放
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, screen_x, screen_y, 0, 0)

            # 恢复鼠标位置
            win32api.SetCursorPos(original_pos)

            print(f"Windows模拟点击位置: ({x}, {y}), 持续时间: {duration_ms}ms")
            return True

        except Exception as e:
            print(f"Windows点击失败: {e}")
            return False

    def get_screen_size(self) -> tuple:
        """
        获取Windows窗口客户区尺寸

        Returns:
            tuple: (width, height) 客户区像素尺寸
        """
        if not self.hwnd:
            if not self._find_window():
                return (800, 600)  # 默认尺寸

        try:
            # 获取客户区尺寸
            client_rect = win32gui.GetClientRect(self.hwnd)
            width = client_rect[2]
            height = client_rect[3]
            return (width, height)
        except Exception as e:
            print(f"获取窗口尺寸失败: {e}")
            return (800, 600)  # 默认尺寸
