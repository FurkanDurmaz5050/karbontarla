from __future__ import annotations

"""Çiftçi profil şemaları."""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class FarmerProfileCreate(BaseModel):
    tc_kimlik_no: str | None = Field(None, max_length=11)
    tarim_id: str | None = None
    il: str | None = None
    ilce: str | None = None
    toplam_arazi_ha: float | None = None


class FarmerProfileUpdate(BaseModel):
    il: str | None = None
    ilce: str | None = None
    toplam_arazi_ha: float | None = None


class FarmerProfileOut(BaseModel):
    id: UUID
    user_id: UUID
    tarim_id: str | None
    il: str | None
    ilce: str | None
    toplam_arazi_ha: float | None
    created_at: datetime

    model_config = {"from_attributes": True}
