from __future__ import annotations

"""NDVI hesaplama servisi."""

import math
import random


class NDVICalculator:
    """NDVI ve ilişkili indekslerin hesaplanması."""

    @staticmethod
    def calculate_ndvi(red: float, nir: float) -> float:
        """Tekil piksel NDVI hesapla."""
        if (nir + red) == 0:
            return 0.0
        return (nir - red) / (nir + red)

    @staticmethod
    def calculate_ndmi(nir: float, swir: float) -> float:
        """Nem indeksi hesapla."""
        if (nir + swir) == 0:
            return 0.0
        return (nir - swir) / (nir + swir)

    @staticmethod
    def ndvi_health_category(ndvi: float) -> str:
        """NDVI değerinden sağlık kategorisi belirle."""
        if ndvi >= 0.6:
            return "Sağlıklı"
        elif ndvi >= 0.4:
            return "Orta"
        elif ndvi >= 0.2:
            return "Stres Altında"
        else:
            return "Çıplak Toprak / Kritik"

    @staticmethod
    def ndvi_to_soc_estimate(ndvi_mean: float, area_ha: float) -> float:
        """NDVI'dan SOC (toprak organik karbon) tahmini.
        
        Formül: SOC_ton = NDVI_mean * area_ha * 3.67 * correction_factor
        correction_factor = 0.47 (IPCC Tier 1)
        """
        correction_factor = 0.47
        soc_ton = ndvi_mean * area_ha * 3.67 * correction_factor
        return round(soc_ton, 4)

    @staticmethod
    def calculate_trend(values: list[float]) -> float:
        """Basit lineer trend hesapla (artış/azalış per index)."""
        n = len(values)
        if n < 2:
            return 0.0
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        if denominator == 0:
            return 0.0
        return numerator / denominator

    @staticmethod
    def generate_ndvi_colormap(ndvi: float) -> tuple[int, int, int]:
        """NDVI → RGB renk dönüşümü.
        
        Kırmızı (düşük) → Sarı (orta) → Yeşil (yüksek)
        """
        ndvi = max(0, min(1, ndvi))
        if ndvi < 0.5:
            r = 255
            g = int(255 * (ndvi / 0.5))
            b = 0
        else:
            r = int(255 * (1 - (ndvi - 0.5) / 0.5))
            g = 255
            b = 0
        return (r, g, b)
