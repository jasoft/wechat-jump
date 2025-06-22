#!/bin/bash
# ADB安装脚本 for macOS

echo "🔧 开始安装ADB工具..."
echo ""

# 检查是否已安装Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ 未检测到Homebrew"
    echo "正在安装Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew已安装"
fi

echo ""
echo "📦 正在安装Android Platform Tools..."
brew install android-platform-tools

echo ""
echo "🔍 验证安装..."
if command -v adb &> /dev/null; then
    echo "✅ ADB安装成功！"
    echo "版本信息:"
    adb version
else
    echo "❌ ADB安装失败"
    echo "请手动安装：brew install android-platform-tools"
fi

echo ""
echo "📱 接下来请："
echo "1. 在手机上开启开发者选项和USB调试"
echo "2. 使用USB线连接手机到电脑"
echo "3. 运行 'adb devices' 检查连接状态"
echo "4. 运行 'python3 simple_screenshot.py' 开始截图"