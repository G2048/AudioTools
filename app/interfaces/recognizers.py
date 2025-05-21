from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any, BinaryIO, TypeAlias

from pydantic import BaseModel

Task_id: TypeAlias = str
File_id: TypeAlias = str

StartTime: TypeAlias = str
EndTime: TypeAlias = str


class Chunk(BaseModel):
    timestamps: tuple[StartTime, EndTime]
    text: str


class RecognizedText(BaseModel):
    chunk_texts: list[Chunk]


# {
#     text: "some text",
#     timestamps: ("00:00:00", "00:00:01"),
# }


class IRecognizedText(ABC):
    @abstractmethod
    def get_ready_text(self) -> RecognizedText:
        pass


class Status(StrEnum):
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    NONE = "NONE"


class CheckStatusFileID(BaseModel):
    status: Status
    file_id: File_id | None
    result: Any | None


class IRecognizer(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def _create_task_id(self) -> Task_id:
        pass

    @abstractmethod
    def send(self, audio_file: BinaryIO) -> Task_id:
        pass

    @abstractmethod
    def check_status(self, task_id: Task_id) -> CheckStatusFileID:
        pass

    @abstractmethod
    def download(self, task_id: Task_id) -> IRecognizedText:
        pass
