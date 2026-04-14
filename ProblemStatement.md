# Problem Statement

## Vision

Create a project that provides weather climate change prediction for cities in India, geographical advantage, related land price today and prediction over each year, current population vs predicted population. With these details, clearly rate the most sustainable and liveable cities, cities where I should buy land today and evaluation of this land price over the years — considering past, present and future till 2050, 2070.

---

## Original Requirements

### Factors Influencing Liveability

- Population
- IT sector influence
- Transport
- Climate change
- Land price
- Geographical location

### Dashboard Requirements

- Filter cities based on countries
- Filter cities based on population
- Filter most sustainable cities based on rating and comparison
- Agriculture land (that can be maintained by trusted parties)

---

## Data Requirements

1. **List of cities country-wise** — open source database
2. **Population / occupant details** for each of the countries
3. **Government plans** on cities — metro work done, transportation available
4. **Geographical location and climate change** — current and projections
5. **Current land price and continuous changes** — historical and projected

---

## Data Sources Identified

### Cities & Population
- https://www.worldometers.info/ — along with population
- https://simplemaps.com/data/world-cities — free CSV download
- Wikipedia — https://en.wikipedia.org/wiki/Lists_of_cities_by_country — list of cities
- GitHub repository — https://github.com/dr5hn/countries-states-cities-database

### Climate & Geography
- India Meteorological Department (IMD)
- IPCC AR6 South Asia regional projections (RCP 4.5 pathway)

### Land Price
- National Real Estate Development Council (NAREDCO)
- Smart Cities Mission data
- Regional real estate market reports

### Infrastructure
- Smart Cities Mission portal
- Census of India 2011
- Metro and transport authority data

---

## Key Questions to Answer

1. Which are the most liveable cities in India today?
2. Which cities will remain sustainable through 2050 and 2070?
3. Where should I buy land today for maximum ROI?
4. How will climate change impact each city differently?
5. Which cities are approaching population saturation?
6. What is the relationship between infrastructure investment and land price growth?

---

## Scope

### Phase 1 (Current)
- 20 major Indian cities (Tier 1, 2, 3)
- Climate projections using IPCC RCP 4.5 pathway
- Land price CAGR-based projections
- Population logistic growth modeling
- Composite scoring engine (Liveability + Sustainability + Investment)

### Phase 2 (Future)
- Expand to all Indian cities
- Integrate real-time data APIs (weather, AQI, real estate)
- Interactive web dashboard with filters and visualizations
- Global city comparison
- Agriculture land analysis with trusted party maintenance model

### Phase 3
- Expand to all areas within the cities
- Create downloadable csv in project assets folder