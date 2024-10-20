from src import db_tables
from src import schemas

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy import select, insert
from src.services import user

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.postgresql import array_agg
from sqlalchemy.sql.functions import func
from src import exceptions


async def new_organization(
    db_session: AsyncSession, new_organization: schemas.OrganizationAttributes
) -> schemas.Organization:
    query = (
        insert(db_tables.organizations)
        .values(**new_organization.dict(exclude={"documents", "tags"}))
        .returning(db_tables.organizations.c.id)
    )

    inserted_id = (await db_session.execute(query)).scalar()

    await add_tags_to_org(db_session, inserted_id, new_organization.tags)

    return await organization_by_id(db_session, inserted_id)


async def organization_by_id(db_session: AsyncSession, id: int) -> schemas.Organization:

    org_tbl = db_tables.organizations
    org_tag_tbl = db_tables.org_tags
    tag_tbl = db_tables.tags

    query = (
        select(
            org_tbl,
            array_agg(
                func.json_build_object("value", tag_tbl.c.id, "label", tag_tbl.c.label)
            ).label("tags"),
        )
        .select_from(
            org_tbl.join(
                org_tag_tbl, org_tbl.c.id == org_tag_tbl.c.organization_id, isouter=True
            ).join(tag_tbl, org_tag_tbl.c.tag_id == tag_tbl.c.id, isouter=True)
        )
        .group_by(org_tbl.c.id)
        .where(org_tbl.c.id == id)
    )

    result = (await db_session.execute(query)).first()

    if result is None:
        raise exceptions.NotFoundException

    return schemas.Organization(**result._mapping)


async def add_tags_to_org(db_sesion: AsyncSession, org_id: int, tags: list[int] | None):
    if tags is None:
        return

    org_tag_tbl = db_tables.org_tags

    await db_sesion.execute(
        insert(org_tag_tbl).values(organization_id=org_id),
        [{"tag_id": tag_id} for tag_id in tags],
    )


async def organization_by_user_data(
    db_session: AsyncSession, user_id: int
) -> schemas.Organization:

    organization_members_tbl = db_tables.organization_members
    org_tbl = db_tables.organizations
    org_tag_tbl = db_tables.org_tags
    tag_tbl = db_tables.tags

    query = (
        select(
            org_tbl,
            array_agg(
                func.json_build_object("value", tag_tbl.c.id, "label", tag_tbl.c.label)
            ).label("tags"),
        )
        .select_from(
            organization_members_tbl.join(org_tbl, organization_members_tbl.c.organization_id == org_tbl.c.id)
            .join(
                org_tag_tbl, org_tbl.c.id == org_tag_tbl.c.organization_id, isouter=True
            ).join(tag_tbl, org_tag_tbl.c.tag_id == tag_tbl.c.id, isouter=True)
        )
        .group_by(org_tbl.c.id)
        .where(organization_members_tbl.c.user_id == user_id)
    )

    result = (await db_session.execute(query)).first()

    if result is None:
        raise exceptions.NotFoundException

    return schemas.Organization(**result._mapping)


async def get_membership_by_user_id(
    db_session: AsyncSession, user_id: int
) -> schemas.Membership:

    organization_members_tbl = db_tables.organization_members

    query = select(organization_members_tbl).where(
        organization_members_tbl.c.user_id == user_id
    )

    result = (await db_session.execute(query)).first()

    if result is None:
        raise exceptions.NotFoundException
    return schemas.Membership(**result._mapping)


async def add_employee(
    db_session: AsyncSession, data: schemas.Membership
) -> schemas.Membership:

    organization_members_tbl = db_tables.organization_members

    query = (
        pg_insert(organization_members_tbl)
        .values(**data.dict())
        .on_conflict_do_update(
            constraint="organization_members_pk", set_=dict(role=data.role)
        )
        .returning()
    )
    await db_session.execute(query)

    result = await get_membership_by_user_id(db_session, data.user_id)
    return result
