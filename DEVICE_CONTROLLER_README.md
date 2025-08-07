# 设备控制器使用说明

## 概述

本项目已经重构，将ADB连接手机的截图和操作功能抽取为独立的设备控制器类，并实现了统一的接口。现在支持两种控制方式：

1. **ADB控制器** (`AdbDeviceController`) - 控制Android手机
2. **Windows控制器** (`WindowsDeviceController`) - 控制Windows应用窗口

## 架构设计

```
DeviceController (抽象基类)
├── AdbDeviceController (ADB手机控制)
└── WindowsDeviceController (Windows窗口控制)
```

### 核心接口

所有设备控制器都实现以下接口：

- `screenshot(save_path)` - 截取屏幕
- `tap(x, y, duration_ms)` - 点击操作
- `get_screen_size()` - 获取屏幕尺寸

## 使用方法

### 1. ADB控制器（控制Android手机）

```python
from device_controller import AdbDeviceController
from main import Jump

# 创建ADB控制器
adb_controller = AdbDeviceController()

# 使用ADB控制器创建Jump实例
jump = Jump("./best.pt", adb_controller)

# 或者使用默认方式（自动使用ADB控制器）
jump = Jump("./best.pt")

# 开始自动跳跃
while True:
    jump.jump(k=1.18)
```

**前提条件：**
- Android手机已连接并开启USB调试
- 已安装ADB工具
- 手机已授权ADB调试

### 2. Windows控制器（控制Windows窗口）

```python
from device_controller import WindowsDeviceController
from main import Jump

# 创建Windows控制器（查找名为"跳一跳"的窗口）
windows_controller = WindowsDeviceController("跳一跳")

# 使用Windows控制器创建Jump实例
jump = Jump("./best.pt", windows_controller)

# 开始自动跳跃
while True:
    jump.jump(k=1.18)
```

**前提条件：**
- 已安装pywin32: `uv add pywin32`
- 有名为"跳一跳"的Windows窗口正在运行
- 窗口可见且未被遮挡

### 3. 直接使用设备控制器

```python
from device_controller import AdbDeviceController, WindowsDeviceController

# ADB控制器示例
adb = AdbDeviceController()
adb.screenshot("./screenshot.png")  # 截图
width, height = adb.get_screen_size()  # 获取屏幕尺寸
adb.tap(width//2, height//2, 100)  # 点击屏幕中央

# Windows控制器示例
windows = WindowsDeviceController("跳一跳")
windows.screenshot("./screenshot.png")  # 截图
width, height = windows.get_screen_size()  # 获取窗口尺寸
windows.tap(width//2, height//2, 100)  # 点击窗口中央
```

## 安装依赖

### 基础依赖
```bash
uv sync
```

### Windows支持（可选）
```bash
uv add pywin32
```

### 标注工具（可选）
```bash
uv add --group labeling labelimg
```

## 测试

运行基础功能测试：
```bash
uv run python test_controllers.py
```

运行完整测试（需要设备连接）：
```bash
uv run python example_usage.py
```

## 配置说明

### ADB配置
- 临时截图路径：`/sdcard/temp_screenshot.png`
- 本地保存路径：可自定义
- 支持自动获取屏幕尺寸

### Windows配置
- 窗口标题：可在初始化时指定
- 支持窗口查找和自动定位
- 支持相对坐标点击

## 错误处理

### 常见问题

1. **ADB连接失败**
   ```bash
   # 重启ADB服务
   adb kill-server
   adb start-server
   adb devices
   ```

2. **Windows模块未安装**
   ```bash
   uv add pywin32
   ```

3. **找不到Windows窗口**
   - 确保窗口标题正确
   - 确保窗口可见且未最小化
   - 可以修改窗口标题参数

4. **模型文件不存在**
   - 确保`best.pt`文件存在
   - 检查模型路径是否正确

## 扩展开发

要添加新的设备控制器，只需继承`DeviceController`基类并实现三个核心方法：

```python
from device_controller import DeviceController

class MyDeviceController(DeviceController):
    def screenshot(self, save_path: str = "./screenshot.png") -> bool:
        # 实现截图逻辑
        pass
    
    def tap(self, x: int, y: int, duration_ms: int = 100) -> bool:
        # 实现点击逻辑
        pass
    
    def get_screen_size(self) -> tuple:
        # 实现获取屏幕尺寸逻辑
        pass
```

## 性能优化

- ADB控制器：每次截图约需1-2秒
- Windows控制器：每次截图约需0.1-0.5秒
- 建议根据实际需求调整跳跃间隔时间

## 注意事项

1. **权限问题**：确保有足够权限访问设备或窗口
2. **坐标系统**：Windows控制器使用相对窗口坐标，ADB使用绝对屏幕坐标
3. **线程安全**：当前实现不是线程安全的，多线程使用需要额外同步
4. **资源清理**：Windows控制器会自动清理GDI资源

## 更新日志

- v0.1.0: 初始版本，支持ADB和Windows两种控制方式
- 重构了原有的Jump类，使用统一的设备控制器接口
- 添加了完整的错误处理和测试用例
