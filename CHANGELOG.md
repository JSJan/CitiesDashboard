# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
