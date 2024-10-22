from fastapi import APIRouter, Depends
from src.dependencies.minio import get_minio_client
from src.dependencies.user import get_current_user
from src.schemas import responses
from minio import Minio
import typing
from src.services import minio

router = APIRouter(prefix="/upload", dependencies=[Depends(get_current_user)])
from fastapi import UploadFile

from src.core.config import settings



@router.post("/")
async def uploadFile(
    file: UploadFile,
    minio_client: typing.Annotated[Minio, Depends(get_minio_client)]
):    
    upload_result = await minio.upload_file(minio_client, file)

    if file.content_type.startswith('image'):
        return responses.GenericResponse(data={
            "imgUrl": f"http://{settings.MINIO_URL}:{settings.MINIO_PORT}/{upload_result.bucket_name}/{upload_result.object_name}"
        })
    
    return responses.GenericResponse(data={
        "file_name": file.filename
    })