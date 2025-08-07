#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO模型训练脚本
用于训练跳一跳游戏的目标检测模型
"""

import os
import sys
from ultralytics import YOLO
import yaml
from pathlib import Path

def check_dataset_structure():
    """检查数据集结构是否完整"""
    print("🔍 检查数据集结构...")
    
    required_paths = [
        "dataset/yolo_dataset/data.yaml",
        "dataset/yolo_dataset/images/train",
        "dataset/yolo_dataset/images/val", 
        "dataset/yolo_dataset/images/test",
        "dataset/yolo_dataset/labels/train",
        "dataset/yolo_dataset/labels/val",
        "dataset/yolo_dataset/labels/test"
    ]
    
    missing_paths = []
    for path in required_paths:
        if not os.path.exists(path):
            missing_paths.append(path)
    
    if missing_paths:
        print("❌ 缺少以下文件或目录:")
        for path in missing_paths:
            print(f"   - {path}")
        return False
    
    # 检查数据集文件数量
    train_images = len(list(Path("dataset/yolo_dataset/images/train").glob("*.png")))
    train_labels = len(list(Path("dataset/yolo_dataset/labels/train").glob("*.txt")))
    val_images = len(list(Path("dataset/yolo_dataset/images/val").glob("*.png")))
    val_labels = len(list(Path("dataset/yolo_dataset/labels/val").glob("*.txt")))
    
    print(f"📊 数据集统计:")
    print(f"   训练集: {train_images} 图片, {train_labels} 标签")
    print(f"   验证集: {val_images} 图片, {val_labels} 标签")
    
    if train_images == 0 or val_images == 0:
        print("❌ 训练集或验证集为空")
        return False
    
    if train_images != train_labels or val_images != val_labels:
        print("⚠️ 警告: 图片和标签文件数量不匹配")
    
    print("✅ 数据集结构检查通过")
    return True

def load_config():
    """加载数据集配置"""
    config_path = "dataset/yolo_dataset/data.yaml"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print(f"📋 数据集配置:")
        print(f"   类别数量: {config['nc']}")
        print(f"   类别名称: {config['names']}")
        return config
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return None

def train_model(epochs=100, batch_size=16, img_size=640, model_name="yolov8n.pt"):
    """训练YOLO模型"""
    print(f"🚀 开始训练YOLO模型...")
    print(f"   模型: {model_name}")
    print(f"   训练轮数: {epochs}")
    print(f"   批次大小: {batch_size}")
    print(f"   图片尺寸: {img_size}")
    
    try:
        # 加载预训练模型
        model = YOLO(model_name)
        
        # 开始训练
        results = model.train(
            data="./dataset/yolo_dataset/data.yaml",
            epochs=epochs,
            batch=batch_size,
            imgsz=img_size,
            patience=50,
            save=True,
            device='auto',  # 自动选择GPU或CPU
            workers=4,
            project='runs/detect',
            name='train',
            exist_ok=True,
            pretrained=True,
            optimizer='auto',
            verbose=True,
            seed=42,
            deterministic=True,
            single_cls=False,
            rect=False,
            cos_lr=False,
            close_mosaic=10,
            resume=False,
            amp=True,
            fraction=1.0,
            profile=False,
            freeze=None,
            lr0=0.01,
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3.0,
            warmup_momentum=0.8,
            warmup_bias_lr=0.1,
            box=7.5,
            cls=0.5,
            dfl=1.5,
            pose=12.0,
            kobj=2.0,
            label_smoothing=0.0,
            nbs=64,
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=0.0,
            translate=0.1,
            scale=0.5,
            shear=0.0,
            perspective=0.0,
            flipud=0.0,
            fliplr=0.5,
            mosaic=1.0,
            mixup=0.0,
            copy_paste=0.0
        )
        
        print("✅ 训练完成!")
        print(f"📁 模型保存在: runs/detect/train/weights/")
        print(f"📊 训练结果: {results}")
        
        return results
        
    except Exception as e:
        print(f"❌ 训练失败: {e}")
        return None

def validate_model(model_path="runs/detect/train/weights/best.pt"):
    """验证训练好的模型"""
    if not os.path.exists(model_path):
        print(f"❌ 模型文件不存在: {model_path}")
        return
    
    print(f"🧪 验证模型: {model_path}")
    
    try:
        model = YOLO(model_path)
        
        # 在验证集上评估
        results = model.val(data="./dataset/yolo_dataset/data.yaml")
        
        print("✅ 模型验证完成!")
        print(f"📊 验证结果: {results}")
        
        return results
        
    except Exception as e:
        print(f"❌ 模型验证失败: {e}")
        return None

def main():
    """主函数"""
    print("🎮 跳一跳YOLO模型训练")
    print("=" * 50)
    
    # 检查数据集结构
    if not check_dataset_structure():
        print("❌ 数据集结构检查失败，请修复后重试")
        return
    
    # 加载配置
    config = load_config()
    if not config:
        print("❌ 配置加载失败")
        return
    
    # 训练参数
    epochs = 100
    batch_size = 16
    img_size = 640
    model_name = "yolov8n.pt"  # 可选: yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
    
    print(f"\n🎯 训练参数:")
    print(f"   预训练模型: {model_name}")
    print(f"   训练轮数: {epochs}")
    print(f"   批次大小: {batch_size}")
    print(f"   图片尺寸: {img_size}")
    
    # 开始训练
    results = train_model(epochs, batch_size, img_size, model_name)
    
    if results:
        # 验证模型
        validate_model()
        
        print("\n🎉 训练流程完成!")
        print("💡 使用提示:")
        print("1. 最佳模型保存在: runs/detect/train/weights/best.pt")
        print("2. 可以将best.pt复制为./best.pt用于游戏")
        print("3. 查看训练结果: runs/detect/train/")
    else:
        print("❌ 训练失败")

if __name__ == "__main__":
    main()
