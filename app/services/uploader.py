import logging

from app.aws import S3Bucket, S3Client
from app.configs.settings import AwsSettingsConfig

logger = logging.getLogger("stdout")


class AwsUploader:
    def __init__(self, settings: AwsSettingsConfig):
        self.s3_client = S3Client(**settings.model_dump())
        self.s3_bucket = S3Bucket(self.s3_client, settings.bucket_name)
        # self.s3_bucket.create_bucket()

    def upload_file(self, file_path: str, object_name: str):
        self.s3_bucket.upload_file(file_path, object_name)

    def get_file(self, object_name: str):
        return self.s3_bucket.get_object(object_name)

    def list_files(self):
        return self.s3_bucket.list_objects()

    def delete_file(self, object_name: str):
        self.s3_bucket.delete_objects([{"Key": object_name}])
