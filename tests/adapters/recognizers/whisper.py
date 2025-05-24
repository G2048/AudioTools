import os
import time
import unittest
from typing import BinaryIO
from unittest.mock import MagicMock

import numpy as np

from app.adapters.converters.ffmpeg import WavConverter
from app.adapters.recognizers.neural import WhisperRecognizer
from app.interfaces.recognizers import (
    Chunk,
    RecognizedText,
    Status,
    StatusFile,
    Task_id,
)

TEST_AUDIO_FILE: str = os.environ.get("TEST_AUDIO_FILE", "")
assert TEST_AUDIO_FILE, "TEST_AUDIO_FILE env variable must be set"
assert os.path.exists(TEST_AUDIO_FILE), "TEST_AUDIO_FILE must be a valid file"

FORMAT = TEST_AUDIO_FILE.split(".")[-1]


class TestWhisperRecognizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recognizer = WhisperRecognizer()

    def test_name(self):
        name = self.recognizer.name
        print(f"Name of neural: {name}")
        self.assertIsNotNone(name)
        self.assertIsInstance(name, str)

    def test_send(self):
        run_task = MagicMock()
        self.recognizer._run_task = run_task
        with open(TEST_AUDIO_FILE, "rb") as f:
            task_id = self.recognizer.send(f, FORMAT)
            print(f"Current task id: {task_id}")
            self.assertIsNotNone(task_id)
            self.assertIsInstance(task_id, str)

    def test_check_status(self):
        task_id = "foobar"
        check_status = self.recognizer.check_status(task_id)
        self.assertIsInstance(check_status, StatusFile)
        self.assertEqual(check_status.status, Status.NONE)
        self.assertIsNone(check_status.file_id)
        # self.assertIsNone(check_status.results)

    def test_download(self):
        task_id = "foobar"
        recognized_text = self.recognizer.download(task_id)
        self.assertIsNone(recognized_text)

    def test__audio_from_file(self):
        sample_rate, np_array = self.recognizer._audio_from_file(TEST_AUDIO_FILE)
        self.assertIsInstance(sample_rate, int)
        self.assertIsInstance(np_array, np.ndarray)

    def convert_audio(self, audio_file: BinaryIO):
        converter = WavConverter()
        return converter.convert(audio_file)

    def test_recognize(self):
        fd = open(TEST_AUDIO_FILE, "rb")
        new_file = self.convert_audio(fd)
        fd.close()
        fd = open(new_file, "rb")
        try:
            print(f"File descriptor is closed: {fd.closed}")
            self.assertFalse(fd.closed, "File NOT MUST be closed")
            task_id = self.recognizer.send(fd, FORMAT)
            print(f"Current task id: {task_id}")
            self.assertIsInstance(task_id, Task_id)

            self.assertFalse(fd.closed, "File NOT MUST be closed")
            status_file = self.recognizer.check_status(task_id)
            print(f"{status_file=}")
            self.assertIsInstance(status_file, StatusFile)
            self.assertNotEqual(status_file.status, Status.ERROR)
            self.assertEqual(status_file.status, Status.PROCESSING)
            self.assertIsNotNone(status_file.file_id)

            self.assertFalse(fd.closed, "File NOT MUST be closed")
            while status_file.status != Status.SUCCESS:
                self.assertFalse(fd.closed, "File NOT MUST be closed")
                status_file = self.recognizer.check_status(task_id)
                time.sleep(1)
                print(f"Current status: {status_file.status}")
                if status_file.status == Status.ERROR:
                    raise Exception

            self.assertFalse(fd.closed, "File NOT MUST be closed")
            recognized_text = self.recognizer.download(task_id)
            self.assertIsNotNone(recognized_text)
            self.assertIsInstance(recognized_text, RecognizedText)
            self.assertIsInstance(recognized_text.chunks, list)
            self.assertIsInstance(recognized_text.chunks[0], Chunk)
            print(f"{recognized_text=}")
        finally:
            fd.close()


if __name__ == "__main__":
    unittest.main()
