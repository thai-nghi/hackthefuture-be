from fastapi import Request

async def get_minio_client(request: Request):
    return request.app.state.minio_client