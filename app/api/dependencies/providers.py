from fastapi.exceptions import HTTPException

from app.adapters.recognizers import Providers
from app.interfaces.recognizers import IRecognizer

recognizers_fabric = Providers()


def get_providers() -> list[str]:
    return recognizers_fabric.list()


def get_recognizer(provider: str) -> IRecognizer:
    name = provider.lower()
    try:
        return recognizers_fabric[name]
    except AttributeError:
        raise HTTPException(status_code=404, detail=f"No such recognizer {name}")
