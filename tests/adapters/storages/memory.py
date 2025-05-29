import unittest
import uuid

from app.adapters.storages.memory import (
    RedisRecognitionStorage,
    RedisTaskStorage,
    TaskIdStatus,
)
from app.interfaces.recognizers import Status
from app.interfaces.storages import TaskMessage


class TestRedisStorage(unittest.TestCase):
    def setUp(self) -> None:
        self.storage = RedisTaskStorage()

    def test_set_and_get(self):
        message = TaskMessage(
            task_id=uuid.uuid1().hex,
            recognizer="mock_recognizer",
            file_id="test_file_id",
        )
        print(f"Request TaskMessage: {message}")
        print()

        success = self.storage.set(message)
        self.assertTrue(success)
        task_message = self.storage.get(message.task_id)
        print(f"Response TaskMessage: {task_message}")
        print()
        self.assertEqual(task_message, message)


class TestRedisRecognitionStorage(unittest.TestCase):
    def setUp(self) -> None:
        self.storage = RedisRecognitionStorage()

    def test_set_and_get(self):
        message = TaskIdStatus(
            task_id=uuid.uuid1().hex,
            status=Status.NEW,
            transcription=None,
        )
        print(f"Request TaskMessage: {message}")
        print()

        self.storage.insert(message)
        task_status = self.storage.select(message.task_id)
        print(f"Response TaskMessage: {task_status}")
        print()
        self.assertEqual(task_status, message)
