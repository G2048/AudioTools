from abc import ABC, abstractmethod
from collections import OrderedDict
from datetime import timedelta
from typing import TypeAlias


class _RecognizedText(OrderedDict):
    with_timestamp: bool = False

    def __str__(self) -> str:
        ready_text = ""
        for timestamps, text in self.items():
            if self.with_timestamp:
                start = timedelta(seconds=int(timestamps[0]))
                end = timedelta(seconds=int(timestamps[1]))
                ready_text += f"{start} - {end}: {text}\n"
            else:
                ready_text += text + "\n"
        return ready_text

    def get_ready_text(self, with_timestamp: bool):
        self.with_timestamp = with_timestamp
        return str(self)


text: TypeAlias = str
start_time: TypeAlias = str
end_time: TypeAlias = str
key: TypeAlias = tuple[start_time, end_time]
RecognizedText: TypeAlias = _RecognizedText[key, text]


class AudioUploaderInterface(ABC):
    @abstractmethod
    def upload(self, file_path: str):
        pass


class SpeechRecognizerInterface(ABC):
    @abstractmethod
    def recognize(self, audio_file: str, channels_count: int) -> RecognizedText:
        pass
