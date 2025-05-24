import logging
import os
import threading
import uuid
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import Any, BinaryIO

import numpy as np
from pydub import AudioSegment

from app.configs import get_neural_settings
from app.drivers.neurals.whisper import NeuralException, Whisper
from app.interfaces.recognizers import (
    Chunk,
    IRecognizer,
    RecognizedText,
    Status,
    StatusFile,
    Task_id,
)

logger = logging.getLogger("app.adapters.recognizers")

# LLMMODEL = "./whisper-large-v3"
neural_settings = get_neural_settings()


class WhisperRecognizer(IRecognizer):
    _whisper: Whisper = Whisper(neural_settings.name)
    _TASKS: dict[Task_id, dict[str, Any]] = {}

    @staticmethod
    def _create_file_id() -> str:
        return str(uuid.uuid1())

    def _create_task_id(self):
        return uuid.uuid1().hex

    @property
    def name(self) -> str:
        return neural_settings.name.replace(".", "").replace("/", "")

    def _run_task(self, task_id: Task_id, file: BinaryIO) -> None:
        thread_task = threading.Thread(
            target=self._transcribe,
            args=(file, task_id),
            daemon=True,
        )
        thread_task.start()

    def send(self, file: BinaryIO, format: str) -> Task_id:
        task_id = self._create_task_id()
        self._TASKS[task_id] = {
            "status": Status.PROCESSING,
            "file_id": self._create_file_id(),
        }
        logger.info(f"Create task for Neural {self.name}: {task_id}")
        self._run_task(task_id, file)
        # audio_array = self.binay_io_to_numpy(audio_file)
        return task_id

    def check_status(self, task_id: str) -> StatusFile:
        status_info = self._TASKS.get(task_id, None)
        if status_info is None:
            return StatusFile()
        return StatusFile(**status_info)

    def download(self, task_id: Task_id) -> RecognizedText | None:
        task_info = self._TASKS.get(task_id)
        if task_info and task_info["status"] == Status.SUCCESS:
            return self._processing_text(task_info["results"]["chunks"])

    def _processing_text(self, chunks: list[dict[str, Any]]) -> RecognizedText:
        processing_text = [
            Chunk(
                timestamps=(str(chunk["timestamp"][0]), str(chunk["timestamp"][1])),
                text=chunk["text"].removeprefix(" "),
            )
            for chunk in chunks
        ]
        return RecognizedText(chunks=processing_text)

    @staticmethod
    def binay_io_to_numpy(binary_io: BinaryIO) -> np.ndarray:
        return np.frombuffer(binary_io.read(), dtype=np.uint8)

    @staticmethod
    def _create_tmp_file(audio_file: BytesIO) -> str:
        tmp_file = NamedTemporaryFile(delete=False, delete_on_close=False)
        logger.debug(f"Create tmp file: {tmp_file.name}")
        # SpooledTemporaryFile закрывается из-за того, передается в другой поток
        logger.debug(f"{audio_file=}")
        tmp_file.writelines(audio_file)
        return tmp_file.file

    def _audio_from_file(
        self,
        filename: BytesIO,
        crop_min: float = 0,
        crop_max: float = 100,
    ) -> tuple[int, np.ndarray]:
        filename = self._create_tmp_file(filename)

        logger.debug(f"Convert to numpy Audio file: {filename=}")
        try:
            audio = AudioSegment.from_file(filename.name)
        except FileNotFoundError as e:
            msg = (
                f"Cannot load audio from file: `{filename}` not found."
                + " Please install `ffmpeg` in your system to use non-WAV audio file formats"
                " and make sure `ffprobe` is in your PATH."
            )
            os.remove(filename.name)
            raise RuntimeError(msg) from e

        logger.debug(f"Audio segment: {audio=}")
        if crop_min != 0 or crop_max != 100:
            audio_start = len(audio) * crop_min / 100
            audio_end = len(audio) * crop_max / 100
            audio = audio[audio_start:audio_end]
        data = np.array(audio.get_array_of_samples())
        if audio.channels > 1:
            data = data.reshape(-1, audio.channels)

        frame_rate = audio.frame_rate
        # os.remove(filename.name)
        return frame_rate, data

    def _transcribe(self, audio_file: BytesIO, task_id: str):
        try:
            logger.debug(f"Transcribe audio:{audio_file=}")
            sr, y = self._audio_from_file(audio_file)
        except Exception as e:
            self._TASKS[task_id]["status"] = Status.ERROR
            logger.error(f"Error While coverting file to numpy: {e}")
            raise e
        try:
            transcribed_text = self._whisper.transcribe(sr, y)
        except NeuralException as e:
            self._TASKS[task_id]["status"] = Status.ERROR
            logger.error(f"Error While transcribing: {e}")
            return
        else:
            self._TASKS[task_id]["status"] = Status.SUCCESS
            self._TASKS[task_id]["results"] = transcribed_text
