from app.adapters.storages.hashers import Sha1Hasher
from app.interfaces.storages import IHasher


def get_hasher() -> IHasher:
    return Sha1Hasher()
