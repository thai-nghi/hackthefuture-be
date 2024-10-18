from fastapi import APIRouter
from src.dependencies import UserDependency
from src.schemas import responses

router = APIRouter(prefix="/user")

@router.get("/", response_model=responses.LoginResponse)
async def get_user_data(
    user: UserDependency
) -> responses.LoginResponse:
    return responses.LoginResponse(data=user)