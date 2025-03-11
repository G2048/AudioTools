import logging

import numpy as np
from transformers import Pipeline, pipeline

from app.configs import get_neural_settings
from app.interfaces import AudioRecognizerInterface

logger = logging.getLogger("stdout")

# LLMMODEL = "./whisper-large-v3"
neural_settings = get_neural_settings()


class LocalNeuralAudioRecognizer(AudioRecognizerInterface):
    transcriber: Pipeline = pipeline(
        "automatic-speech-recognition", max_new_tokens=445, model=neural_settings.name
    )

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

    def recognize(self, audio: np.ndarray) -> str:
        transcribed = self.transcribe(audio)
        logger.debug(f"Transcribed: {transcribed}")
        chunks: list[dict[str, str]] = transcribed["chunks"]
        processing_text = ""
        for chunk in chunks:
            processing_text += f"{chunk['timestamp'][0]} - {chunk['timestamp'][1]}: {chunk['text']}\n"

        return processing_text
