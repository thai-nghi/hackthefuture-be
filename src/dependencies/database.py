from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)


from ..core import config


PG_URL = PostgresDsn.build(
    scheme="postgresql+asyncpg",
    user=config.settings.POSTGRES_USER,
    password=config.settings.POSTGRES_PASSWORD,
    host=config.settings.POSTGRES_HOST,
    port=config.settings.DB_PORT,
    path=f"/{config.settings.POSTGRES_DB}",
)


engine = create_async_engine(PG_URL, future=True, echo=True)


SessionFactory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)


async def get_db():
    db = SessionFactory()
    try:
        yield db
    finally:
        await db.close()
