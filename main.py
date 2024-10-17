from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from fastapi.middleware.cors import CORSMiddleware

from src.endpoints.auth import router as auth_router
from src.endpoints.organization import router as shop_router
from starlette.datastructures import MutableHeaders

from src.core.jwt import decode_token

app = FastAPI(default_response_class=ORJSONResponse)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "*"
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
    access_token = request.cookies.get("access")
    decoded_token = decode_token(access_token)

    if decoded_token is not None:
        request.app.decoded_token = decoded_token

    return await call_next(request)

for router in (auth_router, shop_router):
    app.include_router(router)
