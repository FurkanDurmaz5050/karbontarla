from __future__ import annotations

"""Sentinel-2 API servisi — uydu görüntü çekimi ve mock veri üretimi."""

import math
import random
import base64
import struct
from datetime import datetime, timedelta, timezone
from app.schemas.field import NDVIDataPoint


class SentinelAPIService:
    """ESA Copernicus Sentinel-2 API istemcisi.

    Gerçek API anahtarı yoksa mock veri üretir.
    """

    COPERNICUS_SEARCH_URL = "https://dataspace.copernicus.eu/odata/v1/Products"

    def search_images(self, polygon_wkt: str, date_from: str, date_to: str) -> list[dict]:
        """Belirli bir polygon için Sentinel-2 L2A görüntülerini arar."""
        query_url = (
            f"{self.COPERNICUS_SEARCH_URL}?"
            f"$filter=Collection/Name eq 'SENTINEL-2' "
            f"and ContentDate/Start gt {date_from}T00:00:00.000Z "
            f"and ContentDate/Start lt {date_to}T23:59:59.999Z "
            f"and OData.CSC.Intersects(area=geography'SRID=4326;{polygon_wkt}')"
            f"&$orderby=ContentDate/Start desc&$top=10"
        )
        return [{"query_url": query_url, "note": "Mock mode — gerçek API bağlantısı yok"}]

    def calculate_ndvi(self, red_band, nir_band):
        """NDVI = (NIR - RED) / (NIR + RED)"""
        epsilon = 1e-10
        ndvi = (nir_band - red_band) / (nir_band + red_band + epsilon)
        return ndvi

    def calculate_ndmi(self, nir_band, swir_band):
        """NDMI = (NIR - SWIR) / (NIR + SWIR)"""
        epsilon = 1e-10
        ndmi = (nir_band - swir_band) / (nir_band + swir_band + epsilon)
        return ndmi

    def ndvi_to_carbon_proxy(self, ndvi_mean: float, area_ha: float) -> float:
        """NDVI → SOC tahmini (IPCC Tier 1 katsayısı)."""
        correction_factor = 0.47
        soc_ton = ndvi_mean * area_ha * 3.67 * correction_factor
        return round(soc_ton, 4)

    def calculate_mock_ndvi(
        self,
        soil_type: str | None = None,
        practice: str | None = None,
    ) -> float:
        """Gerçekçi mock NDVI değeri üretir."""
        base = 0.42
        soil_bonus = {
            "Killi": 0.05, "Kumlu": -0.03, "Balçıklı": 0.08,
            "Organik": 0.12, "Tınlı": 0.06,
        }
        practice_bonus = {
            "no_till": 0.10, "reduced_till": 0.06, "conventional": 0.0,
            "cover_crop": 0.08, "composting": 0.12,
        }
        base += soil_bonus.get(soil_type or "", 0)
        base += practice_bonus.get(practice or "", 0)

        day_of_year = datetime.now().timetuple().tm_yday
        seasonal = 0.15 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
        base += seasonal

        noise = random.gauss(0, 0.03)
        return round(max(0.05, min(0.95, base + noise)), 4)

    def generate_mock_ndvi_series(
        self,
        start_date: datetime,
        end_date: datetime,
        interval_days: int = 5,
        base_ndvi: float = 0.45,
        soil_type: str | None = None,
        practice: str | None = None,
    ) -> list[NDVIDataPoint]:
        """Mock NDVI zaman serisi üretir (mevsimsel pattern ile)."""
        series = []
        current = start_date
        soil_bonus = {
            "Killi": 0.05, "Kumlu": -0.03, "Balçıklı": 0.08,
            "Organik": 0.12, "Tınlı": 0.06,
        }.get(soil_type or "", 0)
        practice_bonus = {
            "no_till": 0.10, "reduced_till": 0.06, "conventional": 0.0,
            "cover_crop": 0.08, "composting": 0.12,
        }.get(practice or "", 0)
        adjusted_base = base_ndvi + soil_bonus + practice_bonus

        while current <= end_date:
            skip = random.random() < 0.1
            if skip:
                current += timedelta(days=interval_days)
                continue

            day_of_year = current.timetuple().tm_yday
            seasonal = 0.18 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
            noise = random.gauss(0, 0.025)
            ndvi = max(0.05, min(0.95, adjusted_base + seasonal + noise))
            cloud = round(random.uniform(0, 20), 1)

            series.append(NDVIDataPoint(
                date=current.strftime("%Y-%m-%d"),
                ndvi=round(ndvi, 4),
                cloud_cover=cloud,
            ))
            current += timedelta(days=interval_days)

        return series

    def generate_mock_ndvi_geotiff(self) -> str:
        """Mock NDVI GeoTIFF (basit raster) üretir, base64 döner."""
        width, height = 64, 64
        pixels = []
        for y in range(height):
            for x in range(width):
                cx = (x - width / 2) / (width / 2)
                cy = (y - height / 2) / (height / 2)
                dist = math.sqrt(cx**2 + cy**2)
                ndvi = max(0, min(255, int((1 - dist) * 180 + random.randint(-10, 10))))
                r = max(0, min(255, int(255 * (1 - ndvi / 255))))
                g = max(0, min(255, ndvi))
                b = 50
                pixels.extend([r, g, b])

        raw = bytes(pixels)
        return base64.b64encode(raw).decode("ascii")
