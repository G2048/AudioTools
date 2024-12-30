import logging
from pathlib import Path
from typing import Any, Self, Sequence

from app.aws import S3Bucket, S3Client
from app.configs.settings import AwsBucketSettingsConfig, AwsSettingsConfig

from .interfaces import File, Uploader

logger = logging.getLogger("stdout")


class S3File(File):
    def __init__(self, s3bucket: S3Bucket, file: str, file_path: str = "."):
        self.s3_bucket = s3bucket
        self.file_name = file
        self.path = self._create_path_file(file_path)

    @property
    def name(self) -> str:
        return self.file_name

    def upload(self, path: str = ".") -> Self:
        file_path = str(Path(path) / self.file_name)
        object_path = str(self.path / self.file_name.split("/")[-1])
        logger.info(f"Uploading {file_path} to {object_path}")

        self.s3_bucket.upload_file(file_path, object_path)
        logger.info(f"File {self.file_name} uploaded")
        return self

    def save(self) -> Self:
        file_dump = self.get()
        path = self.path / self.file_name
        with path.open(mode="wb+") as file:
            file.write(file_dump)
        return self

    def get(self) -> bytes:
        object_path = str(self.path / self.file_name)
        object_response = self.s3_bucket.get_object(object_path)
        return object_response["Body"].read()

    def delete(self):
        object_path = str(self.path / self.file_name)
        response = self.s3_bucket.delete_objects([{"Key": object_path}])
        logger.debug(f"{response=}")
        assert response["Deleted"][0]["Key"] == object_path
        logger.info(f"File {self.file_name} deleted")

    def list_files(self) -> list[dict[Any, Any]]:
        return self.s3_bucket.list_objects()["Contents"]


class AwsUploader(Uploader):
    def __init__(self, aws_settings: AwsSettingsConfig, bucket_settings: AwsBucketSettingsConfig):
        s3_client = S3Client(**aws_settings.model_dump())
        self.s3_bucket = S3Bucket(s3_client, bucket_settings.bucket_name)
        self._bucket_settings = bucket_settings

    def create_files(self, files: Sequence[str]) -> list[S3File]:
        return [self.create_file(file) for file in files]

    def create_file(self, file: str) -> S3File:
        return S3File(self.s3_bucket, file, self._bucket_settings.directory_path)

    def list_files(self) -> list[dict[Any, Any]]:
        return self.s3_bucket.list_objects()["Contents"]


# class AwsUploader:
#     def __init__(self, file: File, aws_settings: AwsSettingsConfig, bucket_settings: AwsBucketSettingsConfig):
#         s3_client = S3Client(**aws_settings.model_dump())
#         self.s3_bucket = S3Bucket(s3_client, bucket_settings.bucket_name)
#         self._bucket_settings = bucket_settings
#         # self.s3_bucket.create_bucket()
#         self.path = self._create_path_file(bucket_settings.directory_path)
#         self.path = self._create_path_file()

#     def _create_path_file(self) -> Path:
#         path = Path(self._bucket_settings.directory_path)
#         path.mkdir(parents=True, exist_ok=True)
#         return path

#     def upload_file(self, file_name: str, path: str = "."):
#         file_path = str(Path(path) / file_name)
#         object_path = str(self.path / file_name)
#         self.s3_bucket.upload_file(file_path, object_path)
#         logger.info(f"File {file_name} uploaded")

#     def save_file(self, file_name: str):
#         file_dump = self.get_file(file_name)
#         path = self.path / file_name
#         with path.open(mode="wb+") as file:
#             file.write(file_dump)

#     def get_file(self, file_name: str) -> bytes:
#         object_path = str(self.path / file_name)
#         object_response = self.s3_bucket.get_object(object_path)
#         return object_response["Body"].read()

#     def list_files(self) -> list[dict[Any, Any]]:
#         return self.s3_bucket.list_objects()["Contents"]

#     def delete_file(self, file_name: str):
#         object_path = str(self.path / file_name)
#         response = self.s3_bucket.delete_objects([{"Key": object_path}])
#         logger.debug(f"{response=}")
#         assert response["Deleted"][0]["Key"] == object_path
#         logger.info(f"File {file_name} deleted")
