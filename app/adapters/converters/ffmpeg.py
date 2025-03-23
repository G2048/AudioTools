import logging
import os
from pathlib import Path

import numpy as np
from ffmpy import FFmpeg
from pydub import AudioSegment

from app.interfaces.audio import AudioConverterInterface, AudioFilesInterfase

logger = logging.getLogger("stdout")


class AudioFiles(AudioFilesInterfase):
    __slot__ = ("list_audio", "name", "path", "output_path")

    def __init__(self, file_path: str, output_path: str = "."):
        # name without extension
        self._file = Path(file_path)
        self.name = self._file.stem
        self.list_audio: dict[str, None] = {}
        self.output_path = output_path

    @classmethod
    def create_from_numpy(cls, audio: np.ndarray):
        return

    def create(self, format: str) -> dict[str, None]:
        self.list_audio.update({self._new_path(format): None})
        return self.list_audio

    def _new_path(self, format: str) -> str:
        return os.path.join(self.output_path, f"{self.name}.{format}")

    # @classmethod
    def clean(self):
        self.list_audio.clear()


class AudioConverter(AudioConverterInterface):
    def convert_mp3(self):
        self.convert()

    def convert_ogg(self):
        self.convert("ogg")

    def convert_wav(self):
        self.convert("wav")

    # TODO: Rewrite convert to use pydub
    def convert(self, format: str = "mp3"):
        logger.info(f"Converting {self.file.name} to {format}")
        ff = FFmpeg(inputs={self.file.path: None}, outputs=self.file.create(format))

        logger.debug(f"String for execution: {ff.cmd}")
        try:
            ff.run()
            logger.error(f"Error while converting {self.file} to {format}")
        except Exception as e:
            logger.error(e)
            logger.error(f"Error while converting {self.file} to {format}")
            logger.error(f"String for execution: {ff.cmd}")

    @staticmethod
    def to_numpy(filename: str, crop_min: float = 0, crop_max: float = 100) -> tuple[int, np.ndarray]:
        try:
            segment = AudioSegment.from_file(filename)
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
        except OSError as e:
            raise e
        if crop_min != 0 or crop_max != 100:
            audio_start = len(segment) * crop_min / 100
            audio_end = len(segment) * crop_max / 100
            segment = segment[audio_start:audio_end]
        data = np.array(segment.get_array_of_samples())
        if segment.channels > 1:
            data = data.reshape(-1, segment.channels)
            # np_array = np.mean(np_array, axis=1)
        return segment.frame_rate, data
