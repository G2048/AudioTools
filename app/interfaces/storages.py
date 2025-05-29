from abc import ABC, abstractmethod
from typing import BinaryIO, NewType

from pydantic import BaseModel

from .recognizers import AUDIOFORMAT, File_id, Task_id

TTLTaskId: int = 1800  # 30 minutes


class TaskMessage(BaseModel):
    task_id: Task_id
    recognizer: str
    format: str = AUDIOFORMAT
    file_id: File_id

    def model_dump_json(self, *args, **kwargs):
        return super().model_dump_json(
            exclude_none=True, exclude={"task_id"}, *args, **kwargs
        )


class ITaskStorage(ABC):
    @abstractmethod
    def set(self, message: TaskMessage) -> bool:
        pass

    @abstractmethod
    def get(self, task_id: Task_id) -> TaskMessage | None:
        pass

    @abstractmethod
    def list(self) -> list[TaskMessage] | None:
        pass


HashedFile = NewType("HashedFile", str)


class IHasher(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def empty_value(self) -> str:
        pass

    @abstractmethod
    def hash(self, bfile: BinaryIO) -> HashedFile: ...
