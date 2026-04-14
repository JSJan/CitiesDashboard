"""
Population analysis and projection module for Indian cities.

Models population growth using logistic growth curves with carrying capacity
adjustments for urbanization, migration, and infrastructure limits.
"""

import pandas as pd
import numpy as np
from typing import List
from src.models import CityProfile


def logistic_population(current_pop: int, growth_rate: float,
                        carrying_capacity: int, years: int) -> int:
    """
    Project population using logistic growth model.
    Accounts for saturation as cities approach carrying capacity.
    """
    r = growth_rate / 100
    K = carrying_capacity
    P0 = current_pop
    # Logistic: P(t) = K / (1 + ((K - P0) / P0) * e^(-r*t))
    if P0 >= K:
        return K
    exponent = -r * years
    denominator = 1 + ((K - P0) / P0) * np.exp(exponent)
    return int(K / denominator)


def estimate_carrying_capacity(city: CityProfile) -> int:
    """
    Estimate the urban carrying capacity based on infrastructure,
    water supply, and geographic constraints.
    """
    base = city.population.population_2025
    # Tier-1 metro cities can grow 2-3x, tier-2 can grow 3-5x, tier-3 can grow 5-8x
    multipliers = {1: 2.5, 2: 4.0, 3: 6.0}
    multiplier = multipliers.get(city.tier, 3.0)

    # Water supply limits growth
    water_factor = city.infrastructure.water_supply_score / 10
    # Green cover sustains growth
    green_factor = min(1.5, 1 + city.infrastructure.green_cover_pct / 50)

    capacity = int(base * multiplier * water_factor * green_factor)
    return max(capacity, base)  # can't be less than current


def population_density_projection(city: CityProfile, year: int) -> int:
    """Project population density for a given year."""
    pop = logistic_population(
        city.population.population_2025,
        city.population.growth_rate_pct,
        estimate_carrying_capacity(city),
        year - 2025
    )
    # Assuming city area grows at 0.5% per year (urban sprawl)
    area_growth = (1.005) ** (year - 2025)
    current_area = city.population.population_2025 / city.population.density_per_sqkm
    future_area = current_area * area_growth
    return int(pop / future_area)


def generate_population_timeline(city: CityProfile) -> pd.DataFrame:
    """Generate year-by-year population projection for a single city."""
    years = list(range(2011, 2071))
    populations = []
    carrying_cap = estimate_carrying_capacity(city)

    for year in years:
        if year <= 2011:
            populations.append(city.population.population_2011)
        elif year <= 2020:
            # linear interpolation between 2011 and 2020
            frac = (year - 2011) / (2020 - 2011)
            pop = int(city.population.population_2011 +
                      frac * (city.population.population_2020 - city.population.population_2011))
            populations.append(pop)
        elif year <= 2025:
            frac = (year - 2020) / (2025 - 2020)
            pop = int(city.population.population_2020 +
                      frac * (city.population.population_2025 - city.population.population_2020))
            populations.append(pop)
        else:
            pop = logistic_population(
                city.population.population_2025,
                city.population.growth_rate_pct,
                carrying_cap,
                year - 2025
            )
            populations.append(pop)

    return pd.DataFrame({
        "Year": years,
        "Population": populations,
        "City": city.name
    })


def generate_population_report(cities: List[CityProfile]) -> pd.DataFrame:
    """Generate comparative population analysis."""
    rows = []
    for city in cities:
        carrying_cap = estimate_carrying_capacity(city)
        saturation_pct = round(
            (city.population.population_2025 / carrying_cap) * 100, 1
        )
        growth_2025_to_2050 = round(
            ((city.population.projected_2050 - city.population.population_2025)
             / city.population.population_2025) * 100, 1
        )

        rows.append({
            "City": city.name,
            "State": city.state,
            "Pop 2011 (Census)": f"{city.population.population_2011:,}",
            "Pop 2025 (Est)": f"{city.population.population_2025:,}",
            "Pop 2050 (Proj)": f"{city.population.projected_2050:,}",
            "Pop 2070 (Proj)": f"{city.population.projected_2070:,}",
            "Growth Rate (%/yr)": city.population.growth_rate_pct,
            "Density (per km²)": f"{city.population.density_per_sqkm:,}",
            "Carrying Capacity": f"{carrying_cap:,}",
            "Saturation (%)": saturation_pct,
            "Growth 2025-50 (%)": growth_2025_to_2050,
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Growth Rate (%/yr)", ascending=False)
    return df
