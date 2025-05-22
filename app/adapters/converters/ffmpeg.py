import logging
import os
from pathlib import Path

import numpy as np
from pydub import AudioSegment

from app.interfaces.audio import IAudioConverter

logger = logging.getLogger("app.adapters.converters")


class AudioConverter(IAudioConverter):
    def __init__(self, file: str, output_path: str = "/tmp/"):
        self.output_path = Path(output_path)
        if not self.output_path.exists():
            raise FileNotFoundError(
                f"The output path {self.output_path} does not exist"
            )

        self.current_file = Path(file)
        self._format = self.current_file.suffix
        self.segment = AudioSegment.from_file(file, self._format)

    @property
    def channels(self):
        return self.segment.channels

    @property
    def size(self) -> int:
        return os.path.getsize(self.current_file)

    @property
    def duration(self) -> int:
        return self.segment.duration_seconds

    @property
    def format(self):
        return self._format

    def convert_mp3(self):
        return self.convert("mp3")

    def convert_ogg(self):
        return self.convert("ogg")

    def convert_wav(self):
        return self.convert("wav")

    def _new_path(self, format: str) -> str:
        return os.path.join(self.output_path, f"{self.current_file}.{format}")

    def convert(self, format: str = "wav"):
        logger.info(f"Converting the {self.current_file} file to {format}")
        try:
            # -ac 1 is option that convert audio to 1 channel
            output_after_converting = self.segment.export(
                self._new_path(format),
                format=format,
                parameters=["-ac", "1"],
            )
            new_name = output_after_converting.name
            output_after_converting.close()
        except Exception as e:
            logger.error(f"Error while converting {self.current_file.file} to {format}")
            logger.error(f"{e=}")
            raise e

    def to_format(self, audio: np.ndarray):
        return audio.convert_from_numpy(audio)

    @staticmethod
    def match_target_amplitude(
        sound: AudioSegment, target_dBFS: int | float = -20
    ) -> AudioSegment:
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)

    def to_numpy(
        self, crop_min: float = 0, crop_max: float = 100
    ) -> tuple[int, np.ndarray]:
        if crop_min != 0 or crop_max != 100:
            audio_start = len(self.segment) * crop_min / 100
            audio_end = len(self.segment) * crop_max / 100
            self.segment = self.segment[audio_start:audio_end]
        data = np.array(self.segment.get_array_of_samples())
        if self.segment.channels > 1:
            data = data.reshape(-1, self.segment.channels)
            # np_array = np.mean(np_array, axis=1)
        return self.segment.frame_rate, data
