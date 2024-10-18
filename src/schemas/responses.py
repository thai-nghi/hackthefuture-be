from pydantic import BaseModel
from src import schemas
import typing

class BaseResponse(BaseModel):
    success: bool = True

class GenericResponse(BaseResponse):
    data: dict[str, typing.Any]

class OrganizationResponse(BaseResponse):
    data : schemas.Organization

class LoginResponse(BaseResponse):
    has_account: bool = True
    data: schemas.UserResponse | None
    token: str | None
