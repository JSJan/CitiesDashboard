# India Cities Dashboard

**Sustainability • Liveability • Climate • Land Investment • Population**  
Projections: 2025 → 2050 → 2070

## Overview

A data-driven analysis project that rates Indian cities across multiple dimensions to help identify the most sustainable, liveable, and investment-worthy cities. Covers **20 major cities** across Tier 1, 2, and 3 categories.

## What This Project Answers

1. **Which cities are most liveable and sustainable?** — Composite scoring across climate, infrastructure, air quality, green cover, water supply, and population density
2. **Where should I buy land today?** — Investment recommendations based on price growth potential, sustainability fundamentals, and affordability
3. **How will climate change affect each city?** — Temperature rise, rainfall changes, AQI degradation, flood/cyclone risk through 2050 and 2070
4. **How will land prices evolve?** — Historical CAGR analysis with projections to 2050 and 2070, ROI calculations
5. **How will population change?** — Logistic growth modeling with carrying capacity analysis

## Reports Available

| Report | Command | Description |
|--------|---------|-------------|
| Full Dashboard | `python main.py` | All reports combined |
| Climate Analysis | `python main.py --report climate` | Temperature, rainfall, AQI, risk scoring |
| Land Prices | `python main.py --report land` | Price history, CAGR, ROI projections |
| Population | `python main.py --report population` | Growth rates, density, carrying capacity |
| Master Ranking | `python main.py --report ranking` | Overall city scoring and ranking |
| Buy Recommendations | `python main.py --report buy` | Top cities to invest in today |
| City Deep Dive | `python main.py --city Chennai` | Detailed analysis for one city |

## Cities Covered (20)

**Tier 1:** Mumbai, Delhi, Bengaluru, Chennai, Hyderabad, Kolkata, Pune, Ahmedabad  
**Tier 2:** Coimbatore, Jaipur, Lucknow, Chandigarh, Kochi, Indore, Thiruvananthapuram, Visakhapatnam  
**Tier 3:** Mysuru, Vadodara, Bhubaneswar

## Scoring Methodology

### Liveability Score (0-100)

- Climate comfort (20%) — inverted climate risk
- Infrastructure quality (25%) — healthcare, education, transport, water
- Air quality (15%) — current AQI levels
- Green cover (10%) — percentage of urban green space
- Water supply (10%) — water reliability
- Population density (10%) — congestion penalty for overcrowded cities
- Natural disaster safety (10%) — flood and cyclone risk

### Sustainability Score (0-100)

- Climate resilience (25%) — projected warming severity
- Water security (20%) — rainfall + water supply reliability
- Green cover (15%) — environmental health
- Population pressure (15%) — saturation level vs carrying capacity
- Air quality trend (15%) — AQI trajectory through 2050
- Food security (10%) — terrain suitability for agriculture

### Investment Score (0-100)

- Historical growth momentum (25%) — past CAGR performance
- Affordability (20%) — cheaper cities have more upside
- Infrastructure potential (20%) — metro, airport, IT hub
- Population demand pressure (20%) — growth driving prices
- Climate risk discount (-15%) — risk reduces attractiveness

### Overall Score

`Overall = Liveability (35%) + Sustainability (35%) + Investment (30%)`

## Project Structure

```
├── main.py                     # Entry point - generates all reports
├── requirements.txt            # Python dependencies
├── src/
│   ├── models.py               # Data models (CityProfile, ClimateData, etc.)
│   ├── seed_data.py            # Seed data for 20 Indian cities
│   ├── climate_analysis.py     # Climate risk scoring & projections
│   ├── land_price_analysis.py  # Land price CAGR & ROI analysis
│   ├── population_analysis.py  # Population logistic growth modeling
│   └── scoring_engine.py       # Composite scoring & ranking engine
├── Prompts/                    # Project prompts
└── PromptEngineering/          # Learning notes
```

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## Data Sources Referenced

- Census of India 2011
- India Meteorological Department (IMD)
- IPCC AR6 South Asia regional projections (RCP 4.5 pathway)
- National Real Estate Development Council (NAREDCO)
- Smart Cities Mission data
- [World population data](https://www.worldometers.info/)
- [World cities database](https://simplemaps.com/data/world-cities)
- [Countries-States-Cities DB](https://github.com/dr5hn/countries-states-cities-database)

## Disclaimer

This analysis uses publicly available data and projection models. Land prices and population projections are estimates based on historical trends and IPCC climate scenarios. **This is NOT financial or investment advice.** Always consult professionals before making investment decisions.
