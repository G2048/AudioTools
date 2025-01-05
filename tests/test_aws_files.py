import os
import unittest

from app.configs import get_aws_bucket_settings, get_aws_settings
from app.services import AwsUploader

aws_settings = get_aws_settings()
bucket_settings = get_aws_bucket_settings()
client = AwsUploader(aws_settings, bucket_settings)

TEST_FILE = os.environ.get("TEST_FILE", "")
assert TEST_FILE, "TEST_FILE env variable is not set"


class TestCaseAws(unittest.TestCase):
    def setUp(self):
        self.file = client.create_file(TEST_FILE)

    def tearDown(self):
        pass

    def test_list_files(self):
        files = client.list_files()
        self.assertIsNotNone(files)
        self.assertIsInstance(files, list)

        file = files[0]
        self.assertIsInstance(file, dict)
        self.assertIn("Key", file)
        self.assertIn("LastModified", file)
        self.assertIn("Size", file)
        self.assertIn("ETag", file)
        self.assertIn("StorageClass", file)
        self.assertIn("Owner", file)
        self.assertIn("DisplayName", file["Owner"])
        self.assertIn("ID", file["Owner"])
        print(f"{len(files)=}")
        files_name = [file["Key"] for file in files]
        print(f"{files_name=}")

    def test_get_file(self):
        file_info = client.get(self.file)
        self.assertIsNotNone(file_info)
        self.assertIsInstance(file_info, bytes)

    def test_save_file(self):
        client.save(self.file)

    def test_get_files(self):
        files = client.list_files()
        files_name = [file["Key"] for file in files]

        for file_name in files_name:
            file_info = client.get(file_name)
            self.assertIsNotNone(file_info)
            if file_info:
                print(f"{file_name=}")

    def test_upload_file(self):
        client.upload(self.file, "tests")
        file_dump = client.get(self.file)
        self.assertIsNotNone(file_dump)

    def test_delete_file(self):
        client.delete(self.file)
        try:
            file_info = client.get(self.file)
            self.fail("File should be deleted")
        except Exception:
            pass


if __name__ == "__main__":
    unittest.main()
