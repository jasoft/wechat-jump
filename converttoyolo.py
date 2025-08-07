from pylabel import importer

dataset = importer.ImportVOC(path="./dataset/yolo_label/")
dataset.export.ExportToYoloV5()
