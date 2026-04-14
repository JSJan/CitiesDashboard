# Implementation Deep Dive — Tradeoffs, Data Flow & Learning Guide

This document covers every design decision, tradeoff, and technical concept used in the Cities Dashboard project. It explains **why** things were built the way they are, **how** each module contributes to city scoring, and **what** generates the files in `data/`.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [How City Scores Are Computed](#2-how-city-scores-are-computed)
3. [Data Fetchers — How Real Data Enters the System](#3-data-fetchers)
   - [IMD Weather Fetcher](#31-imd-weather-fetcher-open-meteo-api)
   - [Census Fetcher](#32-census-data-fetcher)
   - [Real Estate Scraper](#33-real-estate-scraper)
4. [ML Models — How Predictions Work](#4-ml-models)
   - [Land Price Predictor (XGBoost/GBR)](#41-land-price-predictor)
   - [Flood & Heat Risk Model](#42-flood--heat-risk-model)
   - [Population Predictor (MLP Neural Network)](#43-population-predictor)
   - [Preference Learner](#44-preference-learner)
5. [LLM Integration — How the AI Layer Works](#5-llm-integration)
   - [Query Engine](#51-query-engine)
   - [Report Generator](#52-report-generator)
   - [News Monitor](#53-news-monitor)
   - [Staleness Detector](#54-staleness-detector)
6. [The `data/` Folder — What Gets Generated and How](#6-the-data-folder)
7. [All Tradeoffs Summary](#7-all-tradeoffs-summary)
8. [Concepts Reference — Learn Each Topic In Depth](#8-concepts-reference)

---

## 1. Architecture Overview

The system has **three layers**, each optional on top of the previous:

```
Layer 1: Core (always works, no external dependencies)
┌─────────────────────────────────────────────────┐
│  Seed Data → Scoring Engine → Master Ranking    │
│  (hardcoded)   (formulas)     (DataFrame)       │
└─────────────────────────────────────────────────┘
          ▲                          │
          │                          ▼
Layer 2: Data Enhancement (optional, needs internet)
┌─────────────────────────────────────────────────┐
│  Weather API  │  Census Data  │  99acres Scraper│
│  → cache JSON │  → cache JSON │  → cache JSON   │
└─────────────────────────────────────────────────┘
          ▲                          │
          │                          ▼
Layer 3: Intelligence (optional, needs scikit-learn / OpenAI)
┌─────────────────────────────────────────────────┐
│  ML Models    │  LLM Queries  │  News Sentiment │
│  → .pkl files │  → answers    │  → alerts       │
└─────────────────────────────────────────────────┘
```

**Key design principle:** Every layer degrades gracefully. If you have no internet, Layer 1 still works. If you have no OpenAI API key, the query engine falls back to regex rules. If XGBoost won't install, it falls back to scikit-learn's GradientBoosting.

### Tradeoff: Why Three Layers Instead of One?

A monolithic system that requires all APIs and ML libraries would be fragile — any missing dependency breaks everything. The layered approach means:
- ✅ A student can clone and run `python main.py` immediately with zero API keys
- ✅ Adding real data improves accuracy incrementally
- ❌ But the layers create **parallel truth sources** — seed data might disagree with scraped data, and there's no automatic reconciliation

---

## 2. How City Scores Are Computed

Every city gets three scores (0–100) that combine into an overall ranking:

### Liveability Score (35% of Overall)

Measures "how pleasant is daily life here?"

| Factor | Weight | How It's Calculated |
|--------|--------|-------------------|
| Climate Comfort | 20% | Inverted climate risk score (lower risk → higher comfort) |
| Infrastructure | 25% | Average of healthcare, education, transport, water scores × 10 |
| Air Quality | 15% | AQI tiers: <50 → 100, <100 → 80, <150 → 50, <200 → 30, else → 10 |
| Green Cover | 10% | `green_cover_pct × 3`, capped at 100 |
| Water Supply | 10% | `water_supply_score × 10` |
| Population Density | 10% | Tier-based: <3000 → 90, <6000 → 70, <10000 → 50, <20000 → 30, else → 10 |
| Flood/Cyclone Risk | 10% | Average of flood risk map + cyclone risk map |

### Sustainability Score (35% of Overall)

Measures "can this city sustain growth long-term?"

| Factor | Weight | How It's Calculated |
|--------|--------|-------------------|
| Climate Resilience | 25% | Temperature rise by 2050: <1.5°C → 90, <2.0°C → 70, <2.5°C → 50, else → 30 |
| Water Security | 20% | Average of (rainfall tiers) + (water supply × 10) |
| Green Cover | 15% | Tiers: >30% → 90, >20% → 70, >10% → 50, else → 30 |
| Population Pressure | 15% | Saturation ratio (pop/carrying_capacity): <30% → 90, <50% → 70, <70% → 50, else → 30 |
| Air Quality Trend | 15% | Projected AQI 2050: <80 → 90, <120 → 70, <150 → 50, else → 30 |
| Food Security | 10% | Terrain: coastal → 60, plain/river → 70, plateau → 65, hill → 50, metro → 40 |

### Investment Score (30% of Overall)

Measures "is this a good place to buy land?"

Computed by `land_investment_score()` with 5 factors:
- **Growth Momentum** (25 pts max) — CAGR tiers: >12% → 25, >8% → 18, >5% → 12, else → 5
- **Affordability** (20 pts max) — Current price: <₹3000 → 20, <₹5000 → 16, <₹8000 → 12, <₹12000 → 8, else → 4
- **Infrastructure** (20 pts max) — Metro rail + international airport + IT hub + transport score bonuses
- **Population Demand** (20 pts max) — Growth rate: >3% → 20, >2% → 15, >1% → 10, else → 5
- **Climate Discount** (−15 pts max) — Climate risk: >70 → −15, >50 → −10, >30 → −5

### Master Ranking Formula

```
Overall Score = Liveability × 0.35 + Sustainability × 0.35 + Investment × 0.30
```

### Tradeoff: Discretized Tiers vs. Continuous Functions

The scoring uses **step functions** (tiers) like "AQI < 50 → score 100, AQI < 100 → score 80". A city with AQI 99 gets 80, but AQI 101 gets 50 — a **30-point cliff** for a 2-unit AQI difference.

**Why tiers?** Simplicity and interpretability. You can explain "this city scored 80 on air quality because AQI is under 100." Continuous functions (e.g., AQI → score via exponential decay) would be smoother but harder to explain.

**Impact:** Cities near tier boundaries get unfairly penalized or rewarded. Surat (AQI 68) and Bhubaneswar (AQI 55) both score 80, even though there's meaningful difference between them.

---

## 3. Data Fetchers

These modules bring real-world data into the system to validate and eventually replace the hardcoded seed data.

### 3.1 IMD Weather Fetcher (Open-Meteo API)

**File:** `src/scrapers/imd_fetcher.py`

**What it does:** Despite the name "IMD Fetcher", it actually uses the [Open-Meteo API](https://open-meteo.com/) — a free weather API that doesn't require an API key. It fetches three types of climate data:

1. **30-Year Climate Baselines** (1991–2020) — Monthly average temperatures and rainfall normals. This tells us "what's the typical weather for this city?"

2. **CMIP6 Climate Projections** — Future climate predictions from the Coupled Model Intercomparison Project Phase 6, the same models used by the IPCC. Returns projected temperatures and rainfall for 2040–2060 and 2060–2080 windows.

3. **Recent Extreme Events** (last 5 years) — Counts heat waves (3+ consecutive days >42°C), cold waves (<10°C), heavy rain events (>100mm/day), and storms (wind >80 km/h).

**How it helps scoring:**
- Baseline temperatures validate/replace the hardcoded `avg_temp_c` in seed data
- Climate projections replace the linear `0.25°C/decade` warming model in `climate_analysis.py` with actual CMIP6 model outputs
- Extreme event counts inform the flood model and climate risk score
- The staleness detector compares fetched data against seed data and flags discrepancies > 2°C

**Concepts to learn:**
- **CMIP6** — see [Section 8.1](#81-cmip6-climate-models)
- **Climate Baselines** — see [Section 8.2](#82-climate-baselines--normals)
- **Open-Meteo API** — see [Section 8.3](#83-open-meteo-api)

**Key tradeoffs:**

| Decision | What We Chose | Alternative | Why |
|----------|--------------|-------------|-----|
| API provider | Open-Meteo (free, no key) | IMD Data Portal (official Indian data) | IMD requires registered access, complex auth. Open-Meteo has global coverage including India |
| Fetch strategy | 5-year chunks | Single 30-year request | API rate limits reject large requests; chunking ensures reliability |
| Heat wave threshold | 3+ days > 42°C | IMD official definition (varies by region) | Simplification; IMD uses station-specific normals |
| SSL handling | Fallback to unverified context | Require proper SSL | macOS Python lacks default certificates; unverified fallback ensures it "just works" (security tradeoff) |
| Cache duration | 24 hours (baselines), implicit (projections) | Real-time | Climate baselines don't change daily; caching avoids redundant API calls |

### 3.2 Census Data Fetcher

**File:** `src/scrapers/census_fetcher.py`

**What it does:** Provides population and demographic data for all 20 cities from three sources:

1. **Census 2011 (Embedded)** — A hardcoded `CENSUS_2011` dictionary with official data: population, decadal growth rate (2001→2011), density, sex ratio, literacy rate for each city.

2. **Population Estimation** — Projects from 2011 census to any year using exponential growth:
$$P_{est} = P_{2011} \times (1 + r_{annual})^{years}$$
where $r_{annual}$ is derived from the decadal growth rate: $r_{annual} = (1 + r_{decadal}/100)^{1/10} - 1$

3. **Migration Flow Estimation** — Subtracts India's natural population growth (~10.5% per decade) from a city's total decadal growth. The difference is attributed to migration:
   - Net migration > 20%: `very_high_inflow` (e.g., Surat at 53.86%)
   - 10–20%: `high_inflow`
   - 0–10%: `moderate_inflow`
   - Negative: `outflow`

4. **World Bank API** (optional) — Fetches India's urban population growth rate from the World Bank Indicators API (`SP.URB.GROW`).

**How it helps scoring:**
- Population estimates validate/update the `population_2025` values in seed data
- Growth rates feed into the Population Demand factor of Investment Score
- Migration flow categorization helps identify cities with strong in-migration (economic attractors) vs. stagnation
- The population pressure sub-score in Sustainability uses the saturation ratio (current pop / carrying capacity)

**Concepts to learn:**
- **Census 2011 vs. 2021** — see [Section 8.4](#84-indian-census-data)
- **Exponential vs. Logistic Growth** — see [Section 8.5](#85-population-growth-models)
- **Migration Estimation** — see [Section 8.6](#86-migration-flow-analysis)

**Key tradeoffs:**

| Decision | What We Chose | Alternative | Why |
|----------|--------------|-------------|-----|
| Census data source | Hardcoded dictionary | Live API from censusindia.gov.in | Census India has no public API; data is in PDF reports. Embedding ensures reliability |
| Base year | Census 2011 (15 years old) | Census 2021 (delayed to 2025+) | 2021 census hasn't been conducted yet due to COVID delays |
| Growth model | Exponential from decadal rate | Logistic with carrying capacity | Exponential is simpler; logistic is used separately in `population_analysis.py` |
| Natural growth assumption | Flat 10.5% decadal nationally | State-level fertility rates | Simplification; actual rates vary (Kerala ~4.9%, Bihar ~25.4%) |
| data.gov.in API | Code exists but unused | Active integration | Requires API key registration; we didn't want another mandatory key |

### 3.3 Real Estate Scraper

**File:** `src/scrapers/real_estate_scraper.py`

**What it does:** Scrapes property listing prices from 99acres.com using HTTP requests and regex-based HTML parsing.

- Fetches listing pages for city-level and area-level (30 Chennai areas) property searches
- Extracts `₹/sqft` prices using 4 regex patterns targeting different HTML structures
- Filters extracted prices to ₹500–₹200,000/sqft range to remove outliers
- Computes avg, median, min, max and listing count
- Records historical snapshots for building time-series trends over multiple pipeline runs

**How it helps scoring:** Scraped prices validate/replace the hardcoded `avg_price_per_sqft_2025` values in seed data. Over time, repeated pipeline runs build historical price series that could feed into the ML land price model.

**Key tradeoffs:**

| Decision | What We Chose | Alternative | Why |
|----------|--------------|-------------|-----|
| Parsing method | Regex on raw HTML | BeautifulSoup/Scrapy | Avoids adding dependencies; but fragile if HTML changes |
| Anti-bot | None (just user-agent header) | Selenium, Playwright | Simple sites often work with HTTP alone; adds significant complexity |
| Rate limiting | 2-second delay | Parallel requests | Respectful scraping; avoids IP bans |
| Cache TTL | 24 hours | Real-time | Property prices don't change hourly; caching avoids unnecessary requests |
| Historical trends | Append-only snapshots | Backfill from archived data | Can only build forward; requires running pipeline monthly for useful trends |

---

## 4. ML Models

### 4.1 Land Price Predictor

**File:** `src/ml/land_price_model.py`

**Algorithm:** Gradient Boosting Regression (XGBoost if available, else scikit-learn's `GradientBoostingRegressor`)

**How it works:**

1. **Feature extraction** — For each city × time-point combination, builds a 12-dimensional feature vector:

| # | Feature | Source | Why It Matters |
|---|---------|--------|----------------|
| 1 | CAGR (2015–2025) | seed data | Historical growth momentum |
| 2 | City tier (1/2/3) | seed data | Metro vs. emerging city dynamics |
| 3 | Population growth rate | seed data | Demand pressure on land |
| 4 | Population density | seed data | Scarcity premium |
| 5 | Infrastructure composite | seed data | Metro + airport + IT hub + transport |
| 6 | Climate risk score | climate_analysis.py | Risk discount on prices |
| 7 | Flood risk (0/1/2) | seed data | Physical risk to property |
| 8 | Green cover % | seed data | Quality of life premium |
| 9 | Water supply score | seed data | Basic habitability |
| 10 | AQI | seed data | Pollution discount |
| 11 | log(current price) | seed data | Price level anchoring |
| 12 | Years forward | training input | Time dimension |

2. **Training data generation** — Creates 140 samples: 20 cities × 7 time points each (2015, 2020, 2025, 2030, 2040, 2050, 2070). Targets are **log-transformed prices** to handle exponential growth.

3. **Model training** — StandardScaler → GradientBoosting (200 trees, max depth 6, learning rate 0.1) → 5-fold cross-validation for R² metric.

4. **Prediction** — For a given city + target year, extracts features → scales → predicts log price → exponentiates → compares with CAGR projection.

**Results:**
- R² = 0.9258 (±0.1033) — appears excellent, but...
- Feature importance: `years_forward` = 74%, `current_price_log` = 24.4%, everything else < 2%
- The model essentially learns: **future_price ≈ f(current_price, time)** — which is exactly what CAGR already does

**How it helps scoring:** Provides an alternative price projection to compare against CAGR. In principle, the ML model accounts for 12 features instead of just growth rate. In practice, it mostly agrees with CAGR because the city-specific features contribute negligibly.

**Concepts to learn:**
- **Gradient Boosting** — see [Section 8.7](#87-gradient-boosting--xgboost)
- **Cross-Validation** — see [Section 8.8](#88-cross-validation)
- **Feature Importance** — see [Section 8.9](#89-feature-importance)
- **Log Transform** — see [Section 8.10](#810-log-transformation-for-price-data)

**Key tradeoff — Training on Projected Data:**

This is the single biggest tradeoff in the ML layer. The model is trained on **our own CAGR projections** (2030, 2040, 2050, 2070 prices) as if they were ground truth. This means:

- The model **cannot outperform CAGR** in a fundamental sense — it's learning to replicate CAGR outputs
- The high R² is misleading — it measures how well the model reproduces our formulas, not how well it predicts real future prices
- **To truly improve:** We'd need actual historical monthly prices from 99acres (years of scraper data), not CAGR projections

This was a conscious tradeoff: building the ML pipeline infrastructure now with synthetic data, so that when real historical price data accumulates from the scraper pipeline, we can retrain with actual targets.

### 4.2 Flood & Heat Risk Model

**File:** `src/ml/flood_model.py`

**Algorithm:** Two separate `GradientBoostingRegressor` models (100 trees, depth 4):
- Model 1: Predicts flood probability (0–1) from geographic/climate features
- Model 2: Predicts heat risk (0–1) from the same features

**How it works:**

1. **Feature extraction** — 11 features: elevation, coastal flag, river proximity, seismic zone, avg rainfall, humidity, cyclone risk (encoded 0–3), projected rainfall change, green cover, density, terrain type (encoded 0–4).

2. **Target generation** — Converts qualitative labels to numeric:
   - Flood risk: `low → 0.1`, `medium → 0.4`, `high → 0.7`
   - Heat risk: `min(1.0, extreme_heat_days / 50)`

3. **Composite score** — Combines predictions: `50% × flood + 30% × heat + 20% × seismic_zone_normalized`

**Results:**
- Flood R² = **−0.37** (worse than always predicting the mean)
- Heat R² = 0.46 (moderate)
- Only 20 samples — far too few for gradient boosting

**Why it's non-functional:** The model tries to learn "which features predict flooding" from only 20 data points. With 11 features and 20 samples, there isn't enough variation to learn patterns. Additionally, the training targets (flood risk labels) are derived from the same seed data that contains the features — **circular logic**.

**How it helps scoring (theoretically):** Would provide probabilistic flood/heat risk that could replace the categorical labels ("low"/"medium"/"high") in the climate risk score. Currently, the categorical approach in the scoring engine is more reliable.

**Key tradeoff:** We built the model infrastructure knowing it wouldn't work with 20 samples. The pipeline is ready for when we have ward-level or area-level data (e.g., 30 Chennai areas × 20 cities = 600 samples), which would make the model viable.

### 4.3 Population Predictor

**File:** `src/ml/population_model.py`

**Algorithm:** Multi-Layer Perceptron (MLP) neural network with 3 hidden layers: 64 → 32 → 16 neurons. Uses Adam optimizer and adaptive learning rate.

**The LSTM vs MLP Tradeoff:**

The roadmap called for an LSTM (Long Short-Term Memory) network — a recurrent neural network designed for sequential data like time series. LSTMs are theoretically ideal for population forecasting because they can learn temporal patterns.

| Aspect | LSTM | MLP (what we built) |
|--------|------|---------------------|
| **Dependency** | PyTorch or TensorFlow (~500MB) | scikit-learn (~30MB) |
| **Sequential learning** | Yes — learns patterns in time sequences | No — treats each sample independently |
| **Data requirement** | Needs long sequences (50+ time points per city) | Works with individual feature vectors |
| **Install complexity** | Often fails on Apple Silicon (M-series Macs) | `pip install scikit-learn` just works |

**Why MLP was chosen:** Adding PyTorch (2GB+ with CUDA) or TensorFlow for a 20-city project was unreasonable overhead. The MLP approximates temporal learning by encoding time-derived features (growth rates between periods, saturation ratio, years forward) as static inputs.

**Results:**
- R² = **−0.78** (extremely poor) with std = 2.30 (wildly unstable)
- Like the land price model, it's trained on logistic growth projections — so it can't beat the logistic model
- The logistic growth model in `population_analysis.py` remains the reliable approach

**Concepts to learn:**
- **LSTM Networks** — see [Section 8.11](#811-lstm-networks)
- **MLP vs. RNN** — see [Section 8.12](#812-mlp-vs-rnn-for-time-series)

### 4.4 Preference Learner

**File:** `src/ml/preference_learner.py`

**Algorithm:** Ridge Regression with positive coefficient constraint

**How it works:**

1. **User provides ratings** — Rate cities 1–10 (e.g., Bengaluru=9, Mumbai=6, Delhi=4)
2. **Feature matrix** — Each rated city becomes a row with 3 features: [liveability_score, sustainability_score, investment_score]
3. **Ridge regression** — Fits `rating = w1 × liveability + w2 × sustainability + w3 × investment`
4. **Weight normalization** — Coefficients are normalized to sum to 1.0, giving personalized weights
5. **Re-ranking** — All cities are re-ranked using the new weights instead of the default 35/35/30

**Example:** If you rate tech-friendly, green cities highly:
- Input: Bengaluru=9, Mysuru=8, Mumbai=6, Delhi=4
- Learned: liveability=0.0, sustainability=0.34, investment=0.66
- Interpretation: "You care about sustainability and investment potential, not generic liveability"
- New top 3: Coimbatore, Mysuru, Indore (replacing the default ranking)

**Key tradeoff — Pairwise Preferences:**
The module accepts pairwise comparisons ("prefer A over B") via `add_pairwise_preference()`, but these are **stored and never used** in `learn_weights()`. Only city ratings are processed. This is intentional scaffolding — implementing pairwise learning properly would require a Bradley-Terry model or similar ranking model, which adds complexity for minimal benefit when we have direct ratings.

**Concepts to learn:**
- **Ridge Regression** — see [Section 8.13](#813-ridge-regression)
- **Preference Learning** — see [Section 8.14](#814-preference-learning--learning-to-rank)

---

## 5. LLM Integration

### 5.1 Query Engine

**File:** `src/llm/query_engine.py`

**Two-tier architecture:**

**Tier 1 — OpenAI Function Calling** (when `OPENAI_API_KEY` is set):
1. User question → sent to `gpt-4o-mini` with 6 tool definitions
2. LLM decides which tool(s) to call (e.g., `get_city_ranking`, `compare_cities`)
3. Tool executes using existing analysis functions
4. Results fed back to LLM for natural language response

**Tier 2 — Rule-Based Parsing** (fallback, no API needed):
Uses regex patterns to detect intent:
- `"compare Mumbai and Bengaluru"` → regex captures city names → calls `_tool_compare_cities()`
- `"top 5 cities for investment"` → regex detects "top" + number → calls `_tool_city_ranking(sort_by="investment")`
- `"land price in Chennai by 2050"` → regex detects city + price keyword + year → calls `_tool_land_price()`

**How it helps:** Lets users query the scoring system in natural language instead of navigating code/dashboards. The rule-based fallback means it works without any API keys.

**Key tradeoff — Stateless Queries:**
Each query is independent — no conversation memory. Asking "what about Pune?" after "compare Mumbai and Bengaluru" won't understand context. Adding conversation state would require session management and token tracking, which was out of scope.

**Concepts to learn:**
- **Function Calling** — see [Section 8.15](#815-openai-function-calling)
- **Intent Recognition** — see [Section 8.16](#816-intent-recognition--nlp-parsing)

### 5.2 Report Generator

**File:** `src/llm/report_generator.py`

Two modes:
- **Template mode** (default) — Python string formatting with hardcoded sections: scores, price analysis (with ROI calculations), climate outlook, population projection, key risks, and buy/hold/avoid recommendation
- **LLM mode** (with OpenAI) — Sends structured data to `gpt-4o-mini` with a system prompt: "You are a senior real estate and urban planning analyst." Gets narrative, contextual reports instead of template fill-in

**Key tradeoff:** Template reports are deterministic (same city → same report every time) but robotic. LLM reports are natural but can hallucinate or vary between runs. Template is always the fallback.

### 5.3 News Monitor

**File:** `src/llm/news_monitor.py`

**How sentiment works:**

Uses keyword bag-of-words scoring on Google News RSS article **titles only**:

```
Positive keywords (21): approved, metro, growth, investment, smart city, green,
                         development, infrastructure, airport, hub, corridor, ...
Negative keywords (20):  flood, pollution, slum, crash, scam, encroachment,
                         drought, demolition, illegal, congestion, ...

Score = (positive_count - negative_count) / total_count
Range: [-1.0, +1.0]
```

**Key tradeoffs:**

| Decision | Implication |
|----------|------------|
| Title-only analysis | Headlines are misleading (clickbait). "Mumbai metro faces delays" has both "metro" (positive) and "delays" (would not match anything) |
| No negation handling | "No new metro planned" → detects "metro" as positive, misses the negation |
| English-only keywords | Misses Hindi/Marathi/Tamil news sources which cover local developments |
| No article body | Full content would give much better sentiment but requires bypassing paywalls |
| 1-hour cache | Aggressive for news, but prevents hammering Google's RSS endpoint |

### 5.4 Staleness Detector

**File:** `src/llm/staleness_detector.py`

Monitors 6 data sources with different freshness thresholds:

| Source | File Checked | Stale After | Why This Threshold |
|--------|-------------|-------------|-------------------|
| Real estate | `data/real_estate_cache.json` | 7 days | Property prices change weekly |
| Weather | `data/weather_cache.json` | 30 days | Climate baselines are stable month-to-month |
| Census | `data/census_cache.json` | 365 days | Census data updates very infrequently |
| ML models | `data/models/*.pkl` | 30 days | Models should be retrained monthly with new data |
| News | `data/news_cache.json` | 1 day | News relevance decays rapidly |
| Pipeline | `data/pipeline_log.json` | 7 days | Pipeline should run at least weekly |

Also cross-validates seed data against weather cache: flags if temperature differs by >2°C or rainfall by >20%.

---

## 6. The `data/` Folder

Everything in the `data/` folder is **auto-generated** — you can delete the entire directory and it will be recreated on the next run. Here's exactly what generates each file:

### Cache Files (generated by scrapers)

| File | Generated By | When | Contents |
|------|-------------|------|----------|
| `data/real_estate_cache.json` | `real_estate_scraper.py` | When scraper runs (pipeline or manual) | City/area prices with timestamps, keyed by slug |
| `data/weather_cache.json` | `imd_fetcher.py` | When weather pipeline runs | Climate baselines & projections, keyed by `{city}_{year_range}` |
| `data/census_cache.json` | `census_fetcher.py` | When census pipeline runs | Population estimates & migration flows |
| `data/news_cache.json` | `news_monitor.py` | When news monitor runs | News articles with sentiment scores, 1-hour TTL |

### Model Files (generated by ML training)

| File | Generated By | When | Contents |
|------|-------------|------|----------|
| `data/models/land_price_model.pkl` | `land_price_model.py` → `train()` | Pipeline ML stage or manual training | Pickled model + StandardScaler |
| `data/models/land_price_metrics.json` | `land_price_model.py` → `train()` | Same as above | R², feature importance, sample count, timestamp |
| `data/models/flood_model.pkl` | `flood_model.py` → `train()` | Manual `train_and_evaluate()` call | Two pickled models (flood + heat) + scaler |
| `data/models/flood_metrics.json` | `flood_model.py` → `train()` | Same | R² (flood + heat), feature importance |
| `data/models/population_model.pkl` | `population_model.py` → `train()` | Manual `train_and_evaluate()` call | Pickled MLP + two scalers (X and y) |
| `data/models/population_metrics.json` | `population_model.py` → `train()` | Same | R², sample count |

### Other Files

| File | Generated By | When | Contents |
|------|-------------|------|----------|
| `data/user_preferences.json` | `preference_learner.py` | When user rates cities | Learned weights, rating history, constraints per user_id |
| `data/pipeline_log.json` | `pipeline.py` | After each pipeline run | Last 30 run logs with timestamps and stage results |
| `data/reports/*.md` | `report_generator.py` | When `generate_and_save_all()` is called | Markdown investment reports per city |

### How Pickle (.pkl) Files Work

Python's `pickle` module serializes Python objects to binary files. Our `.pkl` files contain:

```python
# What gets saved (land_price_model.py):
joblib.dump({
    'model': self.model,      # trained GradientBoostingRegressor
    'scaler': self.scaler,    # fitted StandardScaler
}, filepath)

# What gets loaded:
data = joblib.load(filepath)
self.model = data['model']    # ready to call .predict()
self.scaler = data['scaler']  # ready to call .transform()
```

**Security note:** Never load `.pkl` files from untrusted sources — pickle can execute arbitrary code during deserialization. Our models are only loaded from files we generated ourselves.

---

## 7. All Tradeoffs Summary

### Architectural Tradeoffs

| # | Decision | What We Chose | What We Sacrificed | Why |
|---|----------|--------------|-------------------|-----|
| 1 | Optional dependencies | Graceful fallback everywhere | Optimal accuracy | Any student can run it immediately |
| 2 | Seed data as default | Hardcoded 20-city dataset | Real-time accuracy | Works offline, zero setup |
| 3 | Three-layer architecture | Core → Data → Intelligence | Simplicity | Each layer adds value independently |
| 4 | Single Python process | Sequential pipeline | Throughput | Avoids complexity of async/multiprocessing |

### Data Tradeoffs

| # | Decision | What We Chose | What We Sacrificed | Why |
|---|----------|--------------|-------------------|-----|
| 5 | Open-Meteo over IMD | Free API, no key needed | Official Indian climate data | IMD has no public API |
| 6 | Census 2011 hardcoded | Guaranteed availability | Recency (15 years old) | No Census 2021 exists yet |
| 7 | Regex HTML scraping | No extra dependencies | Reliability (breaks on HTML change) | Avoids BeautifulSoup/Scrapy |
| 8 | 24-hour cache TTL | Reduced API calls | Real-time freshness | Prices/weather don't change hourly |

### ML Tradeoffs

| # | Decision | What We Chose | What We Sacrificed | Why |
|---|----------|--------------|-------------------|-----|
| 9 | Train on projected data | Working pipeline now | True predictive power | No historical price data exists yet; pipeline ready for real data later |
| 10 | MLP over LSTM | 30MB scikit-learn | Sequential pattern learning | Avoids 2GB PyTorch/TF dependency |
| 11 | XGBoost → sklearn fallback | Cross-platform compatibility | Slight accuracy loss | XGBoost needs `libomp` on macOS which often fails |
| 12 | 20-sample flood model | Built infrastructure | Functional model (R² = −0.37) | Pipeline ready for area-level data (600+ samples) |
| 13 | Pairwise preferences stored but unused | Simpler learning | Richer preference signal | Bradley-Terry model adds complexity with minimal benefit given direct ratings |

### LLM Tradeoffs

| # | Decision | What We Chose | What We Sacrificed | Why |
|---|----------|--------------|-------------------|-----|
| 14 | Regex fallback for queries | Works without API key | Natural language understanding | Covers 80% of queries with zero cost |
| 15 | Title-only news sentiment | Fast, no paywalls | Accuracy (headlines mislead) | Article bodies require scraping/LLM processing |
| 16 | Template reports as default | Deterministic output | Narrative quality | LLM reports are optional enhancement |
| 17 | Stateless queries | Simpler implementation | Conversation context | Session management adds complexity |
| 18 | Keyword sentiment | No NLP dependency | Negation handling, sarcasm | Works offline; LLM sentiment is optional future work |

### Scoring Tradeoffs

| # | Decision | What We Chose | What We Sacrificed | Why |
|---|----------|--------------|-------------------|-----|
| 19 | Discretized tier scoring | Interpretable explanations | Smooth transitions | "AQI under 100 = score 80" is easy to explain |
| 20 | Equal liveability/sustainability weight | Balanced long-term view | Short-term investment focus | Reflects the project's vision of sustainable cities |
| 21 | Additive scoring | Simple, transparent | Non-linear interactions | Multiplicative scoring creates harder-to-explain results |
| 22 | Climate risk discount on investment | Conservative pricing | Aggressive growth predictions | Climate risk is real and growing; discounting is prudent |

---

## 8. Concepts Reference

### 8.1 CMIP6 Climate Models

**Coupled Model Intercomparison Project Phase 6** is a framework where ~50 climate research groups worldwide run standardized climate simulations. These models:

- Divide Earth into 3D grid cells (atmosphere, ocean, land)
- Simulate physics: radiation, convection, precipitation, ocean currents
- Run "Shared Socioeconomic Pathways" (SSPs): SSP2-4.5 is "middle of the road" (moderate emissions)
- Output: gridded temperature, rainfall, wind, sea level for every point on Earth through 2100

**In our project:** We use Open-Meteo's Climate API which serves pre-processed CMIP6 data. Specifically, we use the `MRI_AGCM3_2_S` model with `ssp2_4_5` scenario — a Japanese model at relatively high resolution.

**Why it matters:** CMIP6 projections are what the IPCC uses in its Assessment Reports. They represent the scientific consensus on future climate, far more trustworthy than our linear `0.25°C/decade` approximation in `climate_analysis.py`.

### 8.2 Climate Baselines & Normals

A **climate baseline** (or "normal") is the 30-year average of weather variables at a location. The current reference period is 1991–2020. Normals smooth out year-to-year variability to show the "typical" climate.

- **Temperature normal:** Average daily mean temperature per month over 30 years
- **Rainfall normal:** Total monthly rainfall averaged over 30 years
- **Use case:** A city's baseline temperature of 28°C means "expect around 28°C on average" — not that today will be 28°C

**In our project:** `fetch_climate_baseline()` retrieves these from Open-Meteo's Historical API, computing monthly averages from daily data across 1991–2020.

### 8.3 Open-Meteo API

[Open-Meteo](https://open-meteo.com/) is a free, open-source weather API. Key features:
- **No API key required** (for non-commercial use up to 10,000 requests/day)
- Three relevant endpoints:
  1. `/v1/forecast` — 7-day weather forecast
  2. `/v1/archive` — Historical daily data back to 1940
  3. `/v1/climate` — CMIP6 climate projections to 2100
- Input: latitude, longitude, variables requested
- Output: JSON with hourly/daily time series

### 8.4 Indian Census Data

India conducts a national census every 10 years. The last completed census is **Census 2011** (the 2021 census was postponed indefinitely due to COVID-19).

Census 2011 provides:
- Population (total, urban, rural)
- Decadal growth rate (2001–2011)
- Population density (persons/km²)
- Sex ratio (females per 1000 males)
- Literacy rate (%)
- Occupational data

**Why it's still used:** No newer comprehensive source exists. State-level estimates and surveys (NFHS-5, SRS) provide updates on some indicators, but city-level population data hasn't been officially updated since 2011.

### 8.5 Population Growth Models

| Model | Formula | Behavior | When to Use |
|-------|---------|----------|-------------|
| **Exponential** | $P(t) = P_0 \cdot e^{rt}$ | Unlimited growth, gets faster over time | Short-term, unconstrained environments |
| **Logistic** | $P(t) = \frac{K}{1 + \frac{K-P_0}{P_0} \cdot e^{-rt}}$ | S-curve, plateaus at carrying capacity $K$ | Cities with resource constraints |
| **Gompertz** | $P(t) = K \cdot e^{-e^{-b(t-t_0)}}$ | Asymmetric S-curve, slower approach to K | Aging populations |

**In our project:** We use **logistic growth** in `population_analysis.py` because cities have finite carrying capacity (water, space, infrastructure). The MLP model attempts to add ML-based projection but currently underperforms the logistic model.

**Carrying capacity** ($K$) is estimated as:
$$K = Pop_{2025} \times TierMultiplier \times WaterFactor \times GreenFactor$$
- Tier-1: 2.5×, Tier-2: 4.0×, Tier-3: 6.0× (smaller cities have more growth room)
- Water factor: `water_supply_score / 10`
- Green factor: `min(1.5, 1 + green_cover / 50)`

### 8.6 Migration Flow Analysis

**Net migration** = Total population change − Natural increase (births − deaths)

Since India's natural growth is ~10.5% per decade nationally, any city growing faster is gaining people through in-migration (economic pull). A city growing slower is experiencing out-migration or stagnation.

Example: Surat grew 64.4% in 2001–2011. After subtracting 10.5% natural growth:
$$\text{Net migration} = 64.4\% - 10.5\% = 53.9\%$$
This indicates Surat is a massive migration magnet (textile/diamond industry hub), which drives demand for housing and land.

### 8.7 Gradient Boosting & XGBoost

**Gradient Boosting** builds an ensemble of decision trees sequentially. Each new tree tries to correct the errors of the previous ensemble:

1. Start with a simple prediction (mean of targets)
2. Compute residuals (actual − predicted)
3. Train a shallow decision tree on the residuals
4. Add this tree to the ensemble (scaled by learning rate)
5. Repeat for N iterations

**XGBoost** (Extreme Gradient Boosting) is a high-performance implementation that adds:
- Newton-Raphson optimization (uses both gradient and Hessian)
- Tree pruning to prevent overfitting
- Built-in handling of missing values
- Parallelized tree construction

**In our project:** XGBoost is preferred but falls back to scikit-learn's `GradientBoostingRegressor` if XGBoost can't load (common on macOS without `libomp`). Both use 200 trees, max depth 6, and learning rate 0.1. The difference in accuracy is typically <2%.

### 8.8 Cross-Validation

**K-Fold Cross-Validation** splits data into K equal parts, trains on K-1 parts and tests on the remaining 1, rotating through all K folds. Reports average metric ± standard deviation.

```
Fold 1: [Test] [Train] [Train] [Train] [Train]  → R² = 0.92
Fold 2: [Train] [Test] [Train] [Train] [Train]  → R² = 0.88
Fold 3: [Train] [Train] [Test] [Train] [Train]  → R² = 0.95
Fold 4: [Train] [Train] [Train] [Test] [Train]  → R² = 0.91
Fold 5: [Train] [Train] [Train] [Train] [Test]  → R² = 0.97
                                     Average: 0.926 ± 0.033
```

**Why we use it:** With only 140 samples, a single train/test split would be unreliable. 5-fold CV provides a more robust estimate of model quality.

**R² interpretation:**
- R² = 1.0 → perfect predictions
- R² = 0.0 → model is as good as predicting the mean
- R² < 0.0 → model is **worse** than predicting the mean (our flood and population models)

### 8.9 Feature Importance

In gradient boosting, feature importance measures how much each feature contributes to reducing prediction error across all trees. It's computed as the total reduction in loss function attributed to splits on that feature, normalized to sum to 1.0.

**Our land price model's feature importance:**
```
years_forward:          ████████████████████████████████████████ 74.0%
current_price_log:      █████████████  24.4%
infra_score:            ▏  0.5%
population_growth_rate: ▏  0.5%
cagr_2015_2025:         ▏  0.2%
(all others):           ▏  0.4%
```

**Interpretation:** The model learned that time and current price are overwhelmingly predictive of future price. City-specific features (infrastructure, climate, flood risk) barely matter — not because they don't actually affect prices, but because our training data doesn't have enough variation to learn those relationships from only 20 cities.

### 8.10 Log Transformation for Price Data

Land prices follow exponential growth: ₹5,000 → ₹10,000 → ₹20,000 → ₹40,000. The **absolute** differences grow (5K, 10K, 20K) but the **relative** growth is constant (100% each period).

Log transform converts exponential to linear:
$$\log(5000) = 8.52, \quad \log(10000) = 9.21, \quad \log(20000) = 9.90, \quad \log(40000) = 10.60$$

Differences are now equal: 0.69, 0.69, 0.70. This makes gradient boosting work much better because:
- Decision tree splits create equal-width intervals, which work better on linear relationships
- The model doesn't need to learn exponential growth — it learns linear trends in log-space
- Prediction errors are proportional (a 10% error on a ₹5K property is ₹500; on a ₹50K property is ₹5K — both are "10% error" in log-space)

### 8.11 LSTM Networks

**Long Short-Term Memory** is a type of Recurrent Neural Network (RNN) that can learn patterns in sequential data. Key innovation: a **memory cell** with gates that control what information to remember, forget, or output.

```
                    ┌──────────────────────┐
Input ──► [Forget Gate] ─► [Cell State] ─► [Output Gate] ──► Output
              │                  ▲                │
              └── [Input Gate] ──┘                └──► Hidden State
```

- **Forget gate:** "Should I forget this old information?" (sigmoid, 0–1)
- **Input gate:** "Should I store this new information?" (sigmoid × tanh)
- **Output gate:** "What part of the cell state should I output?"

**Why we didn't use it:** LSTMs need:
1. PyTorch or TensorFlow (2GB+ installation)
2. Long time sequences (50+ data points per city; we have 7)
3. GPU for reasonable training speed
4. Significant hyperparameter tuning

Our MLP approximation encodes time-series features as static inputs (growth rates, saturation ratios) instead of learning temporal patterns directly.

### 8.12 MLP vs. RNN for Time Series

| Feature | MLP (feedforward) | RNN/LSTM (recurrent) |
|---------|-------------------|---------------------|
| Input format | Fixed-size feature vector | Sequence of variable length |
| Memory | None; each sample is independent | Hidden state carries context from previous time steps |
| Temporal patterns | Must be manually engineered as features | Learned automatically |
| Training data | Can work with 100+ samples | Needs 1000+ sequences |
| Dependency | scikit-learn | PyTorch/TensorFlow |

For our 20-city, 7-timepoint dataset, MLP with handcrafted temporal features (growth rates, saturation ratio) is the practical choice. LSTM would require orders of magnitude more data.

### 8.13 Ridge Regression

Ridge regression is linear regression with **L2 regularization** — it adds a penalty for large coefficients:

$$\text{Minimize: } \sum(y_i - \hat{y}_i)^2 + \alpha \sum w_j^2$$

- Without regularization: coefficients can be wildly large, especially with correlated features
- With L2 penalty ($\alpha$): coefficients are "shrunk" toward zero, preventing overfitting
- `positive=True`: forces all coefficients ≥ 0 (makes sense for weights — we don't want "negative liveability preference")

**In our project:** The preference learner uses Ridge regression to find the combination of liveability, sustainability, and investment weights that best predicts user ratings. With only 3–5 data points, Ridge's regularization prevents the model from overfitting to the few ratings provided.

### 8.14 Preference Learning / Learning to Rank

**Preference learning** is the problem of learning a user's ranking function from feedback. Three types of feedback:

1. **Pointwise** — "Rate this city 1–10" → regression problem
2. **Pairwise** — "Do you prefer A or B?" → classification problem (Bradley-Terry model)
3. **Listwise** — "Rank these 5 cities" → permutation optimization

**In our project:** We use pointwise feedback (city ratings) with Ridge regression. The learned weights then re-rank all cities using a weighted score:

$$\text{Personalized Score} = w_1 \times \text{Liveability} + w_2 \times \text{Sustainability} + w_3 \times \text{Investment}$$

This is a simple but effective approach when users can provide numeric ratings. For more nuanced preferences, pairwise comparison with a Bradley-Terry model would be better (infrastructure exists but is not yet implemented).

### 8.15 OpenAI Function Calling

**Function calling** (now called "tool use") lets an LLM decide which functions to call based on a user's natural language query:

```
User: "What are the top 3 cities for investment?"

→ LLM receives tool definitions (JSON schemas)
→ LLM responds: tool_call(name="get_city_ranking", args={"top_n": 3, "sort_by": "investment"})
→ Application executes the function with these args
→ Results sent back to LLM
→ LLM generates natural language response with the data
```

**Why it's powerful:** The LLM handles intent recognition, parameter extraction, and response generation in one step. No need for custom NLP pipelines.

**Why we have a fallback:** Function calling requires an API key, costs money (~$0.001/query with gpt-4o-mini), and adds 1–3 seconds latency. The regex-based fallback handles the most common query patterns instantly and for free.

### 8.16 Intent Recognition / NLP Parsing

**Intent recognition** maps a user's utterance to a predefined action category:

```
"compare Mumbai vs Pune"       → intent: COMPARE, entities: [Mumbai, Pune]
"top 5 cities for investment"  → intent: RANKING, params: {n: 5, sort_by: investment}
"land price in Chennai 2050"   → intent: PRICE_LOOKUP, entities: [Chennai], params: {year: 2050}
```

Our rule-based approach uses ordered regex matching:
1. Try `compare X (vs|and|with) Y` pattern
2. Try `(best|top|rank)` pattern
3. Try city name + price keywords
4. Try city name + climate keywords
5. Try filter patterns (`aqi < X`, `price under X`)
6. Fall through to "couldn't understand"

**Limitations:** Regex-based intent recognition is brittle. It can't handle paraphrasing ("which city should I invest in?" vs "top cities for investment"), negation ("cities NOT in Tier 1"), or complex multi-part queries. The LLM tier handles these cases when available.

---

## Summary: How Each Module Affects City Scores

```
                    ┌─── Climate Baselines ─── validate seed temps & rainfall
  IMD Fetcher ──────┤
                    └─── CMIP6 Projections ─── replace linear warming model
                              │
                              ▼
                    ┌─── climate_risk_score() ──► Liveability (20%) + Sustainability (25%)
  Climate Analysis ─┤
                    └─── projected_temp_rise ──► Sustainability: Climate Resilience (25%)
                              │
                              ▼
                    ┌─── population estimates ──► validate seed pop_2025
  Census Fetcher ───┤
                    └─── migration flows ──────► identify growth cities for Investment
                              │
                              ▼
                    ┌─── growth_rate ──► Investment: Population Demand (20%)
  Population ───────┤
                    └─── saturation ratio ──► Sustainability: Population Pressure (15%)
                              │
                              ▼
                    ┌─── ML price projection ──► alternative to CAGR (not yet integrated into score)
  Land Price ML ────┤
                    └─── feature importance ──► insight into what drives prices
                              │
                              ▼
                    ┌─── flood_probability ──► alternative to categorical label (not yet in score)
  Flood Model ─────┤
                    └─── composite_hazard ──► richer risk metric than low/medium/high

  Preference ───────── personalized weights ──► replaces default 35/35/30 weighting
  Learner                                       for individual users
```

**Current state:** The fetchers validate seed data; the ML models provide alternative projections alongside (not replacing) the formula-based approaches. Full integration — where fetched data auto-updates seed data and ML predictions replace CAGR in the score — is the next phase.
