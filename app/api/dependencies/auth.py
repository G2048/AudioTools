import logging
from http import HTTPStatus
from typing import Annotated

from app.services.jwt import JWT, ExpiredSignatureError, InvalidTokenError
from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

security = OAuth2PasswordBearer(tokenUrl="/api/v1/login/")

logger = logging.getLogger("stdout")

jwt = JWT()


def check_auth(token: Annotated[str, Depends(security)]):
    logger.debug(f"Token: {token=}")

    logged_in = False
    status_code = HTTPStatus.UNAUTHORIZED
    error = False
    if token:
        try:
            jwt.validate(token)
        except ExpiredSignatureError:
            logger.info(f"Token expired: {jwt.payload(token)=}")
            detail = "Token expired"
            error = True
        except InvalidTokenError:
            logger.info(f"Token invalid: {token=}")
            detail = "Invalid token"
            error = True

        if error:
            raise HTTPException(
                status_code=status_code,
                detail=detail,
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            logged_in = True
            status_code = HTTPStatus.OK

    return JSONResponse(content={"logged_in": logged_in}, status_code=status_code)
