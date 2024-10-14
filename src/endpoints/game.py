from typing import Annotated
from fastapi import APIRouter, Depends, Path

from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.dependencies.user import get_current_user

from src.exceptions import BadRequestException
from src import schemas

router = APIRouter(prefix="/game", dependencies=[Depends(get_current_user)])

@router.post("/play")
async def find_match():
    """
    """
    pass

@router.post("/lobby")
async def create_lobby():
    """
    """
    pass

@router.post("/lobby/{lobby_id}")
async def join_lobby():
    """
    """
    pass


@router.get("/watch/{match_id}")
async def watch_game():
    """
    """
    pass