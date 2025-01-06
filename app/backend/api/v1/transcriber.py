import logging
import re
from datetime import datetime, timedelta

import numpy as np
from fastapi import APIRouter, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.configs.settings import EmailSettings, get_email_settings
from app.services import AudioConverter, AudioRecognizer, Email, EmailSender

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


class EmailService:
    re_email = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    email_message_template = """Здравствуйте!
    \nВаша расшифровка аудио запроса:
    \n%s
    \nЕсли вы получили это сообщение по ошибке, то сообщите мне по email или в чате.
    """

    def __init__(self, email_settings: EmailSettings):
        self.email_sender = EmailSender(email_settings)

    def send_email(self, emails: tuple[str], text: str):
        logger.info(f"Sending emails to {emails}")
        g_emails = (Email(email, self.email_message_template % text) for email in emails)
        self.email_sender.execute(g_emails)
        return emails

    def filter_emails(self, raw_emails: str) -> tuple[str]:
        logger.debug(f"Doing with {raw_emails}")
        return tuple(filter(self.re_email.findall, raw_emails.split(";")))


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


email_service = EmailService(email_settings)
audio_service = AudioService()
audio_converter = AudioConverter


@router.post("/", response_model=Transcription)
# def create_transcription(file: Annotated[bytes, File()], raw_emails: str):
def create_transcription(file: UploadFile, raw_emails: str):
    start = datetime.now()

    # path_to_audio = request.files["audio"].file.path

    audio: np.ndarray = audio_converter.to_numpy(file.file)
    logger.info(f"Audio: {audio=}")

    audio_service.checking_audio(audio)

    emails = email_service.filter_emails(raw_emails)
    if not emails:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Emails not found")

    # Pre-processing
    text_audio = audio_service.recoginition_audio(audio)
    if not text_audio:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cannot transcribe audio"
        )

    # Post processing
    # I don't know whether uploading file to aws
    email_service.send_email(emails, text_audio)
    execution_time = datetime.now() - start
    return Transcription(time_execution=execution_time.total_seconds())
