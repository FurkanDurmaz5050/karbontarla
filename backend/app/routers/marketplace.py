from __future__ import annotations
from typing import List

"""Marketplace router — karbon kredi alım/satım."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.user import User
from app.models.marketplace import MarketplaceListing, MarketplaceTransaction
from app.models.carbon_credit import CarbonCredit
from app.routers.auth import get_current_user, require_role
from app.schemas.report import (
    MarketplaceListingOut, MarketplaceBuyRequest, MarketplaceTransactionOut,
)

router = APIRouter()

PLATFORM_FEE_RATE = 0.035  # %3.5


@router.get("", response_model=List[MarketplaceListingOut])
async def list_active_listings(
    min_price: float | None = None,
    max_price: float | None = None,
    methodology: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(MarketplaceListing)
        .options(
            joinedload(MarketplaceListing.seller),
            joinedload(MarketplaceListing.credit).joinedload(CarbonCredit.field),
        )
        .where(MarketplaceListing.status == "active")
    )

    if min_price is not None:
        query = query.where(MarketplaceListing.price_per_ton >= min_price)
    if max_price is not None:
        query = query.where(MarketplaceListing.price_per_ton <= max_price)

    query = query.order_by(MarketplaceListing.listed_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    listings = result.unique().scalars().all()

    out = []
    for listing in listings:
        item = MarketplaceListingOut(
            id=listing.id,
            seller_id=listing.seller_id,
            credit_id=listing.credit_id,
            price_per_ton=float(listing.price_per_ton),
            tons_available=float(listing.tons_available),
            status=listing.status,
            listed_at=listing.listed_at,
            expires_at=listing.expires_at,
            seller_name=listing.seller.full_name if listing.seller else None,
            field_name=listing.credit.field.name if listing.credit and listing.credit.field else None,
            methodology=listing.credit.methodology if listing.credit else None,
            vintage_year=listing.credit.vintage_year if listing.credit else None,
        )
        out.append(item)
    return out


@router.get("/{listing_id}", response_model=MarketplaceListingOut)
async def get_listing(
    listing_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MarketplaceListing)
        .options(
            joinedload(MarketplaceListing.seller),
            joinedload(MarketplaceListing.credit).joinedload(CarbonCredit.field),
        )
        .where(MarketplaceListing.id == listing_id)
    )
    listing = result.unique().scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="İlan bulunamadı")

    return MarketplaceListingOut(
        id=listing.id,
        seller_id=listing.seller_id,
        credit_id=listing.credit_id,
        price_per_ton=float(listing.price_per_ton),
        tons_available=float(listing.tons_available),
        status=listing.status,
        listed_at=listing.listed_at,
        expires_at=listing.expires_at,
        seller_name=listing.seller.full_name if listing.seller else None,
        field_name=listing.credit.field.name if listing.credit and listing.credit.field else None,
        methodology=listing.credit.methodology if listing.credit else None,
        vintage_year=listing.credit.vintage_year if listing.credit else None,
    )


@router.post("/{listing_id}/buy", response_model=MarketplaceTransactionOut)
async def buy_credits(
    listing_id: UUID,
    data: MarketplaceBuyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MarketplaceListing).where(MarketplaceListing.id == listing_id)
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="İlan bulunamadı")

    if listing.status != "active":
        raise HTTPException(status_code=400, detail="Bu ilan artık aktif değil")

    if listing.seller_id == current_user.id:
        raise HTTPException(status_code=400, detail="Kendi ilanınızı satın alamazsınız")

    if data.tons_to_buy > float(listing.tons_available):
        raise HTTPException(status_code=400, detail="Yeterli kredi miktarı yok")

    if data.tons_to_buy <= 0:
        raise HTTPException(status_code=400, detail="Geçersiz miktar")

    total_usd = data.tons_to_buy * float(listing.price_per_ton)
    platform_fee = total_usd * PLATFORM_FEE_RATE

    transaction = MarketplaceTransaction(
        listing_id=listing_id,
        buyer_id=current_user.id,
        tons_purchased=data.tons_to_buy,
        total_usd=total_usd,
        platform_fee=platform_fee,
    )
    db.add(transaction)

    remaining = float(listing.tons_available) - data.tons_to_buy
    listing.tons_available = remaining
    if remaining <= 0:
        listing.status = "sold"

    await db.flush()
    return transaction


@router.get("/my/listings", response_model=List[MarketplaceListingOut])
async def my_listings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MarketplaceListing)
        .options(
            joinedload(MarketplaceListing.credit).joinedload(CarbonCredit.field),
        )
        .where(MarketplaceListing.seller_id == current_user.id)
        .order_by(MarketplaceListing.listed_at.desc())
    )
    listings = result.unique().scalars().all()

    out = []
    for listing in listings:
        item = MarketplaceListingOut(
            id=listing.id,
            seller_id=listing.seller_id,
            credit_id=listing.credit_id,
            price_per_ton=float(listing.price_per_ton),
            tons_available=float(listing.tons_available),
            status=listing.status,
            listed_at=listing.listed_at,
            expires_at=listing.expires_at,
            seller_name=current_user.full_name,
            field_name=listing.credit.field.name if listing.credit and listing.credit.field else None,
            methodology=listing.credit.methodology if listing.credit else None,
            vintage_year=listing.credit.vintage_year if listing.credit else None,
        )
        out.append(item)
    return out


@router.get("/my/transactions", response_model=List[MarketplaceTransactionOut])
async def my_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MarketplaceTransaction)
        .where(MarketplaceTransaction.buyer_id == current_user.id)
        .order_by(MarketplaceTransaction.transaction_at.desc())
    )
    return result.scalars().all()
