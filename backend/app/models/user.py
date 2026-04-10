from typing import Optional
"""Kullanıcı modeli."""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, UUID


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(
        String(50), nullable=False, default="FARMER"
    )
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    farmer_profile = relationship("FarmerProfile", back_populates="user", uselist=False)
    listings = relationship("MarketplaceListing", back_populates="seller")
    purchases = relationship("MarketplaceTransaction", back_populates="buyer")
    reports = relationship("MRVReport", back_populates="generated_by_user")
