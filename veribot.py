import cv2
import os
import numpy as np


class VeriBot3000:
    def __init__(self, model):
        self.trash_model = model

    def detect_trash(self, image_src: str):
        image = cv2.imread(image_src)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (224, 224))
        image = np.expand_dims(image, axis=0)
        image = image / 255.0

        # Predict
        predictions = self.trash_model.predict(image)
        if predictions[0][0] > 0.5:
            return True
        return False

    def detect_manipulation(self, image_src: str):
        # Trash detection
        trash_detected = self.detect_trash(image_src)
        if trash_detected:
            print('Trash detected')
        else:
            print('No trash detected')

    def run(self, image_src: str):
        self.detect_manipulation(image_src)
