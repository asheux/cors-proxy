import cv2
import os
import numpy as np
import PIL

# from ultralytics import YOLO
from datetime import datetime
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from PIL import Image


class VeriBot3000:
    def __init__(self, model = None):
        self.trash_model = model

    def check_image_metadata(self, image_src: str):
        image = Image.open(image_src)
        after_date = datetime.strptime('2024:08:19 20:05:46', '%Y:%m:%d %H:%M:%S')
        exif_data = image._getexif()
        if not exif_data:
            return {'non_original': True}

        info = {PIL.ExifTags.TAGS[k]: v for k, v in exif_data.items()}
        when_taken = None
        image_time_zone = None
        if info:
            # Check when the image was taken
            when_taken = info.get('DateTimeOriginal')
            image_time_zone = info.get('OffsetTimeOriginal')

        if when_taken and datetime.strptime(when_taken, '%Y:%m:%d %H:%M:%S') < after_date:
            return {'old_image': True}

        if image_time_zone and image_time_zone != '+03:00':
            return {'outside': True}

        gps_info = info.get('GPSInfo')
        return self.is_within_kenya(gps_info)

    def get_coordinates(self, gps_info):
        if not gps_info:
            return None, None

        gps_values = {PIL.ExifTags.GPSTAGS.get(k, k): v for k, v in gps_info.items()}
        lat = gps_values.get('GPSLatitude')
        lon = gps_values.get('GPSLongitude')
        lat_ref = gps_values.get('GPSLatitudeRef')
        lon_ref = gps_values.get('GPSLongitudeRef')

        if not lat or not lon:
            return None, None

        lat = self.convert_to_degrees(lat)
        lon = self.convert_to_degrees(lon)
        if not lat or not lon:
            return None, None

        if lat_ref != "N":
            lat = -lat
        if lon_ref != "E":
            lon = -lon
        return lat, lon

    def convert_to_degrees(self, item):
        d, m, s = item
        if d == 'nan' or isinstance(d, PIL.TiffImagePlugin.IFDRational):
            return
        if m == 'nan' or isinstance(m, PIL.TiffImagePlugin.IFDRational):
            return
        return d + (m / 60.0) + (s / 3600.0)

    def is_within_kenya(self, gps_info):
        lat, lon = self.get_coordinates(gps_info)
        if not lat or not lon:
            return {'no_gps_data': True}

        kenya_boundary = Polygon([
            (33.909821, -4.677504),  # Southwest
            (41.855083, -4.677504),  # Southeast
            (41.855083, 5.506),      # Northeast
            (33.909821, 5.506)       # Northwest
        ])

        point = Point(lon, lat)
        return {'yes_gps_and_valid': kenya_boundary.contains(point)}

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

    def trash_detection(self, image_src: str):
        # Trash detection
        trash_detected = self.detect_trash(image_src)
        if trash_detected:
            print('Trash detected')
        else:
            print('No trash detected')

    def checkmodel(self, image_src, model):
        model = YOLO(model)
        results = model(image_src)
        result = results[0]
        result.show()
        predictions = result.boxes

        for box in predictions:
            coords = box.xyxy[0].tolist()
            confidence = box.conf[0].item()
            class_id = box.cls[0].item()
            class_name = result.names[int(class_id)]
            print(f"Predicted {class_name} with confidence {confidence:.2f} at {coords}")

    def is_valid(self, image_src: str):
        is_metadata_valid_message = self.check_image_metadata(image_src)
        keys = ['no_gps_data', 'yes_gps_and_valid', 'non_original', 'old_image', 'outside']
        if is_metadata_valid_message.get('non_original'):
            return {'error': 'Ensure the picture uploaded is the original photo.'}, False
        
        if is_metadata_valid_message.get('old_image'):
            return {'error': 'Only photos taken after August, 19 2024 are accepted'}, False

        if is_metadata_valid_message.get('outside'):
            return {
                'error': 'Wrong image geographical location. Not a global function, yet. Try Kenya'
            }, False

#         self.trash_detection(image_src)
        return {'success': 'Image auntenticity verified.'}, True
