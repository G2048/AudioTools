from typing import Self

from fastapi.exceptions import HTTPException

from app.adapters.recognizers import mock, neural
from app.interfaces.recognizers import IRecognizer


class Providers:
    __instance = None
    __registered_fabric: dict[str, IRecognizer] = {}

    def __new__(cls) -> Self:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def register(cls, recognizer: IRecognizer):
        cls.__registered_fabric[recognizer.name] = recognizer

    @classmethod
    def list(cls) -> list[str]:
        return list(cls.__registered_fabric.keys())

    def __getattr__(self, name: str) -> IRecognizer:
        if name in self.__registered_fabric:
            return self.__registered_fabric[name]
        raise AttributeError(f"No such attribute {name}")

    __getitem__ = __getattr__


recognizers_fabric = Providers()
# recognizers_fabric.register(api.SberRecognizer())
recognizers_fabric.register(neural.WhisperRecognizer())
recognizers_fabric.register(mock.MockRecognizer())


def get_providers() -> list[str]:
    return recognizers_fabric.list()


def get_recognizer(provider: str) -> IRecognizer:
    name = provider.lower()
    try:
        return recognizers_fabric[name]
    except AttributeError:
        raise HTTPException(status_code=404, detail=f"No such recognizer {name}")
