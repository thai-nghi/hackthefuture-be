from src import db_tables
from src import schemas
from src import exceptions

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy import select, insert

async def all_countries(db_session: AsyncSession) -> list[schemas.Country]:
    query = select(db_tables.countries)

    rows = (await db_session.execute(query))

    return [schemas.Country(label=row._mapping['label'], value=row._mapping['id']) for row in rows]

async def cities_of_countries(db_session: AsyncSession, country_id: int) -> list[schemas.City]:
    query = select(db_tables.cities).where(db_tables.cities.c.country == country_id)

    rows = (await db_session.execute(query))

    return [schemas.City(label=row._mapping['label'], value=row._mapping['id']) for row in rows]