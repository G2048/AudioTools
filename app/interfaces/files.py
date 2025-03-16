import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self

logger = logging.getLogger("stdout")


class FileInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def upload(self, path: str = ".") -> Self:
        pass

    @abstractmethod
    def get(self) -> bytes:
        pass

    @abstractmethod
    def save(self) -> Self:
        pass

    @abstractmethod
    def delete(self):
        pass

    def _create_path_file(self, bucket_dir: str) -> Path:
        path = Path(bucket_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


class UploaderInterface(ABC):
    def upload(self, file: FileInterface, path: str = "."):
        file.upload(path)
        logger.info(f"File {file.name} uploaded")

    def save(self, file: FileInterface):
        file.save()
        logger.info(f"File {file.name} saved")

    def get(self, file: FileInterface) -> bytes:
        return file.get()

    def delete(self, file: FileInterface):
        file.delete()
