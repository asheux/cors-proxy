import os
import io
import boto3

from urllib import parse
from dotenv import load_dotenv


class S3Client:
    def __init__(self):
        load_dotenv()
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_KEY')
        self.bucket_name = "tccup"
        self.aws_default_region = "us-east-2"

    def get_s3_client(self):
        return boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def upload_file_to_s3(self, file_name, file: io.BytesIO) -> str:
        bucket = self.bucket_name
        client = self.get_s3_client()
        result = client.put_object(Bucket=bucket, Body=file.getvalue(), Key=file_name)

        if result['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception()

        resource_url = f"https://{bucket}.s3.amazonaws.com/{parse.quote(file_name)}"
        return resource_url

    def upload_temp_file_to_s3(self, file_name: str, content) -> str:
        data = io.BytesIO(content.read())
        return self.upload_file_to_s3(file_name, data)
