from __future__ import annotations

"""Tarla şemaları — GeoJSON desteği."""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, date
from typing import Any


class GeoJSONPolygon(BaseModel):
    type: str = "Polygon"
    coordinates: list[list[list[float]]]


class FieldCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    geometry: GeoJSONPolygon
    soil_type: str | None = None
    current_practice: str | None = None
    organic_input_level: str = "medium"


class FieldUpdate(BaseModel):
    name: str | None = None
    soil_type: str | None = None
    current_practice: str | None = None
    organic_input_level: str | None = None
    status: str | None = None


class FieldOut(BaseModel):
    id: UUID
    farmer_id: UUID
    name: str
    area_ha: float
    soil_type: str | None
    current_practice: str | None
    organic_input_level: str
    enrolled_date: date | None
    status: str
    created_at: datetime
    geometry_geojson: dict | None = None

    model_config = {"from_attributes": True}


class NDVIDataPoint(BaseModel):
    date: str
    ndvi: float
    cloud_cover: float | None = None


class NDVISeriesResponse(BaseModel):
    field_id: UUID
    series: list[NDVIDataPoint]
    stats: dict


class SatelliteObservation(BaseModel):
    time: datetime
    field_id: UUID
    ndvi: float | None
    ndmi: float | None
    cloud_cover_pct: float | None
    scene_id: str | None
    satellite: str = "S2A"
