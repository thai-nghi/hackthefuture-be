from typing import Annotated
from fastapi import APIRouter, Depends, Path

from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.dependencies.user import get_current_user

from src.exceptions import BadRequestException
from src import schemas

from src.services import shop as shop_service


router = APIRouter(prefix="/shop", dependencies=[Depends(get_current_user)])

@router.get("/")
async def shop_items(
    db_session: AsyncSession = Depends(get_db),
):
    items = await shop_service.all_items(db_session)

    return {"items": items}


@router.post("/{item_id}")
async def buy_item(
    user: Annotated[schemas.UserResponse, Depends(get_current_user)],
    db_session: AsyncSession = Depends(get_db),
    item_id: int = Path(),
):
    item_detail = await shop_service.item_detail(db_session, item_id)

    if user.rank.value < item_detail.rank_to_unlock.value:
        raise BadRequestException("User rank is lower than required")

    if user.points < item_detail.price:
        raise BadRequestException("User does not have enough points")

    new_point = await shop_service.buy_item(db_session, user.id, item_id, item_detail.price)

    await db_session.commit()

    return {"points": new_point}