"""
Land price analysis and projection module for Indian cities.

Models land price growth using CAGR-based projections with adjustments
for infrastructure development, population pressure, and climate risk.
"""

import pandas as pd
import numpy as np
from typing import List
from src.models import CityProfile


def project_land_price(current_price: float, cagr: float,
                       years: int, adjustment_factor: float = 1.0) -> float:
    """
    Project future land price using CAGR with adjustment.

    Args:
        current_price: current price per sqft (INR)
        cagr: compound annual growth rate (as %)
        years: number of years to project
        adjustment_factor: multiplier for risk/opportunity adjustment
    """
    rate = (cagr / 100) * adjustment_factor
    return round(current_price * ((1 + rate) ** years), 2)


def compute_cagr(start_price: float, end_price: float, years: int) -> float:
    """Compute CAGR between two price points."""
    if start_price <= 0 or years <= 0:
        return 0.0
    return round(((end_price / start_price) ** (1 / years) - 1) * 100, 2)


def land_investment_score(city: CityProfile) -> float:
    """
    Compute a land investment attractiveness score (0-100, higher is better).

    Factors:
    - Historical price growth (CAGR)
    - Current affordability (inverse of current price)
    - Infrastructure development potential
    - Population growth driving demand
    - Climate risk (negative factor)
    """
    score = 0

    # Historical growth momentum (max 25 points)
    cagr = city.land_price.cagr_2015_2025
    if cagr >= 12:
        score += 25
    elif cagr >= 8:
        score += 20
    elif cagr >= 5:
        score += 15
    else:
        score += 8

    # Affordability bonus - cheaper cities have more upside (max 20 points)
    price = city.land_price.avg_price_per_sqft_2025
    if price < 3000:
        score += 20
    elif price < 5000:
        score += 16
    elif price < 8000:
        score += 10
    elif price < 12000:
        score += 5
    else:
        score += 2

    # Infrastructure potential (max 20 points)
    infra = city.infrastructure
    infra_score = 0
    if infra.metro_rail:
        infra_score += 5
    if infra.airport_international:
        infra_score += 5
    if infra.it_hub:
        infra_score += 5
    infra_score += infra.transport_score * 0.5
    score += min(20, infra_score)

    # Population growth demand pressure (max 20 points)
    pop_growth = city.population.growth_rate_pct
    if pop_growth >= 3:
        score += 20
    elif pop_growth >= 2:
        score += 16
    elif pop_growth >= 1:
        score += 10
    else:
        score += 5

    # Climate risk discount (max -15 points)
    from src.climate_analysis import climate_risk_score
    risk = climate_risk_score(city)
    if risk > 70:
        score -= 15
    elif risk > 50:
        score -= 10
    elif risk > 30:
        score -= 5

    return round(max(0, min(100, score)), 1)


def generate_price_timeline(city: CityProfile) -> pd.DataFrame:
    """Generate a year-by-year price projection for a single city."""
    years = list(range(2015, 2071))
    prices = []
    base_price = city.land_price.avg_price_per_sqft_2015
    cagr = city.land_price.cagr_2015_2025

    for year in years:
        if year <= 2015:
            prices.append(city.land_price.avg_price_per_sqft_2015)
        elif year <= 2020:
            prices.append(project_land_price(base_price, cagr, year - 2015))
        elif year <= 2025:
            prices.append(project_land_price(base_price, cagr, year - 2015))
        elif year <= 2035:
            # slight slowdown in tier-1, acceleration in tier-2/3
            factor = 0.9 if city.tier == 1 else 1.1
            prices.append(project_land_price(
                city.land_price.avg_price_per_sqft_2025, cagr, year - 2025, factor))
        elif year <= 2050:
            factor = 0.8 if city.tier == 1 else 1.05
            prices.append(project_land_price(
                city.land_price.avg_price_per_sqft_2025, cagr, year - 2025, factor))
        else:
            factor = 0.7 if city.tier == 1 else 1.0
            prices.append(project_land_price(
                city.land_price.avg_price_per_sqft_2025, cagr, year - 2025, factor))

    return pd.DataFrame({"Year": years, "Price_per_sqft_INR": prices, "City": city.name})


def generate_land_report(cities: List[CityProfile]) -> pd.DataFrame:
    """Generate comparative land price analysis."""
    rows = []
    for city in cities:
        inv_score = land_investment_score(city)
        roi_2050 = round(
            ((city.land_price.projected_price_2050 - city.land_price.avg_price_per_sqft_2025)
             / city.land_price.avg_price_per_sqft_2025) * 100, 1)
        roi_2070 = round(
            ((city.land_price.projected_price_2070 - city.land_price.avg_price_per_sqft_2025)
             / city.land_price.avg_price_per_sqft_2025) * 100, 1)

        rows.append({
            "City": city.name,
            "State": city.state,
            "Tier": city.tier,
            "Price 2015 (₹/sqft)": city.land_price.avg_price_per_sqft_2015,
            "Price 2020 (₹/sqft)": city.land_price.avg_price_per_sqft_2020,
            "Price 2025 (₹/sqft)": city.land_price.avg_price_per_sqft_2025,
            "CAGR 2015-25 (%)": city.land_price.cagr_2015_2025,
            "Projected 2030 (₹/sqft)": city.land_price.projected_price_2030,
            "Projected 2050 (₹/sqft)": city.land_price.projected_price_2050,
            "Projected 2070 (₹/sqft)": city.land_price.projected_price_2070,
            "ROI by 2050 (%)": roi_2050,
            "ROI by 2070 (%)": roi_2070,
            "Investment Score": inv_score,
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Investment Score", ascending=False)
    return df


def monte_carlo_price_simulation(city: CityProfile, n_simulations: int = 1000,
                                 seed: int = 42) -> pd.DataFrame:
    """
    Run Monte Carlo simulation for land price projection with uncertainty bands.

    Varies CAGR using a normal distribution centered on historical CAGR
    with standard deviation proportional to tier volatility.

    Returns DataFrame with Year, P10, P25, P50 (median), P75, P90, Mean columns.
    """
    rng = np.random.default_rng(seed)
    base_cagr = city.land_price.cagr_2015_2025
    base_price = city.land_price.avg_price_per_sqft_2025

    # Higher-tier cities have lower volatility
    volatility = {1: 0.20, 2: 0.30, 3: 0.40}
    cagr_std = base_cagr * volatility.get(city.tier, 0.25)

    years = list(range(2025, 2071))
    # Each simulation: sample a CAGR per year (random walk on growth rate)
    all_paths = np.zeros((n_simulations, len(years)))
    all_paths[:, 0] = base_price

    for sim in range(n_simulations):
        price = base_price
        for i, year in enumerate(years[1:], 1):
            # Annual CAGR varies around base with mean-reversion
            annual_cagr = rng.normal(base_cagr, cagr_std)
            annual_cagr = max(0, annual_cagr)  # price can't have negative growth below 0
            price = price * (1 + annual_cagr / 100)
            all_paths[sim, i] = price

    # Compute percentiles across simulations
    results = pd.DataFrame({
        "Year": years,
        "P10": np.percentile(all_paths, 10, axis=0).astype(int),
        "P25": np.percentile(all_paths, 25, axis=0).astype(int),
        "P50": np.percentile(all_paths, 50, axis=0).astype(int),
        "P75": np.percentile(all_paths, 75, axis=0).astype(int),
        "P90": np.percentile(all_paths, 90, axis=0).astype(int),
        "Mean": np.mean(all_paths, axis=0).astype(int),
        "City": city.name,
    })
    return results
