from typing import Annotated
from fastapi import APIRouter, Body, Path, Query

from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import UserDependency, DatabaseDependency

from src.exceptions import BadRequestException
from src import schemas

from src.schemas import responses

from src.services import event, organization
import datetime

router = APIRouter(prefix="/event", tags=["Events"])


@router.get("/", response_model=responses.EventListResponse)
async def get_event(
    current_user: UserDependency,
    db_session: DatabaseDependency,
    currentPage: Annotated[int, Query(gt=0)] = 0,
    pageSize: Annotated[int, Query(lt=100)] = 6,
    country: Annotated[int | None, Query()] = None,
    city: Annotated[int | None, Query()] = None,
    tags: Annotated[list[int] | None, Query()] = None,
) -> responses.EventListResponse:

    total, events = await event.get_all_event(
        db_session,
        schemas.PaginationIn(currentPage=currentPage, pageSize=pageSize),
        country=country,
        city=city,
        tags=tags,
        start_after=datetime.datetime.now(),
    )
    page_response = schemas.PaginationResponse(total=total, currentPage=currentPage, pageSize=pageSize)
    return responses.EventListResponse(data=events, page=page_response)


@router.post("/", response_model=responses.EventAttributeResponse)
async def create_event(
    current_user: UserDependency,
    db_session: DatabaseDependency,
    data: Annotated[schemas.EventAttributeIn, Body(embed=True)],
) -> responses.EventAttributeResponse:

    if current_user.organization_id is None:
        raise BadRequestException("You must be in an organization to create an event")
    event_data = schemas.EventAttributeMid(
        organizer_id=current_user.organization_id, **data.dict()
    )
    new_event = await event.create_new_event(db_session, event_data)
    await db_session.commit()
    return responses.EventAttributeResponse(data=new_event)


@router.get("/{event_id}", response_model=responses.EventAttributeResponse)
async def get_event(
    current_user: UserDependency,
    db_session: DatabaseDependency,
    event_id: Annotated[int, Path],
) -> responses.EventAttributeResponse:

    retrieved_event = await event.get_event_by_id(db_session, event_id)
    return responses.EventAttributeResponse(data=retrieved_event)


@router.put("/{event_id}", response_model=responses.EventAttributeResponse)
async def get_event(
    current_user: UserDependency,
    db_session: DatabaseDependency,
    event_id: Annotated[int, Path],
    event_data: Annotated[schemas.EventAttributeIn, Body(embed=True)],
) -> responses.EventAttributeResponse:

    event_organizer_id = await event.get_organizer_by_id(db_session, event_id)

    if current_user.organization_id != event_organizer_id:
        raise BadRequestException("User are not the organizer of the event")

    retrieved_event = await event.update_event(db_session, event_id, event_data)
    await db_session.commit()
    return responses.EventAttributeResponse(data=retrieved_event)
