from minio import Minio
from fastapi import UploadFile


def file_type_to_bucket(type: str):
    if type.startswith("image"):
        return "htf-public"
    return "htf"


async def upload_file(client: Minio, file: UploadFile):
    return client.put_object(
        file_type_to_bucket(file.content_type), file.filename, file.file, file.size
    )
