from typing import Optional
"""Karbon kredi modeli."""

import uuid
from datetime import datetime, date
from sqlalchemy import String, Numeric, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, UUID


class CarbonCredit(Base):
    __tablename__ = "carbon_credits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE")
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    vintage_year: Mapped[Optional[int]] = mapped_column()
    baseline_soc: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))
    calculated_soc: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))
    delta_co2_tons: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))
    credit_tons: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))
    tradeable_tons: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))
    ndvi_correction: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))
    verification_status: Mapped[str] = mapped_column(String(50), default="pending")
    verra_serial: Mapped[Optional[str]] = mapped_column(String(100))
    methodology: Mapped[str] = mapped_column(String(50), default="VM0042")
    price_usd: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    certificate_url: Mapped[Optional[str]] = mapped_column(String(500))
    blockchain_tx: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    field = relationship("Field", back_populates="carbon_credits")
    listing = relationship("MarketplaceListing", back_populates="credit", uselist=False)
    reports = relationship("MRVReport", back_populates="credit")
