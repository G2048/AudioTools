import os
import time
import unittest

import numpy as np

from app.adapters.recognizers.neural import NeuralRecognizedText, WhisperRecognizer
from app.interfaces.recognizers import Status

TEST_FILE = os.environ.get("TEST_FILE", "")
assert TEST_FILE, "TEST_FILE environment variable is not set"


class TestNeuralRecognizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recognizer = WhisperRecognizer()

    def test__audio_from_file(self):
        sample_rate, np_array = self.recognizer._audio_from_file(TEST_FILE)
        self.assertIsInstance(sample_rate, int)
        self.assertIsInstance(np_array, np.ndarray)

    def test_recognize(self):
        with open(TEST_FILE, "rb") as f:
            task_id = self.recognizer.send(f)
            self.assertIsInstance(task_id, str)
        status_dict = self.recognizer.check_status(task_id)
        print(f"{status_dict=}")
        self.assertEqual(status_dict["status"], Status.PROCESSING)

        while status_dict["status"] != Status.SUCCESS:
            status_dict = self.recognizer.check_status(task_id)
            time.sleep(1)
        raw_neural_text = self.recognizer.download(task_id)
        self.assertIsInstance(raw_neural_text, NeuralRecognizedText)
        text = raw_neural_text.get_ready_text()
        print(f"{text=}")


if __name__ == "__main__":
    unittest.main()
