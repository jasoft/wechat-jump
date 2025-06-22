#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import subprocess
import datetime

def main():
    # 创建dataset目录
    os.makedirs("dataset", exist_ok=True)
    
    print("📱 开始ADB截图...")
    print("📁 截图将保存到 dataset/ 目录")
    print("⏰ 每2秒截图一次")
    print("🛑 按 Ctrl+C 停止\n")
    
    count = 0
    try:
        while True:
            # 生成文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dataset/screenshot_dataset/screenshot_{timestamp}.png"
            
            # 截图并传输
            subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/temp_screenshot.png"], check=True)
            subprocess.run(["adb", "pull", "/sdcard/temp_screenshot.png", filename], check=True)
            subprocess.run(["adb", "shell", "rm", "/sdcard/temp_screenshot.png"], check=True)
            
            count += 1
            print(f"📸 第 {count} 张截图已保存: {filename}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print(f"\n✅ 截图完成，共保存 {count} 张截图到 dataset/ 目录")
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("请确保:")
        print("1. 手机已连接并开启USB调试")
        print("2. 已安装ADB工具")

if __name__ == "__main__":
    main()