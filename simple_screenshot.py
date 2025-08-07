#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import subprocess
import datetime
import argparse
from device_controller import AdbDeviceController, WindowsDeviceController

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='自动截图工具')
    parser.add_argument('--mode', choices=['adb', 'windows'], default='adb',
                        help='截图模式: adb (Android手机) 或 windows (Windows窗口)')
    parser.add_argument('--window-title', default='跳一跳',
                        help='Windows窗口标题 (仅在windows模式下使用)')
    parser.add_argument('--interval', type=int, default=2,
                        help='截图间隔时间(秒)')
    parser.add_argument('--output-dir', default='dataset/screenshot_dataset',
                        help='截图保存目录')

    args = parser.parse_args()

    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)

    # 根据模式选择控制器
    if args.mode == 'adb':
        controller = AdbDeviceController()
        print("📱 开始ADB截图...")
        print("请确保:")
        print("1. 手机已连接并开启USB调试")
        print("2. 已安装ADB工具")
    else:
        try:
            controller = WindowsDeviceController(args.window_title)
            print(f"🖥️ 开始Windows窗口截图 (窗口: {args.window_title})...")
            print("请确保:")
            print(f"1. 名为'{args.window_title}'的窗口正在运行")
            print("2. 窗口可见且未被遮挡")
            print("3. 程序会自动激活窗口进行截图")
        except Exception as e:
            print(f"❌ 无法初始化Windows控制器: {e}")
            return

    print(f"📁 截图将保存到 {args.output_dir}/ 目录")
    print(f"⏰ 每{args.interval}秒截图一次")
    print("🛑 按 Ctrl+C 停止\n")

    count = 0
    try:
        while True:
            # 生成文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{args.output_dir}/screenshot_{timestamp}.png"

            # 使用控制器截图
            if controller.screenshot(filename):
                count += 1
                print(f"📸 第 {count} 张截图已保存: {filename}")
            else:
                print(f"❌ 截图失败")

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print(f"\n✅ 截图完成，共保存 {count} 张截图到 {args.output_dir}/ 目录")
    except Exception as e:
        print(f"❌ 错误: {e}")
        if args.mode == 'adb':
            print("ADB模式故障排除:")
            print("1. 检查手机连接: adb devices")
            print("2. 重启ADB服务: adb kill-server && adb start-server")
        else:
            print("Windows模式故障排除:")
            print(f"1. 确认窗口'{args.window_title}'存在且可见")
            print("2. 尝试使用不同的窗口标题")
            print("3. 确保窗口没有被其他程序遮挡")
            print("4. 检查是否有足够权限激活窗口")

if __name__ == "__main__":
    main()
