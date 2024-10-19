from src import db_tables
from src import schemas

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy import select, insert, update
from src.services import user

from sqlalchemy.dialects.postgresql import insert as pg_insert
from src import exceptions

async def add_documents(db_session: AsyncSession, uploader_id: int, documents: list[schemas.DocumentAttribute]):
    if documents is None:
        return
    
    await db_session.execute(
        insert(db_tables.documents).values(uploader_id=uploader_id),
        [document.dict() for document in documents]
    )