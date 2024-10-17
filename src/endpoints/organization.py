from typing import Annotated
from fastapi import APIRouter, Depends, Path, Body

from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import (UserDependency, DatabaseDependency)
from src.dependencies.user import get_current_user

from src.exceptions import BadRequestException
from src import schemas
from src.schemas import responses

from src.services import organization, document

router = APIRouter(prefix="/org", dependencies=[Depends(get_current_user)], tags=["Organizations"])


@router.get("/", response_model=responses.OrganizationResponse)
async def user_org(
    current_user: UserDependency,
    db_session: DatabaseDependency,
    
) -> responses.OrganizationResponse:

    data = await organization.organization_by_user_data(
        db_session, current_user.id, current_user.organization
    )

    return responses.OrganizationResponse(data=data)


@router.post("/", response_model=responses.OrganizationResponse)
async def create_org(
    current_user: UserDependency,
    db_session: DatabaseDependency,
    data: Annotated[schemas.OrganizationIn, Body],
) -> responses.OrganizationResponse :
    if current_user.organization is not None:
        raise BadRequestException("User already has an organization")
    
    
    new_organization = await organization.new_organization(db_session, data)

    await document.add_documents(db_session, new_organization.id, data.documents)
    await db_session.commit()

    return responses.OrganizationResponse(data=new_organization)
