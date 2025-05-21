import logging

import numpy as np
from transformers import Pipeline, pipeline

from .exceptions import NeuralException

logger = logging.getLogger("app.drivers.neurals")


class Whisper:
    def __init__(self, model_name: str):
        self.__transcriber: Pipeline = pipeline(
            "automatic-speech-recognition", max_new_tokens=445, model=model_name
        )

    def transcribe(self, frame_rate: int, audio_array: np.ndarray):
        logger.info(f"Audio size: {audio_array.shape}")
        logger.info(f"Audio sampling rate: {frame_rate}")
        # Convert to mono if stereo
        if audio_array.ndim > 1:
            audio_array = audio_array.mean(axis=1)

        audio_array = audio_array.astype(np.float32)
        audio_array /= np.max(np.abs(audio_array))
        try:
            transcribed_text = self.__transcriber(
                {"sampling_rate": frame_rate, "raw": audio_array},
                return_timestamps=True,
            )
        except Exception as e:
            raise NeuralException(f"Error while transcribing: {e}")
        else:
            return transcribed_text
