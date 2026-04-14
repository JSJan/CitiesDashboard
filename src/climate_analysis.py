"""
Climate change analysis and prediction module for Indian cities.

Uses baseline climate data and IPCC-aligned projection models to estimate
temperature, rainfall, air quality, and extreme weather changes through 2050/2070.
"""

import pandas as pd
import numpy as np
from typing import List
from src.models import CityProfile


# IPCC AR6 warming scenarios for South Asia (RCP 4.5 moderate pathway)
WARMING_RATE_PER_DECADE = 0.25  # °C per decade baseline
URBAN_HEAT_ISLAND_FACTOR = 1.3  # cities warm faster than rural


def compute_temperature_projection(current_temp: float, year: int,
                                    base_year: int = 2025,
                                    urban_factor: float = URBAN_HEAT_ISLAND_FACTOR) -> float:
    """Project temperature for a target year using linear warming model."""
    decades = (year - base_year) / 10
    warming = decades * WARMING_RATE_PER_DECADE * urban_factor
    return round(current_temp + warming, 2)


def compute_rainfall_change_pct(current_rainfall_mm: float, year: int,
                                 base_year: int = 2025,
                                 coastal: bool = False) -> float:
    """
    Project % change in rainfall.
    Coastal cities see more intense but erratic rainfall.
    Inland cities may see reduced overall rainfall.
    """
    decades = (year - base_year) / 10
    if coastal:
        change_per_decade = 3.5  # % increase per decade (more intense monsoons)
    else:
        change_per_decade = -1.5  # % decrease per decade (drying trend)
    return round(decades * change_per_decade, 2)


def compute_aqi_projection(current_aqi: float, year: int,
                            base_year: int = 2025,
                            has_industry: bool = True) -> float:
    """
    Project AQI changes based on urbanization trends.
    Assumes moderate policy interventions.
    """
    decades = (year - base_year) / 10
    if has_industry:
        aqi_change_per_decade = 8  # worsening
    else:
        aqi_change_per_decade = 3
    projected = current_aqi + (decades * aqi_change_per_decade)
    return round(max(20, projected), 1)  # AQI can't go below 20 realistically


def compute_extreme_heat_days(current_days: int, year: int,
                               base_year: int = 2025) -> int:
    """Project number of days above 40°C."""
    decades = (year - base_year) / 10
    increase_per_decade = 5
    return max(0, int(current_days + decades * increase_per_decade))


def climate_risk_score(city: CityProfile) -> float:
    """
    Compute a climate risk score (0-100, lower is better/safer).

    Factors:
    - Temperature rise projection
    - Extreme heat days
    - Flood risk
    - Cyclone risk
    - AQI degradation
    - Rainfall volatility
    """
    score = 0

    # Temperature rise impact (max 25 points)
    temp_rise_2050 = city.climate.projected_temp_rise_2050
    score += min(25, temp_rise_2050 * 10)

    # Extreme heat days (max 20 points)
    heat_days = city.climate.extreme_heat_days
    score += min(20, heat_days * 0.5)

    # Flood risk (max 15 points)
    flood_scores = {"low": 3, "medium": 9, "high": 15}
    score += flood_scores.get(city.geo.flood_risk, 5)

    # Cyclone risk (max 15 points)
    cyclone_scores = {"none": 0, "low": 5, "medium": 10, "high": 15}
    score += cyclone_scores.get(city.climate.cyclone_risk, 5)

    # AQI degradation (max 15 points)
    aqi = city.climate.air_quality_index
    if aqi > 200:
        score += 15
    elif aqi > 150:
        score += 12
    elif aqi > 100:
        score += 8
    else:
        score += 3

    # Rainfall change volatility (max 10 points)
    rainfall_change = abs(city.climate.projected_rainfall_change_2050_pct)
    score += min(10, rainfall_change * 0.5)

    return round(min(100, score), 1)


def generate_climate_report(cities: List[CityProfile]) -> pd.DataFrame:
    """Generate a comparative climate analysis DataFrame."""
    rows = []
    for city in cities:
        risk = climate_risk_score(city)
        rows.append({
            "City": city.name,
            "State": city.state,
            "Current Avg Temp (°C)": city.climate.avg_temp_c,
            "Projected Temp 2050 (°C)": round(city.climate.avg_temp_c + city.climate.projected_temp_rise_2050, 1),
            "Projected Temp 2070 (°C)": round(city.climate.avg_temp_c + city.climate.projected_temp_rise_2070, 1),
            "Current AQI": city.climate.air_quality_index,
            "Projected AQI 2050": city.climate.projected_aqi_2050,
            "Rainfall (mm)": city.climate.avg_rainfall_mm,
            "Rainfall Change 2050 (%)": city.climate.projected_rainfall_change_2050_pct,
            "Extreme Heat Days": city.climate.extreme_heat_days,
            "Flood Risk": city.geo.flood_risk,
            "Cyclone Risk": city.climate.cyclone_risk,
            "Climate Risk Score": risk,
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Climate Risk Score", ascending=True)
    return df
