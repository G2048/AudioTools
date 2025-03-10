from abc import ABC, abstractmethod


class SenderInterface(ABC):
    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @abstractmethod
    def check_input(self, recipients: str) -> tuple[str]:
        pass

    @abstractmethod
    def create_message(self, text: str):
        pass

    @abstractmethod
    def send(self, recipients: tuple[str]):
        pass
