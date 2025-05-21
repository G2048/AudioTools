import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self

logger = logging.getLogger("app.interfaces.files")


class IFile(ABC):
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


class IUploader(ABC):
    def upload(self, file: IFile, path: str = "."):
        file.upload(path)
        logger.info(f"File {file.name} uploaded")

    def save(self, file: IFile):
        file.save()
        logger.info(f"File {file.name} saved")

    def get(self, file: IFile) -> bytes:
        return file.get()

    def delete(self, file: IFile):
        file.delete()
