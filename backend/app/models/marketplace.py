from typing import Optional
"""Marketplace modelleri — listeleme ve işlem."""

import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, UUID


class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    credit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("carbon_credits.id")
    )
    price_per_ton: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    tons_available: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active")
    listed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    seller = relationship("User", back_populates="listings")
    credit = relationship("CarbonCredit", back_populates="listing")
    transactions = relationship("MarketplaceTransaction", back_populates="listing")


class MarketplaceTransaction(Base):
    __tablename__ = "marketplace_transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("marketplace_listings.id")
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    tons_purchased: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    total_usd: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    platform_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    transaction_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    blockchain_tx: Mapped[Optional[str]] = mapped_column(String(255))

    listing = relationship("MarketplaceListing", back_populates="transactions")
    buyer = relationship("User", back_populates="purchases")
