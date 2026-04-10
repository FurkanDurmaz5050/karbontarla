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


_seeded = False


async def ensure_seeded():
    """Üretimde her cold start'ta demo kullanıcı ve örnek veriyi oluşturur."""
    global _seeded
    if _seeded:
        return
    _seeded = True

    import os
    if not (os.environ.get("VERCEL") or settings.ENVIRONMENT == "production"):
        return

    import bcrypt
    from sqlalchemy import select

    async with async_session() as session:
        from app.models.user import User
        from app.models.farmer import FarmerProfile
        from app.models.field import Field

        result = await session.execute(select(User).where(User.email == "demo@karbontarla.com"))
        if result.scalar_one_or_none():
            return

        pw_hash = bcrypt.hashpw(b"Demo1234!", bcrypt.gensalt()).decode("utf-8")
        user = User(
            email="demo@karbontarla.com",
            password_hash=pw_hash,
            full_name="Demo Çiftçi",
            role="FARMER",
        )
        session.add(user)
        await session.flush()

        profile = FarmerProfile(
            user_id=user.id,
            il="Konya",
            ilce="Çumra",
            toplam_arazi_ha=45.0,
        )
        session.add(profile)
        await session.flush()

        field = Field(
            farmer_id=profile.id,
            name="Çumra Buğday Tarlası",
            area_ha=15.0,
            soil_type="Killi",
            current_practice="no_till",
            geometry='{"type":"Polygon","coordinates":[[[32.75,37.57],[32.77,37.57],[32.77,37.59],[32.75,37.59],[32.75,37.57]]]}',
            status="active",
        )
        session.add(field)
        await session.commit()
