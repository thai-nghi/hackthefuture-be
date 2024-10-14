from src import db_tables
from src import schemas

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy import select, insert, update
from src.services import user


async def add_point_for_user(
    db_session: AsyncSession, point: int, user_id: int
) -> schemas.UserResponse:
    point_table = db_tables.user_point_gain

    user_table = db_tables.user

    log_query = insert(point_table).values(
        user_id=user_id,
        point=point,
    )

    await db_session.execute(log_query)

    update_query = (
        update(user_table)
        .values(
            total_points=user_table.c.total_points + point,
            points=user_table.c.points + point,
        )
        .where(user_table.c.id == user_id)
    )

    await db_session.execute(update_query)

    print("During add point", type(user_id))

    return await user.user_by_id(db_session, user_id)


async def leaderboard_of_country(
    db_session: AsyncSession,
    country: str,
) -> list[schemas.LeaderboardEntry]:
    user_tbl = db_tables.user

    query = (
        select(
            user_tbl.c.full_name,
            user_tbl.c.total_points,
            user_tbl.c.rank,
            user_tbl.c.id,
        )
        .where(user_tbl.c.country == country)
        .order_by(user_tbl.c.total_points.desc())
        .limit(10)
    )

    result = await db_session.execute(query)

    return [schemas.LeaderboardEntry(**entry._mapping) for entry in result]
