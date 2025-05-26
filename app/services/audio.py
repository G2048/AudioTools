import logging
import os
from decimal import Decimal
from pathlib import Path

import numpy as np
from pydub import AudioSegment
from pydub.utils import mediainfo

logger = logging.getLogger("app.services.audio")


class AudioInfo:
    def __init__(self, file: str):
        self._file = file
        self._metadata: dict[str, str] = mediainfo(self._file)

    @property
    def name(self):
        return Path(self._file).name

    @property
    def channels(self):
        return int(self._metadata["channels"])

    @property
    def bitrate(self):
        return int(self._metadata["bit_rate"])

    @property
    def size(self):
        return int(self._metadata["size"])

    @property
    def duration(self):
        return Decimal(self._metadata["duration"])

    @property
    def format(self):
        return self._metadata["format_name"]

    @property
    def codec(self):
        return self._metadata["codec_name"]

    def __repr__(self):
        return f"AudioChecker(name={self.name}, channels={self.channels}, size={self.size}, duration={self.duration}, format={self.format}, codec={self.codec})"  # noqa: E501

    __str__ = __repr__


class FFmpegConverter:
    # See for more info: https://ffmpeg.org/ffmpeg-formats.html
    _FILE_FORMATS: dict[str, str] = {
        "wma": "asf",
        "opus": "ogg",
    }
    CHANNELS = "1"

    def __init__(self, file: str, output_path: str = "/tmp/"):
        self.output_path = Path(output_path)
        if not self.output_path.exists():
            raise FileNotFoundError(
                f"The output path {self.output_path} does not exist"
            )

        self._file = Path(file)
        _format = self._file.suffix.replace(".", "")
        self._format: str = self._FILE_FORMATS.get(_format, _format)
        self.segment = AudioSegment.from_file(file, self._format)
        # AudioSegment.from_raw()

    @property
    def format(self) -> str:
        return self._format

    @property
    def name(self) -> str:
        return self._file

    @property
    def channels(self) -> int:
        return self.segment.channels

    @property
    def size(self) -> int:
        return os.path.getsize(self._file)

    @property
    def duration(self) -> float:
        return self.segment.duration_seconds

    def convert_mp3(self):
        return self.convert("mp3")

    def convert_ogg(self):
        return self.convert("ogg")

    def convert_wav(self):
        return self.convert("wav")

    def new_path(self, format: str) -> str:
        return os.path.join(self.output_path, f"{self._file.stem}.{format}")

    def convert(self, format="wav", increase_volume: bool = True):
        logger.info(f"Converting the {self._file} file to {format}")
        try:
            # -ac 1 is option that convert audio to 1 channel
            output_after_converting = self.segment.export(
                self.new_path(format),
                format=format,
                parameters=["-ac", self.CHANNELS],
            )
            new_name = output_after_converting.name
            output_after_converting.close()
        except Exception as e:
            logger.error(f"Error while converting {self._file} to {format}")
            logger.error(f"{e=}")
            raise e
        logger.info(f"File {self._file} converted to {format}")
        logger.info(f"New file: {new_name}")
        return FFmpegConverter(new_name)

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
