from src import db_tables
from src import schemas
from src import exceptions

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy import select, insert


async def user_exist_by_email(db_session: AsyncSession, email: str) -> bool:
    user_tbl = db_tables.user

    query = select(user_tbl.c.id).where(user_tbl.c.email == email)

    id = (await db_session.execute(query)).scalar()

    return id is not None


async def create_user_by_email(
    db_session: AsyncSession, user_data: schemas.UserRegister, hashed_password: str
) -> schemas.UserResponse:
    user_tbl = db_tables.user

    query = insert(user_tbl).values(
        full_name=user_data.full_name,
        email=user_data.email,
        password=hashed_password,
        city=user_data.city,
        country=user_data.country,
    )

    (await db_session.execute(query))

    return await user_detail_by_email(db_session, user_data.email)


async def user_password_by_email(db_session: AsyncSession, email: str) -> str | None:
    user_tbl = db_tables.user

    query = select(user_tbl.c.password).where(user_tbl.c.email == email)

    password = (await db_session.execute(query)).scalar()

    return password


async def user_detail_by_email(
    db_session: AsyncSession, email: str
) -> schemas.UserResponse:
    user_tbl = db_tables.user

    query = select(
        user_tbl.c.id,
        user_tbl.c.email,
        user_tbl.c.full_name,
        user_tbl.c.points,
        user_tbl.c.total_points,
        user_tbl.c.city,
        user_tbl.c.country,
        user_tbl.c.rank,
    ).where(user_tbl.c.email == email)

    user = (await db_session.execute(query)).first()

    if user is None:
        raise exceptions.NotFoundException

    return schemas.UserResponse(**user._mapping)


async def get_user_by_google_id(
    db_session: AsyncSession, google_id: str
) -> schemas.UserResponse | None:
    user_tbl = db_tables.user
    google_tbl = db_tables.user_google_id

    query = (
        select(
            user_tbl.c.id,
            user_tbl.c.email,
            user_tbl.c.full_name,
            user_tbl.c.points,
            user_tbl.c.total_points,
            user_tbl.c.city,
            user_tbl.c.country,
            user_tbl.c.rank,
        )
        .select_from(user_tbl.join(google_tbl, google_tbl.c.user_id == user_tbl.c.id))
        .where(google_tbl.c.google_id == google_id)
    )

    user = (await db_session.execute(query)).first()

    return schemas.UserResponse(**user._mapping) if user is not None else None


async def user_by_id(db_session: AsyncSession, id: int) -> schemas.UserResponse:
    user_tbl = db_tables.user

    query = select(
        user_tbl.c.id,
        user_tbl.c.email,
        user_tbl.c.full_name,
        user_tbl.c.points,
        user_tbl.c.total_points,
        user_tbl.c.city,
        user_tbl.c.country,
        user_tbl.c.rank,
    ).where(user_tbl.c.id == id)

    user = (await db_session.execute(query)).first()

    if user is None:
        raise exceptions.NotFoundException

    return schemas.UserResponse(**user._mapping)


async def create_user_by_google_id(
    db_session: AsyncSession,
    google_data: schemas.GoogleCredentalData,
) -> schemas.UserResponse:
    user_tbl = db_tables.user
    google_tbl = db_tables.user_google_id

    query = insert(user_tbl).values(
        full_name=f"{google_data.given_name} {google_data.family_name}",
        email=google_data.email,
        password=None,
        city="Lahti",
        country="Finland",
    )

    inserted_id = (await db_session.execute(query)).inserted_primary_key[0]

    query = insert(google_tbl).values(google_id=google_data.sub, user_id=inserted_id)

    await db_session.execute(query)

    return await get_user_by_google_id(db_session, google_data.sub)
