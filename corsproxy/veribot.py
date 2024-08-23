import cv2
import os
import io
import PIL

from ultralytics import YOLO
from datetime import datetime
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from PIL import Image


class VeriBot3000:
    def __init__(self, model = None):
        self.trash_model = model

    def check_image_metadata(self, file):
        image = Image.open(file)
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

    def trash_detection(self, file, model):
        image = Image.open(file)
        image = image.convert('RGB')
        # Predict
        predictions = self.get_model_prediction(image, model)
        if predictions:
            return True
        return False

    def get_model_prediction(self, image, model):
        model = YOLO(model)
        results = model(image)
        result = results[0]
        # result.show()
        predictions = result.boxes
        classes = [
            'Aerosol', 'Aluminium foil', 'Battery', 'Broken glass',
            'Cigarette', 'Corrugated carton', 'Crisp packet', 'Drink can',
            'Drink carton', 'Egg carton', 'Foam cup', 'Food Can',
            'Food waste', 'Garbage bag', 'Glass', 'Glass bottle',
            'Glass cup', 'Glass jar', 'Magazine paper', 'Meal carton',
            'Metal', 'Metal lid', 'Normal paper', 'Paper', 'Paper bag',
            'Paper cup', 'Paper straw', 'Pizza box', 'Plastic',
            'Plastic film', 'Plastic lid', 'Plastic straw', 'Plastic utensils',
            'Polypropylene bag', 'Pop tab', 'Scrap metal', 'Shoe', 'Spread tub',
            'Squeezable tube', 'Styrofoam piece', 'Tissues', 'Toilet tube',
            'Tupperware', 'Waste', 'Wrapping paper',
        ]
        best_predicted_classes = []

        for box in predictions:
            coords = box.xyxy[0].tolist()
            confidence = box.conf[0].item()
            class_id = box.cls[0].item()
            class_name = result.names[int(class_id)]
            if class_name in classes and confidence > 0.5:
                best_predicted_classes.append(class_name)
        return best_predicted_classes

    def detect_trash(self, file, model):
        # Prediction any indication of trash in the image using CNN
        is_trash_detected = self.trash_detection(file, model)
        return is_trash_detected

    def is_valid(self, file):
        is_metadata_valid_message = self.check_image_metadata(file)
        if is_metadata_valid_message.get('non_original'):
            return {'error': 'Upload the original photo. Tip: If on laptop, use cloud to download.'}, 400
        
        if is_metadata_valid_message.get('old_image'):
            return {'error': 'Only photos taken after August, 19 2024 are accepted'}, 400

        is_inside = is_metadata_valid_message.get('yes_gps_and_valid')
        if is_metadata_valid_message.get('outside') or (is_inside is not None and not is_inside):
            return {
                'error': 'Wrong image geographical location. Not a global function, yet. Try Kenya'
            }, 400

        if is_metadata_valid_message.get('no_gps_data'):
            # Check location based on IP address
            pass 
        return {'data': {'success': 'Image auntenticity verified.'}}, 200
