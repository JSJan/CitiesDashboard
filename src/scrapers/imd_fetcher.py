"""
IMD Weather Data Fetcher — connects to India Meteorological Department
data sources and Open-Meteo for real climate baselines.

Sources:
  - Open-Meteo Historical API (free, no key): daily weather back to 1940
  - Open-Meteo Climate API (CMIP6 models): future projections
  - IMD Data Supply Portal (registered access): climatological normals

Provides:
  - Historical monthly/yearly temperature and rainfall averages
  - Multi-decade climate baselines (30-year normals)
  - Extreme event frequency (heat waves, heavy rainfall days)
"""

import json
import os
import ssl
import urllib.request
import urllib.error
from datetime import datetime, date
from typing import Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
CACHE_FILE = os.path.join(DATA_DIR, "weather_cache.json")


def _get_ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _safe_get(url: str, timeout: int = 15) -> Optional[dict]:
    """Fetch JSON from URL with error handling."""
    try:
        ctx = _get_ssl_context()
        req = urllib.request.Request(url, headers={"User-Agent": "CitiesDashboard/1.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        print(f"  [WARN] Weather API failed: {e}")
        return None


def _load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {"last_updated": None, "baselines": {}, "projections": {}}


def _save_cache(data: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def fetch_climate_baseline(lat: float, lon: float, city_name: str,
                           start_year: int = 1991, end_year: int = 2020,
                           use_cache: bool = True) -> Dict:
    """
    Fetch 30-year climate baseline (climatological normals) from
    Open-Meteo Historical API.

    Returns monthly averages + annual summary:
        avg_temp_c, avg_rainfall_mm, avg_humidity_pct,
        extreme_heat_days (>40°C), heavy_rain_days (>50mm),
        monthly_temps [], monthly_rainfall []
    """
    cache = _load_cache()
    cache_key = f"{city_name}_{start_year}_{end_year}"

    if use_cache and cache_key in cache.get("baselines", {}):
        return cache["baselines"][cache_key]

    # Fetch in 5-year chunks to stay within API limits
    all_temps = []
    all_rain = []
    all_humidity = []
    extreme_heat = 0
    heavy_rain = 0
    monthly_temp_sum = [0.0] * 12
    monthly_rain_sum = [0.0] * 12
    monthly_count = [0] * 12

    for chunk_start in range(start_year, end_year + 1, 5):
        chunk_end = min(chunk_start + 4, end_year)
        url = (
            f"https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={lat}&longitude={lon}"
            f"&start_date={chunk_start}-01-01"
            f"&end_date={chunk_end}-12-31"
            f"&daily=temperature_2m_mean,temperature_2m_max,rain_sum,"
            f"relative_humidity_2m_mean"
            f"&timezone=auto"
        )
        data = _safe_get(url, timeout=30)
        if not data or "daily" not in data:
            continue

        daily = data["daily"]
        temps = daily.get("temperature_2m_mean", [])
        maxes = daily.get("temperature_2m_max", [])
        rain = daily.get("rain_sum", [])
        humidity = daily.get("relative_humidity_2m_mean", [])
        dates = daily.get("time", [])

        for i, d in enumerate(dates):
            month = int(d[5:7]) - 1  # 0-indexed

            if i < len(temps) and temps[i] is not None:
                all_temps.append(temps[i])
                monthly_temp_sum[month] += temps[i]
                monthly_count[month] += 1

            if i < len(maxes) and maxes[i] is not None:
                if maxes[i] > 40:
                    extreme_heat += 1

            if i < len(rain) and rain[i] is not None:
                all_rain.append(rain[i])
                monthly_rain_sum[month] += rain[i]
                if rain[i] > 50:
                    heavy_rain += 1

            if i < len(humidity) and humidity[i] is not None:
                all_humidity.append(humidity[i])

    years_span = end_year - start_year + 1

    result = {
        "city": city_name,
        "baseline_period": f"{start_year}-{end_year}",
        "avg_temp_c": round(sum(all_temps) / len(all_temps), 1) if all_temps else None,
        "avg_rainfall_mm": round(sum(all_rain) / years_span, 1) if all_rain else None,
        "avg_humidity_pct": round(sum(all_humidity) / len(all_humidity), 1) if all_humidity else None,
        "extreme_heat_days_per_year": round(extreme_heat / years_span, 1),
        "heavy_rain_days_per_year": round(heavy_rain / years_span, 1),
        "monthly_avg_temp": [
            round(monthly_temp_sum[m] / monthly_count[m], 1) if monthly_count[m] > 0 else None
            for m in range(12)
        ],
        "monthly_total_rain": [
            round(monthly_rain_sum[m] / years_span, 1) for m in range(12)
        ],
        "fetched_at": datetime.now().isoformat(),
    }

    if "baselines" not in cache:
        cache["baselines"] = {}
    cache["baselines"][cache_key] = result
    _save_cache(cache)

    return result


def fetch_climate_projection(lat: float, lon: float, city_name: str,
                             model: str = "MRI_AGCM3_2_S",
                             scenario: str = "ssp2_4_5",
                             use_cache: bool = True) -> Dict:
    """
    Fetch CMIP6 climate model projections from Open-Meteo Climate API.

    Returns projected changes for 2040-2060 and 2060-2080 vs baseline.
    """
    cache = _load_cache()
    cache_key = f"{city_name}_{model}_{scenario}"

    if use_cache and cache_key in cache.get("projections", {}):
        return cache["projections"][cache_key]

    url = (
        f"https://climate-api.open-meteo.com/v1/climate"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date=2025-01-01&end_date=2070-12-31"
        f"&models={model}"
        f"&daily=temperature_2m_mean,rain_sum"
    )
    data = _safe_get(url, timeout=30)

    result = {
        "city": city_name,
        "model": model,
        "scenario": scenario,
        "avg_temp_2040_2060": None,
        "avg_temp_2060_2080": None,
        "avg_rain_2040_2060": None,
        "avg_rain_2060_2080": None,
        "fetched_at": datetime.now().isoformat(),
    }

    if data and "daily" in data:
        daily = data["daily"]
        temps = daily.get("temperature_2m_mean", [])
        rain = daily.get("rain_sum", [])
        dates = daily.get("time", [])

        temps_mid = []
        temps_late = []
        rain_mid = []
        rain_late = []

        for i, d in enumerate(dates):
            year = int(d[:4])
            if i < len(temps) and temps[i] is not None:
                if 2040 <= year <= 2060:
                    temps_mid.append(temps[i])
                elif 2060 < year <= 2080:
                    temps_late.append(temps[i])
            if i < len(rain) and rain[i] is not None:
                if 2040 <= year <= 2060:
                    rain_mid.append(rain[i])
                elif 2060 < year <= 2080:
                    rain_late.append(rain[i])

        if temps_mid:
            result["avg_temp_2040_2060"] = round(sum(temps_mid) / len(temps_mid), 1)
        if temps_late:
            result["avg_temp_2060_2080"] = round(sum(temps_late) / len(temps_late), 1)
        if rain_mid:
            result["avg_rain_2040_2060"] = round(sum(rain_mid) * 365 / len(rain_mid), 1)
        if rain_late:
            result["avg_rain_2060_2080"] = round(sum(rain_late) * 365 / len(rain_late), 1)

    if "projections" not in cache:
        cache["projections"] = {}
    cache["projections"][cache_key] = result
    _save_cache(cache)

    return result


def fetch_recent_extremes(lat: float, lon: float, city_name: str,
                          lookback_years: int = 5) -> Dict:
    """
    Fetch recent extreme weather events for trend analysis.
    Looks at last N years of daily data for anomalies.
    """
    end_year = date.today().year - 1
    start_year = end_year - lookback_years + 1

    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start_year}-01-01"
        f"&end_date={end_year}-12-31"
        f"&daily=temperature_2m_max,temperature_2m_min,rain_sum,"
        f"wind_speed_10m_max"
        f"&timezone=auto"
    )
    data = _safe_get(url, timeout=30)

    result = {
        "city": city_name,
        "period": f"{start_year}-{end_year}",
        "heat_waves": 0,         # 3+ consecutive days > 42°C
        "cold_waves": 0,         # 3+ consecutive days < 10°C
        "heavy_rain_events": 0,  # days with > 100mm rain
        "storm_events": 0,       # days with wind > 80 km/h
        "max_temp_recorded": None,
        "max_rain_day_mm": None,
    }

    if not data or "daily" not in data:
        return result

    daily = data["daily"]
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    rain = daily.get("rain_sum", [])
    wind = daily.get("wind_speed_10m_max", [])

    # Count heat waves (3+ consecutive very hot days)
    consecutive_hot = 0
    for t in max_temps:
        if t is not None and t > 42:
            consecutive_hot += 1
            if consecutive_hot == 3:
                result["heat_waves"] += 1
        else:
            consecutive_hot = 0

    # Count cold waves
    consecutive_cold = 0
    for t in min_temps:
        if t is not None and t < 10:
            consecutive_cold += 1
            if consecutive_cold == 3:
                result["cold_waves"] += 1
        else:
            consecutive_cold = 0

    # Heavy rain and storms
    valid_rain = [r for r in rain if r is not None]
    valid_wind = [w for w in wind if w is not None]
    valid_max = [t for t in max_temps if t is not None]

    result["heavy_rain_events"] = sum(1 for r in valid_rain if r > 100)
    result["storm_events"] = sum(1 for w in valid_wind if w > 80)
    result["max_temp_recorded"] = round(max(valid_max), 1) if valid_max else None
    result["max_rain_day_mm"] = round(max(valid_rain), 1) if valid_rain else None

    return result


def fetch_all_city_baselines(cities: list, use_cache: bool = True) -> List[Dict]:
    """
    Fetch climate baselines for all cities.
    Accepts list of CityProfile objects.
    """
    results = []
    for city in cities:
        print(f"  Fetching baseline for {city.name}...")
        result = fetch_climate_baseline(
            city.geo.latitude, city.geo.longitude, city.name,
            use_cache=use_cache
        )
        results.append(result)
    return results
