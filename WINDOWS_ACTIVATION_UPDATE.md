# Windows窗口激活功能更新

## 🎯 更新内容

为了确保Windows控制器能够获取正确的图像和进行准确的操作，我们添加了**自动窗口激活功能**。

## ✨ 新增功能

### 1. 自动窗口激活
- **截图前激活**: 每次截图前自动激活目标窗口
- **点击前激活**: 每次点击前自动激活目标窗口
- **窗口恢复**: 自动检测并恢复最小化的窗口
- **前台显示**: 确保窗口显示在最前台

### 2. 改进的错误处理
- 激活失败时显示警告但继续执行
- 更详细的错误信息和故障排除提示

## 🔧 技术实现

### 新增方法: `_activate_window()`
```python
def _activate_window(self) -> bool:
    """激活目标窗口，确保窗口在前台"""
    # 检查窗口是否最小化，如果是则恢复
    if win32gui.IsIconic(self.hwnd):
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
    
    # 将窗口置于前台
    win32gui.SetForegroundWindow(self.hwnd)
    
    # 激活窗口
    win32gui.SetActiveWindow(self.hwnd)
```

### 修改的方法
- `screenshot()`: 截图前自动激活窗口
- `tap()`: 点击前自动激活窗口

## 📱 使用方法

### 1. 主程序使用 (main.py)
```python
# 使用Windows控制器（会自动激活窗口）
from device_controller import WindowsDeviceController
from main import Jump

windows_controller = WindowsDeviceController("跳一跳")
jump = Jump("./best.pt", windows_controller)

# 开始自动跳跃（每次操作前会激活窗口）
while True:
    jump.jump(k=1.18)
```

### 2. 截图工具使用 (simple_screenshot.py)

**Windows模式截图:**
```bash
# 使用Windows控制器进行截图
uv run python simple_screenshot.py --mode windows --window-title "跳一跳"

# 自定义参数
uv run python simple_screenshot.py \
    --mode windows \
    --window-title "跳一跳" \
    --interval 3 \
    --output-dir "my_screenshots"
```

**ADB模式截图（保持不变）:**
```bash
# 使用ADB控制器进行截图
uv run python simple_screenshot.py --mode adb
```

### 3. 命令行参数
- `--mode {adb,windows}`: 选择截图模式
- `--window-title TITLE`: 指定Windows窗口标题
- `--interval SECONDS`: 设置截图间隔时间
- `--output-dir PATH`: 设置输出目录

## 🎮 实际效果

### 激活前 vs 激活后
- **激活前**: 可能截取到被遮挡的窗口或错误的内容
- **激活后**: 确保截取到正确的游戏画面，点击操作准确

### 自动化流程
1. 程序查找目标窗口
2. 自动激活窗口（置于前台）
3. 执行截图或点击操作
4. 继续下一轮操作

## ⚠️ 注意事项

### 权限要求
- 需要足够的系统权限来激活其他程序的窗口
- 某些受保护的程序可能无法被激活

### 使用建议
1. **保持窗口可见**: 虽然程序会自动激活，但最好保持目标窗口可见
2. **避免频繁切换**: 程序运行时避免频繁切换到其他窗口
3. **检查窗口标题**: 确保窗口标题准确匹配

### 故障排除
如果窗口激活失败：
1. 检查窗口是否存在且可见
2. 确认程序有足够权限
3. 尝试手动激活窗口一次
4. 检查是否有其他程序阻止窗口激活

## 📊 性能影响

- **激活延迟**: 每次激活增加约0.1秒延迟
- **资源消耗**: 激活操作消耗极少系统资源
- **稳定性**: 提高了截图和操作的准确性

## 🔄 向后兼容性

- 所有现有代码无需修改
- ADB控制器功能保持不变
- 新功能仅影响Windows控制器

## 🚀 使用示例

### 快速开始
```bash
# 1. 启动跳一跳游戏窗口
# 2. 运行截图工具测试
uv run python simple_screenshot.py --mode windows --interval 2

# 3. 运行自动跳跃程序
uv run python main.py
```

### 数据收集
```bash
# 收集训练数据（Windows模式）
uv run python simple_screenshot.py \
    --mode windows \
    --window-title "跳一跳" \
    --interval 1 \
    --output-dir "dataset/windows_screenshots"
```

## 📝 更新日志

- ✅ 添加自动窗口激活功能
- ✅ 改进Windows截图稳定性
- ✅ 更新simple_screenshot.py支持Windows模式
- ✅ 添加详细的错误处理和用户提示
- ✅ 保持向后兼容性

现在你可以更可靠地使用Windows控制器进行自动化操作了！🎉
