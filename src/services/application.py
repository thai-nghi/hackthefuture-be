from src import db_tables
from src import schemas

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy import select, func, update
from src.exceptions import BadRequestException
from src import schemas

from sqlalchemy.dialects.postgresql import insert as pg_insert

async def get_application_by_id(
    db_session: AsyncSession, application_id: int
)->list[schemas.EventApplication]:
    app_tbl = db_tables.event_applications

    query = select(app_tbl).where(app_tbl.c.id == application_id)

    result = (await db_session.execute(query)).one()
    return schemas.EventApplication(**result._mapping)

async def get_application_by_event_id(
    db_session: AsyncSession, event_id: int
)->list[schemas.EventApplication]:
    app_tbl = db_tables.event_applications

    query = select(app_tbl).where(app_tbl.c.event_id == event_id)

    result = (await db_session.execute(query)).all()
    return [schemas.EventApplication(**application._mapping) for application in result]

async def application_by_org_id(
    db_session: AsyncSession, org_id: int
)->list[schemas.EventApplication]:
    app_tbl = db_tables.event_applications

    query = select(app_tbl).where(app_tbl.c.applicant_id == org_id)

    result = (await db_session.execute(query)).all()
    return [schemas.EventApplication(**application._mapping) for application in result]


async def existing_application(
    db_session: AsyncSession, event_id: int, applicant_id: int
)->bool:
    app_tbl = db_tables.event_applications

    query = select(app_tbl).where(app_tbl.c.event_id == event_id and 
                                  app_tbl.c.applicant_id == applicant_id)

    result = (await db_session.execute(query)).one_or_none()
    return result is not None

async def add_new_application(
    db_session: AsyncSession, event_id: int, user_id: int, event_data: schemas.EventApplicationIn
)->bool:
    if await existing_application(db_session, event_id, event_data.applicant_id):
        raise BadRequestException(detail='Application exists please update it')
    
    app_tbl = db_tables.event_applications
    query = pg_insert(app_tbl) \
            .values(
                event_id = event_id, 
                created_at = func.now(),
                updated_at = func.now(),
                updated_by = user_id,
                status = schemas.ApplicationStatus.IN_PROGRESS, 
                **event_data.dict()
            ).returning(app_tbl.c.id)
    inserted_id =  (await db_session.execute(query)).scalar()
    return await get_application_by_id(inserted_id)

async def update_status(
    db_session: AsyncSession, event_id: int, application_id: int, status_data: schemas.ApplicationStatus
)->bool:
    
    app_tbl = db_tables.event_applications
    query = update(app_tbl) \
            .where(app_tbl.c.applicant_id == application_id
                and app_tbl.c.event_id == event_id) \
            .values(status=status_data.status) \
            .returning(app_tbl.c.id)
    
    updated_id =  (await db_session.execute(query)).scalar()
    return await get_application_by_id(db_session, updated_id)

