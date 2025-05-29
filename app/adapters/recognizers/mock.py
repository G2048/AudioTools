import logging
import threading
import time
import uuid
from typing import BinaryIO

from app.interfaces.recognizers import (
    Chunk,
    IRecognitionStorage,
    IRecognizer,
    RecognizedText,
    Status,
    StatusFile,
    Task_id,
    classproperty,
)

logger = logging.getLogger("app.adapters.recognizers")


class MockRecognizer(IRecognizer):
    _tasks: dict[Task_id, StatusFile] = {}

    def __init__(self, storage: IRecognitionStorage):
        super().__init__(storage)

    def _create_task_id(self) -> str:
        return uuid.uuid1().hex

    @staticmethod
    def _create_file_id() -> str:
        return str(uuid.uuid1())

    @classproperty
    def name(self) -> str:
        return "mock"

    def _imitation_task(self, task_id: str) -> None:
        time.sleep(10)
        self._tasks[task_id].status = Status.SUCCESS
        logger.info(f"Task_id {task_id} is done")

    def send(self, file: BinaryIO, format: str) -> Task_id:
        task_id = self._create_task_id()
        # Write to DB status processing of file_id
        self._tasks[task_id] = StatusFile(
            status=Status.PROCESSING,
            file_id=self._create_file_id(),
        )
        thread_task = threading.Thread(
            target=self._imitation_task, args=(task_id,), daemon=True
        )
        thread_task.start()
        logger.info(f"Create task_id: {task_id}")
        return task_id

    def check_status(self, task_id: str) -> StatusFile:
        return self._tasks.get(task_id) or StatusFile()

    def download(self, task_id: str) -> RecognizedText:
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
        return RecognizedText(chunks=processing_text)
