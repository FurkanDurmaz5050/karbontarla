from __future__ import annotations

"""Karbon kredi şemaları."""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date


class CarbonCreditOut(BaseModel):
    id: UUID
    field_id: UUID
    period_start: date
    period_end: date
    vintage_year: int | None
    baseline_soc: float | None
    calculated_soc: float | None
    delta_co2_tons: float | None
    credit_tons: float | None
    tradeable_tons: float | None
    ndvi_correction: float | None
    verification_status: str
    verra_serial: str | None
    methodology: str
    price_usd: float | None
    certificate_url: str | None
    blockchain_tx: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CarbonCalculationRequest(BaseModel):
    field_id: UUID
    year: int


class CarbonSummary(BaseModel):
    total_credits: float
    total_tradeable: float
    total_value_usd: float
    credits_by_status: dict
    fields_count: int


class CarbonCalculationResult(BaseModel):
    baseline_soc: float
    project_soc: float
    delta_co2_tons: float
    credit_tons: float
    tradeable_tons: float
    ndvi_correction: float
    methodology: str


class ListCreditRequest(BaseModel):
    price_per_ton: float
    tons_to_list: float | None = None
