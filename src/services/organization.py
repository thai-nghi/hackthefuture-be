from src import db_tables
from src import schemas

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy import select, insert
from src.services import user

from sqlalchemy.dialects.postgresql import insert as pg_insert
from src import exceptions


async def new_organization(
    db_session: AsyncSession, new_organization: schemas.OrganizationAttributes
) -> schemas.Organization:
    print(new_organization.dict())
    query = insert(db_tables.organizations).values(**new_organization.dict(exclude={'documents'})).returning(db_tables.organizations.c.id)
    print('-' * 50)
    print(query)
    print('-' * 50)
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
    
    return schemas.Organization(**result._mapping)

async def organization_by_user_data(
        db_session: AsyncSession, user_id: int, organization_name: str
    )-> schemas.Organization:
    org_tbl = db_tables.organizations
    organization_members_tbl = db_tables.organization_members

    query = select(org_tbl).select_from(org_tbl.join(organization_members_tbl, organization_members_tbl.c.user_id == user_id))
    
    result = (await db_session.execute(query)).first()

    if result is None:
        raise exceptions.NotFoundException
    
    return schemas.Organization(**result._mapping)

async def get_membership_by_user_id(
        db_session: AsyncSession, user_id: int   
    )-> schemas.Membership:

    organization_members_tbl = db_tables.organization_members
    query = select(organization_members_tbl).where(organization_members_tbl.c.user_id == user_id)
    result = (await db_session.execute(query)).first()

    if result is None:
        raise exceptions.NotFoundException
    return schemas.Membership(**result._mapping)

async def add_employee(
        db_session: AsyncSession, data: schemas.Membership   
    )-> schemas.Membership:

    organization_members_tbl = db_tables.organization_members
    query = pg_insert(organization_members_tbl).values(
                **data.dict()
            ).on_conflict_do_update(
                constraint="organization_members_pk",
                set_=dict(role = data.role)
            ).returning()
    await db_session.execute(query)

    result = await get_membership_by_user_id(db_session, data.user_id)
    return result