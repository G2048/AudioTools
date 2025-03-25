import time
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

    def test_multiple_tasks(self):
        task_id_1 = self.client.send(b"hello world")
        task_id_2 = self.client.send(b"Clean up the mess")
        self.assertNotEqual(task_id_1, task_id_2)
        self.assertEqual(len(self.client._tasks), 3)
        status_file_id_1 = self.client.check_status(task_id_1)
        status_file_id_2 = self.client.check_status(task_id_2)
        
        while status_file_id_2["status"] != Status.SUCCESS and status_file_id_1["status"] != Status.SUCCESS:
            status_file_id = self.client.check_status(self.task_id)
            time.sleep(5)
            print(f"{status_file_id=}")

        self.assertIsInstance(status_file_id_1["file_id"], str)
        self.assertEqual(status_file_id_1["status"], Status.SUCCESS)
        self.assertIsInstance(status_file_id_2["file_id"], str)
        self.assertEqual(status_file_id_2["status"], Status.SUCCESS)

    def test_wait_status_success(self):
        status_file_id = self.client.check_status(self.task_id)
        print(f"{status_file_id=}")
        while status_file_id["status"] != Status.SUCCESS:
            status_file_id = self.client.check_status(self.task_id)
            time.sleep(5)
            print(f"{status_file_id=}")
        self.assertIsInstance(status_file_id["file_id"], str)
        self.assertEqual(status_file_id["status"], Status.SUCCESS)

    def test_download(self):
        self.client.download(self.task_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
