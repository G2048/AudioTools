import logging
import os
import threading
import uuid
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import BinaryIO

import numpy as np
from pydub import AudioSegment
from transformers import Pipeline, pipeline

from app.configs import get_neural_settings
from app.interfaces.recognizers import (
    RecognizedText,
    RecognizedTextInterface,
    RecognizedTexts,
    RecognizerInterface,
    Status,
)

logger = logging.getLogger("stdout")

# LLMMODEL = "./whisper-large-v3"
neural_settings = get_neural_settings()


class NeuralRecognizedText(RecognizedTextInterface):
    def __init__(self, chunks: list, with_timestamp: bool = True) -> None:
        self.chunks = chunks

    def get_ready_text(self) -> RecognizedTexts:
        processing_text = [
            RecognizedText(
                timestamps=(str(chunk["timestamp"][0]), str(chunk["timestamp"][1])),
                text=chunk["text"].removeprefix(" "),
            )
            for chunk in self.chunks
        ]
        return RecognizedTexts(chunk_texts=processing_text)


class WhisperRecognizer(RecognizerInterface):
    __transcriber: Pipeline = pipeline(
        "automatic-speech-recognition", max_new_tokens=445, model=neural_settings.name
    )
    _TASKS = {}

    @staticmethod
    def _create_file_id() -> str:
        return str(uuid.uuid1())

    def _create_task_id(self):
        return uuid.uuid1().hex

    @property
    def name(self) -> str:
        return neural_settings.name.replace(".", "").replace("/", "")

    def send(self, audio_file: BinaryIO) -> str:
        task_id = self._create_task_id()
        self._TASKS[task_id] = {"status": Status.PROCESSING, "file_id": self._create_file_id()}
        logger.info(f"Create task for Neural {self.name}: {task_id}")

        tmp_audio_file = self._create_tmp_file(audio_file)
        # audio_array = self.binay_io_to_numpy(audio_file)
        thread_task = threading.Thread(target=self._transcribe, args=(tmp_audio_file, task_id), daemon=True)
        thread_task.start()
        return task_id

    def check_status(self, task_id: str) -> dict[str, str]:
        return self._TASKS.get(task_id, None) or {"status": Status.NONE, "file_id": "", "text": ""}

    def download(self, task_id: str) -> NeuralRecognizedText:
        task_info = self._TASKS.get(task_id)
        if task_info and task_info["status"] == Status.SUCCESS:
            return NeuralRecognizedText(task_info["text"]["chunks"])

    @staticmethod
    def binay_io_to_numpy(binary_io: BinaryIO) -> np.ndarray:
        return np.frombuffer(binary_io.read(), dtype=np.uint8)

    @staticmethod
    def _audio_from_file(
        filename: BytesIO, crop_min: float = 0, crop_max: float = 100
    ) -> tuple[int, np.ndarray]:
        logger.debug(f"Convert to numpy Audio file: {filename=}")
        try:
            audio = AudioSegment.from_file(filename.name)
        except FileNotFoundError as e:
            msg = (
                f"Cannot load audio from file: `{filename}` not found."
                + " Please install `ffmpeg` in your system to use non-WAV audio file formats"
                " and make sure `ffprobe` is in your PATH."
            )
            raise RuntimeError(msg) from e
        logger.debug(f"Audio segment: {audio=}")
        if crop_min != 0 or crop_max != 100:
            audio_start = len(audio) * crop_min / 100
            audio_end = len(audio) * crop_max / 100
            audio = audio[audio_start:audio_end]
        data = np.array(audio.get_array_of_samples())
        if audio.channels > 1:
            data = data.reshape(-1, audio.channels)
        return audio.frame_rate, data

    @staticmethod
    def _create_tmp_file(audio_file: BytesIO) -> str:
        tmp_file = NamedTemporaryFile(delete=False)
        tmp_file.writelines(audio_file)
        return tmp_file.file

    def _transcribe(self, audio_file: BytesIO, task_id: str):
        try:
            logger.debug(f"Transcribe audio:{audio_file=}")
            sr, y = self._audio_from_file(audio_file)
            logger.info(f"Audio size: {y.shape}")
            logger.info(f"Audio sampling rate: {sr}")
        except Exception as e:
            self._TASKS[task_id]["status"] = Status.ERROR
            logger.error(f"Error While coverting file to numpy: {e}")
            return
        finally:
            os.remove(audio_file.name)

        # Convert to mono if stereo
        if y.ndim > 1:
            y = y.mean(axis=1)

        y = y.astype(np.float32)
        y /= np.max(np.abs(y))
        try:
            transcribed_text = self.__transcriber({"sampling_rate": sr, "raw": y}, return_timestamps=True)
        except Exception as e:
            self._TASKS[task_id]["status"] = Status.ERROR
            logger.error(f"Error While transcribing: {e}")
            return
        else:
            self._TASKS[task_id]["status"] = Status.SUCCESS
            self._TASKS[task_id]["text"] = transcribed_text
