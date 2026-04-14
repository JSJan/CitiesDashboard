"""
Data Staleness Detector — monitors the freshness of all data sources
and flags outdated entries that need updating.

Checks:
  - Cache file timestamps (real estate, weather, census)
  - Seed data vs latest API data discrepancies
  - Model training age
  - Pipeline run history

Provides:
  - Per-source staleness report
  - Automatic update suggestions
  - Data quality scoring
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
MODEL_DIR = os.path.join(DATA_DIR, "models")


# Staleness thresholds (in days)
THRESHOLDS = {
    "real_estate": 7,      # prices change weekly
    "weather": 30,         # climate data monthly
    "census": 365,         # population data annual
    "ml_models": 30,       # retrain monthly
    "news": 1,             # news should be daily
    "pipeline": 7,         # pipeline should run weekly
}


def _file_age_days(filepath: str) -> float:
    """Get file age in days. Returns inf if file doesn't exist."""
    if not os.path.exists(filepath):
        return float("inf")
    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
    return (datetime.now() - mtime).total_seconds() / 86400


def _read_cache_timestamp(filepath: str) -> str:
    """Read last_updated from a JSON cache file."""
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        return data.get("last_updated")
    except (json.JSONDecodeError, IOError):
        return None


def check_real_estate_staleness() -> Dict:
    """Check real estate data freshness."""
    cache_path = os.path.join(DATA_DIR, "real_estate_cache.json")
    age = _file_age_days(cache_path)
    threshold = THRESHOLDS["real_estate"]

    result = {
        "source": "real_estate",
        "cache_file": cache_path,
        "exists": os.path.exists(cache_path),
        "age_days": round(age, 1) if age != float("inf") else None,
        "threshold_days": threshold,
        "stale": age > threshold,
        "last_updated": _read_cache_timestamp(cache_path),
    }

    if result["stale"]:
        result["suggestion"] = (
            "Run: python -m src.scrapers.pipeline run "
            "or scrape_all_cities() to refresh real estate data."
        )
    return result


def check_weather_staleness() -> Dict:
    """Check weather/climate data freshness."""
    cache_path = os.path.join(DATA_DIR, "weather_cache.json")
    age = _file_age_days(cache_path)
    threshold = THRESHOLDS["weather"]

    result = {
        "source": "weather",
        "cache_file": cache_path,
        "exists": os.path.exists(cache_path),
        "age_days": round(age, 1) if age != float("inf") else None,
        "threshold_days": threshold,
        "stale": age > threshold,
        "last_updated": _read_cache_timestamp(cache_path),
    }

    if result["stale"]:
        result["suggestion"] = (
            "Run: python main.py --report climate --live "
            "to fetch fresh weather data from Open-Meteo."
        )
    return result


def check_census_staleness() -> Dict:
    """Check census/population data freshness."""
    cache_path = os.path.join(DATA_DIR, "census_cache.json")
    age = _file_age_days(cache_path)
    threshold = THRESHOLDS["census"]

    result = {
        "source": "census",
        "cache_file": cache_path,
        "exists": os.path.exists(cache_path),
        "age_days": round(age, 1) if age != float("inf") else None,
        "threshold_days": threshold,
        "stale": age > threshold,
        "last_updated": _read_cache_timestamp(cache_path),
    }

    if result["stale"]:
        result["suggestion"] = (
            "Census data updates infrequently. Check data.gov.in "
            "for new datasets or wait for Census 2031 data."
        )
    return result


def check_model_staleness() -> Dict:
    """Check ML model training freshness."""
    results = {}

    model_files = {
        "land_price": os.path.join(MODEL_DIR, "land_price_model.pkl"),
        "flood": os.path.join(MODEL_DIR, "flood_model.pkl"),
        "population": os.path.join(MODEL_DIR, "population_model.pkl"),
    }

    threshold = THRESHOLDS["ml_models"]

    for name, path in model_files.items():
        age = _file_age_days(path)
        metrics_path = path.replace(".pkl", "_metrics.json").replace("_model_", "_")
        if "land_price" in name:
            metrics_path = os.path.join(MODEL_DIR, "land_price_metrics.json")
        elif "flood" in name:
            metrics_path = os.path.join(MODEL_DIR, "flood_metrics.json")
        elif "population" in name:
            metrics_path = os.path.join(MODEL_DIR, "population_metrics.json")

        results[name] = {
            "exists": os.path.exists(path),
            "age_days": round(age, 1) if age != float("inf") else None,
            "stale": age > threshold,
        }

        if os.path.exists(metrics_path):
            with open(metrics_path, "r") as f:
                metrics = json.load(f)
            results[name]["trained_at"] = metrics.get("trained_at")
            results[name]["r2"] = metrics.get("r2_mean") or metrics.get("flood_r2")

    return {
        "source": "ml_models",
        "threshold_days": threshold,
        "models": results,
        "any_stale": any(m["stale"] for m in results.values()),
        "suggestion": "Run train_and_evaluate() for each model to retrain." if any(m["stale"] for m in results.values()) else None,
    }


def check_news_staleness() -> Dict:
    """Check news monitoring freshness."""
    cache_path = os.path.join(DATA_DIR, "news_cache.json")
    age = _file_age_days(cache_path)
    threshold = THRESHOLDS["news"]

    return {
        "source": "news",
        "cache_file": cache_path,
        "exists": os.path.exists(cache_path),
        "age_days": round(age, 1) if age != float("inf") else None,
        "threshold_days": threshold,
        "stale": age > threshold,
        "last_updated": _read_cache_timestamp(cache_path),
        "suggestion": "Run news_monitor.monitor_all_cities() for latest sentiment." if age > threshold else None,
    }


def check_pipeline_staleness() -> Dict:
    """Check when pipeline was last run."""
    log_path = os.path.join(DATA_DIR, "pipeline_log.json")

    result = {
        "source": "pipeline",
        "log_file": log_path,
        "exists": os.path.exists(log_path),
        "threshold_days": THRESHOLDS["pipeline"],
    }

    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            log = json.load(f)
        last_run = log.get("last_run")
        if last_run:
            age = (datetime.now() - datetime.fromisoformat(last_run)).total_seconds() / 86400
            result["last_run"] = last_run
            result["age_days"] = round(age, 1)
            result["stale"] = age > THRESHOLDS["pipeline"]
            result["total_runs"] = len(log.get("runs", []))
        else:
            result["stale"] = True
            result["age_days"] = None
    else:
        result["stale"] = True
        result["age_days"] = None

    if result.get("stale"):
        result["suggestion"] = "Run: python -m src.scrapers.pipeline run"

    return result


def check_seed_data_accuracy(cities: list = None) -> Dict:
    """
    Compare seed data against cached API data to find discrepancies.
    Flags entries where seed data differs significantly from real data.
    """
    weather_cache = os.path.join(DATA_DIR, "weather_cache.json")
    discrepancies = []

    if not os.path.exists(weather_cache) or not cities:
        return {
            "source": "seed_data_accuracy",
            "discrepancies": [],
            "checked": False,
            "suggestion": "Run weather pipeline first to compare seed vs real data.",
        }

    with open(weather_cache, "r") as f:
        cache = json.load(f)

    baselines = cache.get("baselines", {})

    for city in cities:
        for key, baseline in baselines.items():
            if city.name in key and baseline.get("avg_temp_c"):
                temp_diff = abs(city.climate.avg_temp_c - baseline["avg_temp_c"])
                if temp_diff > 2:
                    discrepancies.append({
                        "city": city.name,
                        "field": "avg_temp_c",
                        "seed_value": city.climate.avg_temp_c,
                        "api_value": baseline["avg_temp_c"],
                        "difference": round(temp_diff, 1),
                        "action": f"Update seed_data.py: {city.name} avg_temp_c "
                                  f"from {city.climate.avg_temp_c} to {baseline['avg_temp_c']}",
                    })

                if baseline.get("avg_rainfall_mm"):
                    rain_diff_pct = abs(
                        city.climate.avg_rainfall_mm - baseline["avg_rainfall_mm"]
                    ) / city.climate.avg_rainfall_mm * 100
                    if rain_diff_pct > 20:
                        discrepancies.append({
                            "city": city.name,
                            "field": "avg_rainfall_mm",
                            "seed_value": city.climate.avg_rainfall_mm,
                            "api_value": baseline["avg_rainfall_mm"],
                            "difference_pct": round(rain_diff_pct, 1),
                            "action": f"Update seed_data.py: {city.name} avg_rainfall_mm",
                        })

    return {
        "source": "seed_data_accuracy",
        "discrepancies": discrepancies,
        "total_checked": len(cities) if cities else 0,
        "issues_found": len(discrepancies),
    }


def check_all_staleness(cities: list = None) -> Dict:
    """Run all staleness checks and return comprehensive report."""
    report = {
        "checked_at": datetime.now().isoformat(),
        "sources": {
            "real_estate": check_real_estate_staleness(),
            "weather": check_weather_staleness(),
            "census": check_census_staleness(),
            "ml_models": check_model_staleness(),
            "news": check_news_staleness(),
            "pipeline": check_pipeline_staleness(),
        },
    }

    if cities:
        report["sources"]["seed_accuracy"] = check_seed_data_accuracy(cities)

    # Overall health score
    stale_count = sum(
        1 for s in report["sources"].values()
        if isinstance(s, dict) and s.get("stale", s.get("any_stale", False))
    )
    total = len(report["sources"])
    report["health_score"] = round((1 - stale_count / total) * 100, 1)
    report["stale_sources"] = stale_count
    report["total_sources"] = total

    # Action items
    actions = []
    for name, source in report["sources"].items():
        if isinstance(source, dict) and source.get("suggestion"):
            actions.append(f"[{name}] {source['suggestion']}")
    report["action_items"] = actions

    return report


def print_staleness_report(cities: list = None):
    """Print a formatted staleness report to console."""
    report = check_all_staleness(cities)

    print("\n" + "=" * 70)
    print("  DATA FRESHNESS REPORT")
    print(f"  Health Score: {report['health_score']}%")
    print(f"  Stale Sources: {report['stale_sources']}/{report['total_sources']}")
    print("=" * 70)

    for name, source in report["sources"].items():
        if not isinstance(source, dict):
            continue
        stale = source.get("stale", source.get("any_stale", False))
        status = "❌ STALE" if stale else "✅ FRESH"
        age = source.get("age_days", "N/A")
        print(f"\n  {name:20s} {status:12s} (age: {age} days)")
        if source.get("suggestion"):
            print(f"    → {source['suggestion']}")

    if report["action_items"]:
        print(f"\n{'─' * 70}")
        print("  ACTION ITEMS:")
        for action in report["action_items"]:
            print(f"    • {action}")

    print()
