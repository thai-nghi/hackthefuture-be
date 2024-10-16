from typing import Annotated
from fastapi import APIRouter, Depends, Path

from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.dependencies.user import get_current_user

from src.exceptions import BadRequestException
from src import schemas

from src.services import shop as shop_service


router = APIRouter(prefix="/fair")