from pydantic import BaseModel
from src import schemas


class BaseResponse(BaseModel):
    success: bool = True

class OrganizationResponse(BaseResponse):
    data : schemas.Organization

class LoginResponse(BaseResponse):
    has_account: bool = True
    user_detail: schemas.UserResponse | None
    avatar: str

class MembershipResponse(BaseResponse):
    data: schemas.Membership

class EventListResponse(BaseResponse):
    data: list[schemas.EventAttribute]

class EventAttributeResponse(BaseResponse):
    data: schemas.EventAttribute