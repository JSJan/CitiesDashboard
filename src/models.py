"""
Data models for Indian cities - core data structures used across all modules.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GeographicalProfile:
    latitude: float
    longitude: float
    elevation_m: float  # meters above sea level
    coastal: bool
    river_proximity: bool
    seismic_zone: int  # 1 (low) to 5 (high risk)
    flood_risk: str  # "low", "medium", "high"
    terrain_type: str  # "plain", "plateau", "hilly", "coastal", "delta"


@dataclass
class ClimateData:
    avg_temp_c: float  # current annual average temp (°C)
    avg_rainfall_mm: float  # annual rainfall (mm)
    humidity_pct: float  # avg humidity %
    air_quality_index: float  # current AQI (lower is better)
    extreme_heat_days: int  # days above 40°C per year
    cyclone_risk: str  # "none", "low", "medium", "high"
    projected_temp_rise_2050: float  # °C above current
    projected_temp_rise_2070: float  # °C above current
    projected_rainfall_change_2050_pct: float  # % change
    projected_rainfall_change_2070_pct: float  # % change
    projected_aqi_2050: float
    projected_aqi_2070: float


@dataclass
class LandPriceData:
    avg_price_per_sqft_2015: float  # INR
    avg_price_per_sqft_2020: float
    avg_price_per_sqft_2025: float
    cagr_2015_2025: float  # compound annual growth rate %
    projected_price_2030: float
    projected_price_2040: float
    projected_price_2050: float
    projected_price_2070: float


@dataclass
class PopulationData:
    population_2011: int  # census
    population_2020: int  # estimated
    population_2025: int  # estimated
    growth_rate_pct: float  # annual %
    projected_2030: int
    projected_2040: int
    projected_2050: int
    projected_2070: int
    density_per_sqkm: int


@dataclass
class InfrastructureScore:
    metro_rail: bool
    airport_international: bool
    it_hub: bool
    healthcare_score: float  # 1-10
    education_score: float  # 1-10
    transport_score: float  # 1-10
    water_supply_score: float  # 1-10
    green_cover_pct: float  # % of area


@dataclass
class CityProfile:
    name: str
    state: str
    tier: int  # 1, 2, or 3
    geo: GeographicalProfile
    climate: ClimateData
    land_price: LandPriceData
    population: PopulationData
    infrastructure: InfrastructureScore
    liveability_score: Optional[float] = None  # computed
    sustainability_score: Optional[float] = None  # computed
    investment_score: Optional[float] = None  # computed
