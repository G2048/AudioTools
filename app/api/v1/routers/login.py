import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict

from app.api.models.users import Token
from app.services.jwt import JWT, ExpiredSignatureError, InvalidTokenError

router = APIRouter(
    prefix="/api/v1/login",
    tags=["Authorization"],
)
logger = logging.getLogger("stdout")


# TODO: add check logick for authentication
def check_auth(username: str, password: str) -> bool:
    return True


# security = HTTPBasic()
security = OAuth2PasswordBearer(tokenUrl="/api/v1/login/")


@router.post("/")
async def login(body: Annotated[OAuth2PasswordRequestFormStrict, Depends()]) -> Token:
    logger.debug(f"Body: {body=}")
    username = body.username.partition("@")[0]
    logged_in = check_auth(username, body.password)
    logger.info(f"Username: {username=}")
    if not logged_in:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = JWT().generate_token({"username": username})
    return Token(access_token=token, token_type="bearer")


@router.get("/")
async def check_login(token: Annotated[str, Depends(security)]):
    logger.debug(f"Token: {token=}")
    jwt = JWT()

    logged_in = False
    status_code = HTTPStatus.UNAUTHORIZED
    error = False
    if token:
        try:
            jwt_token = jwt.validate(token)
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
