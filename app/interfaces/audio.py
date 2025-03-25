from abc import ABC, abstractmethod


class AudioUploaderInterface(ABC):
    @abstractmethod
    def upload(self, file_path: str):
        pass


class AudioConverterInterface(ABC):
    @abstractmethod
    def convert(self, format: str):
        pass


class AudioFilesInterfase(ABC):
    @abstractmethod
    def create(self, format: str) -> dict[str, None]:
        pass
