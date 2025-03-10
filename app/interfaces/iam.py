from abc import ABC, abstractmethod


class ImTokenInterface(ABC):
    @abstractmethod
    def get_token(self) -> str:
        pass
