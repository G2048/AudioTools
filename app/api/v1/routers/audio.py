import logging
import os
import tempfile
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from app.adapters.storages.memory import StorageException
from app.api.dependencies import (
    check_auth,
    get_recognizer,
    get_recognizers,
    get_task_storage,
)
from app.api.dependencies.adapters.recoginze import (
    AdapterSendRecognizeUseCase,
)
from app.api.models.audio import (
    ResponseAvailableRecognizers,
    ResponseStatus,
    ResponseTaskId,
)
from app.interfaces.recognizers import IRecognizer, RecognizedText, Task_id
from app.interfaces.storages import ITaskStorage, TaskMessage

router = APIRouter(
    prefix="/api/v1/audio",
    dependencies=[Depends(check_auth)],
)
logger = logging.getLogger("app.api.v1.routers")


@router.get(
    "/recognizers",
    tags=["Audio Recognition"],
    response_model=ResponseAvailableRecognizers,
)
async def get_available_recognizers(
    recognizers: Annotated[list[str], Depends(get_recognizers)],
) -> ResponseAvailableRecognizers:
    return ResponseAvailableRecognizers(recognizers=recognizers)


# Взять с помощью специального заголовка
@router.get("/status/mock/{task_id}", tags=["Audio Mock"])
def mock_check_status_id(
    task_id: str, client: IRecognizer = Depends(get_recognizer)
) -> ResponseStatus:
    file_status = client.check_status(task_id)
    return ResponseStatus(status=file_status.status, file_id=file_status.file_id)


# TODO: Здесь нужно сделать выбор распознавателя на уровне клиента api
# Сделать выбор распознавателя в виде enum
@router.post("/", tags=["Audio Recognition"])
def send_audio_for_transcription(
    usecase: Annotated[
        AdapterSendRecognizeUseCase, Depends(AdapterSendRecognizeUseCase)
    ],
) -> ResponseTaskId:
    task_id = usecase.execute()
    return ResponseTaskId(task_id=task_id)


# TODO: здесь нужно придумать какую-то фабрику....
@router.get("/status/{task_id}", tags=["Audio Recognition"])
def check_status_id(
    task_id: str,
    recognizer: Annotated[IRecognizer, Depends(get_recognizer)],
) -> ResponseStatus:
    task_status = recognizer.check_status(task_id)
    return ResponseStatus(status=task_status.status, file_id=task_status.file_id)


def write_to_temp_file(text: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w") as f:
        f.write(text)
    return path


# TODO: реализовать получение текста на почту.
# В идеале получение текста должно быть запрошено при расознавании
@router.get("/", tags=["Audio Recognition"])
def get_audio_transcription(
    task_id: str,
    recognizer: Annotated[IRecognizer, Depends(get_recognizer)],
    # with_timestamp: bool = False,
) -> RecognizedText | None:
    logger.info(f"Download {task_id} file...")
    return recognizer.download(task_id)


@router.get("/tasks/", tags=["Audio Tasks"])
def get_list_tasks(
    storage: Annotated[ITaskStorage, Depends(get_task_storage)],
) -> list[TaskMessage] | None:
    try:
        return storage.list()
    except StorageException as e:
        raise HTTPException(status_code=404, detail=e.detail)


@router.get("/tasks/{task_id}", tags=["Audio Tasks"])
def get_task_recognition(
    task_id: Task_id,
    storage: Annotated[ITaskStorage, Depends(get_task_storage)],
) -> TaskMessage | None:
    try:
        return storage.get(task_id)
    except StorageException as e:
        raise HTTPException(status_code=404, detail=e.detail)
