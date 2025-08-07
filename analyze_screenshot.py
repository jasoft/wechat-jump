#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图分析工具
分析单张截图的检测结果，显示检测框和调试信息
"""

import cv2
import numpy as np
import argparse
from ultralytics import YOLO
import os


def analyze_image(
    model_path: str, image_path: str, output_path: str = None, show_window: bool = True
):
    """
    分析图像并显示检测结果

    Args:
        model_path: 模型文件路径
        image_path: 图像文件路径
        output_path: 输出图像路径（可选）
        show_window: 是否显示窗口
    """
    print(f"🔍 分析图像: {image_path}")
    print(f"📦 使用模型: {model_path}")

    # 检查文件是否存在
    if not os.path.exists(model_path):
        print(f"❌ 模型文件不存在: {model_path}")
        return

    if not os.path.exists(image_path):
        print(f"❌ 图像文件不存在: {image_path}")
        return

    # 加载模型
    try:
        model = YOLO(model_path)
        print("✅ 模型加载成功")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return

    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ 无法读取图像: {image_path}")
        return

    print(f"📐 图像尺寸: {image.shape[1]}x{image.shape[0]}")

    # 进行预测
    print("🔮 正在进行预测...")
    results = model(image_path)

    # 分析结果
    detections = []
    player_center = None
    platform_center = None
    all_platforms = []  # 存储所有平台信息

    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                # 获取边界框坐标
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = box.conf[0].cpu().numpy()
                class_id = int(box.cls[0].cpu().numpy())

                # 获取类别名称
                class_name = model.names[class_id]

                # 计算中心点
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                # 记录检测信息
                detection = {
                    "class": class_name,
                    "confidence": confidence,
                    "bbox": (int(x1), int(y1), int(x2), int(y2)),
                    "center": (center_x, center_y),
                    "size": (int(x2 - x1), int(y2 - y1)),
                }
                detections.append(detection)

                # 记录特定对象的中心点
                if class_name == "humen":  # 玩家
                    player_center = (center_x, center_y)
                elif class_name == "cube":  # 平台
                    all_platforms.append(
                        {
                            "center": (center_x, center_y),
                            "confidence": confidence,
                            "y": center_y,
                        }
                    )

    # 显示检测结果统计
    print(f"\n📊 检测结果统计:")
    print(f"   总检测数量: {len(detections)}")

    player_count = sum(1 for d in detections if d["class"] == "humen")
    platform_count = sum(1 for d in detections if d["class"] == "cube")

    print(f"   玩家检测: {player_count} 个")
    print(f"   平台检测: {platform_count} 个")

    # 显示详细检测信息
    print(f"\n📋 详细检测信息:")
    for i, detection in enumerate(detections):
        print(f"   {i+1}. {detection['class']}")
        print(f"      置信度: {detection['confidence']:.3f}")
        print(f"      边界框: {detection['bbox']}")
        print(f"      中心点: {detection['center']}")
        print(f"      尺寸: {detection['size']}")

    # 选择目标平台（应用与main.py相同的逻辑）
    if player_center and all_platforms:
        player_y = player_center[1]

        # 过滤掉Y坐标大于等于玩家的平台（已经跳过的或当前站立的平台）
        valid_platforms = [
            p
            for p in all_platforms
            if p["y"] < player_y - 20  # 添加20像素的缓冲区
        ]

        if valid_platforms:
            # 选择最近的前方平台（Y坐标最大的）
            target_platform = max(valid_platforms, key=lambda p: p["y"])
            platform_center = target_platform["center"]

            print(f"\n🎯 平台选择逻辑:")
            print(f"   玩家Y坐标: {player_y}")
            print(f"   总平台数: {len(all_platforms)}")
            print(f"   有效平台数: {len(valid_platforms)}")
            print(f"   选择的平台Y坐标: {target_platform['y']}")
            print(f"   选择的平台置信度: {target_platform['confidence']:.3f}")
        else:
            print(f"\n⚠️ 平台选择问题:")
            print(f"   玩家Y坐标: {player_y}")
            print(f"   所有平台Y坐标: {[p['y'] for p in all_platforms]}")
            print(f"   未找到有效的目标平台（所有平台都在玩家后方）")
            platform_center = None

    # 计算距离
    distance = 0
    if player_center and platform_center:
        distance = np.sqrt(
            (platform_center[0] - player_center[0]) ** 2
            + (platform_center[1] - player_center[1]) ** 2
        )
        print(f"\n📏 距离计算:")
        print(f"   玩家位置: {player_center}")
        print(f"   平台位置: {platform_center}")
        print(f"   欧几里得距离: {distance:.2f} 像素")

        # 计算不同跳跃系数下的按压时间
        print(f"\n⏱️ 按压时间计算:")
        for k in [0.5, 1.0, 1.18, 1.5, 2.0]:
            press_time = int(distance * k)
            print(f"   k={k}: {press_time}ms")
    else:
        print(f"\n⚠️ 无法计算距离:")
        if not player_center:
            print("   - 未检测到玩家")
        if not platform_center:
            print("   - 未检测到平台")

    # 绘制检测结果
    result_image = image.copy()

    # 绘制检测框和标签
    for detection in detections:
        x1, y1, x2, y2 = detection["bbox"]
        center_x, center_y = detection["center"]
        class_name = detection["class"]
        confidence = detection["confidence"]

        # 选择颜色
        if class_name == "humen":  # 玩家
            color = (0, 255, 0)  # 绿色
        elif class_name == "cube":  # 平台
            color = (255, 0, 0)  # 蓝色
        else:
            color = (0, 255, 255)  # 黄色

        # 绘制边界框
        cv2.rectangle(result_image, (x1, y1), (x2, y2), color, 2)

        # 绘制标签
        label = f"{class_name}: {confidence:.2f}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        cv2.rectangle(
            result_image,
            (x1, y1 - label_size[1] - 10),
            (x1 + label_size[0], y1),
            color,
            -1,
        )
        cv2.putText(
            result_image,
            label,
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
        )

        # 绘制中心点
        cv2.circle(result_image, (center_x, center_y), 5, color, -1)
        cv2.putText(
            result_image,
            f"({center_x},{center_y})",
            (center_x + 10, center_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            color,
            1,
        )

    # 绘制距离线
    if player_center and platform_center:
        cv2.line(result_image, player_center, platform_center, (0, 255, 255), 2)

        # 在线的中点显示距离
        mid_x = (player_center[0] + platform_center[0]) // 2
        mid_y = (player_center[1] + platform_center[1]) // 2
        cv2.putText(
            result_image,
            f"Distance: {distance:.1f}",
            (mid_x, mid_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2,
        )

    # 添加统计信息到图像
    info_y = 30
    line_height = 25

    cv2.putText(
        result_image,
        f"Detections: {len(detections)}",
        (10, info_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )
    info_y += line_height

    cv2.putText(
        result_image,
        f"Player: {player_count}",
        (10, info_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2,
    )
    info_y += line_height

    cv2.putText(
        result_image,
        f"Platform: {platform_count}",
        (10, info_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 0, 0),
        2,
    )
    info_y += line_height

    if distance > 0:
        cv2.putText(
            result_image,
            f"Distance: {distance:.1f}",
            (10, info_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2,
        )

    # 保存结果图像
    if output_path:
        cv2.imwrite(output_path, result_image)
        print(f"💾 结果图像已保存: {output_path}")

    # 显示图像
    if show_window:
        window_name = "检测结果分析"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 600)
        cv2.imshow(window_name, result_image)

        print(f"\n💡 操作提示:")
        print("   - 按任意键关闭窗口")
        print("   - 绿色框: 玩家")
        print("   - 蓝色框: 平台")
        print("   - 黄色线: 距离连线")

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return {
        "detections": detections,
        "player_center": player_center,
        "platform_center": platform_center,
        "distance": distance,
        "player_count": player_count,
        "platform_count": platform_count,
    }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="跳一跳截图分析工具")
    parser.add_argument("--model", default="./best.pt", help="模型文件路径")
    parser.add_argument("--image", required=True, help="图像文件路径")
    parser.add_argument("--output", help="输出图像路径")
    parser.add_argument("--no-window", action="store_true", help="不显示窗口")

    args = parser.parse_args()

    print("🔍 跳一跳截图分析工具")
    print("=" * 50)

    # 分析图像
    result = analyze_image(
        model_path=args.model,
        image_path=args.image,
        output_path=args.output,
        show_window=not args.no_window,
    )

    if result:
        print("\n✅ 分析完成")
    else:
        print("\n❌ 分析失败")


if __name__ == "__main__":
    main()
