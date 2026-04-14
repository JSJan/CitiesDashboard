"""
CSV export module — generates downloadable CSV files for all reports
into the assets/ folder.
"""

import os
import pandas as pd
from typing import List

from src.models import CityProfile
from src.area_models import AreaProfile
from src.seed_data import get_all_cities
from src.chennai_areas_data import get_chennai_areas
from src.climate_analysis import generate_climate_report
from src.land_price_analysis import generate_land_report, generate_price_timeline
from src.population_analysis import generate_population_report, generate_population_timeline
from src.scoring_engine import generate_master_ranking, get_top_cities_to_buy
from src.chennai_area_analysis import (
    generate_area_ranking, generate_zone_summary, get_top_areas_to_buy,
)


ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


def ensure_assets_dir():
    os.makedirs(ASSETS_DIR, exist_ok=True)


def export_all_city_csvs(cities: List[CityProfile]):
    """Export all city-level reports as CSVs."""
    ensure_assets_dir()

    # Climate report
    df = generate_climate_report(cities)
    path = os.path.join(ASSETS_DIR, "climate_analysis.csv")
    df.to_csv(path, index=False)
    print(f"  ✓ {path}")

    # Land price report
    df = generate_land_report(cities)
    path = os.path.join(ASSETS_DIR, "land_price_analysis.csv")
    df.to_csv(path, index=False)
    print(f"  ✓ {path}")

    # Land price timelines (all cities combined)
    timelines = []
    for city in cities:
        timelines.append(generate_price_timeline(city))
    df = pd.concat(timelines, ignore_index=True)
    path = os.path.join(ASSETS_DIR, "land_price_timeline_2015_2070.csv")
    df.to_csv(path, index=False)
    print(f"  ✓ {path}")

    # Population report
    df = generate_population_report(cities)
    path = os.path.join(ASSETS_DIR, "population_analysis.csv")
    df.to_csv(path, index=False)
    print(f"  ✓ {path}")

    # Population timelines
    timelines = []
    for city in cities:
        timelines.append(generate_population_timeline(city))
    df = pd.concat(timelines, ignore_index=True)
    path = os.path.join(ASSETS_DIR, "population_timeline_2011_2070.csv")
    df.to_csv(path, index=False)
    print(f"  ✓ {path}")

    # Master ranking
    df = generate_master_ranking(cities)
    path = os.path.join(ASSETS_DIR, "master_city_ranking.csv")
    df.to_csv(path, index=False)
    print(f"  ✓ {path}")

    # Buy recommendations
    df = get_top_cities_to_buy(cities, top_n=20)
    path = os.path.join(ASSETS_DIR, "city_buy_recommendations.csv")
    df.to_csv(path, index=False)
    print(f"  ✓ {path}")


def export_chennai_area_csvs(areas: List[AreaProfile]):
    """Export all Chennai area-level reports as CSVs."""
    ensure_assets_dir()

    # Area ranking
    df = generate_area_ranking(areas)
    path = os.path.join(ASSETS_DIR, "chennai_area_ranking.csv")
    df.to_csv(path, index=False)
    print(f"  ✓ {path}")

    # Zone summary
    df = generate_zone_summary(areas)
    path = os.path.join(ASSETS_DIR, "chennai_zone_summary.csv")
    df.to_csv(path, index=False)
    print(f"  ✓ {path}")

    # Top areas to buy
    df = get_top_areas_to_buy(areas, top_n=30)
    path = os.path.join(ASSETS_DIR, "chennai_area_buy_recommendations.csv")
    df.to_csv(path, index=False)
    print(f"  ✓ {path}")

    # Raw area data export
    rows = []
    for area in areas:
        rows.append({
            "Area": area.name,
            "Zone": area.zone,
            "Type": area.area_type,
            "Distance from Center (km)": area.distance_from_center_km,
            "Metro": area.metro_connectivity,
            "Railway": area.railway_station,
            "IT Park Nearby": area.it_park_proximity,
            "Hospital Nearby": area.hospital_proximity,
            "Coastal": area.coastal_proximity,
            "Flood Prone": area.flood_prone,
            "Green Cover (%)": area.green_cover_pct,
            "AQI": area.current_aqi,
            "Water Supply (1-10)": area.water_supply_score,
            "Density (/km²)": area.population_density_per_sqkm,
            "Price 2015 (₹/sqft)": area.land_price.price_per_sqft_2015,
            "Price 2020 (₹/sqft)": area.land_price.price_per_sqft_2020,
            "Price 2025 (₹/sqft)": area.land_price.price_per_sqft_2025,
            "CAGR 2015-25 (%)": area.land_price.cagr_2015_2025,
            "Projected 2030 (₹/sqft)": area.land_price.projected_2030,
            "Projected 2040 (₹/sqft)": area.land_price.projected_2040,
            "Projected 2050 (₹/sqft)": area.land_price.projected_2050,
            "Projected 2070 (₹/sqft)": area.land_price.projected_2070,
        })
    df = pd.DataFrame(rows)
    path = os.path.join(ASSETS_DIR, "chennai_area_raw_data.csv")
    df.to_csv(path, index=False)
    print(f"  ✓ {path}")


def export_all():
    """Export everything to assets/."""
    cities = get_all_cities()
    areas = get_chennai_areas()

    print("\n  Exporting city-level CSVs...")
    export_all_city_csvs(cities)

    print("\n  Exporting Chennai area-level CSVs...")
    export_chennai_area_csvs(areas)

    print(f"\n  All CSVs saved to: {ASSETS_DIR}/")
