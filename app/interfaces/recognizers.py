from abc import ABC, abstractmethod
from typing import BinaryIO, TypeAlias

from pydantic import BaseModel

start_time: TypeAlias = str
end_time: TypeAlias = str


class RecognizedText(BaseModel):
    timestamps: tuple[start_time, end_time]
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


task_id: TypeAlias = str
file_id: TypeAlias = str
status: TypeAlias = str


class RecognizerInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def recognize(self, audio_file: BinaryIO) -> task_id:
        pass

    @abstractmethod
    def check_status(self, task_id: str) -> dict[status, file_id]:
        pass

    @abstractmethod
    def download_file(self, file_id: str) -> RecognizedTextInterface:
        pass
