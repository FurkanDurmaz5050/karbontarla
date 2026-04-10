from __future__ import annotations

"""Sentinel-2 uydu veri router."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
import random

from app.database import get_db
from app.models.user import User
from app.models.field import Field
from app.models.farmer import FarmerProfile
from app.routers.auth import get_current_user
from app.schemas.field import NDVISeriesResponse, NDVIDataPoint
from app.services.sentinel_api import SentinelAPIService
from app.services.ndvi_calculator import NDVICalculator

router = APIRouter()
sentinel_service = SentinelAPIService()
ndvi_calculator = NDVICalculator()


@router.get("/ndvi/{field_id}", response_model=NDVISeriesResponse)
async def get_ndvi_series(
    field_id: UUID,
    months: int = Query(default=12, ge=1, le=36),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Field).where(Field.id == field_id))
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Tarla bulunamadı")

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=months * 30)

    series = sentinel_service.generate_mock_ndvi_series(
        start_date=start_date,
        end_date=end_date,
        interval_days=5,
        base_ndvi=0.45,
        soil_type=field.soil_type,
        practice=field.current_practice,
    )

    ndvi_values = [p.ndvi for p in series]
    mean_ndvi = sum(ndvi_values) / len(ndvi_values) if ndvi_values else 0

    if len(ndvi_values) >= 2:
        first_half = ndvi_values[:len(ndvi_values)//2]
        second_half = ndvi_values[len(ndvi_values)//2:]
        trend = (sum(second_half)/len(second_half)) - (sum(first_half)/len(first_half))
        trend_per_month = trend / (months / 2)
    else:
        trend_per_month = 0

    health_score = min(100, max(0, int(mean_ndvi * 120)))

    return NDVISeriesResponse(
        field_id=field_id,
        series=series,
        stats={
            "mean_ndvi": round(mean_ndvi, 4),
            "trend": f"{'+' if trend_per_month >= 0 else ''}{trend_per_month:.4f}/month",
            "health_score": health_score,
            "total_observations": len(series),
        },
    )


@router.get("/image/{field_id}")
async def get_satellite_image(
    field_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Field).where(Field.id == field_id))
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Tarla bulunamadı")

    ndvi_geotiff_b64 = sentinel_service.generate_mock_ndvi_geotiff()

    return {
        "field_id": str(field_id),
        "ndvi_geotiff_base64": ndvi_geotiff_b64,
        "date": datetime.now(timezone.utc).isoformat(),
        "satellite": "S2A",
        "cloud_cover_pct": round(random.uniform(0, 15), 1),
    }


@router.post("/fetch/{field_id}")
async def trigger_satellite_fetch(
    field_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Field).where(Field.id == field_id))
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Tarla bulunamadı")

    ndvi_value = sentinel_service.calculate_mock_ndvi(
        soil_type=field.soil_type,
        practice=field.current_practice,
    )

    return {
        "status": "completed",
        "field_id": str(field_id),
        "ndvi": ndvi_value,
        "ndmi": round(ndvi_value * 0.85 + random.uniform(-0.05, 0.05), 4),
        "scene_id": f"S2A_MSIL2A_{datetime.now().strftime('%Y%m%d')}",
        "cloud_cover_pct": round(random.uniform(0, 10), 1),
        "message": "Uydu verisi başarıyla çekildi",
    }
