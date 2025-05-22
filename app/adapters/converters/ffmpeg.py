import logging
from typing import BinaryIO

from app.interfaces.audio import IAudioConverter

logger = logging.getLogger("app.adapters.converters")


class Mp3Converter(IAudioConverter):
    __slots__ = ()

    def convert(self, file: BinaryIO) -> str:
        return ""


class WavConverter(IAudioConverter):
    __slots__ = ()

    def convert(self, file: BinaryIO) -> str:
        return ""


class OggConverter(IAudioConverter):
    __slots__ = ()

    def convert(self, file: BinaryIO) -> str:
        return ""
