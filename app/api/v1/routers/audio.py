import logging
import os
import tempfile
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from app.api.dependencies import check_auth, get_providers, get_recognizer
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


@router.get("/providers", response_model=ResponseAvailableRecognizers)
async def get_available_recognizers(
    providers: Annotated[list[str], Depends(get_providers)],
) -> ResponseAvailableRecognizers:
    return ResponseAvailableRecognizers(providers=providers)


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
    audiofile: UploadFile,
    provider: Annotated[IRecognizer, Depends(get_recognizer)],
) -> ResponseTaskId:
    logger.debug(f"Type {audiofile.file=}")
    logger.debug(f"Type {audiofile.filename=}")
    # with open(audiofile.file, "rb") as f:
    audiofile.name = audiofile.filename
    FORMAT = "mp3"
    task_id = provider.send(audiofile.file, FORMAT)
    return ResponseTaskId(task_id=task_id)


# TODO: здесь нужно придумать какую-то фабрику....
@router.get("/status/{task_id}")
def check_status_id(
    task_id: str,
    provider: Annotated[IRecognizer, Depends(get_recognizer)],
) -> ResponseStatus:
    task_status = provider.check_status(task_id)
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
    provider: Annotated[IRecognizer, Depends(get_recognizer)],
    # with_timestamp: bool = False,
) -> RecognizedText | None:
    logger.info(f"Download {task_id} file...")
    return provider.download(task_id)
