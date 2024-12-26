import logging

# import ffmpy
import numpy as np
from transformers import Pipeline, pipeline

logger = logging.getLogger("stdout")

# ffmpy.FFmpeg.run(
# inputs={"-i": "pipe:0", "-c:a": "copy", "-f": "mp3", "-"},
# outputs={"pipe:1": "pipe:1"},
# global_options={"-loglevel": "quiet"},
# )


# TODO: Тут должна быть логика загрузки аудио в Yandex Storage
class AudioUploader:
    def __init__(self):
        pass

    def execute(self, audio: np.ndarray):
        pass


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
