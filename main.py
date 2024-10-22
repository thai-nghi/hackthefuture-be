from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from fastapi.middleware.cors import CORSMiddleware

from src.endpoints.auth import router as auth_router
from src.endpoints.event import router as event_router
from src.endpoints.organization import router as organizer_router
from src.endpoints.metadata import router as metadata_router
from src.endpoints.user import router as user_router
from src.endpoints.upload import router as upload_router

from src.core.config import settings

from minio import Minio

app = FastAPI(default_response_class=ORJSONResponse)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def handle_token(request: Request, call_next):
    # access_token = request.cookies.get("access")
    # decoded_token = decode_token(access_token)

    # if decoded_token is not None:
    #     request.app.decoded_token = decoded_token

    return await call_next(request)

print(f"{settings.MINIO_URL}:{settings.MINIO_PORT}")
app.state.minio_client = Minio(
    f"{settings.MINIO_URL}:{settings.MINIO_PORT}",
    access_key=settings.MINIO_ACCESS,
    secret_key=settings.MINIO_SECRET,
    secure=False
)

for router in (auth_router, organizer_router, event_router, metadata_router, user_router, upload_router):
    app.include_router(router)
