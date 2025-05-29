from fastapi import HTTPException

from app.adapters.storages.memory import (
    RedisRecognitionStorage,
    RedisTaskStorage,
    StorageException,
)
from app.interfaces.recognizers import IRecognitionStorage
from app.interfaces.storages import ITaskStorage


def get_task_storage() -> ITaskStorage:
    try:
        return RedisTaskStorage()
    except StorageException as e:
        raise HTTPException(status_code=500, detail=e.detail)


def get_recognition_storage() -> IRecognitionStorage:
    try:
        return RedisRecognitionStorage()
    except StorageException as e:
        raise HTTPException(status_code=500, detail=e.detail)
