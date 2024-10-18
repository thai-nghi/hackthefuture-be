from src import db_tables
from src import schemas
from src import exceptions

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy import select, insert


async def user_exist_by_email(db_session: AsyncSession, email: str) -> bool:
    user_tbl = db_tables.users

    query = select(user_tbl.c.id).where(user_tbl.c.email == email)

    id = (await db_session.execute(query)).scalar()

    return id is not None


async def create_user_by_email(
    db_session: AsyncSession,
    user_data: schemas.UserRegister,
    hashed_password: str | None,
) -> schemas.UserResponse:
    user_tbl = db_tables.users

    query = insert(user_tbl).values(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        password=hashed_password,
        age=user_data.age,
        gender=user_data.gender,
        avatar="",
    )

    (await db_session.execute(query))

    return await user_detail_by_email(db_session, user_data.email)


async def user_password_by_email(db_session: AsyncSession, email: str) -> str | None:
    user_tbl = db_tables.users

    query = select(user_tbl.c.password).where(user_tbl.c.email == email)

    password = (await db_session.execute(query)).scalar()

    return password


async def user_detail_by_email(
    db_session: AsyncSession, email: str
) -> schemas.UserResponse:
    user_tbl = db_tables.users
    organization_members_tbl = db_tables.organization_members
    organizations_tbl = db_tables.organizations

    joined_table = user_tbl.join(
        organization_members_tbl, organization_members_tbl.c.user_id == user_tbl.c.id, isouter=True
    ).join(
        organizations_tbl,
        organizations_tbl.c.id == organization_members_tbl.c.organization_id, isouter=True
    )

    query = (
        select(
            user_tbl.c.id,
            user_tbl.c.email,
            user_tbl.c.first_name,
            user_tbl.c.last_name,
            user_tbl.c.age,
            user_tbl.c.gender,
            user_tbl.c.avatar,
            organizations_tbl.c.organization_name,
            organization_members_tbl.c.organization_id
        )
        .select_from(joined_table)
        .where(user_tbl.c.email == email)
    )

    user = (await db_session.execute(query)).first()

    if user is None:
        raise exceptions.NotFoundException

    return schemas.UserResponse(**user._mapping)


async def get_user_by_google_id(
    db_session: AsyncSession, google_id: str
) -> schemas.UserResponse | None:
    user_tbl = db_tables.users
    google_tbl = db_tables.users_google_id
    organization_members_tbl = db_tables.organization_members
    organizations_tbl = db_tables.organizations

    query = (
        select(
            user_tbl.c.id,
            user_tbl.c.email,
            user_tbl.c.first_name,
            user_tbl.c.last_name,
            user_tbl.c.age,
            user_tbl.c.gender,
            user_tbl.c.avatar,
            organizations_tbl.c.organization_name,
            organization_members_tbl.c.organization_id
        )
        .select_from(
            user_tbl.join(google_tbl, google_tbl.c.user_id == user_tbl.c.id)
            .join(
                organization_members_tbl,
                organization_members_tbl.c.user_id == user_tbl.c.id,
                isouter=True
            )
            .join(
                organizations_tbl,
                organizations_tbl.c.id == organization_members_tbl.c.organization_id,
                isouter=True
            )
        )
        .where(google_tbl.c.google_id == google_id)
    )

    user = (await db_session.execute(query)).first()

    return schemas.UserResponse(**user._mapping) if user is not None else None


async def user_by_id(db_session: AsyncSession, id: int) -> schemas.UserResponse:
    user_tbl = db_tables.users
    organization_members_tbl = db_tables.organization_members
    organizations_tbl = db_tables.organizations

    query = (
        select(
            user_tbl.c.id,
            user_tbl.c.email,
            user_tbl.c.first_name,
            user_tbl.c.last_name,
            user_tbl.c.age,
            user_tbl.c.gender,
            user_tbl.c.avatar,
            organizations_tbl.c.organization_name,
            organization_members_tbl.c.organization_id,
        )
        .select_from(
            user_tbl.join(
                organization_members_tbl,
                organization_members_tbl.c.user_id == user_tbl.c.id,
                isouter=True
            )
            .join(
                organizations_tbl,
                organizations_tbl.c.id == organization_members_tbl.c.organization_id,
                isouter=True
            )
        )
        .where(user_tbl.c.id == id)
    )
    user = (await db_session.execute(query)).first()
    if user is None:
        raise exceptions.NotFoundException

    return schemas.UserResponse(**user._mapping)


async def create_user_by_google_id(
    db_session: AsyncSession,
    google_data: schemas.GoogleCredentalData,
) -> schemas.UserResponse:
    user_tbl = db_tables.users
    google_tbl = db_tables.users_google_id

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
