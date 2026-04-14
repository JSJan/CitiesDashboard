"""
Area and zone-level data model for intra-city analysis.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AreaLandPrice:
    price_per_sqft_2015: float
    price_per_sqft_2020: float
    price_per_sqft_2025: float
    cagr_2015_2025: float
    projected_2030: float
    projected_2040: float
    projected_2050: float
    projected_2070: float


@dataclass
class AreaProfile:
    name: str
    zone: str  # e.g. "North", "South", "Central", "West"
    city: str
    area_type: str  # "residential", "commercial", "mixed", "industrial", "it_corridor"
    distance_from_center_km: float
    metro_connectivity: bool
    railway_station: bool
    it_park_proximity: bool
    hospital_proximity: bool  # major hospital within 5 km
    coastal_proximity: bool
    flood_prone: bool
    green_cover_pct: float
    current_aqi: float
    water_supply_score: float  # 1-10
    land_price: AreaLandPrice
    population_density_per_sqkm: int
    investment_score: Optional[float] = None
    liveability_score: Optional[float] = None
