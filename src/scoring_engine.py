"""
City scoring and rating engine.

Computes composite scores for liveability, sustainability, and investment
potential by combining climate, land price, population, and infrastructure data.
"""

import pandas as pd
from typing import List
from src.models import CityProfile
from src.climate_analysis import climate_risk_score
from src.land_price_analysis import land_investment_score


# --- Weight configurations for scoring ---

LIVEABILITY_WEIGHTS = {
    "climate": 0.20,        # lower climate risk = better
    "infrastructure": 0.25, # healthcare, transport, education
    "air_quality": 0.15,    # current AQI
    "green_cover": 0.10,    # % green area
    "water_supply": 0.10,   # water reliability
    "population_density": 0.10,  # overcrowding penalty
    "flood_cyclone_risk": 0.10,  # natural disaster safety
}

SUSTAINABILITY_WEIGHTS = {
    "climate_resilience": 0.25,   # projected climate stability
    "water_security": 0.20,      # rainfall + water supply
    "green_cover": 0.15,         # environmental health
    "population_pressure": 0.15, # saturation level
    "air_quality_trend": 0.15,   # AQI trajectory
    "food_security": 0.10,       # terrain + agriculture potential
}


def compute_liveability_score(city: CityProfile) -> float:
    """
    Rate city liveability (0-100, higher is better).

    Combines infrastructure quality, environmental conditions,
    and quality-of-life indicators.
    """
    scores = {}

    # Climate comfort (invert risk score)
    risk = climate_risk_score(city)
    scores["climate"] = max(0, 100 - risk)

    # Infrastructure composite
    infra = city.infrastructure
    infra_avg = (
        infra.healthcare_score + infra.education_score +
        infra.transport_score + infra.water_supply_score
    ) / 4 * 10  # scale 1-10 to 0-100
    scores["infrastructure"] = infra_avg

    # Air quality (AQI below 50 is excellent, above 200 is hazardous)
    aqi = city.climate.air_quality_index
    if aqi <= 50:
        scores["air_quality"] = 100
    elif aqi <= 100:
        scores["air_quality"] = 80
    elif aqi <= 150:
        scores["air_quality"] = 50
    elif aqi <= 200:
        scores["air_quality"] = 25
    else:
        scores["air_quality"] = 10

    # Green cover
    scores["green_cover"] = min(100, city.infrastructure.green_cover_pct * 3)

    # Water supply
    scores["water_supply"] = city.infrastructure.water_supply_score * 10

    # Population density penalty (>10000/km² is congested)
    density = city.population.density_per_sqkm
    if density < 3000:
        scores["population_density"] = 90
    elif density < 6000:
        scores["population_density"] = 70
    elif density < 10000:
        scores["population_density"] = 50
    elif density < 20000:
        scores["population_density"] = 30
    else:
        scores["population_density"] = 10

    # Flood and cyclone safety
    flood_map = {"low": 90, "medium": 50, "high": 15}
    cyclone_map = {"none": 100, "low": 75, "medium": 45, "high": 15}
    flood_s = flood_map.get(city.geo.flood_risk, 50)
    cyclone_s = cyclone_map.get(city.climate.cyclone_risk, 50)
    scores["flood_cyclone_risk"] = (flood_s + cyclone_s) / 2

    # Weighted total
    total = sum(
        scores[k] * LIVEABILITY_WEIGHTS[k]
        for k in LIVEABILITY_WEIGHTS
    )
    return round(total, 1)


def compute_sustainability_score(city: CityProfile) -> float:
    """
    Rate city sustainability for long-term viability (0-100, higher is better).

    Focuses on how well the city can sustain its population and
    environment through 2050-2070.
    """
    scores = {}

    # Climate resilience (invert projected warming severity)
    temp_rise_2050 = city.climate.projected_temp_rise_2050
    if temp_rise_2050 < 1.0:
        scores["climate_resilience"] = 90
    elif temp_rise_2050 < 1.5:
        scores["climate_resilience"] = 70
    elif temp_rise_2050 < 2.0:
        scores["climate_resilience"] = 50
    else:
        scores["climate_resilience"] = 25

    # Water security
    rainfall = city.climate.avg_rainfall_mm
    water = city.infrastructure.water_supply_score
    rainfall_score = min(100, rainfall / 15)  # 1500mm = 100
    scores["water_security"] = (rainfall_score + water * 10) / 2

    # Green cover
    scores["green_cover"] = min(100, city.infrastructure.green_cover_pct * 3)

    # Population pressure (how close to carrying capacity)
    from src.population_analysis import estimate_carrying_capacity
    cap = estimate_carrying_capacity(city)
    saturation = city.population.population_2025 / cap
    if saturation < 0.3:
        scores["population_pressure"] = 95
    elif saturation < 0.5:
        scores["population_pressure"] = 75
    elif saturation < 0.7:
        scores["population_pressure"] = 50
    else:
        scores["population_pressure"] = 25

    # Air quality trend
    current_aqi = city.climate.air_quality_index
    future_aqi = city.climate.projected_aqi_2050
    degradation = future_aqi - current_aqi
    if degradation < 10:
        scores["air_quality_trend"] = 80
    elif degradation < 25:
        scores["air_quality_trend"] = 55
    else:
        scores["air_quality_trend"] = 25

    # Food security (terrain suitability)
    terrain_scores = {
        "plain": 85, "delta": 80, "plateau": 60,
        "coastal": 50, "hilly": 40,
    }
    scores["food_security"] = terrain_scores.get(city.geo.terrain_type, 50)

    total = sum(
        scores[k] * SUSTAINABILITY_WEIGHTS[k]
        for k in SUSTAINABILITY_WEIGHTS
    )
    return round(total, 1)


def compute_all_scores(cities: List[CityProfile]) -> List[CityProfile]:
    """Compute and attach all scores to city profiles."""
    for city in cities:
        city.liveability_score = compute_liveability_score(city)
        city.sustainability_score = compute_sustainability_score(city)
        city.investment_score = land_investment_score(city)
    return cities


def generate_master_ranking(cities: List[CityProfile]) -> pd.DataFrame:
    """
    Generate the master ranking table combining all scores.

    Overall rank is a weighted composite:
    - Liveability: 35%
    - Sustainability: 35%
    - Investment Potential: 30%
    """
    cities = compute_all_scores(cities)

    rows = []
    for city in cities:
        overall = round(
            city.liveability_score * 0.35 +
            city.sustainability_score * 0.35 +
            city.investment_score * 0.30,
            1
        )
        rows.append({
            "City": city.name,
            "State": city.state,
            "Tier": city.tier,
            "Liveability": city.liveability_score,
            "Sustainability": city.sustainability_score,
            "Investment": city.investment_score,
            "Overall Score": overall,
            "Current Price (₹/sqft)": f"{city.land_price.avg_price_per_sqft_2025:,.0f}",
            "Price 2050 (₹/sqft)": f"{city.land_price.projected_price_2050:,.0f}",
            "Pop 2025": f"{city.population.population_2025:,}",
            "Pop 2050": f"{city.population.projected_2050:,}",
            "Climate Risk": climate_risk_score(city),
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Overall Score", ascending=False)
    df.insert(0, "Rank", range(1, len(df) + 1))
    return df


def get_top_cities_to_buy(cities: List[CityProfile], top_n: int = 10) -> pd.DataFrame:
    """Get the top N cities where you should buy land today."""
    cities = compute_all_scores(cities)

    rows = []
    for city in cities:
        roi_2050 = round(
            ((city.land_price.projected_price_2050 - city.land_price.avg_price_per_sqft_2025)
             / city.land_price.avg_price_per_sqft_2025) * 100, 1)

        buy_score = round(
            city.investment_score * 0.4 +
            city.sustainability_score * 0.3 +
            min(100, roi_2050 / 10) * 0.3,
            1
        )

        rows.append({
            "City": city.name,
            "State": city.state,
            "Current Price (₹/sqft)": city.land_price.avg_price_per_sqft_2025,
            "Projected 2050 (₹/sqft)": city.land_price.projected_price_2050,
            "ROI 2050 (%)": roi_2050,
            "Investment Score": city.investment_score,
            "Sustainability": city.sustainability_score,
            "Buy Score": buy_score,
            "Recommendation": "Strong Buy" if buy_score >= 65 else
                              "Buy" if buy_score >= 50 else
                              "Hold" if buy_score >= 35 else "Avoid",
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Buy Score", ascending=False).head(top_n)
    df.insert(0, "Rank", range(1, len(df) + 1))
    return df
