import logging
import os
import tempfile
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import check_auth, get_recognizer, get_recognizers
from app.api.dependencies.adapters.recoginze import (
    AdapterSendRecognizeUseCase,
)
from app.api.models.audio import (
    ResponseAvailableRecognizers,
    ResponseStatus,
    ResponseTaskId,
)
from app.interfaces.recognizers import IRecognizer, RecognizedText

router = APIRouter(
    prefix="/api/v1/audio",
    tags=["Audio Trinscribe"],
    dependencies=[Depends(check_auth)],
)
logger = logging.getLogger("app.api.v1.routers")


@router.get("/recognizers", response_model=ResponseAvailableRecognizers)
async def get_available_recognizers(
    recognizers: Annotated[list[str], Depends(get_recognizers)],
) -> ResponseAvailableRecognizers:
    return ResponseAvailableRecognizers(recognizers=recognizers)


# Взять с помощью специального заголовка
@router.get("/status/mock/{task_id}")
def mock_check_status_id(
    task_id: str, client: IRecognizer = Depends(get_recognizer)
) -> ResponseStatus:
    file_status = client.check_status(task_id)
    return ResponseStatus(status=file_status.status, file_id=file_status.file_id)


# TODO: Здесь нужно сделать выбор распознавателя на уровне клиента api
# Сделать выбор распознавателя в виде enum
@router.post("/")
def send_audio_for_transcription(
    usecase: Annotated[
        AdapterSendRecognizeUseCase, Depends(AdapterSendRecognizeUseCase)
    ],
) -> ResponseTaskId:
    task_id = usecase.execute()
    return ResponseTaskId(task_id=task_id)


# TODO: здесь нужно придумать какую-то фабрику....
@router.get("/status/{task_id}")
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
@router.get("/")
def get_audio_transcription(
    task_id: str,
    recognizer: Annotated[IRecognizer, Depends(get_recognizer)],
    # with_timestamp: bool = False,
) -> RecognizedText | None:
    logger.info(f"Download {task_id} file...")
    return recognizer.download(task_id)
