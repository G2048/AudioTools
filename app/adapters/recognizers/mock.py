import logging
import uuid
from enum import StrEnum
from typing import BinaryIO

from app.interfaces.recognizers import (
    RecognizedText,
    RecognizedTextInterface,
    RecognizedTexts,
    RecognizerInterface,
)

logger = logging.getLogger("stdout")


class MockRecognizedText(RecognizedTextInterface):
    def get_ready_text(self) -> RecognizedTexts:
        processing_text = [
            RecognizedText(
                timestamps=("0:00:00", "0:00:10"),
                text="Lore Ipsum",
            ),
            RecognizedText(
                timestamps=("0:00:10", "0:00:20"),
                text="Dolor Sit Amet",
            ),
        ]
        return RecognizedTexts(chunk_texts=processing_text)


class StatusRecognize(StrEnum):
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"
    NONE = "none"


class MockRecognizer(RecognizerInterface):
    def _create_task_id(self):
        return uuid.uuid1().hex

    @property
    def name(self) -> str:
        return "mock"

    def recognize(self, audio_file: BinaryIO) -> str:
        task_id = self._create_task_id()
        self.tasks[task_id] = StatusRecognize.PROCESSING
        logger.info(f"Create task_id: {task_id}")
        return task_id

    def check_status(self, task_id: str) -> dict[str, str]:
        return self.tasks.get(task_id, None) or {"status": StatusRecognize.NONE, "file_id": ""}

    def download_file(self, file_id: str) -> MockRecognizedText:
        return MockRecognizedText()
