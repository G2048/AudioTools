import logging

# import ffmpy
import numpy as np
from ffmpy import FFmpeg
from transformers import Pipeline, pipeline

from app.configs import get_aws_bucket_settings, get_aws_settings

from .uploader import AwsUploader

logger = logging.getLogger("stdout")


aws_settings = get_aws_settings()
bucket_settings = get_aws_bucket_settings()


class AudioUploader:
    __slot__ = "uploader"

    def __init__(self):
        self.uploader = AwsUploader(aws_settings, bucket_settings)

    def execute(self, file_path: str):
        logger.info(f"Uploading {file_path}")
        # Узкое место: если в пути будет несколько директорий,
        # то будет браться только первая - это плохо, но пока не понятно нужно ли большее
        current_path = "." if not len(file_path.split("/")) > 1 else file_path.split("/")[0]
        file = self.uploader.create_file(file_path)
        self.uploader.upload(file, current_path)


class AudioFiles:
    list_audio = {}
    __slot__ = ("list_audio", "file")

    def __init__(self, file: str):
        self.file = file.split(".")[0]

    def convert_from_numpy(self, audio: np.ndarray):
        return

    def create(self, format: str) -> dict:
        formated_file = f"{self.file}.{format}"
        self.list_audio.update({formated_file: None})
        return self.list_audio

    @classmethod
    def clean(cls):
        cls.list_audio.clear()


class AudioConverter:
    def __init__(self, name: str, output_file: AudioFiles):
        self.file = output_file
        self.name = name

    def convert_mp3(self):
        self.convert()

    def convert_ogg(self):
        self.convert("ogg")

    def convert_wav(self):
        self.convert("wav")

    # TODO: add capture of stderr !
    def convert(self, format="mp3"):
        logger.info(f"Converting {self.file} to {format}")
        ff = FFmpeg(inputs={self.name: None}, outputs=self.file.create(format))

        logger.debug(f"String for execution: {ff.cmd}")
        try:
            ff.run()
            logger.error(f"Error while converting {self.file} to {format}")
        except Exception:
            logger.error(f"String for execution: {ff.cmd}")

    def to_format(self, audio: np.ndarray):
        return audio.convert_from_numpy(audio)

    # def _to_format(self, audio: np.ndarray):
    #     return {f"{self.file}.{self.format}": None}


class AudioRecognizer:
    transcriber: Pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")

    def __init__(self):
        pass

    def transcribe(self, audio: np.ndarray):
        sr, y = audio
        logger.info(f"Audio size: {y.shape}")
        logger.info(f"Audio sampling rate: {sr}")

        # Convert to mono if stereo
        if y.ndim > 1:
            y = y.mean(axis=1)

        y = y.astype(np.float32)
        y /= np.max(np.abs(y))

        return self.transcriber({"sampling_rate": sr, "raw": y}, return_timestamps=True)

    def execute(self, audio: np.ndarray) -> str:
        transcribed = self.transcribe(audio)["text"]
        logger.debug(f"Transcribed: {transcribed}")
        return transcribed
