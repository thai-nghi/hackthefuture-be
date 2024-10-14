from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, Response

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db

from src.core.hash import get_password_hash, verify_password
from src.core.jwt import (
    create_token_pair,
    add_refresh_token_cookie,
)
from src.exceptions import BadRequestException
from src import schemas


from src.services import user as user_service

import httpx

router = APIRouter(prefix="/auth")


@router.post("/register")
async def register(
    data: schemas.UserRegister,
    response: Response,
    db_session: AsyncSession = Depends(get_db),
):
    user_exist = await user_service.user_exist_by_email(db_session, data.email)

    if user_exist:
        raise HTTPException(status_code=400, detail="Email has already registered")

    hashed_password = get_password_hash(data.password)

    print(hashed_password)

    created_user = await user_service.create_user_by_email(
        db_session, data, hashed_password
    )

    token_pair = create_token_pair(user=created_user)

    add_refresh_token_cookie(response=response, token=token_pair.refresh.token)

    await db_session.commit()

    return {"token": token_pair.access.token, "user_detail": created_user.dict()}



async def handle_google_login(google_token: str, db_session: AsyncSession) -> schemas.UserResponse:
    """
    Handle login with google
    """
    async with httpx.AsyncClient() as http_client:
        try:
            user_data = await http_client.get(
                f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={google_token}"
            )

            parsed_info = schemas.GoogleCredentalData(**user_data.json())
        except Exception:
            # Invalid token
            raise BadRequestException(detail="Incorrect google token")

    user = await user_service.get_user_by_google_id(db_session, parsed_info.sub)

    print("Google user", user, parsed_info)

    if user is None:
        # a new user
        user = await user_service.create_user_by_google_id(db_session, parsed_info)

    return user

@router.post("/login")
async def login(
    data: schemas.UserLogin,
    response: Response,
    db_session: AsyncSession = Depends(get_db),
):
    if data.google_token is not None:
        # login with google
        user = await handle_google_login(data.google_token, db_session)
        
    if data.email is not None:
        # login with email
        password = await user_service.user_password_by_email(db_session, data.email)

        if not verify_password(data.password, password):
            raise BadRequestException(detail="Incorrect email or password")

        user = await user_service.user_detail_by_email(db_session, data.email)

    token_pair = create_token_pair(user=user)

    add_refresh_token_cookie(response=response, token=token_pair.refresh.token)

    await db_session.commit()

    return {
        "token": token_pair.access.token,
        "user_detail": user.dict(),
        "avatar": "",
    }


@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db_session: AsyncSession = Depends(get_db),
):
    password = await user_service.user_password_by_email(db_session, form_data.username)

    print(get_password_hash(form_data.password))

    if not verify_password(form_data.password, password):
        raise BadRequestException(detail="Incorrect email or password")

    user = await user_service.user_detail_by_email(db_session, form_data.username)

    token_pair = create_token_pair(user=user)

    add_refresh_token_cookie(response=response, token=token_pair.refresh.token)

    return {"access_token": token_pair.access.token, "token_type": "bearer"}
