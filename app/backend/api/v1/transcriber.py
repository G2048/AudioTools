import asyncio
import logging
import re
from datetime import datetime

import numpy as np
from fastapi import APIRouter, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.backend.broker import NatsConnection, NatsPublisher
from app.configs.settings import get_email_settings
from app.services import AudioConverter, AudioRecognizer

# from app.backend.api.v1.transcriber.models import Transcription
# from app.backend.api.v1.transcriber.utils import get_transcription
# from app.backend.core.database import get_db


# @router.get("/transcription", response_model=Transcription)
# async def get_transcription(transcription_id: int, db: Session = Depends(get_db)):
#     transcription = get_transcription(db, transcription_id)
#     if not transcription:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found")
#     return transcription

router = APIRouter(prefix="/v1/transcriber")

logger = logging.getLogger("stdout")
email_settings = get_email_settings()
logger.debug(f"Email settings: {email_settings}")


class Transcription(BaseModel):
    time_execution: float


RE_EMAIL = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def filter_emails(emails: str) -> list[str]:
    logger.debug(f"Doing with {emails}")
    return RE_EMAIL.findall(emails)


class AudioService:
    AUDIO_LIMIT = 10**9

    def __init__(self):
        self.audo_recoginition = AudioRecognizer()

    def recoginition_audio(self, audio: np.ndarray) -> str:
        logger.info("Start Transcription audio file")
        return self.audo_recoginition.execute(audio)

    def checking_audio(self, audio: np.ndarray):
        if not len(audio):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio not found")

        if len(audio) >= self.AUDIO_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Max file size is 1 GB"
            )


audio_service = AudioService()
audio_converter = AudioConverter


class BrokerEmailMessage(BaseModel):
    emails: list[str]
    text_audio: str


async def send_emails_to_broker(public: str, message: BrokerEmailMessage):
    logger.info("Sending emails to broker")
    async with NatsConnection() as nats:
        publisher = NatsPublisher(public, nats.connect)
        await publisher.publish(message.model_dump_json().encode())


def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(coro)
    except Exception as e:
        logger.exception(f"Error: {e}")


PUBLIC = "emails"


@router.post("/", response_model=Transcription)
# def create_transcription(file: Annotated[bytes, File()], emails: str):
def create_transcription(file: UploadFile, emails: list[str]):
    start = datetime.now()

    audio: np.ndarray = audio_converter.to_numpy(file.file)
    logger.info(f"Audio: {audio=}")

    audio_service.checking_audio(audio)

    emails = filter_emails(" ".join(emails))
    if not emails:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Emails not found")

    # Pre-processing
    text_audio = audio_service.recoginition_audio(audio)
    if not text_audio:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cannot transcribe audio"
        )

    message = BrokerEmailMessage(emails=emails, text_audio=text_audio)
    run_async(send_emails_to_broker(PUBLIC, message))

    # Post processing
    execution_time = datetime.now() - start
    return Transcription(time_execution=execution_time.total_seconds())
