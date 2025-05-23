import os
import unittest
from decimal import Decimal
from pathlib import Path

from app.services.audio import AudioInfo, FFmpegConverter
from tests.test_aws_files import TEST_FILE

TEST_AUDIO_FILE: str = os.environ.get("TEST_AUDIO_FILE", "")
assert TEST_AUDIO_FILE, "TEST_AUDIO_FILE env variable must be set"
assert os.path.exists(TEST_AUDIO_FILE), "TEST_AUDIO_FILE must be a valid file"


class TestFFmpegConverter(unittest.TestCase):
    def setUp(self):
        self.converter = FFmpegConverter(TEST_AUDIO_FILE)

    def test_format(self):
        expected_format: str = TEST_FILE.split(".")[-1]
        print(f"Expected format: {expected_format}")
        print(f"Actual format: {self.converter.format}")
        self.assertEqual(self.converter.format, expected_format)

    def test_name(self):
        print(f"Actual path: {self.converter.name}")
        self.assertEqual(self.converter.name, Path(TEST_AUDIO_FILE))

    def test_channels(self):
        print(f"Actual channels: {self.converter.channels}")
        self.assertIsInstance(self.converter.channels, int)
        self.assertEqual(self.converter.channels, 2)

    def test_size(self):
        print(f"Actual size: {self.converter.size}")
        self.assertIsInstance(self.converter.size, int)
        self.assertEqual(self.converter.size, os.path.getsize(TEST_AUDIO_FILE))

    def test_duration(self):
        print(f"Actual duration: {self.converter.duration}")
        self.assertIsInstance(self.converter.duration, float)
        self.assertTrue(self.converter.duration)

    def test_new_path(self):
        format = "wav"
        actual_path = self.converter.new_path(format)
        print(f"Actual path: {actual_path}")

        path = Path(TEST_AUDIO_FILE)
        suffix = path.suffix.replace(".", "")
        self.assertNotEqual(format, suffix, msg="Format must be different than suffix")
        file = path.stem
        expected_path = f"/tmp/{file}.{format}"
        print(f"Expected path: {expected_path}")
        self.assertEqual(actual_path, expected_path)

    def test_convert_wav(self):
        print(f"Actual path: {self.converter.name}")
        print(f"Actual format: {self.converter.format}")
        converted_file = None
        try:
            converted_file = self.converter.convert_wav()
            self.assertEqual(converted_file.format, "wav")
        finally:
            if converted_file:
                os.remove(converted_file.name)

    def test_convert_mp3(self):
        print(f"Actual path: {self.converter.name}")
        print(f"Actual format: {self.converter.format}")
        converted_file = None
        try:
            converted_file = self.converter.convert_mp3()
            self.assertEqual(converted_file.format, "mp3")
        finally:
            if converted_file:
                os.remove(converted_file.name)

    def test_convert_ogg(self):
        print(f"Actual path: {self.converter.name}")
        print(f"Actual format: {self.converter.format}")
        converted_file = None
        try:
            converted_file = self.converter.convert_ogg()
            self.assertEqual(converted_file.format, "ogg")
        finally:
            if converted_file:
                os.remove(converted_file.name)


class TestAudioInfo(unittest.TestCase):
    def setUp(self):
        self.audio_info = AudioInfo(TEST_AUDIO_FILE)

    def test_name(self):
        print(f"Actual name: {self.audio_info.name}")

    def test_channels(self):
        print(f"Actual channels: {self.audio_info.channels}")
        self.assertIsInstance(self.audio_info.channels, int)
        self.assertEqual(self.audio_info.channels, 2)

    def test_bitrate(self):
        size = self.audio_info.size
        duration = self.audio_info.duration
        expected_bitrate = int(size / duration * 8)
        print(f"Actual bitrate: {self.audio_info.bitrate}")
        print(f"Expected bitrate: {expected_bitrate}")
        self.assertIsInstance(self.audio_info.bitrate, int)
        self.assertEqual(self.audio_info.bitrate, expected_bitrate)

    def test_size(self):
        print(f"Actual size: {self.audio_info.size}")
        self.assertIsInstance(self.audio_info.size, int)
        self.assertEqual(self.audio_info.size, os.path.getsize(TEST_AUDIO_FILE))

    def test_duration(self):
        print(f"Actual duration: {self.audio_info.duration}")
        self.assertIsInstance(self.audio_info.duration, Decimal)
        self.assertTrue(self.audio_info.duration)

    def test_format(self):
        print(f"Actual format: {self.audio_info.format}")
        self.assertEqual(self.audio_info.format, "mp3")

    def test_codec(self):
        expected_codec = Path(TEST_FILE).suffix.replace(".", "")
        print(f"Actual codec: {self.audio_info.codec}")
        print(f"Expected codec: {expected_codec}")
        self.assertIsInstance(self.audio_info.codec, str)
        self.assertEqual(self.audio_info.codec, expected_codec)
