from typing import Optional

from pydantic import BaseModel

from app.interfaces.recognizers import File_id, Task_id


class Audio(BaseModel):
    status: str
    file_id: File_id


class ResponseStatus(BaseModel):
    status: str
    file_id: Optional[File_id] = None


class ResponseAvailableRecognizers(BaseModel):
    recognizers: list[str]


class ResponseTaskId(BaseModel):
    task_id: Task_id
