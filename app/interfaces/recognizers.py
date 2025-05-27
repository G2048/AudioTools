from abc import ABC, abstractmethod
from enum import StrEnum
from typing import BinaryIO, Optional, TypeAlias

from pydantic import BaseModel
from typing_extensions import Literal

Task_id: TypeAlias = str
File_id: TypeAlias = str

StartTime: TypeAlias = str
EndTime: TypeAlias = str

AUDIOFORMAT: Literal["wav"]


class Chunk(BaseModel):
    text: str
    timestamps: tuple[StartTime, EndTime]


class RecognizedText(BaseModel):
    chunks: list[Chunk]


class Status(StrEnum):
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    NONE = "NONE"


class StatusFile(BaseModel):
    status: Status = Status.NONE
    file_id: Optional[File_id] = None


class IRecognizer(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def send(self, file: BinaryIO, format: str) -> Task_id:
        pass

    @abstractmethod
    def check_status(self, task_id: Task_id) -> StatusFile:
        pass

    @abstractmethod
    def download(self, task_id: Task_id) -> RecognizedText | None:
        pass
