"""
core/config.py — Pydantic Settings đọc từ .env
Thêm JWT settings cho Phase 2
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database — KHÔNG có default, bắt buộc phải có trong .env
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT — KHÔNG có default
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ROOT_USER: str        
    MINIO_ROOT_PASSWORD: str    
    MINIO_BUCKET: str = "sle-uploads"
    MINIO_SECURE: bool = False

settings = Settings()  # pyright: ignore[reportCallIssue]