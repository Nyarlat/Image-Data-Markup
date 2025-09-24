from ultralytics import YOLO


if __name__ == '__main__':
    model = YOLO("yolo11n-seg.pt")

    results = model.train(data="dataset.yaml", epochs=100, imgsz=640)
