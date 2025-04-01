from datetime import datetime, timedelta

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel, ConfigDict, computed_field

from app.configs.settings import JwtSettings


class JwtPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    sub: str
    token_ttl: int = 20

    @computed_field(return_type=int)
    def exp(self):
        expiration_time = datetime.now() + timedelta(days=self.token_ttl)
        return int(expiration_time.timestamp())

    @computed_field(return_type=int)
    def iat(self):
        return int(datetime.now().timestamp())


class JWT:
    _instance = None
    _jwt_settings = JwtSettings()
    SECRET_KEY = _jwt_settings.secret_key
    ALGORITHM = _jwt_settings.algorithm

    def generate_token(self, payload: JwtPayload) -> str:
        return jwt.encode(payload.model_dump(), self.SECRET_KEY, algorithm=self.ALGORITHM)

    def validate(self, token: str) -> JwtPayload:
        _jwt = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        return JwtPayload(**_jwt)

    def payload(self, token: str) -> JwtPayload:
        _jwt = jwt.decode(token, options={"verify_signature": False})
        return JwtPayload(**_jwt)


__all__ = ("JWT", "JwtPayload", "InvalidTokenError", "ExpiredSignatureError")
