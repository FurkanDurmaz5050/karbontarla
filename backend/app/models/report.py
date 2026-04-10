from typing import Optional
"""MRV rapor modeli."""

import uuid
from datetime import datetime, date
from sqlalchemy import String, Date, DateTime, ForeignKey, LargeBinary, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, UUID


class MRVReport(Base):
    __tablename__ = "mrv_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id")
    )
    credit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("carbon_credits.id")
    )
    report_type: Mapped[str] = mapped_column(String(50), default="monitoring")
    period_start: Mapped[Optional[date]] = mapped_column(Date)
    period_end: Mapped[Optional[date]] = mapped_column(Date)
    pdf_path: Mapped[Optional[str]] = mapped_column(String(500))
    pdf_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    generated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    field = relationship("Field", back_populates="reports")
    credit = relationship("CarbonCredit", back_populates="reports")
    generated_by_user = relationship("User", back_populates="reports")
