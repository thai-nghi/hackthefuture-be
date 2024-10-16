from src import db_tables
from src import schemas

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy import select, insert, update
from src.services import user

from sqlalchemy.dialects.postgresql import insert as pg_insert
from src import exceptions


async def new_organization(
    db_session: AsyncSession, new_organization: schemas.OrganizationIn
) -> schemas.Organization:
    query = insert(db_tables.organizations).values(**new_organization.dict()).returning(db_tables.organizations.c.id)

    inserted_id = (await db_session.execute(query)).scalar()

    return await organization_by_id(db_session, inserted_id)


async def organization_by_id(
    db_session: AsyncSession,
    id: int
) -> schemas.Organization:
    org_tbl = db_tables.organizations

    query = select(org_tbl).where(org_tbl.c.id == id)

    result = (await db_session.execute(query)).first()

    if result is None:
        raise exceptions.NotFoundException
    
    return schemas.ShopItem(**result._mapping)