from typing import Annotated
from fastapi import APIRouter, Depends, Path, Body


from src.dependencies import UserDependency, DatabaseDependency
from src.dependencies.user import get_current_user

from src.exceptions import BadRequestException
from src import schemas
from src.schemas import responses

from src.services import organization, document

router = APIRouter(
    prefix="/org", dependencies=[Depends(get_current_user)], tags=["Organizations"]
)


@router.get("/", response_model=responses.OrganizationResponse)
async def user_org(
    current_user: UserDependency,
    db_session: DatabaseDependency,
) -> responses.OrganizationResponse:

    data = await organization.organization_by_user_data(
        db_session, current_user.id
    )

    return responses.OrganizationResponse(data=data)


@router.post("/", response_model=responses.OrganizationResponse)
async def create_org(
    current_user: UserDependency,
    db_session: DatabaseDependency,
    data: Annotated[schemas.OrganizationIn, Body(embed=True)],
) -> responses.OrganizationResponse:
    if current_user.organization_id is not None:
        raise BadRequestException("User already has an organization")

    new_organization = await organization.new_organization(db_session, data)
    
    await organization.add_employee(
        db_session,
        schemas.Membership(
            user_id=current_user.id,
            organization_id=new_organization.id,
            role=schemas.OrganizationRole.ADMIN,
        ),
    )

    await document.add_documents(db_session, new_organization.id, data.documents)
    
    await db_session.commit()

    return responses.OrganizationResponse(data=new_organization)


@router.post("/add_employee", response_model=responses.OrganizationResponse)
async def add_employee(
    current_user: UserDependency,
    db_session: DatabaseDependency,
    data: Annotated[schemas.Membership, Body(embed=True)],
) -> responses.OrganizationResponse:

    membership_info = await organization.get_membership_by_user_id(current_user.id)

    if membership_info.organization_id != data.organization_id:
        raise BadRequestException("User can only add member to your organization")
    if membership_info.role != schemas.OrganizationRole.ADMIN:
        raise BadRequestException("Only user could add member to an organization")

    new_data = await organization.add_employee(db_session, data)
    return responses.MembershipReponse(data=new_data)
