from __future__ import annotations

"""Çiftçi profil router."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import hashlib

from app.database import get_db
from app.models.user import User
from app.models.farmer import FarmerProfile
from app.routers.auth import get_current_user
from app.schemas.farmer import FarmerProfileCreate, FarmerProfileUpdate, FarmerProfileOut

router = APIRouter()


@router.get("/profile", response_model=FarmerProfileOut)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Çiftçi profili bulunamadı")
    return profile


@router.post("/profile", response_model=FarmerProfileOut, status_code=201)
async def create_profile(
    data: FarmerProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Profil zaten mevcut")

    tc_hash = None
    if data.tc_kimlik_no:
        tc_hash = hashlib.sha256(data.tc_kimlik_no.encode()).hexdigest()

    profile = FarmerProfile(
        user_id=current_user.id,
        tc_kimlik_hash=tc_hash,
        tarim_id=data.tarim_id,
        il=data.il,
        ilce=data.ilce,
        toplam_arazi_ha=data.toplam_arazi_ha,
    )
    db.add(profile)
    await db.flush()
    return profile


@router.put("/profile", response_model=FarmerProfileOut)
async def update_profile(
    data: FarmerProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Çiftçi profili bulunamadı")

    if data.il is not None:
        profile.il = data.il
    if data.ilce is not None:
        profile.ilce = data.ilce
    if data.toplam_arazi_ha is not None:
        profile.toplam_arazi_ha = data.toplam_arazi_ha

    await db.flush()
    return profile
