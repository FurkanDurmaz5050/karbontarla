from __future__ import annotations

"""KarbonTarla — Veritabanı bağlantısı ve session yönetimi."""

import uuid as uuid_module
from sqlalchemy import String, TypeDecorator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings


class UUID(TypeDecorator):
    """SQLite uyumlu UUID tipi — String(36) olarak saklar."""
    impl = String(36)
    cache_ok = True

    def __init__(self, as_uuid=True):
        super().__init__()

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid_module.UUID(value)
        return value


settings = get_settings()

_db_url = settings.get_database_url()
_engine_kwargs = {
    "echo": settings.ENVIRONMENT == "development",
}
if "sqlite" in _db_url:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs["pool_size"] = 20
    _engine_kwargs["max_overflow"] = 10

engine = create_async_engine(_db_url, **_engine_kwargs)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
