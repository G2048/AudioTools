import os
import unittest

from numpy import int16, ndarray

from app.services import AudioConverter

converter = AudioConverter
TEST_FILE = os.environ.get("TEST_FILE")
assert TEST_FILE, "TEST_FILE environment variable not set"

os.environ["LLMMODEL"] = ".whisper"


class TestAudio(unittest.TestCase):
    def test_convert_audio_to_numpy(self):
        audio_array = converter.to_numpy(TEST_FILE)
        self.assertIsInstance(audio_array, ndarray)
        self.assertIsInstance(audio_array.shape, tuple)
        self.assertIsInstance(audio_array.dtype.type(), int16)
        print(f"{audio_array=}")
        # print(f"{dir(audio_array)=}")
        print(audio_array.shape)


if __name__ == "__main__":
    unittest.main()
