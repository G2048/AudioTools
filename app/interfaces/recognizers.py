from abc import ABC, abstractmethod

import numpy as np

RecognizedText = str


class AudioRecognizerInterface(ABC):
    @abstractmethod
    # def execute(self, audio_file: str, channels_count: int) -> RecognizedText:
    def recognize(self, audio: np.ndarray) -> RecognizedText:
        pass
