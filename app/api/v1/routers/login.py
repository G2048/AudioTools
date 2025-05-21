import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict

from app.api.dependencies.auth import check_auth
from app.api.models.users import ResponseToken
from app.api.services.jwt import JWT, JwtPayload

router = APIRouter(
    prefix="/api/v1/login",
    tags=["Authorization"],
)
logger = logging.getLogger("app.api.v1.routers")


# TODO: add check logick for authentication
def registre_user(username: str, password: str) -> bool:
    return True


security = OAuth2PasswordBearer(tokenUrl="/api/v1/login/")


@router.post("/")
def login(body: Annotated[OAuth2PasswordRequestFormStrict, Depends()]) -> ResponseToken:
    logger.debug(f"Body: {body=}")
    username = body.username.partition("@")[0]
    logged_in = registre_user(username, body.password)
    logger.info(f"Username: {username=}")
    if not logged_in:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = JWT.generate_token(JwtPayload(sub=username))
    return ResponseToken(access_token=token, token_type="bearer")


@router.get("/")
def check_login(token: Annotated[str, Depends(check_auth)]):
    return token
