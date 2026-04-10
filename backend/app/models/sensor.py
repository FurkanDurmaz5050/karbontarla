from typing import Optional
"""IoT sensör ve okuma modelleri."""

import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, UUID


class Sensor(Base):
    __tablename__ = "sensors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE")
    )
    sensor_external_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    sensor_type: Mapped[str] = mapped_column(String(100), default="soil_multi")
    name: Mapped[Optional[str]] = mapped_column(String(255))
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7))
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    field = relationship("Field", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sensor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sensors.id", ondelete="CASCADE")
    )
    field_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    soil_moisture: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))
    soil_temp_c: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    soil_ph: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    organic_matter: Mapped[Optional[float]] = mapped_column(Numeric(6, 3))
    co2_flux: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))
    battery_pct: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    signal_quality: Mapped[Optional[int]] = mapped_column(Integer)

    sensor = relationship("Sensor", back_populates="readings")
