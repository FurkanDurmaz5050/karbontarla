from typing import Optional
"""Tarla modeli — GeoJSON geometri desteği."""

import uuid
from datetime import datetime, date
from sqlalchemy import String, Text, Numeric, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, UUID


class Field(Base):
    __tablename__ = "fields"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    farmer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farmer_profiles.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    geometry: Mapped[str] = mapped_column(Text, nullable=False)
    area_ha: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    soil_type: Mapped[Optional[str]] = mapped_column(String(100))
    current_practice: Mapped[Optional[str]] = mapped_column(String(100))
    organic_input_level: Mapped[str] = mapped_column(String(50), default="medium")
    enrolled_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    farmer = relationship("FarmerProfile", back_populates="fields")
    carbon_credits = relationship("CarbonCredit", back_populates="field", cascade="all, delete-orphan")
    sensors = relationship("Sensor", back_populates="field", cascade="all, delete-orphan")
    reports = relationship("MRVReport", back_populates="field")
