from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Any, Iterable, Iterator, Optional, TypeAlias

import redis
from pydantic import BaseModel
from redis.exceptions import ConnectionError

from app.configs.settings import RedisIpcConfig

from .exceptions import ConnectionUnavailable


class RedisMessage(BaseModel):
    key: str
    value: Optional[Any] = None
    ttl: Optional[int] = None

    def model_dump_json(self, *args, **kwargs) -> str:
        return super().model_dump_json(
            exclude_none=True, exclude={"key", "ttl"}, *args, **kwargs
        )


class RedisConnection:
    __slots__ = ("connection",)

    def __init__(self, config: RedisIpcConfig):
        self.connection = redis.Redis(**config.model_dump(), decode_responses=True)
        self.ping()

    def __enter__(self):
        self.ping()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def close(self):
        self.connection.close()

    def ping(self):
        try:
            return self.connection.ping()
        except ConnectionError as e:
            raise ConnectionUnavailable(e)


class classproperty(property):
    __slots__ = ("fget",)

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, owner=None):
        return classmethod(self.fget).__get__(None, owner)()


class DeleteStatus(IntEnum):
    DELETED = 1
    NOT_FOUND = 0


class TTLStatus(IntEnum):
    NOT_FOUND = -2
    DELETED = -1
    OK = 0


class RedisStore(ABC):
    __slots__ = ("_redis",)

    def __init__(self, redis: RedisConnection):
        self._redis = redis.connection

    @classproperty
    def name(cls) -> str:
        return cls.__name__

    def ttl(self, key: str) -> TTLStatus | int:
        return self._redis.ttl(key)

    def delete(self, key: str) -> DeleteStatus:
        return self._redis.delete(key)

    @abstractmethod
    def set(self):
        pass

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def all(self):
        pass


# SCAN
class DictStore(RedisStore):
    __slots__ = ("_redis",)

    def set(self, key: str, value: str, ttl: int | None = None):
        return self._redis.setex(key, ttl, value)

    def get(self, key: str) -> str:
        return self._redis.get(key)

    def all(self, match: str = "*") -> Iterator:
        all = self._redis.scan(match=match)
        return all and all[1]


# HSCAN
class HashStore(RedisStore):
    __slots__ = ("_redis",)

    def set(self, key: str, mapping: dict[Any, Any] | None = None) -> bool:
        return self._redis.hset(key, mapping=mapping)

    def get(self, key: str, field: str):
        return self._redis.hget(key, field)

    def set_key_ttl(self, key: str, ttl: int):
        return self._redis.expire(key, ttl)

    def fields_ttl(self, key: str, fields: Iterable[str]) -> list[TTLStatus | int]:
        return self._redis.httl(key, *fields)

    def fttl(self, key: str, field: str) -> TTLStatus | int:
        ttls = self.fields_ttl(key, (field,))
        return ttls and ttls[0]

    def touch(self, key: str, fields: Iterable[str], ttl: int | None = None):
        keys: list[str] = self._redis.hgetex(key, *fields, ex=ttl)
        return keys and keys[0]

    def set_fields_ttl(self, key: str, fields: Iterable[str], ttl: int | None = None):
        return self.touch(key, fields, ttl)

    def set_fttl(self, key: str, field: str, ttl: int | None = None):
        return self.touch(key, (field,), ttl)

    def getall(self, key: str) -> dict[Any, Any] | None:
        return self._redis.hgetall(key)

    def all(self, key: str, match: str = "*") -> dict[Any, Any]:
        all = self._redis.hscan(key, match=match)
        return all and all[1]


# SSCAN
class SetStore(RedisStore):
    __slots__ = ("_redis",)

    def set(self, key: str, mapping: set[Any]):
        return self._redis.sadd(key, *mapping)

    def get(self, key: str, field: str):
        raise NotImplementedError

    # def all(self, key:str):
    # return self._redis.smembers(key)

    def all(self, key: str, match: str = "*") -> list[str]:
        all = self._redis.sscan(key, match=match)
        return all and all[1]


Key: TypeAlias = str
Rank: TypeAlias = float
Pair: TypeAlias = tuple[Key, Rank]


class SortedSet(BaseModel):
    pairs: list[Pair]


# ZSCAN
class SortedSetStore(SetStore):
    __slots__ = ("_redis",)

    def set(self, key: str, mapping: dict[Any, Any]):
        return self._redis.zadd(key, mapping)

    def all(self, key: str, match: str = "*") -> SortedSet | None:
        all = self._redis.zscan(key, match=match)
        if all:
            return SortedSet(pairs=all[1])
