from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, Response

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import DatabaseDependency

from src.core.hash import get_password_hash, verify_password
from src.core.jwt import (
    create_and_inject_token
)
from src.exceptions import BadRequestException
from src import schemas
from src.schemas import responses


from src.services import user as user_service

import httpx

router = APIRouter(prefix="/auth")


@router.post("/register")
async def register(
    data: schemas.UserRegister,
    response: Response,
    db_session: DatabaseDependency,
):
    user_exist = await user_service.user_exist_by_email(db_session, data.email)

    if user_exist:
        raise HTTPException(status_code=400, detail="Email has already registered")

    hashed_password = get_password_hash(data.password)

    created_user = await user_service.create_user_by_email(
        db_session, data, hashed_password
    )

    create_and_inject_token(response, created_user)

    await db_session.commit()

    return {}


@router.post("register_google", response_model=responses.LoginResponse)
async def register_google_user(
    data: schemas.GoogleRegister,
    response: Response,
    db_session: DatabaseDependency,
) -> responses.LoginResponse:
    user_exist = await user_service.user_exist_by_email(db_session, data.email)

    if user_exist:
        raise HTTPException(status_code=400, detail="Email has already registered")

    created_user = await user_service.create_user_by_email(
        db_session, data, None
    )

    create_and_inject_token(response, created_user)

    await db_session.commit()

    return responses.LoginResponse(user_detail=created_user, avatar="")



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

    return user

@router.post("/login", response_model=responses.LoginResponse)
async def login(
    data: schemas.UserLogin,
    response: Response,
    db_session: DatabaseDependency,
):
    if data.google_token is not None:
        # login with google
        user = await handle_google_login(data.google_token, db_session)

        if user is None:
            return responses.LoginResponse(has_account=False, token="", user_detail=None, avatar="")
        
    if data.email is not None:
        # login with email
        password = await user_service.user_password_by_email(db_session, data.email)

        if password is None or not verify_password(data.password, password):
            raise BadRequestException(detail="Incorrect email or password")

        user = await user_service.user_detail_by_email(db_session, data.email)

    create_and_inject_token(response, user)

    await db_session.commit()

    return responses.LoginResponse(user_detail=user, avatar="")


@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db_session: DatabaseDependency,
):
    password = await user_service.user_password_by_email(db_session, form_data.username)

    if not verify_password(form_data.password, password):
        raise BadRequestException(detail="Incorrect email or password")

    user = await user_service.user_detail_by_email(db_session, form_data.username)

    create_and_inject_token(response, user)

    return {}
