from __future__ import annotations
from typing import List

"""Karbon hesaplama router — VM0042 metodolojisi."""

from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.field import Field
from app.models.farmer import FarmerProfile
from app.models.carbon_credit import CarbonCredit
from app.routers.auth import get_current_user
from app.schemas.carbon import (
    CarbonCreditOut, CarbonCalculationRequest, CarbonSummary,
    CarbonCalculationResult, ListCreditRequest,
)
from app.services.carbon_engine import CarbonEngine

router = APIRouter()
carbon_engine = CarbonEngine()


@router.get("/credits", response_model=List[CarbonCreditOut])
async def list_credits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile_result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        return []

    field_ids_result = await db.execute(
        select(Field.id).where(Field.farmer_id == profile.id)
    )
    field_ids = [row[0] for row in field_ids_result.all()]
    if not field_ids:
        return []

    result = await db.execute(
        select(CarbonCredit)
        .where(CarbonCredit.field_id.in_(field_ids))
        .order_by(CarbonCredit.created_at.desc())
    )
    return result.scalars().all()


@router.get("/credits/summary", response_model=CarbonSummary)
async def get_credits_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile_result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        return CarbonSummary(
            total_credits=0, total_tradeable=0, total_value_usd=0,
            credits_by_status={}, fields_count=0,
        )

    field_ids_result = await db.execute(
        select(Field.id).where(Field.farmer_id == profile.id)
    )
    field_ids = [row[0] for row in field_ids_result.all()]

    credits_result = await db.execute(
        select(CarbonCredit).where(CarbonCredit.field_id.in_(field_ids))
    )
    credits = credits_result.scalars().all()

    total_credits = sum(float(c.credit_tons or 0) for c in credits)
    total_tradeable = sum(float(c.tradeable_tons or 0) for c in credits)
    total_value = sum(float(c.tradeable_tons or 0) * float(c.price_usd or 25) for c in credits)

    status_counts = {}
    for c in credits:
        status_counts[c.verification_status] = status_counts.get(c.verification_status, 0) + 1

    return CarbonSummary(
        total_credits=round(total_credits, 2),
        total_tradeable=round(total_tradeable, 2),
        total_value_usd=round(total_value, 2),
        credits_by_status=status_counts,
        fields_count=len(field_ids),
    )


@router.get("/credits/{credit_id}", response_model=CarbonCreditOut)
async def get_credit(
    credit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CarbonCredit).where(CarbonCredit.id == credit_id)
    )
    credit = result.scalar_one_or_none()
    if not credit:
        raise HTTPException(status_code=404, detail="Karbon kredisi bulunamadı")
    return credit


@router.post("/calculate", response_model=CarbonCalculationResult)
async def calculate_carbon(
    data: CarbonCalculationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Field).where(Field.id == data.field_id))
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Tarla bulunamadı")

    calc_result = carbon_engine.calculate_annual_credits(
        area_ha=float(field.area_ha),
        soil_type=field.soil_type or "Balçıklı",
        current_practice=field.current_practice or "no_till",
        organic_input_level=field.organic_input_level or "medium",
        year=data.year,
    )

    credit = CarbonCredit(
        field_id=data.field_id,
        period_start=date(data.year, 1, 1),
        period_end=date(data.year, 12, 31),
        vintage_year=data.year,
        baseline_soc=calc_result.baseline_soc,
        calculated_soc=calc_result.project_soc,
        delta_co2_tons=calc_result.delta_co2_tons,
        credit_tons=calc_result.credit_tons,
        tradeable_tons=calc_result.tradeable_tons,
        ndvi_correction=calc_result.ndvi_correction,
        methodology="VM0042",
        price_usd=25.0,
    )
    db.add(credit)
    await db.flush()

    return calc_result


@router.post("/credits/{credit_id}/list")
async def list_credit_on_marketplace(
    credit_id: UUID,
    data: ListCreditRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.marketplace import MarketplaceListing

    result = await db.execute(
        select(CarbonCredit).where(CarbonCredit.id == credit_id)
    )
    credit = result.scalar_one_or_none()
    if not credit:
        raise HTTPException(status_code=404, detail="Karbon kredisi bulunamadı")

    if credit.verification_status != "verified":
        raise HTTPException(status_code=400, detail="Yalnızca doğrulanmış krediler listelenebilir")

    tons = data.tons_to_list or float(credit.tradeable_tons or 0)
    if tons <= 0:
        raise HTTPException(status_code=400, detail="Listelenecek ton miktarı 0'dan büyük olmalı")

    listing = MarketplaceListing(
        seller_id=current_user.id,
        credit_id=credit_id,
        price_per_ton=data.price_per_ton,
        tons_available=tons,
    )
    db.add(listing)
    await db.flush()

    return {"message": "Kredi pazara çıkarıldı", "listing_id": str(listing.id)}
