import logging
from typing import BinaryIO

from app.interfaces.audio import IAudioConverter
from app.services.audio import FFmpegConverter

logger = logging.getLogger("app.adapters.converters")


class Mp3Converter(IAudioConverter):
    __slots__ = ()

    def convert(self, file: BinaryIO) -> str:
        converter = FFmpegConverter(file.name)
        segment = converter.convert_mp3()
        return segment.name


class WavConverter(IAudioConverter):
    __slots__ = ()

    def convert(self, file: BinaryIO) -> str:
        converter = FFmpegConverter(file.name)
        segment = converter.convert_wav()
        return segment.name


class OggConverter(IAudioConverter):
    __slots__ = ()

    def convert(self, file: BinaryIO) -> str:
        converter = FFmpegConverter(file.name)
        segment = converter.convert_ogg()
        return segment.name
