import os

from ultralytics import YOLO


class TrashDetection:
    def __init__(self, data_folder: str, yaml_file: str):
        self.data_folder = data_folder
        self.yaml_file = yaml_file
        self.home = os.getcwd()
        self.model = self.model()
    
    def train_model(self):
        self.model.train(
            data=f"{self.home}/{self.data_folder}/{self.yaml_file}",
            epochs=100,
            imgsz=640,
        )

    def val_model(self):
        self.model.val()

    def test_model(self):
        self.model.test()

    def model(self):
        # Load pre-trained model
        model = YOLO('yolov8n.pt')
        return model

    def export(self):
        self.train_model()
        self.val_model()
        self.test_model()
        self.model.export()


if __name__ == "__main__":
    td = TrashDetection('dataset', 'data.yaml')
    td.export()
