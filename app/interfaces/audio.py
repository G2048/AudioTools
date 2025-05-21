from abc import ABC, abstractmethod
from enum import StrEnum
from typing import BinaryIO


class IAudioUploader(ABC):
    @abstractmethod
    def upload(self, file_path: str):
        pass


# class IAudioConverter(ABC):
#     @abstractmethod
#     def convert(self, format: str):
#         pass


class IAudioFiles(ABC):
    @abstractmethod
    def create(self, format: str) -> dict[str, None]:
        pass


class AudioFormats(StrEnum):
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"


class IAudioFiles(ABC):
    __slot__ = ("list_audio", "name", "path", "output_path")

    def __init__(self, file_path: str, output_path: str = "."):
        # name without extension
        self._file = Path(file_path)
        self.name = self._file.stem
        self.list_audio: dict[str, None] = {}
        self.output_path = output_path

    def clean(self):
        self.list_audio.clear()


class IAudioConverter(ABC):
    def __init__(self, file: IAudioFiles, format: AudioFormats):
        self.file = file
        self.format = format
        # self.file = output_file
        # self.file_path = file_path

    @abstractmethod
    def convert(self, file: BinaryIO | str) -> str:
        pass


# class SenderFile(ABC):
#     logger = logging.getLogger("app.core.audio")
#     # def __init__(self, audiofile: BinaryIO):
#     #     self._audiofile = audiofile

#     @staticmethod
#     def create_tmp(audiofile: BinaryIO):
#         file_format = audiofile.name.split(".")[-1]
#         tmp_audiofile = NamedTemporaryFile(suffix=f".{file_format}", delete_on_close=False)
#         tmp_audiofile.write(audiofile.read())
#         tmp_audiofile.close()
#         audiofile.close()
#         return tmp_audiofile.name

#     @staticmethod
#     def convert(audio_path: str):
#         format = "mp3"
#         self.logger.info(f"Conver file to {format} format")
#         self.logger.info(f"Original audio file: {audio_path}")

#         file_format = audio_path.split(".")[-1].lower()
#         self.logger.info(f"File format: {file_format}")

#         # FFMPEG не знает форматата "wma", поэтому его нужно перевести в "asf"
#         if file_format == "wma":
#             old_audio_path = audio_path
#             audio_path = audio_path.lower().replace(".wma", ".asf")
#             os.rename(old_audio_path, audio_path)
#             self.logger.info(f"New audio file: {audio_path}")

#         audio = IAudioConverter(audio_path, IAudioFiles(audio_path))

#         if file_format not in ("mp3", "ogg"):
#             audio = audio.convert(format)
#             self.logger.info(f"New audio file: {audio.name}")
#             audio_path = audio.name
#         return audio_path, audio.channels

#     @abstractmethod
#     def recognize(self, audiofile: BinaryIO, hints: list[str] | None = None) -> str:
#         pass


# class Checker(ABC):
#     @abstractmethod
#     def check_status(self, task_id: str) -> tuple[str, str]:
#         pass


# class Downloader(ABC):
#     @abstractmethod
#     def download(self, file_id: str, with_timestamp: bool = False) -> str:
#         pass


# class Fabric(ABC):
#     def __init__(self, api: BaseApi):
#         self.api = api

#     @abstractmethod
#     def get_sender(self) -> SenderFile:
#         pass

#     @abstractmethod
#     def get_downloader(self) -> Downloader:
#         pass

#     @abstractmethod
#     def get_checker(self) -> Checker:
#         pass
