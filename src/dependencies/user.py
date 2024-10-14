from typing import Annotated
from fastapi import Depends

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.core.jwt import (
    decode_access_token,
    SUB,
)

from src import schemas


from src.services import user as user_service


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db_session: AsyncSession = Depends(get_db),
) -> schemas.UserResponse:
    payload = await decode_access_token(token=token)

    return await user_service.user_by_id(db_session, int(payload[SUB]))
