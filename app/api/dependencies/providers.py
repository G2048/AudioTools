from typing import Annotated

from fastapi import Depends
from fastapi.exceptions import HTTPException

from app.adapters.recognizers import Providers
from app.interfaces.recognizers import IRecognizer, Task_id
from app.interfaces.storages import ITaskStorage

from .storages import get_task_storage

recognizers_fabric = Providers()


def get_recognizers() -> list[str]:
    return recognizers_fabric.list()


def get_recognizer(
    provider: str,
) -> IRecognizer:
    name = provider.lower()
    try:
        return recognizers_fabric[name]
    except AttributeError:
        raise HTTPException(status_code=404, detail=f"No such recognizer {name}")


def get_recognizer_by_task_id(
    task_id: Task_id,
    storage: Annotated[ITaskStorage, Depends(get_task_storage)],
) -> IRecognizer:
    task_message = storage.get(task_id)
    try:
        return recognizers_fabric[task_message.recognizer]
    except AttributeError:
        raise HTTPException(status_code=404, detail=f"Task_id {task_id} not found")
