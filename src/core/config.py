from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    POSTGRES_HOST: str = "127.0.0.1"
    DB_PORT: str = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 24*60
    REFRESH_TOKEN_EXPIRES_MINUTES: int = 15 * 24 * 60  # 15 days

    SECRET_KEY: str

    MINIO_ACCESS: str
    MINIO_SECRET: str
    MINIO_URL: str
    DOCUMENT_BUCKET_NAME: str
    IMAGE_BUCKET_NAME: str
    MINIO_PORT: str

    class Config:
        env_file = '.dev.env'
        env_file_encoding = 'utf-8'


class DevSettings(Settings):
    
    class Config:
        env_file = '.dev.env'
        env_file_encoding = 'utf-8'

current_env = os.getenv("ENV", "dev")

if current_env != "dev":
    settings = Settings()
else:
    settings = DevSettings()
