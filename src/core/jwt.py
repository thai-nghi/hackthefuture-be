import uuid
import sys
from datetime import timedelta, datetime, timezone

from jose import jwt, JWTError
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from . import config
from src.schemas import TokenPair, JwtTokenSchema, UserResponse
from src.exceptions import AuthFailedException


REFRESH_COOKIE_NAME = "refresh"
SUB = "sub"
EXP = "exp"
IAT = "iat"
JTI = "jti"


def _get_utc_now():
    return datetime.now(timezone.utc)


def _create_token(payload: dict, expire: datetime) -> JwtTokenSchema:
    return JwtTokenSchema(
        token=jwt.encode(
            {**payload, EXP: expire},
            config.settings.SECRET_KEY,
            algorithm=config.settings.ALGORITHM,
        ),
        expire=expire,
        payload=payload,
    )

def decode_token(token: str) -> dict | None:
    if token is None:
        return none
    try:
        return jwt.decode(
            token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM]
        )
    except JWTError:
        return None


async def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM]
        )
    except JWTError:
        raise AuthFailedException()

    return payload


def refresh_token_state(response: Response, refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token,
            config.settings.SECRET_KEY,
            algorithms=[config.settings.ALGORITHM],
        )
    except JWTError as ex:
        print(str(ex))
        raise AuthFailedException()
    new_expire = _get_utc_now() + timedelta(
        minutes=config.settings.ACCESS_TOKEN_EXPIRES_MINUTES
    )

    new_access_token = _create_token(payload, new_expire)
    response.set_cookie(
        key="access",
        value=new_access_token.token,
        expires=int(new_expire.timestamp()),
        httponly=True,
    )


def add_refresh_token_cookie(response: Response, token: str):
    exp = _get_utc_now() + timedelta(
        minutes=config.settings.REFRESH_TOKEN_EXPIRES_MINUTES
    )
    exp.replace(tzinfo=timezone.utc)

    response.set_cookie(
        key="refresh",
        value=token,
        expires=int(exp.timestamp()),
        httponly=True,
    )


def create_and_inject_token(response: Response, user: UserResponse):
    create_time = _get_utc_now()

    payload = {SUB: str(user.id), JTI: str(uuid.uuid4()), IAT: create_time}

    token_details = [
        ("access", config.settings.ACCESS_TOKEN_EXPIRES_MINUTES),
        ("refresh", config.settings.REFRESH_TOKEN_EXPIRES_MINUTES),
    ]

    for token_name, refresh_minutes in token_details:
        expire = create_time + timedelta(minutes=refresh_minutes)
        token = _create_token(payload, expire)
        response.set_cookie(
            key=token_name,
            value=token.token,
            expires=int(expire.timestamp()),
            httponly=True,
        )
