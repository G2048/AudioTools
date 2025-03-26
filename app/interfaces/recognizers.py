from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any, BinaryIO, TypeAlias

from pydantic import BaseModel

Start_Time: TypeAlias = str
End_Time: TypeAlias = str


class RecognizedText(BaseModel):
    timestamps: tuple[Start_Time, End_Time]
    text: str


class RecognizedTexts(BaseModel):
    chunk_texts: list[RecognizedText]


# {
#     text: "some text",
#     timestamps: ("00:00:00", "00:00:01"),
# }


class RecognizedTextInterface(ABC):
    @abstractmethod
    def get_ready_text(self) -> RecognizedTexts:
        pass


class Status(StrEnum):
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    NONE = "NONE"


Task_id: TypeAlias = str
File_id: TypeAlias = str


class CheckStatusFileID(BaseModel):
    status: Status
    file_id: File_id | None
    result: Any | None


class RecognizerInterface(ABC):
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
    def check_status(self, task_id: Task_id) -> CheckStatusFileID | dict[Status, File_id]:
        pass

    @abstractmethod
    def download(self, task_id: Task_id) -> RecognizedTextInterface:
        pass
