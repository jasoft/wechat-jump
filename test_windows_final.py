#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows控制器最终测试脚本
验证截图和点击功能是否正常工作
"""

import time
from device_controller import WindowsDeviceController

def test_windows_controller():
    """测试Windows控制器的所有功能"""
    print("🧪 开始Windows控制器完整测试...")
    
    try:
        # 创建Windows控制器
        controller = WindowsDeviceController("跳一跳")
        print("✅ Windows控制器创建成功")
        
        # 获取窗口尺寸
        width, height = controller.get_screen_size()
        print(f"📐 窗口尺寸: {width} x {height}")
        
        # 测试截图功能
        print("\n📸 测试截图功能...")
        for i in range(3):
            screenshot_path = f"./test_screenshot_{i+1}.png"
            if controller.screenshot(screenshot_path):
                print(f"✅ 截图 {i+1} 成功: {screenshot_path}")
            else:
                print(f"❌ 截图 {i+1} 失败")
            time.sleep(1)
        
        # 测试点击功能
        print(f"\n🖱️ 测试点击功能...")
        test_positions = [
            (width // 4, height // 2),      # 左侧
            (width // 2, height // 2),      # 中央
            (3 * width // 4, height // 2),  # 右侧
        ]
        
        for i, (x, y) in enumerate(test_positions):
            print(f"点击位置 {i+1}: ({x}, {y})")
            if controller.tap(x, y, 100):
                print(f"✅ 点击 {i+1} 成功")
            else:
                print(f"❌ 点击 {i+1} 失败")
            time.sleep(0.5)
        
        print("\n🎉 Windows控制器测试完成！")
        print("请检查生成的截图文件，确认内容是否为跳一跳窗口")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_jump_integration():
    """测试与Jump类的集成"""
    print("\n🎮 测试与Jump类的集成...")
    
    try:
        from main import Jump
        
        # 使用Windows控制器创建Jump实例
        controller = WindowsDeviceController("跳一跳")
        jump = Jump("./best.pt", controller)
        
        print("✅ Jump类集成成功")
        
        # 测试一次截图和预测
        print("📸 测试截图和预测...")
        if jump.screenshot("./test_jump_integration.png"):
            print("✅ Jump类截图成功")
            
            try:
                distance = jump.predict("./test_jump_integration.png")
                print(f"🎯 预测距离: {distance}")
                print("✅ Jump类预测成功")
            except Exception as e:
                print(f"⚠️ 预测失败（可能是模型文件问题）: {e}")
        else:
            print("❌ Jump类截图失败")
        
        return True
        
    except Exception as e:
        print(f"❌ Jump类集成测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始Windows控制器最终测试\n")
    
    # 基础功能测试
    basic_success = test_windows_controller()
    
    # 集成测试
    integration_success = test_jump_integration()
    
    # 总结
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print(f"基础功能测试: {'✅ 通过' if basic_success else '❌ 失败'}")
    print(f"Jump类集成测试: {'✅ 通过' if integration_success else '❌ 失败'}")
    
    if basic_success and integration_success:
        print("\n🎉 所有测试通过！Windows控制器已准备就绪！")
        print("\n💡 使用提示:")
        print("1. 运行 'uv run python main.py' 开始自动跳跃")
        print("2. 运行 'uv run python simple_screenshot.py --mode windows' 进行数据收集")
    else:
        print("\n⚠️ 部分测试失败，请检查配置")
