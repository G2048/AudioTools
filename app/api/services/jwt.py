from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.configs.settings import JwtSettings


def uuid_str_factory() -> str:
    return str(uuid4())


class JwtPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    sub: str
    ttl: int = 900
    jti: str = Field(default_factory=uuid_str_factory)

    @computed_field(return_type=int)
    def exp(self):
        expiration_time = datetime.now() + timedelta(seconds=self.ttl)
        return int(expiration_time.timestamp())

    @computed_field(return_type=int)
    def iat(self):
        return int(datetime.now().timestamp())


class JwtRefreshTokenPayload(JwtPayload):
    version: int
    user_agent: Optional[str] = "curl"
    ttl: int = 30 * 24 * 60 * 60  # 30 days in seconds


class JWT:
    _instance = None
    _jwt_settings = JwtSettings()
    SECRET_KEY = _jwt_settings.secret_key
    ALGORITHM = _jwt_settings.algorithm

    @classmethod
    def generate_token(cls, payload: JwtPayload) -> str:
        return jwt.encode(payload.model_dump(), cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def validate(cls, token: str) -> JwtPayload:
        _jwt = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
        return JwtPayload(**_jwt)

    @classmethod
    def payload(cls, token: str) -> JwtPayload:
        _jwt = jwt.decode(token, options={"verify_signature": False})
        return JwtPayload(**_jwt)


__all__ = ("JWT", "JwtPayload", "InvalidTokenError", "ExpiredSignatureError")
