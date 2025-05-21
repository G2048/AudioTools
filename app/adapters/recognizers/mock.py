import logging
import threading
import time
import uuid
from typing import BinaryIO

from app.interfaces.recognizers import (
    Chunk,
    File_id,
    RecognizedText,
    RecognizedTextInterface,
    RecognizerInterface,
    Status,
)

logger = logging.getLogger("app.adapters.recognizers")


class MockRecognizedText(RecognizedTextInterface):
    def get_ready_text(self) -> RecognizedText:
        processing_text = [
            Chunk(
                timestamps=("0:00:00", "0:00:10"),
                text="Lore Ipsum",
            ),
            Chunk(
                timestamps=("0:00:10", "0:00:20"),
                text="Dolor Sit Amet",
            ),
        ]
        return RecognizedText(chunk_texts=processing_text)


class MockRecognizer(RecognizerInterface):
    _tasks = {}

    def _create_task_id(self) -> str:
        return uuid.uuid1().hex

    @staticmethod
    def _create_file_id() -> str:
        return str(uuid.uuid1())

    @property
    def name(self) -> str:
        return "mock"

    def _imitation_task(self, task_id: str) -> None:
        time.sleep(10)
        self._tasks[task_id]["status"] = Status.SUCCESS
        logger.info(f"Task_id {task_id} is done")

    def send(self, audio_file: BinaryIO) -> str:
        task_id = self._create_task_id()
        # Write to DB status processing of file_id
        self._tasks[task_id] = {
            "status": Status.PROCESSING,
            "file_id": self._create_file_id(),
        }
        thread_task = threading.Thread(
            target=self._imitation_task, args=(task_id,), daemon=True
        )
        thread_task.start()
        logger.info(f"Create task_id: {task_id}")
        return task_id

    def check_status(self, task_id: str) -> dict[Status, File_id]:
        return self._tasks.get(task_id) or {"status": Status.NONE, "file_id": ""}

    def download(self, task_id: str) -> MockRecognizedText:
        return MockRecognizedText()
