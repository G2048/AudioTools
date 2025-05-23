import os
import unittest

from app.adapters.converters.ffmpeg import Mp3Converter, OggConverter, WavConverter
from app.services.audio import AudioInfo

TEST_AUDIO_FILE: str = os.environ.get("TEST_AUDIO_FILE", "")
assert TEST_AUDIO_FILE, "TEST_AUDIO_FILE env variable must be set"
assert os.path.exists(TEST_AUDIO_FILE), "TEST_AUDIO_FILE must be a valid file"


class TestMp3Converter(unittest.TestCase):
    audio_info = AudioInfo(TEST_AUDIO_FILE)

    def setUp(self) -> None:
        self.converter = Mp3Converter()
        self.EXPECTED_AUDIO_FORMAT = "mp3"

    def test_converter(self):
        new_file = None
        try:
            with open(TEST_AUDIO_FILE, "rb") as f:
                new_file = self.converter.convert(f)
                self.assertTrue(os.path.exists(new_file))
                audio_info = AudioInfo(new_file)
                self.assertEqual(audio_info.format, self.EXPECTED_AUDIO_FORMAT)
                self.assertNotEqual(audio_info.format, self.audio_info.format)
        finally:
            if new_file:
                print(f"Removing {new_file}")
                os.remove(new_file)


class TestWavConverter(TestMp3Converter):
    def setUp(self) -> None:
        self.converter = WavConverter()
        self.EXPECTED_AUDIO_FORMAT = "wav"


class TestOggConverter(TestMp3Converter):
    def setUp(self) -> None:
        self.converter = OggConverter()
        self.EXPECTED_AUDIO_FORMAT = "ogg"


if __name__ == "__main__":
    unittest.main(verbosity=2)
