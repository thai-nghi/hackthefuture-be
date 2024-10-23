from src import db_tables
from src import schemas

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy import select, func, update
from src.exceptions import BadRequestException
from src import schemas

from sqlalchemy.dialects.postgresql import insert as pg_insert


def build_application_query(
    application_id: int | None = None,
    event_id: int | None = None,
    org_id: int | None = None,
):
    app_tbl = db_tables.event_applications
    org_tbl = db_tables.organizations
    country_tbl = db_tables.countries
    city_tbl = db_tables.cities
    event_tbl = db_tables.events

    query = select(
        app_tbl,
        org_tbl.c.organization_name.label("applicant_name"),
        org_tbl.c.contact_address.label("applicant_address"),
        org_tbl.c.contact_phone.label("applicant_phone"),
        org_tbl.c.email.label("applicant_email"),
        org_tbl.c.size.label("applicant_size"),
        org_tbl.c.years_of_operation.label("applicant_years_of_operation"),
        org_tbl.c.country.label("applicant_country"),
        org_tbl.c.city.label("applicant_city"),
        country_tbl.c.label.label("applicant_country_label"),
        city_tbl.c.label.label("applicant_city_label"),
        event_tbl.c.event_name,
    ).select_from(
        app_tbl.join(org_tbl, app_tbl.c.applicant_id == org_tbl.c.id)
        .join(country_tbl, org_tbl.c.country == country_tbl.c.id)
        .join(city_tbl, org_tbl.c.city == city_tbl.c.id)
        .join(event_tbl, event_tbl.c.id == app_tbl.c.event_id)
    )

    if application_id is not None:
        query = query.where(application_id == app_tbl.c.id)

    if event_id is not None:
        query = query.where(app_tbl.c.event_id == event_id)

    if org_id is not None:
        query = query.where(app_tbl.c.applicant_id == org_id)

    return query


async def get_application_by_id(
    db_session: AsyncSession, application_id: int
) -> list[schemas.EventApplication]:
    query = build_application_query(application_id=application_id)

    result = (await db_session.execute(query)).first()
    return schemas.EventApplication(**result._mapping)


async def get_application_by_event_id(
    db_session: AsyncSession, event_id: int
) -> list[schemas.EventApplication]:
    query = build_application_query(event_id=event_id)

    result = (await db_session.execute(query)).all()
    return [schemas.EventApplication(**application._mapping) for application in result]


async def application_by_org_id(
    db_session: AsyncSession, org_id: int
) -> list[schemas.EventApplication]:
    query = build_application_query(org_id=org_id)

    result = (await db_session.execute(query)).all()
    return [schemas.EventApplication(**application._mapping) for application in result]


async def existing_application(
    db_session: AsyncSession, event_id: int, applicant_id: int
) -> bool:
    app_tbl = db_tables.event_applications

    query = select(app_tbl.c.id).where(
        app_tbl.c.event_id == event_id and app_tbl.c.applicant_id == applicant_id
    )

    result = (await db_session.execute(query)).one_or_none()
    return result is not None


async def add_new_application(
    db_session: AsyncSession,
    event_id: int,
    org_id: int,
    event_data: schemas.EventApplicationIn,
) -> bool:
    if await existing_application(db_session, event_id, org_id):
        raise BadRequestException(detail="Application exists please update it")

    app_tbl = db_tables.event_applications
    query = (
        pg_insert(app_tbl)
        .values(
            event_id=event_id,
            updated_by=org_id,
            applicant_id=org_id,
            status=schemas.ApplicationStatus.IN_PROGRESS,
            **event_data.dict()
        )
        .returning(app_tbl.c.id)
    )
    inserted_id = (await db_session.execute(query)).scalar()
    return await get_application_by_id(db_session, inserted_id)


async def update_status(
    db_session: AsyncSession,
    event_id: int,
    application_id: int,
    status_data: schemas.ApplicationStatus,
) -> bool:
    print(status_data, application_id)
    app_tbl = db_tables.event_applications
    query = (
        update(app_tbl)
        .where(
            app_tbl.c.id == application_id
        )
        .values(status=status_data)
        .returning(app_tbl.c.id)
    )

    updated_id = (await db_session.execute(query)).scalar()
    return await get_application_by_id(db_session, updated_id)
