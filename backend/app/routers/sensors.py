from __future__ import annotations
from typing import List, Optional

"""Sensör router — IoT cihaz yönetimi ve veri okuma."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.models.user import User
from app.models.sensor import Sensor, SensorReading
from app.routers.auth import get_current_user
from app.schemas.report import SensorCreate, SensorOut, SensorReadingOut

router = APIRouter()


@router.get("", response_model=List[SensorOut])
async def list_sensors(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Sensor).order_by(Sensor.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=SensorOut, status_code=201)
async def create_sensor(
    data: SensorCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(Sensor).where(Sensor.sensor_external_id == data.sensor_external_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bu sensör ID'si zaten kayıtlı")

    sensor = Sensor(
        field_id=data.field_id,
        sensor_external_id=data.sensor_external_id,
        sensor_type=data.sensor_type,
        name=data.name,
        latitude=data.latitude,
        longitude=data.longitude,
    )
    db.add(sensor)
    await db.flush()
    return sensor


@router.get("/{sensor_id}", response_model=SensorOut)
async def get_sensor(
    sensor_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Sensor).where(Sensor.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensör bulunamadı")
    return sensor


@router.get("/{sensor_id}/readings", response_model=List[SensorReadingOut])
async def get_sensor_readings(
    sensor_id: UUID,
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(SensorReading)
        .where(SensorReading.sensor_id == sensor_id, SensorReading.timestamp >= since)
        .order_by(SensorReading.timestamp.desc())
        .limit(1000)
    )
    return result.scalars().all()


@router.get("/{sensor_id}/latest", response_model=Optional[SensorReadingOut])
async def get_latest_reading(
    sensor_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SensorReading)
        .where(SensorReading.sensor_id == sensor_id)
        .order_by(SensorReading.timestamp.desc())
        .limit(1)
    )
    reading = result.scalar_one_or_none()
    if not reading:
        return None
    return reading
