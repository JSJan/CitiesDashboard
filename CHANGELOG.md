# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.4.0] - 2026-04-14

### Added — Phase 3B: Real Data Integration

- **Real Estate Scraper** (`src/scrapers/real_estate_scraper.py`) — scrape property prices from 99acres with caching (24hr TTL), rate limiting (2s delay), and regex price extraction for 20 cities + 30 Chennai areas
- **IMD/Climate Fetcher** (`src/scrapers/imd_fetcher.py`) — Open-Meteo Historical & CMIP6 Climate Projection API client for 30-year climate baselines, monthly normals, and extreme event detection (heat waves, heavy rain, storms)
- **Census Data Fetcher** (`src/scrapers/census_fetcher.py`) — embedded Census 2011 data for all 20 cities with World Bank API integration for urbanization rates, population estimation with growth rate extrapolation, and migration flow analysis
- **Automated Data Pipeline** (`src/scrapers/pipeline.py`) — 5-stage orchestrated pipeline (real estate → weather → census → ML update → staleness check) with CLI interface (`python -m src.scrapers.pipeline run|watch|status`), logging to `data/pipeline_log.json`

### Added — Phase 3C: ML Model Training

- **Land Price Predictor** (`src/ml/land_price_model.py`) — XGBoost/GradientBoosting model with 12 features (CAGR, tier, infrastructure, climate risk, etc.), R²=0.93, model persistence to `data/models/`, comparison with CAGR extrapolation
- **Flood & Heat Risk Model** (`src/ml/flood_model.py`) — composite hazard scoring combining flood probability, heat risk, seismic exposure, and cyclone risk with categorical risk labels
- **Population Predictor** (`src/ml/population_model.py`) — MLP neural network (64→32→16 hidden layers) for population projection, comparison with logistic growth model
- **Preference Learner** (`src/ml/preference_learner.py`) — personalized scoring from user ratings and pairwise preferences using Ridge regression, learns custom liveability/sustainability/investment weights, supports constraints (e.g., max AQI, min green cover)

### Added — Phase 3D: LLM Integration

- **Natural Language Query Engine** (`src/llm/query_engine.py`) — rule-based parser + optional OpenAI function calling for 6 query types: ranking, comparison, land price, climate, filter, Chennai areas
- **Report Generator** (`src/llm/report_generator.py`) — template-based + optional LLM narrative reports for cities with scores, price analysis, climate outlook, and recommendations
- **News Monitor** (`src/llm/news_monitor.py`) — Google News RSS feed parser with keyword-based sentiment analysis, infrastructure project detection, and city-level sentiment summaries
- **Staleness Detector** (`src/llm/staleness_detector.py`) — data freshness monitoring across 6 sources (real estate, weather, census, ML models, news, pipeline) with configurable thresholds and actionable remediation suggestions

### Changed

- Updated `requirements.txt` with `scikit-learn>=1.3`, `xgboost>=2.0` (optional), `openai>=1.0` (optional)
- Query engine normalizes ranking output keys to lowercase/snake_case for API consistency
- Compare query now uses case-insensitive city name matching

---

## [0.3.0] - 2026-04-14

### Added

- **Interactive Web Dashboard** (`dashboard.py`) — Streamlit + Plotly web app with 7 pages:
  - Master Ranking — overall city scores with color-coded table and grouped bar chart
  - City Comparison — radar chart comparison of 2–4 cities across 6 dimensions
  - Climate Analysis — temperature projections and AQI trajectory charts
  - Land Price Analysis — price timeline 2015–2070 with buy recommendations
  - Population Analysis — logistic growth projections and growth-vs-density scatter
  - Chennai Areas — zone summary, area ranking with price-vs-CAGR scatter, buy recs
  - Investment Calculator — ROI estimator for any city or Chennai area with timeline chart
- **Real-Time Data Fetchers** (`src/data_fetchers.py`)
  - Open-Meteo API integration (current weather, historical climate, CMIP6 projections)
  - OpenWeatherMap API integration (AQI air pollution data, optional)
  - SSL fallback for macOS certificate issues
- **Live Data CLI Flag** — `python3 main.py --report climate --live` fetches real API data before generating reports
- **Implementation Guide** (`Implementation.md`) — comprehensive data source mapping, API integration guide, and phased implementation roadmap
- Sidebar filters for city tier and state on all dashboard pages
- `streamlit>=1.30` and `plotly>=5.18` added to `requirements.txt`

---

## [0.2.0] - 2026-04-14

### Added

- **Chennai Area-Level Analysis** — 30 areas across 6 zones (North, Central, South, West, IT Corridor/OMR, ECR Belt)
  - `src/area_models.py` — `AreaProfile` and `AreaLandPrice` data models
  - `src/chennai_areas_data.py` — seed data for 30 Chennai areas with zone classification
  - `src/chennai_area_analysis.py` — area-level liveability and investment scoring, zone summaries, buy recommendations
- **CSV Export Module** (`src/csv_export.py`)
  - Exports 11 CSV files to `assets/` folder covering all city and area reports
  - New CLI option: `python3 main.py --report export`
- **Chennai Area Reports** — new CLI option: `python3 main.py --report chennai`
  - Zone-wise summary with avg prices, CAGR, AQI, scores
  - Area ranking (30 areas ranked by Overall = Liveability 40% + Investment 60%)
  - Top 10 areas to buy land recommendations
- **NextSteps.md** — optimization analysis document covering:
  - Current calculation accuracy assessment
  - Where ML models should be used (land price, climate, population, scoring)
  - Where LLMs should be used (policy analysis, NL queries, report generation, data enrichment)
  - Implementation roadmap (Phase 3A through 3D)

### Fixed

- `flood_risk` attribute references now correctly point to `city.geo.flood_risk` instead of `city.climate.flood_risk`

---

## [0.1.0] - 2026-04-14

### Added

- **Data Models** — `CityProfile`, `GeographicalProfile`, `ClimateData`, `LandPriceData`, `PopulationData`, `InfrastructureScore` dataclasses in `src/models.py`
- **Seed Data** — realistic data for 20 major Indian cities across Tier 1 (8), Tier 2 (9), and Tier 3 (3) in `src/seed_data.py`
  - Tier 1: Mumbai, Delhi, Bengaluru, Chennai, Hyderabad, Kolkata, Pune, Ahmedabad
  - Tier 2: Coimbatore, Jaipur, Lucknow, Chandigarh, Kochi, Indore, Thiruvananthapuram, Visakhapatnam
  - Tier 3: Mysuru, Vadodara, Bhubaneswar
- **Climate Analysis Module** (`src/climate_analysis.py`)
  - IPCC-aligned temperature projection model
  - Rainfall change modeling (coastal vs inland)
  - AQI degradation projection
  - Extreme heat day projection
  - Climate risk scoring (0-100)
  - Comparative climate report generation
- **Land Price Analysis Module** (`src/land_price_analysis.py`)
  - CAGR-based price projections with tier-based adjustment
  - Land investment attractiveness scoring
  - Year-by-year price timeline generation (2015–2070)
  - ROI calculations for 2050 and 2070
  - Comparative land report generation
- **Population Analysis Module** (`src/population_analysis.py`)
  - Logistic growth model with carrying capacity
  - Carrying capacity estimation based on infrastructure and resources
  - Population density projection with urban sprawl factor
  - Year-by-year population timeline (2011–2070)
  - Comparative population report generation
- **Scoring Engine** (`src/scoring_engine.py`)
  - Liveability scoring (7 weighted factors)
  - Sustainability scoring (6 weighted factors)
  - Investment scoring with climate risk discount
  - Master ranking: Overall = Liveability (35%) + Sustainability (35%) + Investment (30%)
  - Top cities to buy land recommendation with Strong Buy / Buy / Hold / Avoid ratings
- **CLI Dashboard** (`main.py`)
  - `--report all` — full dashboard (default)
  - `--report climate` — climate analysis only
  - `--report land` — land price analysis only
  - `--report population` — population analysis only
  - `--report ranking` — master city ranking
  - `--report buy` — top cities to buy land
  - `--city <name>` — deep dive into a specific city
- **Project Docs** — `ReadME.md` with full methodology, project structure, and usage guide
- **Problem Statement** — `ProblemStatement.md` with original vision, requirements, and scope
