import os
import unittest
from unittest.mock import MagicMock

from app.adapters.converters.ffmpeg import Mp3Converter
from app.adapters.recognizers.mock import MockRecognizer  # noqa: F401
from app.adapters.recognizers.neural import WhisperRecognizer
from app.usecases.transcribe import SendRecognizeUseCase

TEST_AUDIO_FILE: str = os.environ.get("TEST_AUDIO_FILE", "")
assert TEST_AUDIO_FILE, "TEST_AUDIO_FILE env variable must be set"
assert os.path.exists(TEST_AUDIO_FILE), "TEST_AUDIO_FILE must be a valid file"


class TestAudioSendRecognizeUseCase(unittest.TestCase):
    def setUp(self) -> None:
        self.converter = Mp3Converter()
        self.recognizer = WhisperRecognizer()
        self.usecase = SendRecognizeUseCase(
            recognizer=self.recognizer,
            audio_converter=self.converter,
        )

    def test_usecase(self):
        run_task = MagicMock()
        self.recognizer._run_task = run_task

        with open(TEST_AUDIO_FILE, "rb") as f:
            task_id = self.usecase.execute(f)
            print(f"Current task id: {task_id}")
            self.assertIsNotNone(task_id)
            self.assertIsInstance(task_id, str)
