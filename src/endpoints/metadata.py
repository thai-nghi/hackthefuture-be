from fastapi import APIRouter, Path

from src import schemas
from src.schemas import responses
from src.dependencies import DatabaseDependency
from src.services import metadata
from typing import Annotated

router = APIRouter(prefix="/metadata", tags=["Metadata"])


@router.get("/user")
async def user_metadata(db_session: DatabaseDependency):
    countries = await metadata.all_countries(db_session)
    return responses.GenericResponse(
        data={
            "gender": [
                {"label": gender_value.capitalize(), "value": gender_value}
                for gender_value in schemas.Gender._member_names_
            ],
            "countries": countries,
        }
    )


@router.get("/cities/{country_id}")
async def citie_of_countries(
    db_session: DatabaseDependency, country_id: Annotated[int, Path()]
):
    cities = await metadata.cities_of_countries(db_session, country_id)

    return responses.GenericResponse(data={"cities": cities})
