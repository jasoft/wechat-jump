#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备控制器使用示例
演示如何使用ADB控制器和Windows控制器
"""

from main import Jump
from device_controller import AdbDeviceController, WindowsDeviceController


def test_adb_controller():
    """测试ADB控制器"""
    print("=== 测试ADB控制器 ===")
    
    try:
        # 创建ADB控制器
        adb_controller = AdbDeviceController()
        
        # 测试截图
        print("正在测试ADB截图...")
        if adb_controller.screenshot("./test_adb_screenshot.png"):
            print("✅ ADB截图成功")
        else:
            print("❌ ADB截图失败")
            return False
        
        # 获取屏幕尺寸
        width, height = adb_controller.get_screen_size()
        print(f"📱 手机屏幕尺寸: {width}x{height}")
        
        # 测试点击（在屏幕中央点击）
        print("正在测试ADB点击...")
        if adb_controller.tap(width // 2, height // 2, 100):
            print("✅ ADB点击成功")
        else:
            print("❌ ADB点击失败")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ ADB控制器测试失败: {e}")
        return False


def test_windows_controller():
    """测试Windows控制器"""
    print("\n=== 测试Windows控制器 ===")
    
    try:
        # 创建Windows控制器
        windows_controller = WindowsDeviceController("跳一跳")
        
        # 测试截图
        print("正在测试Windows截图...")
        if windows_controller.screenshot("./test_windows_screenshot.png"):
            print("✅ Windows截图成功")
        else:
            print("❌ Windows截图失败")
            return False
        
        # 获取窗口尺寸
        width, height = windows_controller.get_screen_size()
        print(f"🖥️ 窗口尺寸: {width}x{height}")
        
        # 测试点击（在窗口中央点击）
        print("正在测试Windows点击...")
        if windows_controller.tap(width // 2, height // 2, 100):
            print("✅ Windows点击成功")
        else:
            print("❌ Windows点击失败")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Windows控制器测试失败: {e}")
        return False


def test_jump_with_adb():
    """测试使用ADB控制器的Jump类"""
    print("\n=== 测试Jump类 + ADB控制器 ===")
    
    try:
        # 使用ADB控制器创建Jump实例
        adb_controller = AdbDeviceController()
        jump = Jump("./best.pt", adb_controller)
        
        # 测试截图
        print("正在测试Jump类截图...")
        if jump.screenshot("./test_jump_adb.png"):
            print("✅ Jump类ADB截图成功")
        else:
            print("❌ Jump类ADB截图失败")
            return False
            
        # 测试预测（如果模型文件存在）
        try:
            distance = jump.predict("./test_jump_adb.png")
            print(f"🎯 预测距离: {distance}")
        except Exception as e:
            print(f"⚠️ 预测失败（可能是模型文件不存在）: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Jump类ADB测试失败: {e}")
        return False


def test_jump_with_windows():
    """测试使用Windows控制器的Jump类"""
    print("\n=== 测试Jump类 + Windows控制器 ===")
    
    try:
        # 使用Windows控制器创建Jump实例
        windows_controller = WindowsDeviceController("跳一跳")
        jump = Jump("./best.pt", windows_controller)
        
        # 测试截图
        print("正在测试Jump类截图...")
        if jump.screenshot("./test_jump_windows.png"):
            print("✅ Jump类Windows截图成功")
        else:
            print("❌ Jump类Windows截图失败")
            return False
            
        # 测试预测（如果模型文件存在）
        try:
            distance = jump.predict("./test_jump_windows.png")
            print(f"🎯 预测距离: {distance}")
        except Exception as e:
            print(f"⚠️ 预测失败（可能是模型文件不存在）: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Jump类Windows测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 开始测试设备控制器...")
    
    # 测试ADB控制器
    adb_success = test_adb_controller()
    
    # 测试Windows控制器
    windows_success = test_windows_controller()
    
    # 测试Jump类与ADB控制器
    jump_adb_success = test_jump_with_adb()
    
    # 测试Jump类与Windows控制器
    jump_windows_success = test_jump_with_windows()
    
    # 总结测试结果
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print(f"ADB控制器: {'✅ 成功' if adb_success else '❌ 失败'}")
    print(f"Windows控制器: {'✅ 成功' if windows_success else '❌ 失败'}")
    print(f"Jump类+ADB: {'✅ 成功' if jump_adb_success else '❌ 失败'}")
    print(f"Jump类+Windows: {'✅ 成功' if jump_windows_success else '❌ 失败'}")
    
    if all([adb_success, windows_success, jump_adb_success, jump_windows_success]):
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败，请检查相关配置")
        print("\n💡 提示:")
        print("- ADB测试失败：请确保手机已连接并开启USB调试")
        print("- Windows测试失败：请确保有名为'跳一跳'的窗口正在运行")
        print("- 模型预测失败：请确保best.pt模型文件存在")


if __name__ == "__main__":
    main()
