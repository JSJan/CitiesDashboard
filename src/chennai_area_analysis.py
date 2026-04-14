"""
Chennai area-level analysis and scoring module.

Provides zone-wise and area-wise liveability and investment scoring
for granular intra-city analysis.
"""

import pandas as pd
from typing import List
from src.area_models import AreaProfile


def compute_area_liveability(area: AreaProfile) -> float:
    """
    Score area liveability (0-100, higher is better).

    Factors: AQI, green cover, water supply, flood risk,
    connectivity, healthcare proximity, density.
    """
    score = 0

    # Air quality (max 20)
    if area.current_aqi <= 50:
        score += 20
    elif area.current_aqi <= 80:
        score += 16
    elif area.current_aqi <= 100:
        score += 12
    elif area.current_aqi <= 150:
        score += 6
    else:
        score += 2

    # Green cover (max 15)
    score += min(15, area.green_cover_pct * 0.8)

    # Water supply (max 15)
    score += area.water_supply_score * 1.5

    # Flood safety (max 10)
    score += 0 if area.flood_prone else 10

    # Connectivity (max 15)
    conn = 0
    if area.metro_connectivity:
        conn += 6
    if area.railway_station:
        conn += 5
    if area.distance_from_center_km < 10:
        conn += 4
    elif area.distance_from_center_km < 20:
        conn += 2
    score += min(15, conn)

    # Healthcare proximity (max 10)
    score += 10 if area.hospital_proximity else 3

    # Density penalty (max 15)
    if area.population_density_per_sqkm < 5000:
        score += 15
    elif area.population_density_per_sqkm < 10000:
        score += 12
    elif area.population_density_per_sqkm < 20000:
        score += 8
    elif area.population_density_per_sqkm < 30000:
        score += 4
    else:
        score += 1

    return round(min(100, score), 1)


def compute_area_investment(area: AreaProfile) -> float:
    """
    Score area investment potential (0-100, higher is better).

    Factors: CAGR, affordability, IT proximity, infrastructure
    growth potential, density headroom.
    """
    score = 0

    # CAGR momentum (max 25)
    cagr = area.land_price.cagr_2015_2025
    if cagr >= 11:
        score += 25
    elif cagr >= 9:
        score += 22
    elif cagr >= 7:
        score += 16
    elif cagr >= 5:
        score += 10
    else:
        score += 5

    # Affordability — cheaper areas have more upside (max 20)
    price = area.land_price.price_per_sqft_2025
    if price < 5000:
        score += 20
    elif price < 7000:
        score += 16
    elif price < 10000:
        score += 12
    elif price < 15000:
        score += 6
    else:
        score += 2

    # IT corridor proximity (max 15)
    if area.it_park_proximity:
        score += 15
    elif area.area_type == "it_corridor":
        score += 15

    # Infrastructure growth (max 15)
    infra = 0
    if not area.metro_connectivity:
        infra += 5  # potential metro expansion upside
    if area.railway_station:
        infra += 4
    if area.distance_from_center_km > 15:
        infra += 6  # suburban growth corridor
    score += min(15, infra)

    # Density headroom (max 15)
    if area.population_density_per_sqkm < 5000:
        score += 15
    elif area.population_density_per_sqkm < 10000:
        score += 12
    elif area.population_density_per_sqkm < 20000:
        score += 8
    else:
        score += 3

    # Flood risk discount (max -10)
    if area.flood_prone:
        score -= 10

    return round(max(0, min(100, score)), 1)


def score_all_areas(areas: List[AreaProfile]) -> List[AreaProfile]:
    """Compute and attach scores to all areas."""
    for area in areas:
        area.liveability_score = compute_area_liveability(area)
        area.investment_score = compute_area_investment(area)
    return areas


def generate_area_ranking(areas: List[AreaProfile]) -> pd.DataFrame:
    """Generate area-level ranking for Chennai."""
    areas = score_all_areas(areas)
    rows = []
    for area in areas:
        roi_2050 = round(
            ((area.land_price.projected_2050 - area.land_price.price_per_sqft_2025)
             / area.land_price.price_per_sqft_2025) * 100, 1)
        overall = round(
            area.liveability_score * 0.4 + area.investment_score * 0.6, 1)
        rows.append({
            "Area": area.name,
            "Zone": area.zone,
            "Type": area.area_type,
            "Liveability": area.liveability_score,
            "Investment": area.investment_score,
            "Overall": overall,
            "Price 2025 (₹/sqft)": f"{area.land_price.price_per_sqft_2025:,.0f}",
            "Price 2050 (₹/sqft)": f"{area.land_price.projected_2050:,.0f}",
            "ROI 2050 (%)": roi_2050,
            "CAGR (%)": area.land_price.cagr_2015_2025,
            "AQI": area.current_aqi,
            "Flood Risk": "Yes" if area.flood_prone else "No",
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Overall", ascending=False)
    df.insert(0, "Rank", range(1, len(df) + 1))
    return df


def generate_zone_summary(areas: List[AreaProfile]) -> pd.DataFrame:
    """Generate zone-level summary statistics."""
    areas = score_all_areas(areas)
    zone_data = {}
    for area in areas:
        if area.zone not in zone_data:
            zone_data[area.zone] = []
        zone_data[area.zone].append(area)

    rows = []
    for zone, zone_areas in zone_data.items():
        avg_price = sum(a.land_price.price_per_sqft_2025 for a in zone_areas) / len(zone_areas)
        avg_price_2050 = sum(a.land_price.projected_2050 for a in zone_areas) / len(zone_areas)
        avg_cagr = sum(a.land_price.cagr_2015_2025 for a in zone_areas) / len(zone_areas)
        avg_aqi = sum(a.current_aqi for a in zone_areas) / len(zone_areas)
        avg_live = sum(a.liveability_score for a in zone_areas) / len(zone_areas)
        avg_inv = sum(a.investment_score for a in zone_areas) / len(zone_areas)
        flood_pct = sum(1 for a in zone_areas if a.flood_prone) / len(zone_areas) * 100
        avg_green = sum(a.green_cover_pct for a in zone_areas) / len(zone_areas)

        rows.append({
            "Zone": zone,
            "Areas": len(zone_areas),
            "Avg Price 2025 (₹)": f"{avg_price:,.0f}",
            "Avg Price 2050 (₹)": f"{avg_price_2050:,.0f}",
            "Avg CAGR (%)": round(avg_cagr, 1),
            "Avg AQI": round(avg_aqi, 0),
            "Avg Liveability": round(avg_live, 1),
            "Avg Investment": round(avg_inv, 1),
            "Flood Prone (%)": round(flood_pct, 0),
            "Avg Green Cover (%)": round(avg_green, 1),
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Avg Investment", ascending=False)
    return df


def get_top_areas_to_buy(areas: List[AreaProfile], top_n: int = 10) -> pd.DataFrame:
    """Get the top N areas in Chennai to buy land."""
    areas = score_all_areas(areas)
    rows = []
    for area in areas:
        roi_2050 = round(
            ((area.land_price.projected_2050 - area.land_price.price_per_sqft_2025)
             / area.land_price.price_per_sqft_2025) * 100, 1)
        buy_score = round(
            area.investment_score * 0.5 +
            area.liveability_score * 0.2 +
            min(100, roi_2050 / 10) * 0.3, 1)

        rows.append({
            "Area": area.name,
            "Zone": area.zone,
            "Price 2025 (₹/sqft)": area.land_price.price_per_sqft_2025,
            "Projected 2050 (₹/sqft)": area.land_price.projected_2050,
            "ROI 2050 (%)": roi_2050,
            "CAGR (%)": area.land_price.cagr_2015_2025,
            "Investment": area.investment_score,
            "Liveability": area.liveability_score,
            "Buy Score": buy_score,
            "Recommendation": (
                "Strong Buy" if buy_score >= 65 else
                "Buy" if buy_score >= 50 else
                "Hold" if buy_score >= 35 else "Avoid"
            ),
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Buy Score", ascending=False).head(top_n)
    df.insert(0, "Rank", range(1, len(df) + 1))
    return df
