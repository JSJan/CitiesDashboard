"""
News Monitoring & Sentiment Analysis — tracks real estate,
infrastructure, and policy news for cities.

Sources:
  - Google News RSS (free, no key)
  - NewsAPI.org (free tier: 100 req/day, optional key)

Provides:
  - City-specific news feed
  - Sentiment scoring per article
  - Infrastructure announcement detection
  - Policy impact alerts

Sentiment analysis uses a keyword-based approach (no ML needed).
Optionally uses LLM for richer sentiment understanding.
"""

import os
import re
import json
import ssl
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
NEWS_CACHE = os.path.join(DATA_DIR, "news_cache.json")

# Sentiment keywords
POSITIVE_KEYWORDS = [
    "approved", "launched", "inaugurated", "boost", "growth", "investment",
    "metro", "airport", "highway", "IT park", "smart city", "development",
    "record high", "demand", "infrastructure", "green", "affordable",
    "prices rising", "emerging", "hotspot", "appreciat",
]

NEGATIVE_KEYWORDS = [
    "flood", "waterlog", "pollution", "encroachment", "illegal",
    "collapse", "delay", "stalled", "protest", "decline", "crash",
    "risk", "disaster", "warning", "contaminated", "drought",
    "prices falling", "bubble", "overpriced", "slump",
]

INFRA_KEYWORDS = [
    "metro", "airport", "highway", "flyover", "bridge", "rail",
    "expressway", "IT corridor", "SEZ", "smart city", "port",
    "industrial", "tech park", "ring road", "MRTS", "BRTS",
]


def _get_ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _fetch_url(url: str, timeout: int = 10) -> Optional[str]:
    try:
        ctx = _get_ssl_context()
        req = urllib.request.Request(url, headers={
            "User-Agent": "CitiesDashboard/1.0",
            "Accept": "application/xml,text/xml,*/*",
        })
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  [WARN] News fetch failed: {e}")
        return None


def _load_cache() -> dict:
    if os.path.exists(NEWS_CACHE):
        with open(NEWS_CACHE, "r") as f:
            return json.load(f)
    return {"last_updated": None, "cities": {}}


def _save_cache(data: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    with open(NEWS_CACHE, "w") as f:
        json.dump(data, f, indent=2)


def compute_sentiment(text: str) -> Dict:
    """
    Compute sentiment score for a text using keyword matching.
    Returns score between -1.0 (negative) and 1.0 (positive).
    """
    text_lower = text.lower()

    pos_count = sum(1 for kw in POSITIVE_KEYWORDS if kw.lower() in text_lower)
    neg_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw.lower() in text_lower)
    total = pos_count + neg_count

    if total == 0:
        return {"score": 0.0, "label": "neutral", "positive": 0, "negative": 0}

    score = (pos_count - neg_count) / total

    label = "neutral"
    if score > 0.3:
        label = "positive"
    elif score < -0.3:
        label = "negative"

    return {
        "score": round(score, 3),
        "label": label,
        "positive": pos_count,
        "negative": neg_count,
    }


def detect_infrastructure(text: str) -> List[str]:
    """Detect infrastructure-related announcements in text."""
    text_lower = text.lower()
    found = [kw for kw in INFRA_KEYWORDS if kw.lower() in text_lower]
    return found


def fetch_city_news(city: str, max_results: int = 10,
                    use_cache: bool = True) -> List[Dict]:
    """
    Fetch recent news articles for a city from Google News RSS.

    Returns list of:
        {title, link, published, source, sentiment, infra_keywords}
    """
    cache = _load_cache()

    if use_cache and city in cache.get("cities", {}):
        cached = cache["cities"][city]
        cached_time = datetime.fromisoformat(cached.get("fetched_at", "2000-01-01"))
        if (datetime.now() - cached_time).total_seconds() < 3600:  # 1 hour cache
            return cached.get("articles", [])

    # Google News RSS for city + real estate/property
    query = urllib.request.quote(f"{city} India real estate property")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

    xml_content = _fetch_url(url)
    articles = []

    if xml_content:
        try:
            root = ET.fromstring(xml_content)
            items = root.findall(".//item")[:max_results]

            for item in items:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                pub_date = item.findtext("pubDate", "")
                source = item.findtext("source", "")

                sentiment = compute_sentiment(title)
                infra = detect_infrastructure(title)

                articles.append({
                    "title": title,
                    "link": link,
                    "published": pub_date,
                    "source": source,
                    "sentiment": sentiment,
                    "infra_keywords": infra,
                })
        except ET.ParseError:
            pass

    # Cache results
    if "cities" not in cache:
        cache["cities"] = {}
    cache["cities"][city] = {
        "articles": articles,
        "fetched_at": datetime.now().isoformat(),
    }
    _save_cache(cache)

    return articles


def get_city_sentiment_summary(city: str) -> Dict:
    """
    Get overall sentiment summary for a city based on recent news.
    """
    articles = fetch_city_news(city)

    if not articles:
        return {
            "city": city,
            "total_articles": 0,
            "avg_sentiment": 0,
            "sentiment_label": "no data",
            "infra_mentions": [],
        }

    scores = [a["sentiment"]["score"] for a in articles]
    avg = sum(scores) / len(scores) if scores else 0

    all_infra = []
    for a in articles:
        all_infra.extend(a.get("infra_keywords", []))

    label = "neutral"
    if avg > 0.2:
        label = "positive"
    elif avg < -0.2:
        label = "negative"

    return {
        "city": city,
        "total_articles": len(articles),
        "avg_sentiment": round(avg, 3),
        "sentiment_label": label,
        "positive_articles": sum(1 for s in scores if s > 0.3),
        "negative_articles": sum(1 for s in scores if s < -0.3),
        "infra_mentions": list(set(all_infra)),
        "latest_headlines": [a["title"] for a in articles[:5]],
    }


def monitor_all_cities(city_names: List[str]) -> List[Dict]:
    """
    Monitor news sentiment for all cities.
    Returns sorted by sentiment (most positive first).
    """
    results = []
    for city in city_names:
        print(f"  Monitoring news for {city}...")
        summary = get_city_sentiment_summary(city)
        results.append(summary)

    results.sort(key=lambda x: x["avg_sentiment"], reverse=True)
    return results


def get_infrastructure_alerts(city_names: List[str]) -> List[Dict]:
    """
    Get infrastructure-related news alerts across all cities.
    Useful for updating infrastructure scores.
    """
    alerts = []
    for city in city_names:
        articles = fetch_city_news(city)
        for article in articles:
            if article.get("infra_keywords"):
                alerts.append({
                    "city": city,
                    "headline": article["title"],
                    "keywords": article["infra_keywords"],
                    "sentiment": article["sentiment"]["label"],
                    "published": article["published"],
                })

    return alerts
