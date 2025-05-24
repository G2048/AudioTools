import logging
from typing import BinaryIO

from app.interfaces.audio import IAudioConverter
from app.services.audio import FFmpegConverter

logger = logging.getLogger("app.adapters.converters")


class MixinConverter(IAudioConverter):
    __slots__ = ()
    _format = ""

    @property
    def format(self) -> str:
        return self._format

    def convert(self, file: BinaryIO) -> str:
        converter = FFmpegConverter(file.name)
        segment = converter.convert(self._format)
        return segment.name


class Mp3Converter(MixinConverter):
    __slots__ = ()
    _format = "mp3"


class WavConverter(MixinConverter):
    __slots__ = ()
    _format = "wav"


class OggConverter(MixinConverter):
    __slots__ = ()
    _format = "ogg"
