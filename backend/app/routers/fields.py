from __future__ import annotations
from typing import List

"""Tarla yönetimi router — GeoJSON geometri desteği."""

from uuid import UUID
from datetime import date
import math
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.database import get_db
from app.models.user import User
from app.models.farmer import FarmerProfile
from app.models.field import Field
from app.routers.auth import get_current_user
from app.schemas.field import FieldCreate, FieldUpdate, FieldOut

router = APIRouter()


async def _get_farmer_profile(user: User, db: AsyncSession) -> FarmerProfile:
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Çiftçi profili bulunamadı. Önce profil oluşturun.")
    return profile


def _calculate_polygon_area_ha(coordinates: list) -> float:
    """Shoelace formula ile polygon alanını hektar olarak hesapla."""
    ring = coordinates[0] if coordinates else []
    if len(ring) < 3:
        return 0.0
    # Convert degrees to approximate meters using center latitude
    lats = [p[1] for p in ring]
    center_lat = sum(lats) / len(lats)
    lat_rad = math.radians(center_lat)
    m_per_deg_lat = 111132.0
    m_per_deg_lon = 111132.0 * math.cos(lat_rad)

    area_m2 = 0.0
    n = len(ring)
    for i in range(n):
        j = (i + 1) % n
        x1 = ring[i][0] * m_per_deg_lon
        y1 = ring[i][1] * m_per_deg_lat
        x2 = ring[j][0] * m_per_deg_lon
        y2 = ring[j][1] * m_per_deg_lat
        area_m2 += x1 * y2 - x2 * y1
    area_m2 = abs(area_m2) / 2.0
    return round(area_m2 / 10000.0, 4)


def _field_to_out(field: Field) -> FieldOut:
    geojson = json.loads(field.geometry) if field.geometry else None
    return FieldOut(
        id=field.id,
        farmer_id=field.farmer_id,
        name=field.name,
        area_ha=float(field.area_ha),
        soil_type=field.soil_type,
        current_practice=field.current_practice,
        organic_input_level=field.organic_input_level,
        enrolled_date=field.enrolled_date,
        status=field.status,
        created_at=field.created_at,
        geometry_geojson=geojson,
    )


@router.get("", response_model=List[FieldOut])
async def list_fields(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_farmer_profile(current_user, db)
    result = await db.execute(
        select(Field)
        .where(Field.farmer_id == profile.id)
        .order_by(Field.created_at.desc())
    )
    fields = result.scalars().all()
    return [_field_to_out(f) for f in fields]


@router.post("", response_model=FieldOut, status_code=201)
async def create_field(
    data: FieldCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_farmer_profile(current_user, db)
    geojson_dict = {"type": data.geometry.type, "coordinates": data.geometry.coordinates}
    geojson_str = json.dumps(geojson_dict)
    area_ha = _calculate_polygon_area_ha(data.geometry.coordinates)

    field = Field(
        farmer_id=profile.id,
        name=data.name,
        geometry=geojson_str,
        area_ha=area_ha,
        soil_type=data.soil_type,
        current_practice=data.current_practice,
        organic_input_level=data.organic_input_level,
        enrolled_date=date.today(),
    )
    db.add(field)
    await db.flush()
    return _field_to_out(field)


@router.get("/{field_id}", response_model=FieldOut)
async def get_field(
    field_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_farmer_profile(current_user, db)
    result = await db.execute(
        select(Field).where(Field.id == str(field_id), Field.farmer_id == profile.id)
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Tarla bulunamadı")
    return _field_to_out(field)


@router.put("/{field_id}", response_model=FieldOut)
async def update_field(
    field_id: UUID,
    data: FieldUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_farmer_profile(current_user, db)
    result = await db.execute(
        select(Field).where(Field.id == str(field_id), Field.farmer_id == profile.id)
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Tarla bulunamadı")

    if data.name is not None:
        field.name = data.name
    if data.soil_type is not None:
        field.soil_type = data.soil_type
    if data.current_practice is not None:
        field.current_practice = data.current_practice
    if data.organic_input_level is not None:
        field.organic_input_level = data.organic_input_level
    if data.status is not None:
        field.status = data.status

    await db.flush()
    return _field_to_out(field)


@router.delete("/{field_id}")
async def delete_field(
    field_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_farmer_profile(current_user, db)
    result = await db.execute(
        select(Field).where(Field.id == str(field_id), Field.farmer_id == profile.id)
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Tarla bulunamadı")
    await db.delete(field)
    await db.flush()
    return {"message": "Tarla silindi"}
