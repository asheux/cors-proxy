import hashlib
import io
import os
import requests
import PIL

from datetime import datetime

from PIL import Image
from corsproxy.models import Block, db


class Blockchain:
    def __init__(self):
        self.chain = []
        self.initialize_chain()

    def get_exif_data(self, image_file):
        image = Image.open(image_file)
        exif_data = image._getexif()
        if exif_data is not None:
            return {PIL.ExifTags.TAGS[k]: v for k, v in exif_data.items()}
        return {}

    def hash_image(self, image_file):
        image = Image.open(image_file)
        normalized_image = image.convert('RGB').resize((256, 256))
        image_byte = io.BytesIO()
        normalized_image.save(image_byte, format=image.format)
        image_data = image_byte.getvalue()

        # Included original creation date for accuracy
        exif_data = self.get_exif_data(image_file)
        relevant_metadata = exif_data.get('DateTimeOriginal', '')
        combined_data = image_data + relevant_metadata.encode()
        return hashlib.sha256(combined_data).hexdigest()

    def initialize_chain(self):
        last_block = Block.query.order_by(Block.index.desc()).first()
        if not last_block:
            genesis_block = self.create_genesis_block()
            db.session.add(genesis_block)
            db.session.commit()
        else:
            self.chain.append(last_block)

    def create_genesis_block(self):
        timestamp = datetime.utcnow()
        image_hash = "Genesis Image Hash"
        block_hash = self.calculate_hash(0, timestamp, image_hash, "0")
        block = Block(
            index=0,
            timestamp=timestamp,
            image_hash=image_hash,
            block_hash=block_hash,
            previous_hash="0"
        )
        return block

    def calculate_hash(self, index, timestamp, image_hash, previous_hash):
        value = f"{index}{timestamp}{image_hash}{previous_hash}"
        return hashlib.sha256(value.encode()).hexdigest()

    def add_block(self, image_hash):
        latest_block = Block.query.order_by(Block.index.desc()).first()
        index = latest_block.index + 1
        timestamp = datetime.utcnow()
        previous_hash = latest_block.block_hash
        block_hash = self.calculate_hash(index, timestamp, image_hash, previous_hash)

        new_block = Block(
            index=index,
            timestamp=timestamp,
            image_hash=image_hash,
            previous_hash=previous_hash,
            block_hash=block_hash
        )
        db.session.add(new_block)
        db.session.commit()
        self.chain.append(new_block)

    def process_image(self, image_path):
        image_hash = self.hash_image(image_path)
        if Block.query.filter_by(image_hash=image_hash).first():
            return True

        self.add_block(image_hash)
        return False

