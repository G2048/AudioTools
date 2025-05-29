from typing import Self

from app.interfaces.recognizers import IRecognizer

from .. import recognizers


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


_recognizers_fabric = Providers()
_recognizers_fabric.register(recognizers.MockRecognizer)
_recognizers_fabric.register(recognizers.WhisperRecognizer)
# classes = tuple(filter(lambda x: x.istitle(), dir(recognizers)))
# print(f"Register recognizers: {classes}")
# print(f"{dir(recognizers)=}")

# for recognizer in classes:
#     print(f"Register recognizer: {recognizer}")
#     _recognizers_fabric.register(recognizer())
