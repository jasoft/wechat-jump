#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的控制器测试脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from device_controller import DeviceController, AdbDeviceController, WindowsDeviceController
    print("✅ 成功导入设备控制器模块")
except ImportError as e:
    print(f"❌ 导入设备控制器模块失败: {e}")
    sys.exit(1)

try:
    from main import Jump
    print("✅ 成功导入Jump类")
except ImportError as e:
    print(f"❌ 导入Jump类失败: {e}")
    sys.exit(1)

def test_basic_functionality():
    """测试基本功能"""
    print("\n=== 测试基本功能 ===")
    
    # 测试ADB控制器创建
    try:
        adb_controller = AdbDeviceController()
        print("✅ ADB控制器创建成功")
    except Exception as e:
        print(f"❌ ADB控制器创建失败: {e}")
    
    # 测试Windows控制器创建
    try:
        windows_controller = WindowsDeviceController("跳一跳")
        print("✅ Windows控制器创建成功")
    except Exception as e:
        print(f"❌ Windows控制器创建失败: {e}")
    
    # 测试Jump类创建（使用默认ADB控制器）
    try:
        jump = Jump("./best.pt")
        print("✅ Jump类创建成功（默认ADB控制器）")
    except Exception as e:
        print(f"❌ Jump类创建失败: {e}")
    
    # 测试Jump类创建（使用Windows控制器）
    try:
        windows_controller = WindowsDeviceController("跳一跳")
        jump_windows = Jump("./best.pt", windows_controller)
        print("✅ Jump类创建成功（Windows控制器）")
    except Exception as e:
        print(f"❌ Jump类创建失败（Windows控制器）: {e}")

if __name__ == "__main__":
    print("🧪 开始基本功能测试...")
    test_basic_functionality()
    print("\n✅ 基本功能测试完成")
