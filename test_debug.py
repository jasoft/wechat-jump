#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试调试功能
"""

from debug_jump import DebugJump
from device_controller import WindowsDeviceController
import os


def test_debug_analysis():
    """测试调试分析功能"""
    print("🧪 测试调试分析功能")
    
    # 创建Windows控制器
    try:
        device_controller = WindowsDeviceController("跳一跳")
        print("✅ Windows控制器创建成功")
    except Exception as e:
        print(f"❌ Windows控制器创建失败: {e}")
        return
    
    # 创建调试Jump实例
    debug_jump = DebugJump("./best.pt", device_controller, debug=False)  # 不显示窗口
    
    # 测试截图和分析
    screenshot_path = "./test_debug_screenshot.png"
    
    print("📸 正在截图...")
    if debug_jump.screenshot(screenshot_path):
        print("✅ 截图成功")
        
        print("🔍 正在分析...")
        distance, debug_info = debug_jump.predict_with_debug(screenshot_path)
        
        print(f"\n📊 分析结果:")
        print(f"   玩家检测: {'✓' if debug_info['player_detected'] else '✗'}")
        print(f"   平台检测: {'✓' if debug_info['platform_detected'] else '✗'}")
        print(f"   检测数量: {len(debug_info['detections'])}")
        print(f"   计算距离: {distance:.2f}")
        
        if debug_info['player_center']:
            print(f"   玩家位置: {debug_info['player_center']}")
        if debug_info['platform_center']:
            print(f"   平台位置: {debug_info['platform_center']}")
        
        # 显示所有检测到的对象
        print(f"\n🔍 检测详情:")
        for i, detection in enumerate(debug_info['detections']):
            print(f"   {i+1}. {detection['class']} (置信度: {detection['confidence']:.3f})")
            print(f"      中心点: {detection['center']}")
        
        # 计算按压时间
        if distance > 0:
            k = 1.18
            press_time = int(distance * k)
            print(f"\n⏱️ 按压时间计算:")
            print(f"   距离: {distance:.2f} 像素")
            print(f"   系数: {k}")
            print(f"   按压时间: {press_time} ms")
        
        return True
    else:
        print("❌ 截图失败")
        return False


def test_single_jump():
    """测试单次跳跃"""
    print("\n🎮 测试单次跳跃")
    
    try:
        device_controller = WindowsDeviceController("跳一跳")
        debug_jump = DebugJump("./best.pt", device_controller, debug=False)
        
        # 执行一次调试跳跃
        result = debug_jump.debug_jump(k=1.18)
        
        if result:
            print("✅ 跳跃测试成功")
        else:
            print("❌ 跳跃测试失败")
        
        return result
        
    except Exception as e:
        print(f"❌ 跳跃测试异常: {e}")
        return False


def main():
    """主函数"""
    print("🚀 跳一跳调试功能测试")
    print("=" * 50)
    
    # 测试分析功能
    analysis_success = test_debug_analysis()
    
    if analysis_success:
        # 测试跳跃功能
        jump_success = test_single_jump()
        
        print(f"\n📈 测试结果:")
        print(f"   分析功能: {'✅ 成功' if analysis_success else '❌ 失败'}")
        print(f"   跳跃功能: {'✅ 成功' if jump_success else '❌ 失败'}")
        
        if analysis_success and jump_success:
            print(f"\n🎉 所有测试通过！")
            print(f"💡 现在可以运行完整的调试模式:")
            print(f"   uv run python debug_jump.py")
        else:
            print(f"\n⚠️ 部分测试失败，请检查配置")
    else:
        print(f"\n❌ 基础分析功能失败，请检查模型和设备连接")


if __name__ == "__main__":
    main()
