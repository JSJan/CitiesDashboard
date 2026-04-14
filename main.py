#!/usr/bin/env python3
"""
India Cities Dashboard - Main Entry Point

Generates comprehensive reports on liveability, sustainability,
land investment potential, climate risk, and population projections
for 20 major Indian cities with forecasts through 2050 and 2070.

Usage:
    python main.py                    # Full dashboard
    python main.py --report climate   # Climate report only
    python main.py --report land      # Land price report only
    python main.py --report population # Population report only
    python main.py --report ranking   # Master ranking only
    python main.py --report buy       # Top cities to buy land
"""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from tabulate import tabulate

from src.seed_data import get_all_cities
from src.climate_analysis import generate_climate_report
from src.land_price_analysis import generate_land_report, generate_price_timeline
from src.population_analysis import generate_population_report, generate_population_timeline
from src.scoring_engine import (
    generate_master_ranking,
    get_top_cities_to_buy,
    compute_all_scores,
)
from src.chennai_areas_data import get_chennai_areas
from src.chennai_area_analysis import (
    generate_area_ranking,
    generate_zone_summary,
    get_top_areas_to_buy,
)
from src.csv_export import export_all
from src.data_fetchers import fetch_all_for_city


def print_section(title: str, df: pd.DataFrame):
    """Print a formatted section with title and table."""
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100)
    print(tabulate(df, headers="keys", tablefmt="fancy_grid",
                   showindex=False, numalign="right"))
    print()


def run_climate_report(cities):
    df = generate_climate_report(cities)
    print_section("CLIMATE CHANGE ANALYSIS & RISK ASSESSMENT", df)
    print("  Interpretation:")
    print("  - Climate Risk Score: 0 (safest) to 100 (most at risk)")
    print("  - Lower scores indicate better climate resilience")
    print("  - Factors: temperature rise, AQI, floods, cyclones, rainfall changes")


def run_land_report(cities):
    df = generate_land_report(cities)
    print_section("LAND PRICE ANALYSIS & INVESTMENT POTENTIAL", df)
    print("  Interpretation:")
    print("  - Investment Score: 0 (poor) to 100 (excellent)")
    print("  - ROI = projected return on investment from today's price")
    print("  - CAGR = compound annual growth rate over past decade")


def run_population_report(cities):
    df = generate_population_report(cities)
    print_section("POPULATION ANALYSIS & PROJECTIONS", df)
    print("  Interpretation:")
    print("  - Saturation % = how close current pop is to carrying capacity")
    print("  - Lower saturation = more growth headroom")
    print("  - Carrying capacity based on infrastructure & resources")


def run_master_ranking(cities):
    df = generate_master_ranking(cities)
    print_section("MASTER CITY RANKING - LIVEABILITY, SUSTAINABILITY & INVESTMENT", df)
    print("  Scoring Formula:")
    print("  Overall = Liveability (35%) + Sustainability (35%) + Investment (30%)")
    print()

    # Highlight top 5
    top5 = df.head(5)
    print("  TOP 5 MOST SUSTAINABLE & LIVEABLE CITIES:")
    for _, row in top5.iterrows():
        print(f"    #{int(row['Rank'])} {row['City']} ({row['State']}) "
              f"- Score: {row['Overall Score']}")
    print()

    # Highlight bottom 3 (most challenged)
    bottom3 = df.tail(3)
    print("  CITIES FACING MOST CHALLENGES:")
    for _, row in bottom3.iterrows():
        print(f"    #{int(row['Rank'])} {row['City']} ({row['State']}) "
              f"- Score: {row['Overall Score']}")


def run_buy_recommendations(cities):
    df = get_top_cities_to_buy(cities, top_n=10)
    print_section("TOP CITIES TO BUY LAND TODAY (Best ROI & Sustainability)", df)
    print("  Recommendation Key:")
    print("  - Strong Buy: Excellent growth + sustainability + affordability")
    print("  - Buy: Good fundamentals with moderate risk")
    print("  - Hold: Decent but watch for risks")
    print("  - Avoid: High risk or poor growth outlook")


def run_chennai_areas(areas):
    """Run Chennai area and zone-level analysis."""
    df_zone = generate_zone_summary(areas)
    print_section("CHENNAI ZONE-WISE SUMMARY", df_zone)

    df_rank = generate_area_ranking(areas)
    print_section("CHENNAI AREA RANKING (30 Areas across 6 Zones)", df_rank)
    print("  Scoring: Overall = Liveability (40%) + Investment (60%)")

    df_buy = get_top_areas_to_buy(areas, top_n=10)
    print_section("TOP 10 AREAS TO BUY LAND IN CHENNAI TODAY", df_buy)
    print("  Buy Score = Investment (50%) + Liveability (20%) + ROI Potential (30%)")


def run_csv_export():
    """Export all reports as CSV files to assets/ folder."""
    print("\n" + "=" * 100)
    print("  EXPORTING ALL REPORTS TO CSV")
    print("=" * 100)
    export_all()


def run_city_deep_dive(cities, city_name: str):
    """Deep dive into a specific city."""
    city = next((c for c in cities if c.name.lower() == city_name.lower()), None)
    if not city:
        print(f"City '{city_name}' not found. Available: {[c.name for c in cities]}")
        return

    compute_all_scores([city])

    print("\n" + "=" * 100)
    print(f"  DEEP DIVE: {city.name}, {city.state} (Tier {city.tier})")
    print("=" * 100)

    # Geography
    print(f"\n  GEOGRAPHY:")
    print(f"    Location: {city.geo.latitude}°N, {city.geo.longitude}°E")
    print(f"    Elevation: {city.geo.elevation_m}m | Terrain: {city.geo.terrain_type}")
    print(f"    Coastal: {'Yes' if city.geo.coastal else 'No'} | "
          f"Seismic Zone: {city.geo.seismic_zone} | "
          f"Flood Risk: {city.geo.flood_risk}")

    # Climate
    print(f"\n  CLIMATE TODAY vs FUTURE:")
    print(f"    Avg Temp:     {city.climate.avg_temp_c}°C → "
          f"{city.climate.avg_temp_c + city.climate.projected_temp_rise_2050:.1f}°C (2050) → "
          f"{city.climate.avg_temp_c + city.climate.projected_temp_rise_2070:.1f}°C (2070)")
    print(f"    Rainfall:     {city.climate.avg_rainfall_mm}mm "
          f"({city.climate.projected_rainfall_change_2050_pct:+.1f}% by 2050)")
    print(f"    AQI:          {city.climate.air_quality_index} → "
          f"{city.climate.projected_aqi_2050} (2050) → "
          f"{city.climate.projected_aqi_2070} (2070)")
    print(f"    Heat Days:    {city.climate.extreme_heat_days} days > 40°C/year")
    print(f"    Cyclone Risk: {city.climate.cyclone_risk}")

    # Land Prices
    print(f"\n  LAND PRICE TRAJECTORY (₹/sqft):")
    print(f"    2015: ₹{city.land_price.avg_price_per_sqft_2015:,.0f}")
    print(f"    2020: ₹{city.land_price.avg_price_per_sqft_2020:,.0f}")
    print(f"    2025: ₹{city.land_price.avg_price_per_sqft_2025:,.0f} (TODAY)")
    print(f"    2030: ₹{city.land_price.projected_price_2030:,.0f}")
    print(f"    2050: ₹{city.land_price.projected_price_2050:,.0f}")
    print(f"    2070: ₹{city.land_price.projected_price_2070:,.0f}")
    print(f"    CAGR (2015-25): {city.land_price.cagr_2015_2025}%")

    # Population
    print(f"\n  POPULATION TRAJECTORY:")
    print(f"    2011 Census: {city.population.population_2011:,}")
    print(f"    2025 Est:    {city.population.population_2025:,}")
    print(f"    2050 Proj:   {city.population.projected_2050:,}")
    print(f"    2070 Proj:   {city.population.projected_2070:,}")
    print(f"    Growth Rate: {city.population.growth_rate_pct}%/year")
    print(f"    Density:     {city.population.density_per_sqkm:,}/km²")

    # Scores
    print(f"\n  SCORES:")
    print(f"    Liveability:    {city.liveability_score}/100")
    print(f"    Sustainability: {city.sustainability_score}/100")
    print(f"    Investment:     {city.investment_score}/100")
    overall = round(
        city.liveability_score * 0.35 +
        city.sustainability_score * 0.35 +
        city.investment_score * 0.30, 1)
    print(f"    OVERALL:        {overall}/100")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="India Cities Dashboard - Sustainability & Investment Analysis"
    )
    parser.add_argument(
        "--report",
        choices=["climate", "land", "population", "ranking", "buy",
                 "chennai", "export", "all"],
        default="all",
        help="Type of report to generate",
    )
    parser.add_argument(
        "--city",
        type=str,
        help="Deep dive into a specific city (e.g., --city Bengaluru)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Fetch live weather/AQI data from APIs instead of using seed data",
    )

    args = parser.parse_args()
    cities = get_all_cities()
    areas = get_chennai_areas()

    print("\n" + "╔" + "═" * 98 + "╗")
    print("║" + "  INDIA CITIES DASHBOARD".center(98) + "║")
    print("║" + "  Sustainability • Liveability • Climate • Land Investment • Population".center(98) + "║")
    print("║" + "  Projections: 2025 → 2050 → 2070".center(98) + "║")
    print("╚" + "═" * 98 + "╝")

    if args.live:
        print("\n  Fetching live data from APIs (Open-Meteo + OpenWeatherMap)...")
        print("  " + "-" * 60)
        for city in cities:
            live = fetch_all_for_city(city.geo.latitude, city.geo.longitude, city.name)
            # Update seed data with live values where available
            if "historical_climate" in live:
                hist = live["historical_climate"]
                if hist.get("avg_temp_c"):
                    city.climate.avg_temp_c = hist["avg_temp_c"]
                if hist.get("total_rainfall_mm_per_year"):
                    city.climate.avg_rainfall_mm = hist["total_rainfall_mm_per_year"]
                if hist.get("avg_humidity_pct"):
                    city.climate.humidity_pct = hist["avg_humidity_pct"]
            if "aqi" in live:
                city.climate.air_quality_index = live["aqi"]["aqi_india_approx"]
        print("  " + "-" * 60)
        print("  Live data merged with seed data.\n")

    if args.city:
        run_city_deep_dive(cities, args.city)
        return

    if args.report in ("all", "climate"):
        run_climate_report(cities)

    if args.report in ("all", "land"):
        run_land_report(cities)

    if args.report in ("all", "population"):
        run_population_report(cities)

    if args.report in ("all", "ranking"):
        run_master_ranking(cities)

    if args.report in ("all", "buy"):
        run_buy_recommendations(cities)

    if args.report in ("all", "chennai"):
        run_chennai_areas(areas)

    if args.report in ("all", "export"):
        run_csv_export()

    if args.report == "all":
        print("\n" + "=" * 100)
        print("  DISCLAIMER")
        print("=" * 100)
        print("  This analysis uses publicly available data and projection models.")
        print("  Land prices and population projections are estimates based on")
        print("  historical trends and IPCC climate scenarios (RCP 4.5 pathway).")
        print("  This is NOT financial or investment advice. Always consult")
        print("  professionals before making investment decisions.")
        print("=" * 100)


if __name__ == "__main__":
    main()
