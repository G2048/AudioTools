import logging
from typing import BinaryIO

from app.interfaces.audio import IAudioConverter
from app.interfaces.recognizers import IRecognizer, Task_id

logger = logging.getLogger("app.usecases.transcribe")


class RecognitionError(Exception):
    detail = "Recognition error"


class AudioRecognitionError(RecognitionError):
    detail = "Error while converting audio"


class SendRecognizeUseCase:
    def __init__(
        self,
        recognizer: IRecognizer,
        audio_converter: IAudioConverter,
    ):
        self.recognizer = recognizer
        self.converter = audio_converter

    def execute(self, audio_file: BinaryIO) -> Task_id:
        try:
            converted_audio: str = self.converter.convert(audio_file)
        except Exception as e:
            logger.error(f"Error while converting audio: {e}")
            raise AudioRecognitionError

        with open(converted_audio, "rb") as f:
            try:
                task_id = self.recognizer.send(f, self.converter.format)
            except Exception as e:
                logger.error(f"Error while sending audio to recognizer: {e}")
                raise RecognitionError
        return task_id
