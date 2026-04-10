from __future__ import annotations

"""Demo veri seed router — sensör, okuma ve karbon verileri oluşturur."""

import random
import uuid
import math
from datetime import datetime, timedelta, timezone, date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.farmer import FarmerProfile
from app.models.field import Field
from app.models.sensor import Sensor, SensorReading
from app.models.carbon_credit import CarbonCredit
from app.models.marketplace import MarketplaceListing, MarketplaceTransaction
from app.routers.auth import get_current_user
from app.services.carbon_engine import CarbonEngine

router = APIRouter()


@router.post("/sensors")
async def seed_sensor_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Her tarla için sensör ve 90 günlük okuma verisi oluşturur."""

    # Kullanıcının tarlalarını bul
    profile_result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        return {"message": "Profil bulunamadı, önce tarla ekleyin"}

    fields_result = await db.execute(
        select(Field).where(Field.farmer_id == profile.id)
    )
    fields = fields_result.scalars().all()
    if not fields:
        return {"message": "Tarla bulunamadı, önce tarla ekleyin"}

    sensors_created = 0
    readings_created = 0

    for field in fields:
        # Her tarla için 2 sensör oluştur
        existing = await db.execute(
            select(func.count(Sensor.id)).where(Sensor.sensor_external_id.like(f"KT-SNS-{str(field.id)[:8]}%"))
        )
        if existing.scalar() > 0:
            continue

        import json
        geo = json.loads(field.geometry) if isinstance(field.geometry, str) else field.geometry
        coords = geo.get("coordinates", [[[32.45, 37.87]]])[0]
        center_lat = sum(c[1] for c in coords) / len(coords)
        center_lon = sum(c[0] for c in coords) / len(coords)

        sensor_configs = [
            {
                "name": f"{field.name} — Toprak Sensörü A",
                "offset_lat": 0.002,
                "offset_lon": 0.001,
            },
            {
                "name": f"{field.name} — Toprak Sensörü B",
                "offset_lat": -0.001,
                "offset_lon": 0.002,
            },
        ]

        for i, cfg in enumerate(sensor_configs):
            sensor = Sensor(
                field_id=field.id,
                sensor_external_id=f"KT-SNS-{str(field.id)[:8]}-{i+1:02d}",
                sensor_type="soil_multi",
                name=cfg["name"],
                latitude=center_lat + cfg["offset_lat"],
                longitude=center_lon + cfg["offset_lon"],
                status="active",
            )
            db.add(sensor)
            await db.flush()
            sensors_created += 1

            # 90 günlük okuma verisi — saatte 1
            now = datetime.now(timezone.utc)
            readings_count = 90 * 24  # 90 gün × 24 saat

            # Temel parametreler (toprak tipine göre)
            base_moisture = {"Killi": 42, "Kumlu": 28, "Balçıklı": 38, "Tınlı": 35, "Organik": 48}.get(field.soil_type or "", 35)
            base_temp = 16.0
            base_ph = {"Killi": 7.2, "Kumlu": 6.5, "Balçıklı": 6.8, "Tınlı": 6.9, "Organik": 5.8}.get(field.soil_type or "", 6.8)
            base_om = {"Killi": 3.2, "Kumlu": 1.8, "Balçıklı": 4.1, "Tınlı": 3.5, "Organik": 8.5}.get(field.soil_type or "", 3.5)
            base_co2 = {"no_till": 3.8, "reduced_till": 4.5, "conventional": 5.2, "cover_crop": 3.2, "composting": 4.0}.get(field.current_practice or "", 4.0)

            batch = []
            for h in range(0, readings_count, 4):  # Her 4 saatte 1 kayıt = 6/gün
                ts = now - timedelta(hours=h)
                day_of_year = ts.timetuple().tm_yday
                hour = ts.hour

                # Mevsimsel ve günlük döngüler
                seasonal = math.sin(2 * math.pi * (day_of_year - 80) / 365)
                diurnal = math.sin(2 * math.pi * (hour - 6) / 24)

                moisture = base_moisture + seasonal * 8 - diurnal * 3 + random.gauss(0, 2.5)
                temp = base_temp + seasonal * 12 + diurnal * 4 + random.gauss(0, 1.0)
                ph = base_ph + random.gauss(0, 0.15)
                om = base_om + seasonal * 0.3 + random.gauss(0, 0.1)
                co2 = base_co2 + seasonal * 1.5 + diurnal * 0.8 + random.gauss(0, 0.5)
                battery = max(10, 100 - (h / readings_count) * 30 + random.gauss(0, 2))
                signal = max(40, min(100, 85 + random.randint(-15, 10)))

                reading = SensorReading(
                    sensor_id=sensor.id,
                    field_id=field.id,
                    timestamp=ts,
                    soil_moisture=round(max(5, min(95, moisture)), 2),
                    soil_temp_c=round(max(-5, min(45, temp)), 2),
                    soil_ph=round(max(4.0, min(9.0, ph)), 2),
                    organic_matter=round(max(0.5, min(15, om)), 3),
                    co2_flux=round(max(0.1, co2), 4),
                    battery_pct=round(max(5, min(100, battery)), 2),
                    signal_quality=int(signal),
                )
                batch.append(reading)
                readings_created += 1

            db.add_all(batch)

    await db.flush()
    return {
        "message": f"Demo verisi oluşturuldu",
        "sensors_created": sensors_created,
        "readings_created": readings_created,
    }


@router.post("/carbon")
async def seed_carbon_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Her tarla için karbon kredisi hesaplar ve kaydeder."""

    profile_result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        return {"message": "Profil bulunamadı"}

    fields_result = await db.execute(
        select(Field).where(Field.farmer_id == profile.id)
    )
    fields = fields_result.scalars().all()

    engine = CarbonEngine()
    credits_created = 0

    for field in fields:
        # Son 2 yıl için kredi oluştur
        for year in [2025, 2026]:
            existing = await db.execute(
                select(CarbonCredit).where(
                    CarbonCredit.field_id == field.id,
                    CarbonCredit.vintage_year == year,
                )
            )
            if existing.scalar_one_or_none():
                continue

            result = engine.calculate_annual_credits(
                area_ha=float(field.area_ha),
                soil_type=field.soil_type or "Balçıklı",
                current_practice=field.current_practice or "no_till",
                organic_input_level=field.organic_input_level or "medium",
                year=year,
            )

            credit = CarbonCredit(
                field_id=field.id,
                period_start=date(year, 1, 1),
                period_end=date(year, 12, 31),
                vintage_year=year,
                baseline_soc=result.baseline_soc,
                calculated_soc=result.project_soc,
                delta_co2_tons=result.delta_co2_tons,
                credit_tons=result.credit_tons,
                tradeable_tons=result.tradeable_tons,
                ndvi_correction=result.ndvi_correction,
                methodology="VM0042",
                verification_status="verified" if year == 2025 else "pending",
                verra_serial=f"VCS-{year}-TR-{uuid.uuid4().hex[:6].upper()}" if year == 2025 else None,
                price_usd=25.0,
            )
            db.add(credit)
            credits_created += 1

    await db.flush()
    return {
        "message": f"Karbon kredileri oluşturuldu",
        "credits_created": credits_created,
    }


@router.post("/all")
async def seed_all_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Tüm demo verilerini tek seferde oluşturur."""
    result_sensors = await seed_sensor_data(current_user=current_user, db=db)
    result_carbon = await seed_carbon_data(current_user=current_user, db=db)
    result_marketplace = await seed_marketplace_data(current_user=current_user, db=db)
    return {
        "message": "Tüm demo verileri oluşturuldu",
        "sensors": result_sensors,
        "carbon": result_carbon,
        "marketplace": result_marketplace,
    }


@router.post("/marketplace")
async def seed_marketplace_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pazar yerine örnek listeleme ve işlem verileri oluşturur."""

    # Mevcut listelemeleri kontrol et
    existing = await db.execute(select(func.count(MarketplaceListing.id)))
    if existing.scalar() > 0:
        return {"message": "Pazar verileri zaten mevcut", "listings_created": 0, "transactions_created": 0}

    # Demo alıcı kullanıcılar oluştur
    from app.routers.auth import hash_password

    buyer_configs = [
        {"email": "alici1@karbontarla.com", "full_name": "Mehmet Yılmaz", "company": "EkoEnerji A.Ş."},
        {"email": "alici2@karbontarla.com", "full_name": "Zeynep Kara", "company": "YeşilGelecek Ltd."},
        {"email": "alici3@karbontarla.com", "full_name": "Ali Demir", "company": "KarbonOfset Danışmanlık"},
    ]

    buyer_ids = []
    for cfg in buyer_configs:
        existing_user = await db.execute(select(User).where(User.email == cfg["email"]))
        user = existing_user.scalar_one_or_none()
        if not user:
            user = User(
                email=cfg["email"],
                password_hash=hash_password("Buyer1234!"),
                full_name=cfg["full_name"],
            )
            db.add(user)
            await db.flush()
        buyer_ids.append(user.id)

    # Verified/pending karbon kredilerini al
    credits_result = await db.execute(
        select(CarbonCredit).where(CarbonCredit.verification_status == "verified")
    )
    credits = credits_result.scalars().all()

    if not credits:
        return {"message": "Verified karbon kredisi bulunamadı — önce /seed/carbon çalıştırın"}

    listings_created = 0
    transactions_created = 0

    # Her kredi için bir listeleme oluştur
    listing_prices = [22.50, 25.00, 28.75, 30.00, 18.50]
    now = datetime.now(timezone.utc)

    for idx, credit in enumerate(credits):
        price = listing_prices[idx % len(listing_prices)]
        tons = float(credit.tradeable_tons) * 0.8  # %80'ini listele

        listing = MarketplaceListing(
            seller_id=current_user.id,
            credit_id=credit.id,
            price_per_ton=price,
            tons_available=round(tons, 4),
            status="active",
            listed_at=now - timedelta(days=random.randint(1, 30)),
        )
        db.add(listing)
        await db.flush()
        listings_created += 1

        # Her listeleme için 1-2 geçmiş işlem oluştur
        num_transactions = random.randint(1, 2)
        remaining = tons
        for t in range(num_transactions):
            if remaining <= 0.01:
                break
            buy_tons = round(remaining * random.uniform(0.2, 0.5), 4)
            if buy_tons < 0.01:
                break
            total = round(buy_tons * price, 2)
            fee = round(total * 0.035, 2)

            buyer_id = buyer_ids[t % len(buyer_ids)]
            tx = MarketplaceTransaction(
                listing_id=listing.id,
                buyer_id=buyer_id,
                tons_purchased=buy_tons,
                total_usd=total,
                platform_fee=fee,
                transaction_at=now - timedelta(days=random.randint(0, 15)),
                blockchain_tx=f"0x{uuid.uuid4().hex[:40]}",
            )
            db.add(tx)
            remaining -= buy_tons
            transactions_created += 1

        # Kalan miktarı güncelle
        listing.tons_available = round(remaining, 4)
        if remaining <= 0.01:
            listing.status = "sold"

    # Ek: Farklı fiyatlarda birkaç bağımsız listeleme
    extra_listings = [
        {"price": 15.00, "tons": 5.5, "status": "active"},
        {"price": 35.00, "tons": 2.0, "status": "active"},
        {"price": 20.00, "tons": 0.0, "status": "sold"},
    ]
    if credits:
        for el in extra_listings:
            listing = MarketplaceListing(
                seller_id=buyer_ids[0],  # Alıcılardan biri de satıyor
                credit_id=credits[0].id,
                price_per_ton=el["price"],
                tons_available=el["tons"],
                status=el["status"],
                listed_at=now - timedelta(days=random.randint(5, 45)),
            )
            db.add(listing)
            listings_created += 1

    await db.flush()
    return {
        "message": "Pazar verileri oluşturuldu",
        "listings_created": listings_created,
        "transactions_created": transactions_created,
        "buyers_created": len(buyer_ids),
    }
