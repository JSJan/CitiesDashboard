"""
Live data fetchers — pull real-time weather, AQI, and climate projections
from free public APIs to replace/augment static seed data.

APIs used:
  - Open-Meteo (no key needed): current weather, historical, CMIP6 climate
  - OpenWeatherMap (free key): AQI air pollution data

Usage:
    from src.data_fetchers import fetch_current_weather, fetch_aqi, fetch_climate_projection
"""

import os
import json
import ssl
import urllib.request
import urllib.error
from typing import Optional


def _get_ssl_context():
    """Create an SSL context; falls back to unverified if certs unavailable."""
    try:
        ctx = ssl.create_default_context()
        # Quick test to see if default certs work
        urllib.request.urlopen("https://api.open-meteo.com", timeout=5, context=ctx)
        return ctx
    except Exception:
        ctx = ssl._create_unverified_context()
        return ctx


# --- Open-Meteo: Free, no API key ---

OPEN_METEO_CURRENT = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_HISTORICAL = "https://archive-api.open-meteo.com/v1/archive"
OPEN_METEO_CLIMATE = "https://climate-api.open-meteo.com/v1/climate"

# --- OpenWeatherMap: Free tier, API key required for AQI ---

OWM_AQI_URL = "https://api.openweathermap.org/data/2.5/air_pollution"


def _safe_get(url: str, timeout: int = 10) -> Optional[dict]:
    """Fetch JSON from a URL with error handling."""
    try:
        ctx = _get_ssl_context()
        req = urllib.request.Request(url, headers={"User-Agent": "CitiesDashboard/1.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        print(f"  [WARN] API call failed: {e}")
        return None


def fetch_current_weather(lat: float, lon: float) -> Optional[dict]:
    """
    Fetch current weather from Open-Meteo (no API key needed).

    Returns dict with:
        temperature_c, humidity_pct, wind_speed_kmh, weather_code
    """
    params = (
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
        f"&timezone=auto"
    )
    data = _safe_get(OPEN_METEO_CURRENT + params)
    if not data or "current" not in data:
        return None

    current = data["current"]
    return {
        "temperature_c": current.get("temperature_2m"),
        "humidity_pct": current.get("relative_humidity_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "weather_code": current.get("weather_code"),
    }


def fetch_historical_climate(lat: float, lon: float,
                              start_year: int = 2020,
                              end_year: int = 2024) -> Optional[dict]:
    """
    Fetch historical annual averages from Open-Meteo archive.

    Returns dict with:
        avg_temp_c, total_rainfall_mm, avg_humidity_pct
    """
    params = (
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start_year}-01-01&end_date={end_year}-12-31"
        f"&daily=temperature_2m_mean,precipitation_sum,relative_humidity_2m_mean"
        f"&timezone=auto"
    )
    data = _safe_get(OPEN_METEO_HISTORICAL + params)
    if not data or "daily" not in data:
        return None

    daily = data["daily"]
    temps = [t for t in (daily.get("temperature_2m_mean") or []) if t is not None]
    rain = [r for r in (daily.get("precipitation_sum") or []) if r is not None]
    humidity = [h for h in (daily.get("relative_humidity_2m_mean") or []) if h is not None]

    if not temps:
        return None

    years = end_year - start_year + 1
    return {
        "avg_temp_c": round(sum(temps) / len(temps), 1),
        "total_rainfall_mm_per_year": round(sum(rain) / years, 0) if rain else None,
        "avg_humidity_pct": round(sum(humidity) / len(humidity), 1) if humidity else None,
    }


def fetch_climate_projection(lat: float, lon: float,
                              model: str = "MRI_AGCM3_2_S",
                              scenario: str = "ssp2_4_5") -> Optional[dict]:
    """
    Fetch CMIP6 climate projections from Open-Meteo Climate API.

    Models available: EC_Earth3P_HR, MRI_AGCM3_2_S, NICAM16_8S, etc.
    Scenarios: ssp2_4_5 (moderate), ssp5_8_5 (worst case)

    Returns dict with projected temps for 2050 and 2070 periods.
    """
    # Fetch 2040-2060 window for "2050" projection
    params_2050 = (
        f"?latitude={lat}&longitude={lon}"
        f"&start_date=2040-01-01&end_date=2060-12-31"
        f"&models={model}"
        f"&daily=temperature_2m_mean"
        f"&timezone=auto"
    )
    data_2050 = _safe_get(OPEN_METEO_CLIMATE + params_2050)

    # Fetch 2060-2080 window for "2070" projection
    params_2070 = (
        f"?latitude={lat}&longitude={lon}"
        f"&start_date=2060-01-01&end_date=2080-12-31"
        f"&models={model}"
        f"&daily=temperature_2m_mean"
        f"&timezone=auto"
    )
    data_2070 = _safe_get(OPEN_METEO_CLIMATE + params_2070)

    result = {}

    if data_2050 and "daily" in data_2050:
        temps_key = f"temperature_2m_mean_{model}"
        temps = data_2050["daily"].get(temps_key) or data_2050["daily"].get("temperature_2m_mean", [])
        valid = [t for t in temps if t is not None]
        if valid:
            result["avg_temp_2050_period"] = round(sum(valid) / len(valid), 1)

    if data_2070 and "daily" in data_2070:
        temps_key = f"temperature_2m_mean_{model}"
        temps = data_2070["daily"].get(temps_key) or data_2070["daily"].get("temperature_2m_mean", [])
        valid = [t for t in temps if t is not None]
        if valid:
            result["avg_temp_2070_period"] = round(sum(valid) / len(valid), 1)

    return result if result else None


def fetch_aqi(lat: float, lon: float, api_key: Optional[str] = None) -> Optional[dict]:
    """
    Fetch current AQI from OpenWeatherMap Air Pollution API.
    Requires a free API key (sign up at openweathermap.org).

    Returns dict with:
        aqi (1-5 scale), pm2_5, pm10, no2, o3, co
    """
    key = api_key or os.environ.get("OWM_API_KEY")
    if not key:
        return None  # silently skip if no key

    url = f"{OWM_AQI_URL}?lat={lat}&lon={lon}&appid={key}"
    data = _safe_get(url)

    if not data or "list" not in data or not data["list"]:
        return None

    item = data["list"][0]
    main_aqi = item.get("main", {}).get("aqi")  # 1=Good, 5=Very Poor
    components = item.get("components", {})

    # Convert OWM 1-5 scale to approximate India AQI (0-500)
    aqi_map = {1: 40, 2: 80, 3: 130, 4: 220, 5: 350}
    approx_aqi = aqi_map.get(main_aqi, 100)

    return {
        "aqi_india_approx": approx_aqi,
        "aqi_owm_scale": main_aqi,
        "pm2_5": components.get("pm2_5"),
        "pm10": components.get("pm10"),
        "no2": components.get("no2"),
        "o3": components.get("o3"),
        "co": components.get("co"),
    }


def fetch_all_for_city(lat: float, lon: float, city_name: str = "") -> dict:
    """
    Fetch all available live data for a city.
    Returns a combined dict; missing fields will be None.
    """
    print(f"  Fetching live data for {city_name} ({lat}, {lon})...")

    result = {"city": city_name, "source": "live_api"}

    weather = fetch_current_weather(lat, lon)
    if weather:
        result["current_weather"] = weather
        print(f"    ✓ Current weather: {weather['temperature_c']}°C")

    historical = fetch_historical_climate(lat, lon)
    if historical:
        result["historical_climate"] = historical
        print(f"    ✓ Historical avg: {historical['avg_temp_c']}°C, "
              f"{historical.get('total_rainfall_mm_per_year', '?')}mm rain")

    projection = fetch_climate_projection(lat, lon)
    if projection:
        result["climate_projection"] = projection
        print(f"    ✓ Climate projection: {projection}")

    aqi = fetch_aqi(lat, lon)
    if aqi:
        result["aqi"] = aqi
        print(f"    ✓ AQI: {aqi['aqi_india_approx']} (PM2.5: {aqi['pm2_5']})")
    else:
        print(f"    ⊘ AQI: skipped (no OWM_API_KEY)")

    return result
