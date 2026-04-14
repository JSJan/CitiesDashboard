"""
Automated Data Pipeline — orchestrates all data fetchers,
scrapers, and model updates on a scheduled basis.

Features:
  - Runs all scrapers and API fetchers sequentially
  - Updates cached data in data/ directory
  - Records price snapshots for historical trend building
  - Generates freshness report
  - Can be run via cron or as a scheduled task

Usage:
    # One-time run
    python -m src.scrapers.pipeline run

    # Continuous (runs every 24 hours)
    python -m src.scrapers.pipeline watch

    # Freshness check only
    python -m src.scrapers.pipeline status
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
PIPELINE_LOG = os.path.join(DATA_DIR, "pipeline_log.json")


def _load_log() -> dict:
    if os.path.exists(PIPELINE_LOG):
        with open(PIPELINE_LOG, "r") as f:
            return json.load(f)
    return {"runs": [], "last_run": None}


def _save_log(log: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PIPELINE_LOG, "w") as f:
        json.dump(log, f, indent=2)


def run_real_estate_pipeline(cities: list = None, areas: list = None) -> Dict:
    """Scrape real estate prices for all cities and Chennai areas."""
    from src.scrapers.real_estate_scraper import (
        scrape_city_avg_price, scrape_area_prices, record_price_snapshot
    )

    result = {"stage": "real_estate", "status": "success", "details": {}}

    if cities:
        result["details"]["cities_scraped"] = 0
        for city in cities:
            try:
                data = scrape_city_avg_price(city.name, use_cache=False)
                if data.get("avg_price"):
                    record_price_snapshot(city.name, data["avg_price"])
                    result["details"]["cities_scraped"] += 1
            except Exception as e:
                print(f"  [ERROR] Scraping {city.name}: {e}")

    if areas:
        result["details"]["areas_scraped"] = 0
        for area in areas:
            try:
                data = scrape_area_prices("Chennai", area.name, use_cache=False)
                if data.get("avg_price"):
                    record_price_snapshot("Chennai", data["avg_price"], area=area.name)
                    result["details"]["areas_scraped"] += 1
            except Exception as e:
                print(f"  [ERROR] Scraping {area.name}: {e}")

    return result


def run_weather_pipeline(cities: list) -> Dict:
    """Fetch climate baselines and extreme event data for all cities."""
    from src.scrapers.imd_fetcher import (
        fetch_climate_baseline, fetch_recent_extremes
    )

    result = {"stage": "weather", "status": "success", "details": {}}
    result["details"]["baselines_fetched"] = 0
    result["details"]["extremes_fetched"] = 0

    for city in cities:
        try:
            baseline = fetch_climate_baseline(
                city.geo.latitude, city.geo.longitude, city.name,
                use_cache=False
            )
            if baseline.get("avg_temp_c"):
                result["details"]["baselines_fetched"] += 1

            extremes = fetch_recent_extremes(
                city.geo.latitude, city.geo.longitude, city.name
            )
            if extremes.get("max_temp_recorded"):
                result["details"]["extremes_fetched"] += 1
        except Exception as e:
            print(f"  [ERROR] Weather for {city.name}: {e}")

    return result


def run_census_pipeline() -> Dict:
    """Fetch and compute population estimates and migration flows."""
    from src.scrapers.census_fetcher import (
        get_all_population_estimates, get_all_migration_flows,
        fetch_urbanization_rate
    )

    result = {"stage": "census", "status": "success", "details": {}}

    try:
        pop_estimates = get_all_population_estimates()
        result["details"]["population_estimates"] = len(pop_estimates)

        migration = get_all_migration_flows()
        result["details"]["migration_flows"] = len(migration)

        urban = fetch_urbanization_rate()
        result["details"]["urbanization_data"] = "fetched" if urban else "failed"
    except Exception as e:
        result["status"] = "partial"
        print(f"  [ERROR] Census pipeline: {e}")

    return result


def run_ml_update(cities: list) -> Dict:
    """Re-train ML models with latest data (if models exist)."""
    result = {"stage": "ml_update", "status": "skipped", "details": {}}

    try:
        from src.ml.land_price_model import LandPricePredictor
        predictor = LandPricePredictor()
        predictor.train(cities)
        result["status"] = "success"
        result["details"]["land_price_model"] = "retrained"
    except ImportError:
        result["details"]["land_price_model"] = "module not available"
    except Exception as e:
        result["details"]["land_price_model"] = f"error: {e}"

    return result


def run_staleness_check() -> Dict:
    """Check data freshness across all cached sources."""
    from src.llm.staleness_detector import check_all_staleness
    return check_all_staleness()


def run_full_pipeline(cities: list = None, areas: list = None) -> Dict:
    """
    Run the complete data pipeline:
    1. Scrape real estate prices
    2. Fetch weather baselines
    3. Compute census estimates
    4. Update ML models
    5. Check data staleness
    """
    print("=" * 70)
    print("  INDIA CITIES DASHBOARD — DATA PIPELINE")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    if cities is None:
        from src.seed_data import get_all_cities
        cities = get_all_cities()

    if areas is None:
        from src.chennai_areas_data import get_chennai_areas
        areas = get_chennai_areas()

    run_log = {
        "started_at": datetime.now().isoformat(),
        "stages": [],
    }

    # Stage 1: Real Estate
    print("\n[1/5] Scraping real estate prices...")
    stage1 = run_real_estate_pipeline(cities, areas)
    run_log["stages"].append(stage1)
    print(f"  Done: {stage1['details']}")

    # Stage 2: Weather
    print("\n[2/5] Fetching weather data...")
    stage2 = run_weather_pipeline(cities)
    run_log["stages"].append(stage2)
    print(f"  Done: {stage2['details']}")

    # Stage 3: Census
    print("\n[3/5] Computing census/population estimates...")
    stage3 = run_census_pipeline()
    run_log["stages"].append(stage3)
    print(f"  Done: {stage3['details']}")

    # Stage 4: ML Update
    print("\n[4/5] Updating ML models...")
    stage4 = run_ml_update(cities)
    run_log["stages"].append(stage4)
    print(f"  Done: {stage4['details']}")

    # Stage 5: Staleness Check
    print("\n[5/5] Checking data staleness...")
    try:
        stage5 = run_staleness_check()
        run_log["stages"].append({"stage": "staleness", "status": "success",
                                  "details": stage5})
    except Exception as e:
        run_log["stages"].append({"stage": "staleness", "status": "error",
                                  "details": str(e)})

    run_log["completed_at"] = datetime.now().isoformat()
    run_log["duration_seconds"] = round(
        (datetime.fromisoformat(run_log["completed_at"]) -
         datetime.fromisoformat(run_log["started_at"])).total_seconds(), 1
    )

    # Save to log
    log = _load_log()
    log["runs"].append(run_log)
    log["last_run"] = run_log["completed_at"]
    # Keep only last 30 runs
    if len(log["runs"]) > 30:
        log["runs"] = log["runs"][-30:]
    _save_log(log)

    print(f"\n{'=' * 70}")
    print(f"  Pipeline completed in {run_log['duration_seconds']}s")
    print(f"  Log saved to: {PIPELINE_LOG}")
    print(f"{'=' * 70}")

    return run_log


def get_pipeline_status() -> Dict:
    """Get current pipeline status and data freshness."""
    log = _load_log()
    status = {
        "last_run": log.get("last_run"),
        "total_runs": len(log.get("runs", [])),
        "data_files": {},
    }

    # Check cache files
    cache_files = {
        "real_estate": os.path.join(DATA_DIR, "real_estate_cache.json"),
        "weather": os.path.join(DATA_DIR, "weather_cache.json"),
        "census": os.path.join(DATA_DIR, "census_cache.json"),
    }

    for name, path in cache_files.items():
        if os.path.exists(path):
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            age = datetime.now() - mtime
            status["data_files"][name] = {
                "exists": True,
                "last_modified": mtime.isoformat(),
                "age_hours": round(age.total_seconds() / 3600, 1),
                "stale": age > timedelta(days=7),
            }
        else:
            status["data_files"][name] = {"exists": False, "stale": True}

    return status


def watch(interval_hours: int = 24):
    """Run pipeline continuously at specified interval."""
    print(f"Pipeline watching mode — runs every {interval_hours} hours")
    print("Press Ctrl+C to stop.\n")
    while True:
        run_full_pipeline()
        print(f"\nNext run in {interval_hours} hours...")
        time.sleep(interval_hours * 3600)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Data Pipeline Manager")
    parser.add_argument("command", choices=["run", "watch", "status"],
                        help="run: one-time, watch: continuous, status: check freshness")
    parser.add_argument("--interval", type=int, default=24,
                        help="Hours between runs in watch mode (default: 24)")
    args = parser.parse_args()

    if args.command == "run":
        run_full_pipeline()
    elif args.command == "watch":
        watch(args.interval)
    elif args.command == "status":
        status = get_pipeline_status()
        print(json.dumps(status, indent=2))
