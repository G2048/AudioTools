import unittest
from typing import Optional

# from tests.drivers.aws.buckets import AwsBuckets
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.drivers.aws import S3Bucket, S3BucketAlreadyExists, S3Client, S3Object
from app.drivers.aws.models import (
    Bucket,
    Content,
    ResponseDeletedObjects,
    ResponseHead,
)


class TestS3Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TEST_S3_", case_sensitive=False)

    endpoint_url: str
    access_key: str
    secret_key: str
    session_token: Optional[str] = None
    # region_name: str


class TestS3Bucket(unittest.TestCase):
    def setUp(self):
        self.BUCKET_NAME = "test"
        self.client = S3Client(TestS3Config())
        self.bucket = S3Bucket(self.client, self.BUCKET_NAME)
        self.test_create_bucket()

    def tearDown(self):
        self.test_delete()

    def test_create(self):
        try:
            created_bucket = self.bucket.create()
            print()
            print("Created bucket. Ok.")
        except S3BucketAlreadyExists:
            deleted_bucket = self.bucket.delete()
            print()
            print("Deleted bucket. Ok.")
            print(f"{deleted_bucket=}")
            created_bucket = self.bucket.create()
            print("Created bucket. Ok.")

            print()
        print(f"{created_bucket=}")
        self.assertIsNotNone(created_bucket)
        with self.assertRaises(S3BucketAlreadyExists):
            self.bucket.create()
        print()
        print("Asssert with S3BucketAlreadyExists. Ok.")

    def test_delete(self):
        deleted_bucket = self.bucket.delete()
        self.assertTrue(deleted_bucket)
        print("Deleted bucket. Ok.")

    def test_list(self):
        buckets = self.bucket.list()
        print(f"{buckets=}")
        self.assertIsInstance(buckets, list)
        self.assertIsInstance(buckets[0], Bucket)
        print("List buckets. Ok.")

    def test_head(self):
        head = self.bucket.head()
        print(f"{head=}")
        self.assertIsInstance(head, ResponseHead)
        print("Head bucket. Ok.")

    def test_upload(self):
        print(f"Uploading the {self.OBJECT_NAME} file")
        created_bucket = self.bucket.upload(".", self.OBJECT_NAME)


class TestS3Object(unittest.TestCase):
    TEXT = """This command opens a network socket and returns a channel identifier that may be used in future invocations of commands like read, puts and flush.  At present only the TCP network protocol is supported
    over  IPv4  and  IPv6;  future  releases may include support for additional protocols.  The socket command may be used to open either the client or server side of a connection, depending on whether the
    -server switch is specified.

    Note that the default encoding for all sockets is the system encoding, as returned by encoding system.  Most of the time, you will need to use chan configure to alter this to something  else,  such  as
    utf-8 (ideal for communicating with other Tcl processes) or iso8859-1 (useful for many network protocols, especially the older ones)."""

    @classmethod
    def setUpClass(cls):
        cls.BUCKET_NAME = "test"
        cls.OBJECT_NAME = "test.txt"
        cls._create_object()
        cls.client = S3Client(TestS3Config())
        cls.bucket = S3Bucket(cls.client, cls.BUCKET_NAME)
        cls.object = S3Object(cls.bucket, cls.OBJECT_NAME)
        cls._create_bucket()

    @classmethod
    def tearDownClass(cls):
        # cls._delete_bucket()
        pass

    @classmethod
    def _create_object(cls):
        print(f"Creating the {cls.OBJECT_NAME} file")
        with open(cls.OBJECT_NAME, "w") as f:
            f.write(cls.TEXT)

    def test_bucket_prune(self):
        self.test_upload()
        print(f"Prune the {self.BUCKET_NAME} bucket")
        prune_result = self.bucket.prune()
        print(f"{prune_result=}")
        self.assertIsNotNone(prune_result)
        self.assertIsInstance(prune_result, ResponseDeletedObjects)
        print("Prune bucket. Ok.")
        print()

    def test_bucket_list_objects(self):
        self.test_upload()
        print(f"List the {self.BUCKET_NAME} bucket objects")
        list_objects_result = self.bucket.list_objects()
        print(f"{list_objects_result=}")
        self.assertIsInstance(list_objects_result, list)
        print("List bucket objects. Ok.")
        print()

    def test_upload(self):
        print(f"Uploading the {self.OBJECT_NAME} file")
        upload_result = self.object.upload(self.OBJECT_NAME)
        print(f"{upload_result=}")
        self.assertIsNone(upload_result)
        print("Upload object. Ok.")
        print()

    def test_binary_upload(self):
        print(f"Binary Uploading the {self.OBJECT_NAME} file")
        with open(self.OBJECT_NAME, "rb") as f:
            object_upload = self.object.binary_upload(f)
        print(f"{object_upload =}")
        self.assertIsNone(object_upload)
        print("Binary Upload object. Ok.")
        print()

    def test_get(self):
        print(f"Get the {self.OBJECT_NAME}: ")
        object_info = self.object.get()
        self.assertIsNotNone(object_info)
        object_body = object_info.read()
        self.assertIsInstance(object_body, bytes)
        print(f"{object_body=}")
        self.assertEqual(object_body, bytes(self.TEXT, "utf-8"))
        print("Get object. Ok.")
        print()

    def test_list(self):
        print("List objects:")
        objects = self.object.list()
        print(f"{objects=}")
        self.assertIsInstance(objects, list)
        self.assertIsInstance(objects[0], Content)
        print("List objects. Ok.")
        print()

    def test_delete(self):
        print("Delete object:")
        deleted_object = self.object.delete()
        print(f"{deleted_object=}")
        self.assertIsNotNone(deleted_object)
        self.assertTrue(deleted_object)
        print("Delete object. Ok.")
        print()

    @classmethod
    def _create_bucket(cls):
        try:
            created_bucket = cls.bucket.create()
            print()
            print("Created bucket. Ok.")
            print(f"{created_bucket=}")
            assert created_bucket
        except S3BucketAlreadyExists:
            print("Bucket already exists. Ok.")
            print()

    @classmethod
    def _delete_bucket(cls):
        deleted_bucket = cls.bucket.delete()
        assert deleted_bucket, "Delete bucket failed"
        print("Deleted bucket. Ok.")
