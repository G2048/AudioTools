import json
from typing import Any, Optional

import redis
from pydantic import BaseModel

from app.configs.settings import RedisIpcConfig


class RedisMessage(BaseModel):
    key: str
    value: Optional[Any] = None
    ttl: Optional[int] = None

    def model_dump_json(self, *args, **kwargs) -> str:
        return super().model_dump_json(
            exclude_none=True, exclude={"key", "ttl"}, *args, **kwargs
        )


class RedisException(Exception):
    pass


class TTLNotProvided(RedisException):
    detail = "Must provide TTL for RedisIPC.setx!"


class ValueNotProvided(RedisException):
    detail = "Must provide value for RedisIPC.set!"


class RedisIPC:
    def __init__(self, config: RedisIpcConfig):
        self.redis = redis.Redis(**config.model_dump(), decode_responses=True)

    def get(self, key: str) -> RedisMessage:
        response = self.redis.get(key)
        print(f"Response from RedisIPC.get: {response}")
        ttl = self.redis.ttl(key)
        if ttl == -2:
            ttl = None
        if response:
            response = json.loads(response).get("value")
        return RedisMessage(key=key, value=response, ttl=ttl)

    def check_ttl_key(self, key):
        return self.redis.ttl(key)

    def set(self, message: RedisMessage):
        if not message.value:
            raise ValueNotProvided
        response = self.redis.set(message.key, message.model_dump_json())
        return RedisMessage(key=message.key, value=response)

    def setx(self, message: RedisMessage) -> bool:
        # message.ttl = message.ttl or 10
        if not message.ttl:
            raise TTLNotProvided
        if not message.value:
            raise ValueNotProvided
        return self.redis.setex(message.key, message.ttl, message.model_dump_json())

    def delete(self, key):
        return self.redis.delete(key)

    def exists(self, key):
        return self.redis.exists(key)

    def incr(self, key):
        return self.redis.incr(key)

    def decr(self, key):
        return self.redis.decr(key)

    def keys(self, pattern):
        return self.redis.keys(pattern)

    def flushdb(self):
        return self.redis.flushdb()

    def flushall(self):
        return self.redis.flushall()

    def info(self):
        return self.redis.info()

    def ping(self):
        return self.redis.ping()
