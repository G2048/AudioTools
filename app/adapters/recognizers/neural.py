import logging
import os
import threading
import uuid
from io import BytesIO
from typing import Any, BinaryIO

import numpy as np
from pydub import AudioSegment

from app.configs import get_neural_settings
from app.drivers.neurals.whisper import NeuralException, Whisper
from app.interfaces.recognizers import (
    Chunk,
    IRecognitionStorage,
    IRecognizer,
    RecognizedText,
    Status,
    StatusFile,
    Task_id,
    TaskIdStatus,
    classproperty,
)

logger = logging.getLogger("app.adapters.recognizers")

# LLMMODEL = "./whisper-large-v3"
neural_settings = get_neural_settings()


class WhisperRecognizer(IRecognizer):
    _whisper: Whisper = Whisper(neural_settings.name)

    def __init__(self, storage: IRecognitionStorage):
        self._storage = storage

    def _create_task_id(self):
        return uuid.uuid1().hex

    @classproperty
    def name(cls) -> str:
        return neural_settings.name.replace(".", "").replace("/", "")

    def _run_task(self, task_id: Task_id, file: BinaryIO) -> None:
        thread_task = threading.Thread(
            target=self._transcribe,
            args=(file, task_id),
            daemon=True,
        )
        thread_task.start()

    def _create_task(self, task_id: Task_id):
        self._task_structure = TaskIdStatus(task_id=task_id, status=Status.NEW)
        self._storage.insert(self._task_structure)

    def _update_task(self, status: Status, transcription: RecognizedText | None = None):
        self._task_structure.status = status
        if transcription:
            self._task_structure.transcription = transcription
        self._storage.insert(self._task_structure)

    def send(self, file: BinaryIO, format: str) -> Task_id:
        # По идее, при создании task_id и Status.New - должна происходить постановка в очередь задач
        task_id = self._create_task_id()
        self._create_task(task_id)
        # TODO: Тут должна происходить постановка в очередь задач

        logger.info(f"Create task for Neural {self.name}: {task_id}")
        self._run_task(task_id, file)
        # audio_array = self.binay_io_to_numpy(audio_file)
        return task_id

    def check_status(self, task_id: Task_id) -> StatusFile:
        task_status = self._storage.select(task_id)
        status_info = {"status": task_status.status}
        return StatusFile(**status_info)

    def download(self, task_id: Task_id) -> RecognizedText | None:
        task_status = self._storage.select(task_id)
        return task_status.transcription

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
    def _binay_io_to_numpy(binary_io: BinaryIO) -> np.ndarray:
        return np.frombuffer(binary_io.read(), dtype=np.uint8)

    def _audio_from_file(
        self,
        filename: BytesIO,
        crop_min: float = 0,
        crop_max: float = 100,
    ) -> tuple[int, np.ndarray]:
        if filename.closed:
            filename = open(filename.name, "rb")
        try:
            audio = AudioSegment.from_file(filename.name)
        except FileNotFoundError as e:
            os.remove(filename.name)
            raise RuntimeError(
                f"Cannot load audio from file: `{filename}` not found"
            ) from e

        logger.debug(f"Audio segment: {audio=}")
        if crop_min != 0 or crop_max != 100:
            audio_start = len(audio) * crop_min / 100
            audio_end = len(audio) * crop_max / 100
            audio = audio[audio_start:audio_end]
        data = np.array(audio.get_array_of_samples())
        if audio.channels > 1:
            data = data.reshape(-1, audio.channels)

        frame_rate = audio.frame_rate
        return frame_rate, data

    def _transcribe(self, audio_file: BytesIO, task_id: str):
        self._update_task(Status.PROCESSING)
        try:
            logger.debug(f"Transcribe audio:{audio_file=}")
            sr, y = self._audio_from_file(audio_file)
        except Exception as e:
            logger.warning(f"Close audio file {audio_file.name=}")
            self._update_task(Status.ERROR)
            logger.error(f"Error While coverting file to numpy: {e}")
            raise e
        try:
            transcribed_text = self._whisper.transcribe(sr, y)
        except NeuralException as e:
            logger.warning(f"Close audio file {audio_file.name=}")
            # audio_file.close()
            self._update_task(Status.ERROR)
            logger.error(f"Error While transcribing: {e}")
            return
        else:
            self._update_task(
                Status.SUCCESS,
                self._processing_text(
                    transcribed_text["chunks"],
                ),
            )
