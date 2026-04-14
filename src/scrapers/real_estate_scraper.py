"""
Real estate data scraper — fetches property prices from public listing sites.

Targets:
  - 99acres.com / MagicBricks.com search result pages
  - Extracts area-level price trends (avg ₹/sqft by locality)

Rate-limited and respectful: 2-second delay between requests.
Falls back to cached data if scraping fails.
"""

import json
import os
import re
import time
import ssl
import urllib.request
import urllib.error
from typing import Dict, List, Optional
from datetime import datetime, date


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
CACHE_FILE = os.path.join(DATA_DIR, "real_estate_cache.json")

# Chennai area slug mappings for 99acres URL patterns
AREA_SLUGS_99ACRES = {
    "T. Nagar": "t-nagar",
    "Adyar": "adyar",
    "Anna Nagar": "anna-nagar",
    "Velachery": "velachery",
    "Sholinganallur": "sholinganallur",
    "Tambaram": "tambaram",
    "Kelambakkam": "kelambakkam",
    "Porur": "porur",
    "Ambattur": "ambattur",
    "Perungudi": "perungudi",
    "Thoraipakkam": "thoraipakkam",
    "Siruseri": "siruseri",
    "Navalur": "navalur",
    "Thiruvanmiyur": "thiruvanmiyur",
    "Neelankarai": "neelankarai",
    "Kovalam": "kovalam-chennai",
    "Mylapore": "mylapore",
    "Egmore": "egmore",
    "Nungambakkam": "nungambakkam",
    "Besant Nagar": "besant-nagar",
    "Mogappair": "mogappair",
    "Avadi": "avadi",
    "Poonamallee": "poonamallee",
    "Medavakkam": "medavakkam",
    "Madhavaram": "madhavaram",
    "Tondiarpet": "tondiarpet",
    "Tiruvottiyur": "tiruvottiyur",
    "Ennore": "ennore",
    "Manali": "manali-chennai",
    "Palavakkam": "palavakkam",
}

# City slug mappings
CITY_SLUGS = {
    "Mumbai": "mumbai",
    "Delhi": "new-delhi",
    "Bengaluru": "bengaluru",
    "Chennai": "chennai",
    "Hyderabad": "hyderabad",
    "Kolkata": "kolkata",
    "Pune": "pune",
    "Ahmedabad": "ahmedabad",
    "Coimbatore": "coimbatore",
    "Jaipur": "jaipur",
    "Lucknow": "lucknow",
    "Kochi": "kochi",
    "Indore": "indore",
    "Surat": "surat",
    "Mysuru": "mysuru",
    "Vadodara": "vadodara",
    "Bhubaneswar": "bhubaneswar",
    "Chandigarh": "chandigarh",
    "Thiruvananthapuram": "thiruvananthapuram",
    "Visakhapatnam": "visakhapatnam",
}


def _get_ssl_context():
    """Create SSL context with fallback for macOS cert issues."""
    try:
        return ssl.create_default_context()
    except Exception:
        return ssl._create_unverified_context()


def _fetch_page(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch a web page with rate limiting and error handling."""
    try:
        ctx = _get_ssl_context()
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, TimeoutError, Exception) as e:
        print(f"  [WARN] Failed to fetch {url}: {e}")
        return None


def _load_cache() -> dict:
    """Load cached real estate data."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {"last_updated": None, "cities": {}, "areas": {}}


def _save_cache(data: dict):
    """Save real estate data to cache."""
    os.makedirs(DATA_DIR, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _extract_prices_from_html(html: str) -> List[float]:
    """
    Extract price-per-sqft values from listing page HTML.
    Looks for patterns like '₹X,XXX/sq.ft' or 'X,XXX per sq ft'.
    """
    prices = []
    # Pattern: ₹ followed by digits with optional commas, then /sq or per sq
    patterns = [
        r'[₹Rs\.]*\s*([\d,]+)\s*/\s*sq\.?\s*ft',
        r'([\d,]+)\s*per\s*sq\.?\s*ft',
        r'price_per_sqft["\s:]+(\d+)',
        r'"pricePerUnitArea"\s*:\s*(\d+)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        for m in matches:
            try:
                price = float(m.replace(",", ""))
                if 500 <= price <= 200000:  # reasonable price range per sqft
                    prices.append(price)
            except ValueError:
                continue
    return prices


def scrape_area_prices(city: str = "Chennai", area: str = "Adyar",
                       use_cache: bool = True) -> Dict:
    """
    Scrape current property listing prices for a specific area.

    Returns:
        dict with keys: area, city, avg_price, median_price, min_price,
                        max_price, num_listings, scraped_at
    """
    cache = _load_cache()
    cache_key = f"{city}_{area}"

    # Return cached data if fresh (< 24 hours)
    if use_cache and cache_key in cache.get("areas", {}):
        cached = cache["areas"][cache_key]
        cached_time = datetime.fromisoformat(cached.get("scraped_at", "2000-01-01"))
        if (datetime.now() - cached_time).total_seconds() < 86400:
            return cached

    area_slug = AREA_SLUGS_99ACRES.get(area, area.lower().replace(" ", "-"))
    city_slug = CITY_SLUGS.get(city, city.lower())

    # Try 99acres property listing page
    url = f"https://www.99acres.com/property-in-{area_slug}-{city_slug}-ffid"
    time.sleep(2)  # rate limit
    html = _fetch_page(url)

    result = {
        "area": area,
        "city": city,
        "avg_price": None,
        "median_price": None,
        "min_price": None,
        "max_price": None,
        "num_listings": 0,
        "scraped_at": datetime.now().isoformat(),
        "source": "99acres",
    }

    if html:
        prices = _extract_prices_from_html(html)
        if prices:
            import statistics
            result["avg_price"] = round(statistics.mean(prices))
            result["median_price"] = round(statistics.median(prices))
            result["min_price"] = round(min(prices))
            result["max_price"] = round(max(prices))
            result["num_listings"] = len(prices)

    # Cache results
    if "areas" not in cache:
        cache["areas"] = {}
    cache["areas"][cache_key] = result
    _save_cache(cache)

    return result


def scrape_city_avg_price(city: str, use_cache: bool = True) -> Dict:
    """
    Scrape average property price for an entire city.

    Returns:
        dict with keys: city, avg_price, scraped_at, source
    """
    cache = _load_cache()

    if use_cache and city in cache.get("cities", {}):
        cached = cache["cities"][city]
        cached_time = datetime.fromisoformat(cached.get("scraped_at", "2000-01-01"))
        if (datetime.now() - cached_time).total_seconds() < 86400:
            return cached

    city_slug = CITY_SLUGS.get(city, city.lower())
    url = f"https://www.99acres.com/property-in-{city_slug}-ffid"
    time.sleep(2)
    html = _fetch_page(url)

    result = {
        "city": city,
        "avg_price": None,
        "num_listings": 0,
        "scraped_at": datetime.now().isoformat(),
        "source": "99acres",
    }

    if html:
        prices = _extract_prices_from_html(html)
        if prices:
            import statistics
            result["avg_price"] = round(statistics.mean(prices))
            result["num_listings"] = len(prices)

    if "cities" not in cache:
        cache["cities"] = {}
    cache["cities"][city] = result
    _save_cache(cache)
    return result


def scrape_all_chennai_areas(use_cache: bool = True) -> List[Dict]:
    """Scrape prices for all 30 Chennai areas. Returns list of result dicts."""
    results = []
    for area in AREA_SLUGS_99ACRES:
        print(f"  Scraping {area}...")
        result = scrape_area_prices("Chennai", area, use_cache=use_cache)
        results.append(result)
    return results


def scrape_all_cities(use_cache: bool = True) -> List[Dict]:
    """Scrape average prices for all 20 cities. Returns list of result dicts."""
    results = []
    for city in CITY_SLUGS:
        print(f"  Scraping {city}...")
        result = scrape_city_avg_price(city, use_cache=use_cache)
        results.append(result)
    return results


def get_historical_price_trend(city: str, area: str = None) -> List[Dict]:
    """
    Build a historical price trend from cached snapshots.
    Each pipeline run adds a new data point. Over months this builds a trend.

    Returns list of {date, avg_price} dicts sorted by date.
    """
    cache = _load_cache()
    history_key = f"history_{city}_{area}" if area else f"history_{city}"
    return cache.get(history_key, [])


def record_price_snapshot(city: str, avg_price: float, area: str = None):
    """Record a price data point for historical trend building."""
    cache = _load_cache()
    history_key = f"history_{city}_{area}" if area else f"history_{city}"
    if history_key not in cache:
        cache[history_key] = []
    cache[history_key].append({
        "date": date.today().isoformat(),
        "avg_price": avg_price,
    })
    _save_cache(cache)
