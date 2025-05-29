from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any, BinaryIO, Callable, Literal, Optional, TypeAlias

from pydantic import BaseModel

Task_id: TypeAlias = str
File_id: TypeAlias = str

StartTime: TypeAlias = str
EndTime: TypeAlias = str

AUDIOFORMAT: Literal["wav"] = "wav"


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


class TaskIdStatus(BaseModel):
    task_id: Task_id
    status: Status = Status.NONE
    transcription: Optional[RecognizedText] = None
    # file_id: Optional[File_id] = None


class IRecognitionStorage(ABC):
    @abstractmethod
    def insert(self, task_status: TaskIdStatus) -> None:
        pass

    @abstractmethod
    def select(self, task_id: Task_id) -> TaskIdStatus:
        pass


class classproperty(property):
    __slots__ = ("fget",)

    def __init__(self, fget: Callable[[Any], Any]) -> None:
        self.fget = fget

    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


class IRecognizer(ABC):
    def __init__(self, storage: IRecognitionStorage):
        pass

    @classproperty
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
