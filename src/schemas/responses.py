from pydantic import BaseModel
from src import schemas


class BaseResponse(BaseModel):
    success: bool = True


class OrganizationResponse(BaseResponse):
    data : schemas.Organization


