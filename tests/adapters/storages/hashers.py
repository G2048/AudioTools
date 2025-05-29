import os
import sys
import unittest

from app.adapters.storages.hashers import Sha1Hasher

TEST_AUDIO_FILE = os.environ.get("TEST_AUDIO_FILE")
assert TEST_AUDIO_FILE, "TEST_AUDIO_FILE env variable is not set"
assert os.path.exists(TEST_AUDIO_FILE), "TEST_AUDIO_FILE does not exist"
assert sys.getsizeof(TEST_AUDIO_FILE) > 0, "TEST_AUDIO_FILE is empty"


class TestSha1Hasher(unittest.TestCase):
    def setUp(self) -> None:
        self.hasher = Sha1Hasher()

    def test_hash(self):
        with open(TEST_AUDIO_FILE, "rb") as f:
            hash_file = self.hasher.hash(f)
            print(f"{self.hasher.name} hash of {TEST_AUDIO_FILE} file: {hash_file}")
            self.assertIsInstance(hash_file, str)
        prev_hash = self.hasher._hasher.hexdigest()
        self.assertEqual(prev_hash, self.hasher.empty_value)
        self.assertNotEqual(hash_file, self.hasher.empty_value)
