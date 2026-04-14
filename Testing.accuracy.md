# Testing, Accuracy & User Integration Guide

How the Cities Dashboard validates data, how accurate results are, and how LLM/user input works.

---

## 1. How We Test & Validate Data Correctness

### 1.1 Automated Test Suite — 50 Tests Across 9 Categories

We now have a comprehensive validation suite at `tests/test_validation.py` with **50 tests** covering:

| Category | Tests | What It Validates |
|----------|-------|-------------------|
| **Seed Data Integrity** | 13 | All 20 cities have valid ranges for temp (15–35°C), rainfall (300–3500mm), AQI (0–500), CAGR (0–25%), coordinates (within India), prices (positive & increasing), population (positive & growing), infrastructure scores (0–10), green cover (0–100%) |
| **Scoring Engine** | 8 | All scores are 0–100, overall = 35% live + 35% sustain + 30% invest (verified per-city), ranking is sorted descending, buy recommendations use valid ratings (Strong Buy/Buy/Hold/Avoid), Delhi liveability < Mysuru (AQI penalty) |
| **Climate Analysis** | 5 | Temperature increases over time, rise magnitude is 0.5–4°C by 2050 (IPCC plausible), climate risk 0–100, AQI projections don't decrease, coastal rainfall increases |
| **Land Price** | 5 | CAGR formula is mathematically correct, projected prices positive, investment scores 0–100, Monte Carlo percentiles ordered (P10 ≤ P25 ≤ P50 ≤ P75 ≤ P90), base year P50 within 20% of actual |
| **Population** | 3 | Logistic growth bounded by carrying capacity, carrying capacity ≥ current pop, population increases for growing cities |
| **Census Data** | 3 | Census 2011 values match known reference ranges (Mumbai ~12.4M, Chennai ~4.68M), 2025 estimates > 2011 census, migration categories are valid |
| **ML Models** | 4 | Land price model trains and predicts positive values, R² > 0 (better than mean), flood model probabilities 0–1 and hazard 0–100, preference learner weights sum to 1.0 |
| **LLM Integration** | 6 | Ranking/compare/price queries return correct intents, unknown queries don't crash, template reports generate >100 chars, staleness detector runs |
| **Cross-Module Consistency** | 3 | Seed CAGR matches computed CAGR from 2015→2025 prices, population timelines are monotonically increasing, query engine ranking matches direct ranking |

**Run the tests:**
```bash
python tests/test_validation.py            # standalone (no pytest needed)
python -m pytest tests/ -v                 # with pytest
```

### 1.2 Data Validation Mechanisms Built Into the Code

| Mechanism | Where | What It Does |
|-----------|-------|--------------|
| **Score clamping** | `chennai_area_analysis.py`, `land_price_analysis.py` | `max(0, min(100, score))` ensures scores never go outside 0–100 |
| **Probability clipping** | `flood_model.py` | `np.clip(..., 0, 1)` ensures flood/heat probabilities stay in 0–1 |
| **Null/existence guards** | All scrapers and fetchers | Check `if not data`, `if "key" not in data` before processing API responses |
| **Seed vs API cross-check** | `staleness_detector.py` → `check_seed_data_accuracy()` | Compares hardcoded temperatures against Open-Meteo API data; flags if diff > 2°C or rainfall differs by > 20% |
| **Model training guards** | `population_model.py`, `land_price_model.py` | `if not self.trained` prevents prediction on untrained models |
| **Price range filter** | `real_estate_scraper.py` | Filters extracted prices to ₹500–₹200,000/sqft to remove outlier/garbage values |
| **Try/except per stage** | `pipeline.py` | Each pipeline stage is wrapped individually so one failure doesn't block others |

### 1.3 What Validation Is Missing (Honest Assessment)

| Gap | Impact | Mitigation |
|-----|--------|------------|
| **No schema validation** on seed data (e.g., Pydantic) | A typo in seed_data.py (e.g., AQI=8000) would propagate | Test suite catches range violations |
| **No input sanitization** on LLM queries | Prompt injection possible if OpenAI key is set | Rule-based fallback is safe; LLM mode trusts OpenAI's safety |
| **No integration tests** with live APIs | Can't verify API response format changes | Scrapers have try/except; staleness detector flags missing data |
| **No regression tests** | Score changes after code edits go undetected | Cross-module consistency tests catch formula drift |

---

## 2. How Accurate Are the Results?

### 2.1 Accuracy by Module

| Module | Accuracy Assessment | Evidence | Confidence |
|--------|-------------------|----------|------------|
| **Scoring Engine** | ⭐⭐⭐⭐ High (for what it does) | Formulas are transparent, weighted, and produce sensible rankings (Mysuru #1, Delhi near bottom) | High — formulas are deterministic and tested |
| **Climate Projections** | ⭐⭐⭐ Moderate | Linear 0.25°C/decade is within IPCC SSP2-4.5 range for India, but oversimplified | Medium — CMIP6 data from IMD fetcher is more accurate |
| **Land Price (CAGR)** | ⭐⭐ Low for 25+ years | CAGR assumes constant growth; real markets have crashes, booms, policy shocks | Low beyond 10 years — Monte Carlo adds uncertainty bands |
| **Land Price (ML)** | ⭐⭐ Misleading | R²=0.93, but 98% of importance is `time` + `current_price` — effectively CAGR with extra steps | Low — trained on own projections, not real historical data |
| **Population (Logistic)** | ⭐⭐⭐ Moderate | Logistic S-curve is standard for city growth; carrying capacity is estimated, not measured | Medium — better than exponential, worse than agent-based models |
| **Population (MLP)** | ⭐ Non-functional | R² = −0.78 (worse than predicting the mean) | None — logistic model is the real approach |
| **Flood Model** | ⭐ Non-functional | R² = −0.37 (20 samples, 11 features = can't learn) | None — categorical labels from seed data are more reliable |
| **Census Data** | ⭐⭐⭐⭐ High (but dated) | Official Census 2011 values are authoritative, but 15 years old | High for 2011, decreasing for 2025 estimates |

### 2.2 ML Model Metrics (from `data/models/`)

| Model | R² (mean ± std) | Samples | Features | Verdict |
|-------|-----------------|---------|----------|---------|
| **Land Price** | 0.9258 ± 0.1033 | 140 | 12 | Usable but misleading — dominated by time (74%) and current price (24%) |
| **Flood** | −0.3737 | 20 | 11 | **Non-functional** — worse than always predicting the average |
| **Flood (Heat)** | 0.4568 | 20 | 11 | Weak — barely better than mean |
| **Population** | −0.7822 ± 2.2971 | 140 | 14 | **Non-functional** — extreme instability |

**What R² means:**
- R² = 1.0: Perfect predictions
- R² = 0.0: Model is equivalent to always predicting the mean
- R² < 0.0: Model is **worse** than predicting the mean (actively harmful predictions)

### 2.3 Why the ML Models Struggle

**Root cause: insufficient and circular training data.**

```
The core problem:

  Seed Data (CAGR formula) ──► Training Targets (projected prices)
         │                              ▲
         │                              │
         └──► ML Model trains on ───────┘

  The ML model is trying to learn the output of the formula
  that generated the training data. It cannot outperform the formula.
```

**To get genuinely better ML predictions, we need:**
1. Real historical monthly prices from 99acres scraper (months of pipeline runs)
2. Ward-level or area-level data (30 Chennai areas × 20 cities = 600 samples for flood model)
3. External features the seed data doesn't capture (interest rates, GDP, infrastructure timelines)

### 2.4 Accuracy Improvement Path

| Current State | What Would Improve It | Expected Accuracy Gain |
|--------------|----------------------|----------------------|
| CAGR extrapolation for prices | Monthly price time-series from 99acres | +20-30% for 5-10 year projections |
| Linear 0.25°C/decade warming | Use CMIP6 data from `imd_fetcher.py` directly in scoring | +15-20% for climate predictions |
| Census 2011 population | Annual population estimates from state registries | +10-15% for population projections |
| 20-sample flood model | Area-level flood data (ward boundaries + flood history) | R² could go from −0.37 to 0.60+ |
| Keyword sentiment analysis | LLM-powered article sentiment (with OpenAI) | +30-40% sentiment accuracy |

---

## 3. How LLM Integration Works

### 3.1 Architecture: Two-Tier Query System

```
User Question (string)
        │
        ▼
   ┌─────────────────┐
   │  OPENAI_API_KEY  │──── set? ───► Tier 1: LLM Function Calling
   │   in env vars?   │                  │
   └─────────────────┘                   │
        │ not set                        ▼
        ▼                    ┌──────────────────────┐
   Tier 2: Rule-Based       │ gpt-4o-mini receives  │
   Regex Parsing             │ question + 6 tool     │
        │                    │ definitions           │
        ▼                    └──────────────────────┘
   Pattern Match:                        │
   • "compare X and Y"                  ▼
   • "top N cities for X"          LLM picks tool:
   • "price in <city>"            get_city_ranking()
   • "climate in <city>"         compare_cities()
   • "AQI < N, price < N"       get_land_price_info()
   • "Chennai areas"             filter_cities()
        │                        get_chennai_areas()
        ▼                        get_climate_analysis()
   Execute tool function                 │
        │                                ▼
        ▼                    Execute same tool function
   Return structured data          │
   {answer, data, method}         ▼
                             LLM generates natural
                             language response
                                    │
                                    ▼
                             Return {answer, data, method}
```

### 3.2 The 6 Tools Available to the LLM

| Tool | What It Does | Underlying Function |
|------|-------------|-------------------|
| `get_city_ranking` | Top N cities sorted by any score dimension | `generate_master_ranking()` |
| `compare_cities` | Side-by-side comparison of 2-4 cities | Collects scores + prices + climate per city |
| `get_land_price_info` | Price lookup for a city at a target year | Returns current, projected, ROI, CAGR |
| `filter_cities` | Filter by constraints (AQI < X, price < Y) | Iterates cities, applies numeric filters |
| `get_chennai_areas` | Top areas to buy in Chennai | `get_top_areas_to_buy()` |
| `get_climate_analysis` | Climate risk breakdown for a city | `climate_risk_score()` + projections |

### 3.3 Rule-Based Fallback (No API Key Needed)

The regex-based parser handles the most common queries without any API:

```python
# Pattern: "compare Mumbai and Bengaluru"
r'compare\s+(\w+)\s+(?:vs|and|with)\s+(\w+)'

# Pattern: "top 5 cities for investment"  
r'(best|top|rank)' → extracts N from r'top\s+(\d+)'

# Pattern: "land price in Chennai by 2050"
city detected + "price" keyword → extracts year from r'20[2-7]\d'

# Pattern: "cities with AQI under 80 and price below 5000"
r'aqi\s*(?:<|under|below)\s*(\d+)' → numeric filter
```

**Coverage:** Rule-based mode handles ~80% of typical queries. It fails on paraphrased questions ("where should I invest?" vs "top cities for investment"), multi-part queries, and conversations.

### 3.4 Report Generation (Template vs LLM)

| Aspect | Template Mode (default) | LLM Mode (with OpenAI) |
|--------|------------------------|----------------------|
| **Trigger** | No `OPENAI_API_KEY` set | `OPENAI_API_KEY` is set |
| **Output** | Structured Markdown with sections: Scores, Price Analysis, Climate, Population, Risks, Recommendation | Narrative prose from "senior real estate analyst" persona |
| **Determinism** | Same city → identical report every time | Varies between runs (LLM temperature) |
| **Cost** | Free | ~$0.002 per report (gpt-4o-mini) |
| **Quality** | Functional but robotic | Natural, contextual, but may hallucinate |
| **Fallback** | N/A | Falls back to template on any error |

---

## 4. How User Input Is Provided

### 4.1 Three Input Channels

#### Channel 1: Streamlit Dashboard (`dashboard.py`)

Interactive web UI with the following input widgets:

| Widget | Type | What It Controls |
|--------|------|-----------------|
| Page selector | `st.sidebar.radio` | Navigate 7 pages (Ranking, Comparison, Climate, etc.) |
| Tier filter | `st.sidebar.multiselect` | Filter cities by tier [1, 2, 3] |
| State filter | `st.sidebar.multiselect` | Filter by state |
| Price range | `st.sidebar.slider` | Min–max ₹/sqft filter |
| Min score | `st.sidebar.slider` | Minimum overall score threshold |
| City comparison | `st.multiselect` | Select 2–4 cities for radar chart |
| Monte Carlo city | `st.selectbox` | Pick city for price simulation |
| Zone filter | `st.multiselect` | Filter Chennai areas by zone |
| Investment mode | `st.radio` | City vs Chennai Area investment |
| City/Area selectors | `st.selectbox` | Pick city/area for investment calculator |
| Investment area | `st.number_input` | Area in sq ft for ROI calculation |

**Note:** The LLM query engine is **not yet wired** into the dashboard — there's no text input for natural language questions in the Streamlit UI.

#### Channel 2: CLI (`main.py`)

```bash
python main.py --report all              # Full dashboard (default)
python main.py --report climate           # Climate analysis only
python main.py --report land              # Land price analysis
python main.py --report population        # Population projections
python main.py --report ranking           # Master city ranking
python main.py --report buy               # Top cities to buy land
python main.py --report chennai           # Chennai areas analysis
python main.py --report export            # Export 11 CSVs
python main.py --city Mumbai              # Deep dive into a city
python main.py --report climate --live    # Fetch live API data first
```

#### Channel 3: Python API (programmatic)

```python
# Query Engine
from src.llm.query_engine import QueryEngine
qe = QueryEngine(cities)
result = qe.query("top 5 cities for investment")

# Preference Learner
from src.ml.preference_learner import PreferenceLearner
pl = PreferenceLearner()
pl.add_city_rating("Bengaluru", 9)     # Rate cities 1-10
pl.add_city_rating("Mumbai", 6)
pl.set_constraint("aqi", "<", 100)      # Hard constraints
weights = pl.learn_weights(cities)       # Learn personalized weights
ranking = pl.personalized_ranking(cities)  # Re-rank with your preferences

# Pipeline
python -m src.scrapers.pipeline run      # Fetch all data + retrain models
python -m src.scrapers.pipeline status   # Check data freshness
python -m src.scrapers.pipeline watch    # Auto-run every 24 hours
```

### 4.2 User Input → Score Impact Flow

```
User rates cities (Preference Learner)
    │
    ▼
Ridge Regression learns weights
    │
    ▼
Replaces default 35/35/30 → personalized weights
    │
    ▼
Cities re-ranked by: w1×Liveability + w2×Sustainability + w3×Investment
    │
    ▼
User sees personalized top cities

Example:
  Ratings: Bengaluru=9, Mysuru=8, Mumbai=6, Delhi=4
  Learned: liveability=0%, sustainability=34%, investment=66%
  "You prioritize sustainability and investment over generic liveability"
  New #1: Coimbatore (was #6 overall)
```

### 4.3 What's Not Yet Connected

| Feature | Status | How to Connect |
|---------|--------|---------------|
| LLM query in dashboard | API exists, not in Streamlit | Add `st.text_input` → `QueryEngine.query()` → display results |
| Preference learner in dashboard | API exists, not in Streamlit | Add rating widgets → `PreferenceLearner` → show personalized ranking |
| News sentiment in dashboard | API exists, not in Streamlit | Add news page → `monitor_all_cities()` → sentiment charts |
| ML predictions in dashboard | Models exist, not visualized | Add ML vs CAGR comparison charts to Land Price page |
| Report download | Generator exists, not in Streamlit | Add `st.download_button` → `generate_city_report()` |

---

## 5. Running the Full Validation

```bash
# Run all 50 validation tests
python tests/test_validation.py

# Check data freshness
python -m src.scrapers.pipeline status

# Run full pipeline (fetch data + retrain models + check staleness)
python -m src.scrapers.pipeline run

# Query the system
python -c "
from src.seed_data import get_all_cities
from src.scoring_engine import compute_all_scores
from src.llm.query_engine import QueryEngine
cities = get_all_cities(); compute_all_scores(cities)
qe = QueryEngine(cities)
print(qe.query('top 5 cities for investment'))
"
```
