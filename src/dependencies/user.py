from typing import Annotated
from fastapi import Depends, Request, Response

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.core.jwt import (
    decode_token,
    SUB,
    refresh_token_state
)

from src import schemas


from src.services import user as user_service
from src.exceptions import AuthTokenExpiredException


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db_session: Annotated[AsyncSession, Depends(get_db)],
    request: Request,
    response: Response
) -> schemas.UserResponse:
    
    # try:
    #     payload = request.app.decoded_token
    # except AttributeError:
    #     payload = None

    # if payload is None:
    #     refresh_token = request.cookies.get("refresh", "")

    #     payload = decode_token(refresh_token)

    #     if payload is None:
    #         raise AuthTokenExpiredException
    #     else:
    #         refresh_token_state(response, refresh_token)

    payload = decode_token(token)

    if payload is None:
        raise AuthTokenExpiredException

    return await user_service.user_by_id(db_session, int(payload[SUB]))
