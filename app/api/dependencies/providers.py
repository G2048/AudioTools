# from app.adapters.recognizers import api, mock, neural
from fastapi.exceptions import HTTPException

from app.adapters.recognizers import mock, neural
from app.interfaces.recognizers import RecognizerInterface


class Providers:
    # class FabricRecognizers:
    __registered_fabric: dict[str, RecognizerInterface] = {}

    @classmethod
    def register(cls, recognizer: RecognizerInterface):
        cls.__registered_fabric[recognizer.name] = recognizer

    def list(self) -> list[str]:
        return list(self.__registered_fabric.keys())

    def __getattr__(self, name: str) -> RecognizerInterface:
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


def get_recognizer(provider: str) -> RecognizerInterface:
    name = provider.lower()
    try:
        return recognizers_fabric[name]
    except AttributeError:
        raise HTTPException(status_code=404, detail=f"No such recognizer {name}")
