import logging
import os
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import Depends, UploadFile
from fastapi.exceptions import HTTPException

from app.adapters.converters.ffmpeg import ConverterFactory
from app.api.dependencies import get_recognizer
from app.interfaces.recognizers import IRecognizer, Task_id
from app.usecases.transcribe import RecognitionError, SendRecognizeUseCase

logger = logging.getLogger("app.api.dependencies.adapters")


class AdapterSendRecognizeUseCase(SendRecognizeUseCase):
    FORMAT = "wav"

    def __init__(
        self,
        audiofile: UploadFile,
        recognizer: Annotated[IRecognizer, Depends(get_recognizer)],
    ):
        self.recognizer = recognizer
        self._converter = ConverterFactory().get_converter(self.FORMAT)
        logger.info(f"Upload audiofile: {audiofile.filename}")
        logger.debug(f"Type {audiofile.filename=}")
        self.audiofile = self._create_temp_file(audiofile)
        super().__init__(
            recognizer=self.recognizer,
            audio_converter=self._converter,
        )

    def _create_temp_file(self, audiofile: UploadFile):
        tmp_file = NamedTemporaryFile(
            suffix=self.FORMAT, delete=False, delete_on_close=False
        )
        tmp_file.write(audiofile.file.read())
        tmp_file.seek(0)
        logger.debug(f"Created temp file {tmp_file.name=}")
        return tmp_file

    def execute(self) -> Task_id:
        try:
            f = open(self.audiofile.name, "rb")
            return super().execute(f)
        except RecognitionError as e:
            raise HTTPException(status_code=500, detail=e.detail)
        finally:
            logger.debug(f"Delete temp file {self.audiofile.name=}")
            os.remove(self.audiofile.name)


def get_usecase() -> AdapterSendRecognizeUseCase:
    return AdapterSendRecognizeUseCase
