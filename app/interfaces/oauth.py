from abc import ABC, abstractmethod


class IAccessToken(ABC):
    @abstractmethod
    def get_token(self) -> str:
        pass
