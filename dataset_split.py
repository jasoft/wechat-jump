import os
import shutil
import random
 
def make_yolo_dataset(images_folder, labels_folder, output_folder, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    # 创建目标文件夹
    os.makedirs(os.path.join(output_folder, 'images/train'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'images/val'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'images/test'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'labels/train'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'labels/val'), exist_ok=True)
    os.makedirs(os.path.join(output_folder, 'labels/test'), exist_ok=True)
 
    # 获取图片和标签的文件名（不包含扩展名）
    image_files = [os.path.splitext(f)[0] for f in os.listdir(images_folder) if f.endswith('.png')]
    label_files = [os.path.splitext(f)[0] for f in os.listdir(labels_folder) if f.endswith('.txt')]
    matched_files = list(set(image_files) & set(label_files))
 
    # 打乱顺序并划分为训练集、验证集和测试集
    random.shuffle(matched_files)
    train_count = int(len(matched_files) * train_ratio)
    val_count = int(len(matched_files) * val_ratio)
    train_files = matched_files[:train_count]
    val_files = matched_files[train_count:train_count + val_count]
    test_files = matched_files[train_count + val_count:]
 
    # 移动文件到对应文件夹
    def move_files(files, src_images_path, src_labels_path, dst_images_path, dst_labels_path):
        for file in files:
            src_image_file = os.path.join(src_images_path, f"{file}.png")
            src_label_file = os.path.join(src_labels_path, f"{file}.txt")
            dst_image_file = os.path.join(dst_images_path, f"{file}.png")
            dst_label_file = os.path.join(dst_labels_path, f"{file}.txt")
 
            if os.path.exists(src_image_file) and os.path.exists(src_label_file):
                shutil.copy(src_image_file, dst_image_file)
                shutil.copy(src_label_file, dst_label_file)
 
    # 移动文件
    move_files(train_files, images_folder, labels_folder, os.path.join(output_folder, 'images/train'), os.path.join(output_folder, 'labels/train'))
    move_files(val_files, images_folder, labels_folder, os.path.join(output_folder, 'images/val'), os.path.join(output_folder, 'labels/val'))
    move_files(test_files, images_folder, labels_folder, os.path.join(output_folder, 'images/test'), os.path.join(output_folder, 'labels/test'))
 
    print("数据集划分完成！")
 
if __name__ == "__main__":
    images_folder = './dataset/screenshot_dataset/'
    labels_folder = './dataset/yolo_label/'
    output_folder = './dataset/yolo_dataset/'
    make_yolo_dataset(images_folder, labels_folder, output_folder)
