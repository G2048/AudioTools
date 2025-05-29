from typing import Annotated, Literal

from fastapi import Depends
from fastapi.exceptions import HTTPException

from app.adapters.recognizers import Providers
from app.adapters.storages.memory import TaskIdNotFoundError
from app.interfaces.recognizers import IRecognitionStorage, IRecognizer, Task_id
from app.interfaces.storages import ITaskStorage

from .storages import get_recognition_storage, get_task_storage

recognizers_fabric = Providers()


def get_recognizers() -> list[str]:
    return recognizers_fabric.list()


def get_recognizer(
    storage: Annotated[IRecognitionStorage, Depends(get_recognition_storage)],
    recognizer: Literal[*get_recognizers()],
) -> IRecognizer:
    name = recognizer.lower()
    try:
        return recognizers_fabric[name](storage)
    except AttributeError:
        raise HTTPException(status_code=404, detail=f"No such recognizer {name}")


def get_recognizer_by_task_id(
    task_id: Task_id,
    storage: Annotated[ITaskStorage, Depends(get_task_storage)],
    recognizer_storage: Annotated[
        IRecognitionStorage, Depends(get_recognition_storage)
    ],
) -> IRecognizer:
    try:
        task_message = storage.get(task_id)
        return recognizers_fabric[task_message.recognizer](recognizer_storage)
    except (AttributeError, TaskIdNotFoundError):
        raise HTTPException(status_code=404, detail=f"Task_id {task_id} not found")
