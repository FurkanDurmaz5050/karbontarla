from typing import Optional
"""Çiftçi profil modeli."""

import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, UUID


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    tc_kimlik_hash: Mapped[Optional[str]] = mapped_column(String(255))
    tarim_id: Mapped[Optional[str]] = mapped_column(String(50))
    il: Mapped[Optional[str]] = mapped_column(String(100))
    ilce: Mapped[Optional[str]] = mapped_column(String(100))
    toplam_arazi_ha: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="farmer_profile")
    fields = relationship("Field", back_populates="farmer", cascade="all, delete-orphan")
