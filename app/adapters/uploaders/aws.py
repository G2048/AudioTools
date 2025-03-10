import logging

from app.configs import get_aws_bucket_settings, get_aws_settings
from app.interfaces import AudioUploaderInterface
from app.services.uploader import AwsUploader

aws_settings = get_aws_settings()
bucket_settings = get_aws_bucket_settings()

logger = logging.getLogger("stdout")


class AudioAwsUploader(AudioUploaderInterface):
    __slot__ = "uploader"

    def __init__(self):
        self.uploader = AwsUploader(aws_settings, bucket_settings)

    def execute(self, file_path: str):
        logger.info(f"Uploading {file_path}")
        # Узкое место: если в пути будет несколько директорий,
        # то будет браться только первая - это плохо, но пока не понятно нужно ли большее
        current_path = "." if not len(file_path.split("/")) > 1 else file_path.split("/")[0]
        file = self.uploader.create_file(file_path)
        self.uploader.upload(file, current_path)
