from __future__ import annotations

"""Rapor şemaları."""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date


class ReportGenerateRequest(BaseModel):
    field_id: UUID
    credit_id: UUID | None = None
    report_type: str = "monitoring"
    period_start: date
    period_end: date
    include_satellite_maps: bool = True
    methodology: str = "VM0042"


class ReportOut(BaseModel):
    id: UUID
    field_id: UUID
    credit_id: UUID | None
    report_type: str
    period_start: date | None
    period_end: date | None
    pdf_path: str | None
    generated_at: datetime
    generated_by: UUID | None

    model_config = {"from_attributes": True}


class SensorCreate(BaseModel):
    field_id: UUID
    sensor_external_id: str
    sensor_type: str = "soil_multi"
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class SensorOut(BaseModel):
    id: UUID
    field_id: UUID
    sensor_external_id: str
    sensor_type: str
    name: str | None
    latitude: float | None
    longitude: float | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SensorReadingOut(BaseModel):
    id: UUID
    sensor_id: UUID
    field_id: UUID
    timestamp: datetime
    soil_moisture: float | None
    soil_temp_c: float | None
    soil_ph: float | None
    organic_matter: float | None
    co2_flux: float | None
    battery_pct: float | None
    signal_quality: int | None

    model_config = {"from_attributes": True}


class MarketplaceListingOut(BaseModel):
    id: UUID
    seller_id: UUID
    credit_id: UUID
    price_per_ton: float
    tons_available: float
    status: str
    listed_at: datetime
    expires_at: datetime | None
    seller_name: str | None = None
    field_name: str | None = None
    methodology: str | None = None
    vintage_year: int | None = None

    model_config = {"from_attributes": True}


class MarketplaceBuyRequest(BaseModel):
    tons_to_buy: float


class MarketplaceTransactionOut(BaseModel):
    id: UUID
    listing_id: UUID
    buyer_id: UUID
    tons_purchased: float
    total_usd: float
    platform_fee: float
    transaction_at: datetime
    blockchain_tx: str | None

    model_config = {"from_attributes": True}
