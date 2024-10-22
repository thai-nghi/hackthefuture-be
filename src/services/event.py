from src import db_tables
from src import schemas

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy import select, update, func

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.postgresql import array_agg
from src import exceptions
import datetime


async def get_all_event(
    db_session: AsyncSession,
    page_config: schemas.PaginationIn,
    city: int | None = None,
    country: int | None = None,
    tags: list[int] | None = None,
    start_after: datetime.datetime | None = None,
) -> list[schemas.EventAttribute]:

    event_tbl = db_tables.events

    query = build_event_select_query(city=city, country=country, tags=tags, start_after=start_after)

    offset = page_config.pageSize * (page_config.currentPage-1)
    query = query.limit(page_config.pageSize).offset(offset)

    all_events = (await db_session.execute(query)).all()

    query = select(func.count()).select_from(event_tbl)
    total = (await db_session.execute(query)).scalar()
    return total, [schemas.EventAttribute(**event._mapping) for event in all_events]


def build_event_select_query(
    city: int | None = None,
    country: int | None = None,
    tags: list[int] | None = None,
    start_after: datetime.datetime | None = None,
    org_id: int | None = None,
    event_id: int | None = None,
):
    event_tbl = db_tables.events
    org_tbl = db_tables.organizations
    tag_tbl = db_tables.tags
    event_tag_tbl = db_tables.event_tag
    country_tbl = db_tables.countries
    city_tbl = db_tables.cities

    join_stmt = (
        event_tbl.join(org_tbl, org_tbl.c.id == event_tbl.c.organizer_id, isouter=True)
        .join(country_tbl, event_tbl.c.country == country_tbl.c.id)
        .join(city_tbl, event_tbl.c.city == city_tbl.c.id)
        .join(event_tag_tbl, event_tbl.c.id == event_tag_tbl.c.event_id, isouter=True)
        .join(tag_tbl, event_tag_tbl.c.tag_id == tag_tbl.c.id, isouter=True)
    )

    query = (
        select(
            event_tbl.c.id,
            event_tbl.c.organizer_id,
            event_tbl.c.event_name,
            event_tbl.c.street_addr,
            event_tbl.c.description,
            event_tbl.c.phone_contact,
            event_tbl.c.pictures,
            event_tbl.c.details,
            event_tbl.c.status,
            event_tbl.c.start_date,
            event_tbl.c.end_date,
            org_tbl.c.organization_name.label("organizer"),
            country_tbl.c.label.label("country"),
            city_tbl.c.label.label("city"),
            array_agg(
                func.json_build_object("value", tag_tbl.c.id, "label", tag_tbl.c.label)
            ).label("tags"),
        )
        .select_from(join_stmt)
        .group_by(
            event_tbl.c.id,
            country_tbl.c.label,
            city_tbl.c.label,
            org_tbl.c.organization_name,
        )
    )

    if city is not None:
        query = query.where(event_tbl.c.city == city)

    if country is not None:
        query = query.where(event_tbl.c.country == country)

    if tags is not None:
        query = query.where(event_tag_tbl.c.tag_id.in_(tags))

    if start_after is not None:
        query = query.where(event_tbl.c.start_date > start_after)

    if org_id is not None:
        query = query.where(event_tbl.c.organizer_id == org_id)

    if event_id is not None:
        query = query.where(event_tbl.c.id == event_id)

    return query


async def event_by_org_id(
    db_session: AsyncSession, org_id: int
) -> schemas.EventAttribute:
    query = build_event_select_query(start_after=datetime.datetime.now(), org_id=org_id)

    result = (await db_session.execute(query)).first()

    if result is None:
        raise exceptions.NotFoundException

    return schemas.EventAttribute(**result._mapping)


async def get_event_by_id(db_session: AsyncSession, id: int) -> schemas.EventAttribute:

    query = build_event_select_query(event_id=id)

    result = (await db_session.execute(query)).first()

    if result is None:
        raise exceptions.NotFoundException

    return schemas.EventAttribute(**result._mapping)


async def create_new_event(
    db_session: AsyncSession, event_data: schemas.EventAttributeMid
) -> schemas.EventAttribute:

    event_tbl = db_tables.events

    query = (
        pg_insert(event_tbl)
        .values(**event_data.dict(exclude={"tags"}))
        .returning(event_tbl.c.id)
    )

    inserted_id = (await db_session.execute(query)).scalar()

    await add_tags_to_event(db_session, inserted_id, event_data.tags)

    return await get_event_by_id(db_session, inserted_id)


async def add_tags_to_event(
    db_sesion: AsyncSession, event_id: int, tags: list[int] | None
):
    if tags is None:
        return

    event_tag_tbl = db_tables.event_tag

    await db_sesion.execute(
        pg_insert(event_tag_tbl).values(event_id=event_id),
        [{"tag_id": tag_id} for tag_id in tags],
    )


async def update_event(
    db_session: AsyncSession, event_id: int, event_data: schemas.EventAttribute
) -> schemas.EventAttribute:

    event_tbl = db_tables.events

    query = (
        update(event_tbl)
        .where(event_tbl.c.id == event_id)
        .values(**event_data.dict(exclude={"id"}))
        .returning(event_tbl.c.id)
    )

    update_id = (await db_session.execute(query)).scalar()

    return await get_event_by_id(db_session, update_id)


async def get_organizer_by_id(db_session: AsyncSession, id: int) -> int:

    event = await get_event_by_id(db_session, id)
    return event.organizer_id
