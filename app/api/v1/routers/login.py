import logging
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.api.models.users import Token, UserLogin
from app.services.jwt import JWT, ExpiredSignatureError, InvalidTokenError

router = APIRouter(
    prefix="/login",
    tags=["Authorization"],
)
logger = logging.getLogger("stdout")


# TODO: add check logick for authentication
def check_auth(username: str, password: str) -> bool:
    return True


@router.post("/")
async def login(body: UserLogin) -> Token:
    username = body.username.partition("@")[0]
    logged_in = check_auth(username, body.password)
    if not logged_in:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = JWT().generate_token({"username": username})
    return Token(access_token=token, token_type="bearer")


@router.get("/")
async def check_login(request: Request):
    jwt = JWT()
    token = request.headers.get("Authorization", "")
    clear_token = token.replace("Bearer ", "")
    logger.debug(f"Token: {clear_token=}")

    logged_in = False
    status_code = HTTPStatus.UNAUTHORIZED
    error = False
    if clear_token:
        try:
            jwt_token = jwt.validate(clear_token)
        except ExpiredSignatureError:
            logger.info(f"Token expired: {jwt.payload(clear_token)=}")
            detail = "Token expired"
            error = True
        except InvalidTokenError:
            logger.info(f"Token invalid: {clear_token=}")
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
