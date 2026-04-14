# Implementation Guide

A phase-by-phase guide covering where the data comes from, how to replace seed data with real sources, API integrations, and building the interactive web dashboard.

---

## Part 1: Seed Data — Where It Comes From & Source of Truth

### Current State

All data in `src/seed_data.py` and `src/chennai_areas_data.py` is **manually compiled** from approximate values found in publicly available reports. Here's the exact origin of each data field and the authoritative source to replace it:

### City-Level Data Sources

| Data Field | Current Source (Approximate) | Source of Truth (Authoritative) | How to Access |
|-----------|------------------------------|--------------------------------|---------------|
| **Population (2011)** | Census of India 2011 | Census of India, Registrar General | <https://censusindia.gov.in> — free PDF/Excel downloads |
| **Population (2020-2025 est)** | UN World Urbanization Prospects | UN DESA Population Division | <https://population.un.org/wup/> — free CSV download |
| **Population projections (2030-2070)** | Manual logistic growth model | UN World Population Prospects + National Commission on Population | <https://population.un.org/wpp/> |
| **Lat/Long, Elevation** | Google Maps / Wikipedia | Survey of India / GeoNames | <https://www.geonames.org/> — free API (username required) |
| **Seismic Zone** | BIS IS 1893 | Bureau of Indian Standards | <https://bis.gov.in> — zone map is public |
| **Flood Risk** | NDMA reports | National Disaster Management Authority | <https://ndma.gov.in> + CWC flood atlas |
| **Avg Temperature** | IMD climatological normals | India Meteorological Department | <https://dsp.imdpune.gov.in/> — registered access |
| **Avg Rainfall** | IMD climatological normals | IMD Pune Data Supply Portal | <https://dsp.imdpune.gov.in/> |
| **Air Quality Index** | CPCB CAAQMS dashboard | Central Pollution Control Board | API: <https://aqinow.org> (was app.cpcbccr.com) |
| **Climate projections (2050/2070)** | IPCC AR6 WG1 Chapter 12 Atlas | IPCC Interactive Atlas | <https://interactive-atlas.ipcc.ch/> — free, downloadable |
| **Land prices** | Newspaper reports, broker estimates | State registration dept (guideline values) + 99acres/Magicbricks | State IGR portals (e.g., <https://tnreginet.gov.in> for TN) |
| **Infrastructure (metro, airport)** | Wikipedia / news articles | Ministry of Housing & Urban Affairs | <https://smartcities.gov.in>, <https://mohua.gov.in> |
| **Healthcare/Education scores** | NITI Aayog SDG Index | NITI Aayog | <https://sdgindiaindex.niti.gov.in/> |
| **Green cover %** | Forest Survey of India ISFR | FSI India State of Forest Report | <https://fsi.nic.in/> |

### Chennai Area-Level Data Sources

| Data Field | Source of Truth | Access |
|-----------|----------------|--------|
| **Zone classification** | CMDA Master Plan | <https://www.cmdachennai.gov.in/> |
| **Area land prices** | TN Registration Dept (guideline values) | <https://tnreginet.gov.in> — guideline values by survey number |
| **Listing prices** | 99acres / Magicbricks | Web scraping (no official API) |
| **Flood-prone areas** | Greater Chennai Corporation flood map | <https://chennaicorporation.gov.in> |
| **Metro connectivity** | Chennai Metro Rail Ltd | <https://chennaimetrorail.org> |
| **AQI by area** | TNPCB monitoring stations | <https://tnpcb.gov.in> |
| **Population density** | Census ward-level data | Census of India town tables |

---

## Part 2: Free APIs for Real-Time Data

### API 1: OpenWeatherMap (Weather & AQI)

- **What:** Current weather, 5-day forecast, Air Pollution data for any lat/long
- **Free tier:** 1,000 calls/day, current weather + AQI
- **API key:** Sign up at <https://openweathermap.org/api>
- **Endpoints used:**
  - Weather: `https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric`
  - AQI: `https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={key}`

### API 2: Open-Meteo (Weather — No API Key Needed)

- **What:** Current + historical weather, climate projections, no key required
- **Free tier:** Unlimited for non-commercial, 10,000 calls/day
- **Base URL:** `https://api.open-meteo.com/v1/forecast`
- **Climate projections:** `https://climate-api.open-meteo.com/v1/climate` (CMIP6 models!)
- **Historical:** `https://archive-api.open-meteo.com/v1/archive`

### API 3: data.gov.in (Indian Government Open Data)

- **What:** Census data, infrastructure, various government datasets
- **Free tier:** Unlimited with API key
- **API key:** Register at <https://data.gov.in>
- **Docs:** <https://data.gov.in/apis>

### API 4: World Bank Climate API

- **What:** Historical climate + projections by country
- **Free tier:** Unlimited, no key
- **Base URL:** `https://climateknowledgeportal.worldbank.org/api/`

### API 5: GeoNames (Geography)

- **What:** City coordinates, elevation, timezone, nearby features
- **Free tier:** 1,000 calls/hour (username required)
- **Base URL:** `http://api.geonames.org/`

---

## Part 3: Implementation Phases

---

### PHASE 1 — Replace Static Seed Data with Live API Fetchers

**Goal:** Fetch real current weather, AQI, and climate projections from free APIs instead of hardcoded values.

**Files created:**

- `src/data_fetchers.py` — API clients for Open-Meteo + OpenWeatherMap
- `.env` — API keys (optional, Open-Meteo needs none)

**What changes:**

- Weather data (temp, rainfall, humidity) comes from Open-Meteo historical API
- AQI comes from OpenWeatherMap Air Pollution API (or stays static if no key)
- Climate projections (2050/2070) come from Open-Meteo CMIP6 climate API
- Seed data is used as fallback when APIs are unavailable

**How to run:**

```bash
# Without API key (Open-Meteo only, no AQI)
python3 main.py --report climate --live

# With OpenWeatherMap API key for AQI
echo "OWM_API_KEY=your_key_here" > .env
python3 main.py --report climate --live
```

---

### PHASE 2 — Interactive Web Dashboard with Streamlit

**Goal:** Replace CLI tables with a visual, filterable web dashboard.

**Files created:**

- `dashboard.py` — Streamlit app entry point
- `requirements.txt` — updated with `streamlit` and `plotly`

**Features:**

1. **City Rankings** — sortable table with color-coded scores
2. **City Comparison** — side-by-side comparison of 2-3 cities
3. **Chennai Area Map** — zone-wise heatmap of prices and scores
4. **Price Timeline Charts** — interactive line charts (2015→2070)
5. **Population Growth Charts** — with carrying capacity overlay
6. **Climate Risk Radar** — spider/radar chart per city
7. **Investment Calculator** — "If I invest ₹X today in City Y, what's my return?"
8. **Filters** — by tier, state, price range, score thresholds

**How to run:**

```bash
pip3 install streamlit plotly
streamlit run dashboard.py
```

---

### PHASE 3 — ML-Powered Predictions (Future)

See [NextSteps.md](NextSteps.md) for full ML/LLM integration roadmap.

**Summary:**

- Replace CAGR with Prophet/XGBoost time-series models
- Train on real historical price data from web scraping pipeline
- Add uncertainty bands (Monte Carlo simulation)
- LLM-powered natural language query interface

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DASHBOARD LAYER                          │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │   CLI (main.py)  │  │ Web (dashboard.py)│                    │
│  └────────┬─────────┘  └────────┬─────────┘                    │
│           │                      │                               │
├───────────┴──────────────────────┴──────────────────────────────┤
│                      ANALYSIS LAYER                             │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐       │
│  │  Climate   │ │ Land     │ │ Pop      │ │  Scoring  │       │
│  │  Analysis  │ │ Price    │ │ Analysis │ │  Engine   │       │
│  └─────┬──────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘       │
│        │              │            │              │              │
├────────┴──────────────┴────────────┴──────────────┴─────────────┤
│                        DATA LAYER                               │
│  ┌─────────────────┐  ┌─────────────────────┐                  │
│  │   Seed Data     │  │   Live API Fetcher  │                  │
│  │  (seed_data.py) │  │ (data_fetchers.py)  │                  │
│  │  (fallback)     │  │  Open-Meteo / OWM   │                  │
│  └─────────────────┘  └─────────────────────┘                  │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────────┐                  │
│  │  Chennai Areas  │  │   CSV Export        │                  │
│  │  (30 zones)     │  │  (assets/ folder)   │                  │
│  └─────────────────┘  └─────────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```
