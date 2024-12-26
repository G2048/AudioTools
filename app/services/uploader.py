import logging
from pathlib import Path
from typing import Any

from app.aws import S3Bucket, S3Client
from app.configs.settings import AwsBucketSettingsConfig, AwsSettingsConfig

logger = logging.getLogger("stdout")


class AwsUploader:
    def __init__(self, aws_settings: AwsSettingsConfig, bucket_settings: AwsBucketSettingsConfig):
        s3_client = S3Client(**aws_settings.model_dump())
        self.s3_bucket = S3Bucket(s3_client, bucket_settings.bucket_name)
        self._bucket_settings = bucket_settings
        # self.s3_bucket.create_bucket()
        self.path = self._create_path_file()

    def _create_path_file(self) -> Path:
        path = Path(self._bucket_settings.directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def upload_file(self, file_name: str):
        file_path = f"tests/{file_name}"
        object_path = str(self.path / file_name)
        self.s3_bucket.upload_file(file_path, object_path)
        logger.info(f"File {file_name} uploaded")

    def save_file(self, file_name: str):
        file_dump = self.get_file(file_name)
        path = self.path / file_name
        with path.open(mode="wb+") as file:
            file.write(file_dump)

    def get_file(self, file_name: str) -> bytes:
        object_path = str(self.path / file_name)
        object_response = self.s3_bucket.get_object(object_path)
        return object_response["Body"].read()

    def list_files(self) -> list[dict[Any, Any]]:
        return self.s3_bucket.list_objects()["Contents"]

    def delete_file(self, file_name: str):
        object_path = str(self.path / file_name)
        response = self.s3_bucket.delete_objects([{"Key": object_path}])
        logger.debug(f"{response=}")
        assert response["Deleted"][0]["Key"] == object_path
        logger.info(f"File {file_name} deleted")
