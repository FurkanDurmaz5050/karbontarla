from __future__ import annotations

"""KarbonTarla — Ortam değişkenleri konfigürasyonu."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Veritabanı (varsayılan: SQLite lokal)
    DATABASE_URL: str = "sqlite+aiosqlite:///./karbontarla.db"

    # JWT
    JWT_SECRET_KEY: str = "change-this-to-a-random-secret-key-at-least-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # Copernicus Sentinel-2
    COPERNICUS_CLIENT_ID: str = ""
    COPERNICUS_CLIENT_SECRET: str = ""

    # Uygulama
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # PDF
    PDF_OUTPUT_DIR: str = "./reports"

    class Config:
        env_file = ".env"
        extra = "allow"

    def get_database_url(self) -> str:
        url = self.DATABASE_URL
        if self.ENVIRONMENT == "production" and "sqlite" in url and "/tmp/" not in url:
            url = "sqlite+aiosqlite:////tmp/karbontarla.db"
        return url


@lru_cache()
def get_settings() -> Settings:
    return Settings()
