from src import db_tables
from src import schemas

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy import select, update, func

from sqlalchemy.dialects.postgresql import insert as pg_insert
from src import exceptions


async def get_all_event (
    db_session: AsyncSession, 
    page_config: schemas.PaginationIn
) -> list[schemas.EventAttribute]:
    
    
    event_tbl = db_tables.events
    
    offset = page_config.pageSize * page_config.currentPage
    query = select(event_tbl).limit(page_config.pageSize).offset(offset)
    
    all_events = (await db_session.execute(query)).all()
    
    query = select(func.count()).select_from(event_tbl)
    total = (await db_session.execute(query)).scalar()
    return total, [schemas.EventAttribute(**event._mapping) for event in all_events]

async def get_event_by_id(
    db_session: AsyncSession,
    id: int
) -> schemas.EventAttribute:
    
    event_tbl = db_tables.events
    org_tbl = db_tables.organizations
    
    query = select(
                event_tbl, 
                org_tbl.c.organization_name
            ).join(
                org_tbl, 
                org_tbl.c.id == event_tbl.c.organizer_id,
                isouter=True
            ).where(event_tbl.c.id == id)

    result = (await db_session.execute(query)).first()

    if result is None:
        raise exceptions.NotFoundException

    return schemas.EventAttribute(**result._mapping)

async def create_new_event(
        db_session: AsyncSession, 
        event_data: schemas.EventAttributeMid
    )-> schemas.EventAttribute:
    
    event_tbl = db_tables.events

    query = pg_insert(event_tbl).values(**event_data.dict()).returning(event_tbl.c.id)
    
    inserted_id = (await db_session.execute(query)).scalar()
    
    return await get_event_by_id(db_session, inserted_id)


async def update_event(
        db_session: AsyncSession, event_id: int, event_data: schemas.EventAttribute
    )-> schemas.EventAttribute:

    event_tbl = db_tables.events

    query = update(event_tbl).where(event_tbl.c.id == event_id).values(**event_data.dict(exclude={"id"})).returning(event_tbl.c.id)
    
    update_id = (await db_session.execute(query)).scalar()
    
    return await get_event_by_id(db_session, update_id)


async def get_organizer_by_id(
    db_session: AsyncSession,
    id: int
) -> int:
    
    event = await get_event_by_id(db_session, id)
    return event.organizer_id