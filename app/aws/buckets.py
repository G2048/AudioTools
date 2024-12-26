from .base import S3Client


class S3Bucket:
    def __init__(self, client: S3Client, bucket_name: str):
        self.s3_client = client.s3_client
        self.bucket_name = bucket_name

    def create_bucket(self):
        self.s3_client.create_bucket(Bucket=self.bucket_name)

    # object_name is file
    def _get_object(self, object_name: str):
        return self.s3_client.get_object(Bucket=self.bucket_name, Key=object_name)

    def get_object(self, object_name: str):
        get_object_response = self._get_object(object_name)
        logger.debug(f"{get_object_response=}")
        return get_object_response["Body"].read()

    def _list_objects(self):
        return self.s3_client.list_objects(Bucket=self.bucket_name)

    def list_objects(self) -> list:
        return self._list_objects()["Contents"]

    def upload_file(self, file_path: str, object_name: str):
        # s3.upload_file("this_script.py", "bucket-name", "script/py_script.py")
        self.s3_client.upload_file(file_path, self.bucket_name, object_name)

    # Remove objects from bucket
    def delete_objects(self, object_names: list[dict]):
        # object_names = [{"Key": "object_name"}, {"Key": "script/py_script.py"}]
        response = self.s3_client.delete_objects(Bucket=self.bucket_name, Delete={"Objects": object_names})
