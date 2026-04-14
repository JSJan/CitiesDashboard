"""
Automated Report Generator — creates narrative reports and
investment memos for cities and areas.

Works with or without LLM:
  - With OpenAI: generates rich narrative text from data
  - Without: uses template-based report generation

Output formats: Markdown, plain text
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional


REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "reports")


class ReportGenerator:
    """Generate narrative reports for cities and areas."""

    def __init__(self, cities: list = None, areas: list = None):
        self.cities = cities or []
        self.areas = areas or []
        self.openai_client = None
        self._init_openai()

    def _init_openai(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return
        try:
            import openai
            self.openai_client = openai.OpenAI(api_key=api_key)
        except ImportError:
            pass

    def generate_city_report(self, city_name: str) -> str:
        """Generate a comprehensive report for a single city."""
        city = next((c for c in self.cities if c.name == city_name), None)
        if not city:
            return f"City '{city_name}' not found."

        from src.climate_analysis import climate_risk_score
        from src.population_analysis import estimate_carrying_capacity

        data = {
            "name": city.name,
            "state": city.state,
            "tier": city.tier,
            "liveability": city.liveability_score,
            "sustainability": city.sustainability_score,
            "investment": city.investment_score,
            "climate_risk": climate_risk_score(city),
            "price_2025": city.land_price.avg_price_per_sqft_2025,
            "price_2050": city.land_price.projected_price_2050,
            "price_2070": city.land_price.projected_price_2070,
            "cagr": city.land_price.cagr_2015_2025,
            "population_2025": city.population.population_2025,
            "population_2050": city.population.projected_2050,
            "carrying_cap": estimate_carrying_capacity(city),
            "aqi": city.climate.air_quality_index,
            "aqi_2050": city.climate.projected_aqi_2050,
            "temp": city.climate.avg_temp_c,
            "temp_rise_2050": city.climate.projected_temp_rise_2050,
            "flood_risk": city.geo.flood_risk,
            "cyclone_risk": city.climate.cyclone_risk,
        }

        if self.openai_client:
            return self._llm_city_report(data)
        return self._template_city_report(data)

    def _template_city_report(self, d: Dict) -> str:
        """Template-based city report (no LLM needed)."""
        roi_2050 = round((d["price_2050"] - d["price_2025"]) / d["price_2025"] * 100, 1)
        roi_2070 = round((d["price_2070"] - d["price_2025"]) / d["price_2025"] * 100, 1)
        saturation = round(d["population_2025"] / d["carrying_cap"] * 100, 1)
        pop_growth = round((d["population_2050"] - d["population_2025"]) / d["population_2025"] * 100, 1)

        # Investment recommendation
        if d["investment"] and d["investment"] > 65:
            rec = "**Strong Buy** — High growth potential with strong fundamentals."
        elif d["investment"] and d["investment"] > 50:
            rec = "**Buy** — Good growth potential with acceptable risk."
        elif d["investment"] and d["investment"] > 35:
            rec = "**Hold** — Moderate potential; consider if other factors align."
        else:
            rec = "**Avoid** — Risk-adjusted returns may not justify investment."

        # Risk assessment
        risks = []
        if d["flood_risk"] == "high":
            risks.append("High flood risk may impact property values")
        if d["climate_risk"] > 60:
            risks.append("Significant climate change exposure")
        if d["aqi"] > 150:
            risks.append("Poor air quality may deter residents")
        if saturation > 80:
            risks.append("Approaching population carrying capacity")

        risk_text = "\n".join(f"- {r}" for r in risks) if risks else "- No major risk factors identified"

        report = f"""# {d['name']} — City Investment & Liveability Report

**Generated:** {datetime.now().strftime('%Y-%m-%d')}  
**State:** {d['state']} | **Tier:** {d['tier']}

---

## Scores Summary

| Metric | Score |
|--------|-------|
| Liveability | {d['liveability']:.1f} / 100 |
| Sustainability | {d['sustainability']:.1f} / 100 |
| Investment | {d['investment']:.1f} / 100 |
| Climate Risk | {d['climate_risk']:.1f} / 100 |

---

## Land Price Analysis

- **Current Price (2025):** ₹{d['price_2025']:,.0f}/sqft
- **Projected 2050:** ₹{d['price_2050']:,.0f}/sqft (ROI: +{roi_2050}%)
- **Projected 2070:** ₹{d['price_2070']:,.0f}/sqft (ROI: +{roi_2070}%)
- **Historical CAGR:** {d['cagr']}%

### Investment Recommendation

{rec}

---

## Climate Outlook

- **Current Avg Temperature:** {d['temp']}°C → **2050:** {d['temp'] + d['temp_rise_2050']:.1f}°C (+{d['temp_rise_2050']}°C)
- **Air Quality (AQI):** {d['aqi']} → **2050:** {d['aqi_2050']}
- **Flood Risk:** {d['flood_risk'].title()}
- **Cyclone Risk:** {d['cyclone_risk'].title()}

---

## Population Outlook

- **Current (2025):** {d['population_2025']:,}
- **Projected 2050:** {d['population_2050']:,} (+{pop_growth}%)
- **Carrying Capacity:** {d['carrying_cap']:,}
- **Saturation:** {saturation}%

---

## Key Risks

{risk_text}

---

*Disclaimer: This report is based on projected data and should not be used as sole basis for investment decisions.*
"""
        return report

    def _llm_city_report(self, data: Dict) -> str:
        """LLM-enhanced city report."""
        prompt = (
            f"Write a professional investment analysis report for {data['name']}, India. "
            f"Data: {json.dumps(data)}. "
            f"Include: executive summary, investment recommendation (buy/hold/avoid), "
            f"climate risk assessment, growth outlook, and key risks. "
            f"Use markdown formatting. Be specific with numbers."
        )

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a senior real estate and urban planning analyst."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception:
            return self._template_city_report(data)

    def generate_all_city_reports(self) -> Dict[str, str]:
        """Generate reports for all cities. Returns {city_name: report_text}."""
        reports = {}
        for city in self.cities:
            print(f"  Generating report for {city.name}...")
            reports[city.name] = self.generate_city_report(city.name)
        return reports

    def generate_executive_summary(self) -> str:
        """Generate an executive summary across all cities."""
        from src.scoring_engine import generate_master_ranking

        df = generate_master_ranking(self.cities)
        top_3 = df.head(3)
        bottom_3 = df.tail(3)

        top_names = ", ".join(top_3["City"].tolist())
        bottom_names = ", ".join(bottom_3["City"].tolist())

        # Best investment
        from src.scoring_engine import get_top_cities_to_buy
        buy_df = get_top_cities_to_buy(self.cities, top_n=3)
        buy_names = ", ".join(buy_df["City"].tolist()) if "City" in buy_df.columns else "N/A"

        summary = f"""# India Cities Dashboard — Executive Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d')}  
**Cities Analyzed:** {len(self.cities)}

---

## Top Rated Cities

The top 3 cities by overall score are: **{top_names}**

## Best Investment Opportunities

Top cities to buy land today: **{buy_names}**

## Key Findings

- **{len([c for c in self.cities if c.tier == 1])} Tier-1 metros** analyzed alongside **{len([c for c in self.cities if c.tier in [2, 3]])} Tier-2/3 cities**
- Average land price across all cities: ₹{sum(c.land_price.avg_price_per_sqft_2025 for c in self.cities) / len(self.cities):,.0f}/sqft
- Cities with highest climate risk: {', '.join(c.name for c in sorted(self.cities, key=lambda c: getattr(c, 'climate_risk_val', 0), reverse=True)[:3]) if hasattr(self.cities[0], 'climate_risk_val') else 'See climate report'}

---

*Full city-level reports available via `report_generator.generate_all_city_reports()`*
"""
        return summary

    def save_reports(self, reports: Dict[str, str]):
        """Save generated reports to data/reports/ directory."""
        os.makedirs(REPORT_DIR, exist_ok=True)
        for city_name, report in reports.items():
            filename = f"{city_name.lower().replace(' ', '_')}_report.md"
            filepath = os.path.join(REPORT_DIR, filename)
            with open(filepath, "w") as f:
                f.write(report)
        print(f"  Saved {len(reports)} reports to {REPORT_DIR}/")

    def generate_and_save_all(self):
        """Generate and save all reports + executive summary."""
        reports = self.generate_all_city_reports()
        reports["executive_summary"] = self.generate_executive_summary()
        self.save_reports(reports)
        return reports
