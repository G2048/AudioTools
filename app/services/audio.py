import logging
import os

import numpy as np
import pydub
from ffmpy import FFmpeg
from gradio import processing_utils
from transformers import Pipeline, pipeline

from app.configs import get_aws_bucket_settings, get_aws_settings

from .uploader import AwsUploader

logger = logging.getLogger("stdout")


aws_settings = get_aws_settings()
bucket_settings = get_aws_bucket_settings()
# LLMMODEL = "./whisper-large-v3"
LLMMODEL = os.environ.get("LLMMODEL")
assert LLMMODEL, "Environment variable LLMMODEL is not set. Choose path to LLM model"


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


class AudioFile:
    __slot__ = ("list_audio", "name", "path", "output_path")

    def __init__(self, file_path: str, output_path: str = "."):
        # name without extension
        self.path = file_path
        self.name = os.path.basename(file_path).split(".")[0]
        self.list_audio = {}
        self.output_path = output_path

    @classmethod
    def create_from_numpy(cls, audio: np.ndarray):
        return

    def create(self, format: str) -> dict:
        self.list_audio.update({self.new_path(format): None})
        return self.list_audio

    def new_path(self, format: str):
        return os.path.join(self.output_path, f"{self.name}.{format}")

    # @classmethod
    def clean(self):
        self.list_audio.clear()


class AudioConverter:
    def __init__(self, file: AudioFile):
        self.file = file
        # self.file = output_file
        # self.file_path = file_path

    def convert_mp3(self):
        self.convert()

    def convert_ogg(self):
        self.convert("ogg")

    def convert_wav(self):
        self.convert("wav")

    # TODO: add capture of stderr !
    def convert(self, format="mp3"):
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
    def to_numpy(file: str, format: str) -> np.ndarray:
        return processing_utils.audio_from_file(file)[1]

    @staticmethod
    def _to_format(audio: np.ndarray):
        # pydub.AudioSegment.from_mp3()
        segment = pydub.AudioSegment.from_file(file, format)
        np_array = np.array(segment.get_array_of_samples())
        if segment.channels > 1:
            np_array = np.mean(np_array, axis=1)
        return segment.frame_rate, np_array


class AudioRecognizer:
    transcriber: Pipeline = pipeline("automatic-speech-recognition", max_new_tokens=445, model=LLMMODEL)

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
        transcribed = self.transcribe(audio)
        logger.debug(f"Transcribed: {transcribed}")
        chunks: list[dict[str, str]] = transcribed["chunks"]
        processing_text = ""
        for chunk in chunks:
            processing_text += f'{chunk["timestamp"][0]} - {chunk["timestamp"][1]}: {chunk["text"]}\n'

        return processing_text
