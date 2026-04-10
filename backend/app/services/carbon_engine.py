from __future__ import annotations

"""Karbon hesaplama motoru — Verra VCS VM0042 metodolojisi."""

import math
import random
from dataclasses import dataclass


@dataclass
class CarbonResult:
    baseline_soc: float
    project_soc: float
    delta_co2_tons: float
    credit_tons: float
    tradeable_tons: float
    ndvi_correction: float
    methodology: str = "VM0042"


class CarbonEngine:
    """Verra VCS VM0042 — Improved Agricultural Land Management hesaplama motoru."""

    # IPCC 2019 Tier 1 toprak referans SOC değerleri (tC/ha)
    # Türkiye iklim bölgesi: Warm Temperate, Dry
    SOC_REF = {
        "Kumlu": 38.0,
        "Balçıklı": 47.5,
        "Killi": 58.0,
        "Organik": 86.0,
        "Tınlı": 52.0,
        # English enum mappings
        "SANDY": 38.0,
        "CLAY_LOAM": 58.0,
        "LOAM": 47.5,
        "SILT_LOAM": 52.0,
        "ORGANIC": 86.0,
    }

    # VM0042 Tablo 1 — FMG: Toprak işleme faktörü
    FMG_FACTORS = {
        "conventional": 1.0,
        "reduced_till": 1.08,
        "no_till": 1.15,
        "min_till": 1.08,
        "cover_crop": 1.11,
        "composting": 1.17,
        # English enum mappings
        "CONVENTIONAL": 1.0,
        "REDUCED_TILLAGE": 1.08,
        "NO_TILL": 1.15,
        "MIN_TILL": 1.08,
        "COVER_CROP": 1.11,
        "COMPOSTING": 1.17,
    }

    # Organik girdi faktörü (FI)
    FI_FACTORS = {
        "low": 0.92,
        "medium": 1.0,
        "high": 1.11,
        "high_with_manure": 1.17,
    }

    IPCC_CO2_C_RATIO = 3.667  # 1 tC → 3.667 tCO₂e
    UNCERTAINTY_BUFFER = 0.85  # %15 belirsizlik kesintisi
    PERMANENCE_BUFFER = 0.90   # %10 kalıcılık tampon havuzu

    def calculate_annual_credits(
        self,
        area_ha: float,
        soil_type: str,
        current_practice: str,
        organic_input_level: str = "medium",
        year: int = 2025,
        historical_ndvi: list[float] | None = None,
    ) -> CarbonResult:
        """Yıllık karbon kredi hesaplaması — VM0042 tam uygulama."""

        # ADIM 1: Temel SOC referans değeri
        soc_ref = self.SOC_REF.get(soil_type, 47.5)

        # ADIM 2: Uygulama faktörleri
        flu = 1.0  # Arazi kullanımı faktörü (tarım = 1.0)
        fmg = self.FMG_FACTORS.get(current_practice, 1.0)
        fi = self.FI_FACTORS.get(organic_input_level, 1.0)

        # ADIM 3: Baseline SOC (konvansiyonel tarım referans senaryosu)
        baseline_soc = soc_ref * flu * 1.0 * 1.0  # FMG=1.0, FI=1.0

        # ADIM 4: Proje SOC (iyileştirilmiş pratikler ile)
        project_soc = soc_ref * flu * fmg * fi

        # ADIM 5: NDVI-SOC düzeltme katsayısı
        if historical_ndvi and len(historical_ndvi) > 0:
            mean_ndvi = sum(historical_ndvi) / len(historical_ndvi)
        else:
            mean_ndvi = self._generate_mock_annual_ndvi(soil_type, current_practice)

        ndvi_correction = 0.82 + (mean_ndvi * 0.35)

        # ADIM 6: Delta SOC (ton C/ha)
        delta_soc = (project_soc - baseline_soc) * ndvi_correction

        # ADIM 7: CO₂ dönüşümü (ton C → ton CO₂e)
        delta_co2 = delta_soc * area_ha * self.IPCC_CO2_C_RATIO

        # ADIM 8: Belirsizlik kesintisi (%15)
        credit_tons = delta_co2 * self.UNCERTAINTY_BUFFER

        # Negatif kredi kontrolü
        if credit_tons < 0:
            credit_tons = 0.0

        # ADIM 9: Kalıcılık tampon havuzu (%10)
        tradeable_tons = credit_tons * self.PERMANENCE_BUFFER

        return CarbonResult(
            baseline_soc=round(baseline_soc, 4),
            project_soc=round(project_soc, 4),
            delta_co2_tons=round(delta_co2, 4),
            credit_tons=round(credit_tons, 4),
            tradeable_tons=round(tradeable_tons, 4),
            ndvi_correction=round(ndvi_correction, 4),
        )

    def _generate_mock_annual_ndvi(self, soil_type: str, practice: str) -> float:
        """Yıllık ortalama mock NDVI üret."""
        base = 0.45
        soil_bonus = {
            "Killi": 0.05, "Kumlu": -0.03, "Balçıklı": 0.08,
            "Organik": 0.12, "Tınlı": 0.06,
            "SANDY": -0.03, "CLAY_LOAM": 0.05, "LOAM": 0.08,
            "SILT_LOAM": 0.06, "ORGANIC": 0.12,
        }.get(soil_type, 0)
        practice_bonus = {
            "no_till": 0.10, "reduced_till": 0.06, "conventional": 0.0,
            "cover_crop": 0.08, "composting": 0.12,
            "NO_TILL": 0.10, "REDUCED_TILLAGE": 0.06, "CONVENTIONAL": 0.0,
            "COVER_CROP": 0.08, "COMPOSTING": 0.12, "MIN_TILL": 0.06,
        }.get(practice, 0)
        return round(base + soil_bonus + practice_bonus + random.gauss(0, 0.02), 4)

    def calculate_total_value(
        self,
        tradeable_tons: float,
        price_per_ton_usd: float = 25.0,
    ) -> dict:
        """Kredi değerini hesapla."""
        total_usd = tradeable_tons * price_per_ton_usd
        platform_fee = total_usd * 0.035  # %3.5 platform komisyonu
        net_revenue = total_usd - platform_fee
        usd_to_try = 38.5  # Yaklaşık USD/TRY kuru
        return {
            "total_usd": round(total_usd, 2),
            "platform_fee_usd": round(platform_fee, 2),
            "net_revenue_usd": round(net_revenue, 2),
            "net_revenue_try": round(net_revenue * usd_to_try, 2),
        }

    def full_calculation_report(
        self,
        area_ha: float,
        soil_type: str,
        current_practice: str,
        organic_input_level: str,
        year: int,
    ) -> dict:
        """Tam hesaplama raporu (PDF için)."""
        result = self.calculate_annual_credits(
            area_ha=area_ha,
            soil_type=soil_type,
            current_practice=current_practice,
            organic_input_level=organic_input_level,
            year=year,
        )
        value = self.calculate_total_value(result.tradeable_tons)

        return {
            "methodology": "Verra VCS VM0042",
            "methodology_name": "Improved Agricultural Land Management (IALM)",
            "year": year,
            "area_ha": area_ha,
            "soil_type": soil_type,
            "practice": current_practice,
            "organic_input_level": organic_input_level,
            "soc_ref": self.SOC_REF.get(soil_type, 47.5),
            "fmg": self.FMG_FACTORS.get(current_practice, 1.0),
            "fi": self.FI_FACTORS.get(organic_input_level, 1.0),
            "baseline_soc": result.baseline_soc,
            "project_soc": result.project_soc,
            "ndvi_correction": result.ndvi_correction,
            "delta_co2_tons": result.delta_co2_tons,
            "uncertainty_buffer": self.UNCERTAINTY_BUFFER,
            "credit_tons": result.credit_tons,
            "permanence_buffer": self.PERMANENCE_BUFFER,
            "tradeable_tons": result.tradeable_tons,
            "value": value,
        }
