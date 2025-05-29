import hashlib
from typing import BinaryIO

from app.interfaces.storages import HashedFile, IHasher


class Sha1Hasher(IHasher):
    CHUNK_SIZE = 2048

    def __init__(self):
        self.__hasher = hashlib.sha1
        self._hasher = self.__hasher()

    @property
    def name(self) -> str:
        return "sha1"

    @property
    def empty_value(self) -> str:
        return self.__hasher().hexdigest()

    def reset(self):
        self._hasher = self.__hasher()

    def _calculate_hash(self, bfile: BinaryIO) -> str:
        for chunk in iter(lambda: bfile.read(self.CHUNK_SIZE), b""):
            self._hasher.update(chunk)
        try:
            return self._hasher.hexdigest()
        finally:
            self.reset()

    def hash(self, bfile: BinaryIO) -> HashedFile:
        hash = self._calculate_hash(bfile)
        return HashedFile(hash)
