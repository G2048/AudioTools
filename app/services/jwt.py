from datetime import datetime, timedelta

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel

from app.configs.settings import JwtSettings


class JwtPayload(BaseModel):
    exp: int
    iat: int
    sub: str


class JWT:
    _instance = None
    _jwt_settings = JwtSettings()
    SECRET_KEY = _jwt_settings.secret_key
    ALGORITHM = _jwt_settings.algorithm

    def generate_token(self, data: dict, live_days: int = 20) -> str:
        expiration_time = datetime.now() + timedelta(days=live_days)
        payload = JwtPayload(
            exp=int(expiration_time.timestamp()),
            iat=int(datetime.now().timestamp()),
            sub=data["username"],
        )

        token = jwt.encode(payload.model_dump(), self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    def validate(self, token: str) -> JwtPayload:
        _jwt = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        return JwtPayload(**_jwt)

    def payload(self, token: str) -> JwtPayload:
        _jwt = jwt.decode(token, options={"verify_signature": False})
        return JwtPayload(**_jwt)


__all__ = ("JWT", "JwtPayload", "InvalidTokenError", "ExpiredSignatureError")
