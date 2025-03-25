import unittest

from app.adapters.recognizers.mock import MockRecognizer
from app.interfaces.recognizers import Status


class TestMockRecognizer(unittest.TestCase):
    def setUp(self) -> None:
        self.client = MockRecognizer()
        file_bytes = b"hello world"
        self.task_id = self.client.send(file_bytes)

    def test_task_id_is_not_exist(self):
        status_dict = self.client.check_status("NONE")
        self.assertDictEqual(status_dict, {"status": Status.NONE, "file_id": ""})

    def test_send(self):
        print(f"{self.task_id=}")
        self.assertIsNotNone(self.task_id)
        self.assertIsInstance(self.task_id, str)

    def test_check_status(self):
        status_file_id = self.client.check_status(self.task_id)
        print(f"{status_file_id=}")
        self.assertIsInstance(status_file_id["file_id"], str)
        self.assertEqual(status_file_id["status"], Status.PROCESSING)

    def test_download(self):
        self.client.download(self.task_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
