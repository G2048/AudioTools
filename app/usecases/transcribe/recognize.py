import logging
from typing import BinaryIO

from app.interfaces.audio import IAudioConverter
from app.interfaces.recognizers import IRecognizer, Task_id
from app.interfaces.storages import ITaskStorage, TaskMessage

logger = logging.getLogger("app.usecases.transcribe")


class RecognitionError(Exception):
    detail = "Recognition error"


class AudioRecognitionError(RecognitionError):
    detail = "Error while converting audio"


class StorageRecognitionError(RecognitionError):
    detail = "Error to store audio task id"


class SendRecognizeUseCase:
    def __init__(
        self,
        recognizer: IRecognizer,
        audio_converter: IAudioConverter,
        storage: ITaskStorage,
    ):
        self.recognizer = recognizer
        self.converter = audio_converter
        self.storage = storage

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
        try:
            self.storage.set(
                TaskMessage(
                    task_id=task_id,
                    recognizer=self.recognizer.name,
                    file_id=audio_file.name,
                )
            )
        except Exception as e:
            logger.error(f"Error while send task_id to storage: {e}")
            raise StorageRecognitionError
        return task_id
