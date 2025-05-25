import unittest
import uuid

from app.adapters.storages.memory import RedisTaskStorage
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
