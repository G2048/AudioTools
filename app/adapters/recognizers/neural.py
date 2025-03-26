import logging
import threading
import uuid
from pathlib import Path
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
                text=chunk["text"],
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
        return neural_settings.name

    def send(self, audio_file: BinaryIO) -> str:
        task_id = self._create_task_id()
        self._TASKS[task_id] = {"status": Status.PROCESSING, "file_id": self._create_file_id()}
        logger.info(f"Create task for Neural {self.name}: {task_id}")

        # audio_array = self.binay_io_to_numpy(audio_file)
        thread_task = threading.Thread(target=self._transcribe, args=(audio_file.name, task_id), daemon=True)
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
    def _audio_from_file(filename: str, crop_min: float = 0, crop_max: float = 100) -> tuple[int, np.ndarray]:
        try:
            audio = AudioSegment.from_file(filename)
        except FileNotFoundError as e:
            isfile = Path(filename).is_file()
            msg = (
                f"Cannot load audio from file: `{'ffprobe' if isfile else filename}` not found."
                + " Please install `ffmpeg` in your system to use non-WAV audio file formats"
                " and make sure `ffprobe` is in your PATH."
                if isfile
                else ""
            )
            raise RuntimeError(msg) from e
        if crop_min != 0 or crop_max != 100:
            audio_start = len(audio) * crop_min / 100
            audio_end = len(audio) * crop_max / 100
            audio = audio[audio_start:audio_end]
        data = np.array(audio.get_array_of_samples())
        if audio.channels > 1:
            data = data.reshape(-1, audio.channels)
        return audio.frame_rate, data

    def _transcribe(self, audio_file: str, task_id: str):
        print(f"Transcribe audio:{audio_file=}")
        sr, y = self._audio_from_file(audio_file)
        logger.info(f"Audio size: {y.shape}")
        logger.info(f"Audio sampling rate: {sr}")

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
