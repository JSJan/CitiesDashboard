"""
Natural Language Query Engine — LLM-powered interface that lets users
ask questions in plain English and get structured answers.

Supports:
  - City comparison queries ("Compare Mumbai vs Pune for retirement")
  - Filter queries ("Cities with AQI < 80 and price under 5000")
  - Recommendation queries ("Best area in Chennai to buy land today")
  - Analytical queries ("How will climate change affect Bengaluru?")

LLM backends: Anthropic Claude (ANTHROPIC_API_KEY) or OpenAI (OPENAI_API_KEY).
Falls back to rule-based parsing when no API key is available.
"""

import os
import json
import re
from typing import Dict, List, Optional, Callable


# Tool definitions for OpenAI function calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_city_ranking",
            "description": "Get the master ranking of all cities with scores",
            "parameters": {
                "type": "object",
                "properties": {
                    "top_n": {"type": "integer", "description": "Number of top cities to return"},
                    "sort_by": {"type": "string", "enum": ["overall", "liveability", "sustainability", "investment"]},
                    "tier": {"type": "integer", "description": "Filter by tier (1, 2, or 3)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_cities",
            "description": "Compare 2-4 cities across all dimensions",
            "parameters": {
                "type": "object",
                "properties": {
                    "cities": {"type": "array", "items": {"type": "string"}, "description": "List of city names"},
                },
                "required": ["cities"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_land_price_info",
            "description": "Get land price details and projections for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "year": {"type": "integer", "description": "Target year for projection"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter_cities",
            "description": "Filter cities by constraints like AQI, price, tier, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_aqi": {"type": "number"},
                    "max_price": {"type": "number"},
                    "min_green_cover": {"type": "number"},
                    "tier": {"type": "integer"},
                    "no_flood_risk": {"type": "boolean"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_chennai_areas",
            "description": "Get Chennai area recommendations by zone or criteria",
            "parameters": {
                "type": "object",
                "properties": {
                    "zone": {"type": "string"},
                    "max_price": {"type": "number"},
                    "top_n": {"type": "integer"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_climate_analysis",
            "description": "Get climate change analysis and risk for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                },
                "required": ["city"],
            },
        },
    },
]


# Anthropic tool definitions (different schema format)
ANTHROPIC_TOOLS = [
    {
        "name": "get_city_ranking",
        "description": "Get the master ranking of all cities with scores",
        "input_schema": {
            "type": "object",
            "properties": {
                "top_n": {"type": "integer", "description": "Number of top cities to return"},
                "sort_by": {"type": "string", "enum": ["overall", "liveability", "sustainability", "investment"]},
                "tier": {"type": "integer", "description": "Filter by tier (1, 2, or 3)"},
            },
        },
    },
    {
        "name": "compare_cities",
        "description": "Compare 2-4 cities across all dimensions",
        "input_schema": {
            "type": "object",
            "properties": {
                "cities": {"type": "array", "items": {"type": "string"}, "description": "List of city names"},
            },
            "required": ["cities"],
        },
    },
    {
        "name": "get_land_price_info",
        "description": "Get land price details and projections for a city",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "year": {"type": "integer", "description": "Target year for projection"},
            },
            "required": ["city"],
        },
    },
    {
        "name": "filter_cities",
        "description": "Filter cities by constraints like AQI, price, tier, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "max_aqi": {"type": "number"},
                "max_price": {"type": "number"},
                "min_green_cover": {"type": "number"},
                "tier": {"type": "integer"},
                "no_flood_risk": {"type": "boolean"},
            },
        },
    },
    {
        "name": "get_chennai_areas",
        "description": "Get Chennai area recommendations by zone or criteria",
        "input_schema": {
            "type": "object",
            "properties": {
                "zone": {"type": "string"},
                "max_price": {"type": "number"},
                "top_n": {"type": "integer"},
            },
        },
    },
    {
        "name": "get_climate_analysis",
        "description": "Get climate change analysis and risk for a city",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
            },
            "required": ["city"],
        },
    },
]


class QueryEngine:
    """
    Natural language query engine with LLM function calling.
    Supports Anthropic Claude or OpenAI GPT. Falls back to rule-based parsing
    when no API key is available.
    """

    def __init__(self, cities: list = None, areas: list = None):
        self.cities = cities
        self.areas = areas
        self.openai_client = None
        self.anthropic_client = None
        self.llm_provider = None  # "anthropic" or "openai"
        self._init_llm()
        self._init_tools()

    def _init_llm(self):
        """Initialize LLM client — prefers Anthropic, then OpenAI."""
        # Try Anthropic first
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                self.llm_provider = "anthropic"
                return
            except ImportError:
                pass

        # Fall back to OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=api_key)
                self.llm_provider = "openai"
            except ImportError:
                pass

    def _init_tools(self):
        """Register tool functions."""
        self.tools: Dict[str, Callable] = {
            "get_city_ranking": self._tool_city_ranking,
            "compare_cities": self._tool_compare_cities,
            "get_land_price_info": self._tool_land_price,
            "filter_cities": self._tool_filter_cities,
            "get_chennai_areas": self._tool_chennai_areas,
            "get_climate_analysis": self._tool_climate_analysis,
        }

    def query(self, question: str) -> Dict:
        """
        Process a natural language query.
        Uses LLM if available, otherwise falls back to rule-based parsing.

        Returns:
            {"answer": str, "data": dict/list, "method": "llm"|"rules", "provider": str}
        """
        if self.anthropic_client:
            return self._query_with_anthropic(question)
        if self.openai_client:
            return self._query_with_llm(question)
        return self._query_with_rules(question)

    def _query_with_anthropic(self, question: str) -> Dict:
        """Use Anthropic Claude with tool use to answer queries."""
        system_prompt = (
            "You are an expert on Indian cities — sustainability, liveability, "
            "climate, land prices, and population. Use the provided tools to "
            "answer questions with data. Be concise and specific."
        )

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system_prompt,
                tools=ANTHROPIC_TOOLS,
                messages=[{"role": "user", "content": question}],
            )

            # Check if Claude wants to use tools
            tool_uses = [b for b in response.content if b.type == "tool_use"]

            if tool_uses:
                results = {}
                tool_results = []
                for tool_use in tool_uses:
                    fn_name = tool_use.name
                    fn_args = tool_use.input

                    if fn_name in self.tools:
                        result = self.tools[fn_name](**fn_args)
                        results[fn_name] = result
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": json.dumps(result, default=str),
                        })

                # Get final response with tool results
                final = self.anthropic_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    system=system_prompt,
                    tools=ANTHROPIC_TOOLS,
                    messages=[
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": response.content},
                        {"role": "user", "content": tool_results},
                    ],
                )
                # Extract text from response
                text_blocks = [b.text for b in final.content if b.type == "text"]
                return {
                    "answer": "\n".join(text_blocks) if text_blocks else None,
                    "data": results,
                    "method": "llm",
                    "provider": "anthropic",
                }

            # No tool use — direct text answer
            text_blocks = [b.text for b in response.content if b.type == "text"]
            return {
                "answer": "\n".join(text_blocks) if text_blocks else None,
                "data": None,
                "method": "llm",
                "provider": "anthropic",
            }

        except Exception as e:
            result = self._query_with_rules(question)
            result["llm_error"] = str(e)
            return result

    def _query_with_llm(self, question: str) -> Dict:
        """Use OpenAI function calling to answer queries."""
        messages = [
            {"role": "system", "content": (
                "You are an expert on Indian cities — sustainability, liveability, "
                "climate, land prices, and population. Use the provided tools to "
                "answer questions with data. Be concise and specific."
            )},
            {"role": "user", "content": question},
        ]

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )

            msg = response.choices[0].message

            # If tool calls were made, execute them
            if msg.tool_calls:
                results = {}
                for tool_call in msg.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)

                    if fn_name in self.tools:
                        result = self.tools[fn_name](**fn_args)
                        results[fn_name] = result

                        messages.append(msg.model_dump())
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result, default=str),
                        })

                # Get final response with tool results
                final = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                )
                return {
                    "answer": final.choices[0].message.content,
                    "data": results,
                    "method": "llm",
                }

            return {
                "answer": msg.content,
                "data": None,
                "method": "llm",
            }

        except Exception as e:
            # Fall back to rules
            result = self._query_with_rules(question)
            result["llm_error"] = str(e)
            return result

    def _query_with_rules(self, question: str) -> Dict:
        """Rule-based query parsing (no LLM needed)."""
        q = question.lower().strip()

        # Pattern: Compare X vs Y
        compare = re.findall(
            r'compare\s+(\w+)\s+(?:vs|and|with)\s+(\w+)', q
        )
        if compare:
            return {
                "answer": None,
                "data": self._tool_compare_cities(list(compare[0])),
                "method": "rules",
                "intent": "compare",
            }

        # Pattern: Best/top cities
        if re.search(r'(best|top|rank)', q):
            n = 5
            match = re.search(r'top\s+(\d+)', q)
            if match:
                n = int(match.group(1))

            tier = None
            tier_match = re.search(r'tier\s*(\d)', q)
            if tier_match:
                tier = int(tier_match.group(1))

            sort_by = "overall"
            if "invest" in q or "buy" in q:
                sort_by = "investment"
            elif "live" in q:
                sort_by = "liveability"
            elif "sustain" in q or "green" in q:
                sort_by = "sustainability"

            return {
                "answer": None,
                "data": self._tool_city_ranking(top_n=n, sort_by=sort_by, tier=tier),
                "method": "rules",
                "intent": "ranking",
            }

        # Pattern: Price/land queries
        city_match = self._find_city_in_query(q)
        if city_match and any(w in q for w in ["price", "land", "invest", "buy", "cost"]):
            year = 2050
            year_match = re.search(r'20[2-7]\d', q)
            if year_match:
                year = int(year_match.group())
            return {
                "answer": None,
                "data": self._tool_land_price(city=city_match, year=year),
                "method": "rules",
                "intent": "land_price",
            }

        # Pattern: Climate queries
        if city_match and any(w in q for w in ["climate", "weather", "temperature", "flood", "rain"]):
            return {
                "answer": None,
                "data": self._tool_climate_analysis(city=city_match),
                "method": "rules",
                "intent": "climate",
            }

        # Pattern: Filter queries (AQI < X, price < Y)
        filters = {}
        aqi_match = re.search(r'aqi\s*(?:<|under|below)\s*(\d+)', q)
        if aqi_match:
            filters["max_aqi"] = float(aqi_match.group(1))
        price_match = re.search(r'(?:price|cost)\s*(?:<|under|below)\s*[₹]?\s*([\d,]+)', q)
        if price_match:
            filters["max_price"] = float(price_match.group(1).replace(",", ""))
        if "no flood" in q or "flood safe" in q or "flood-safe" in q:
            filters["no_flood_risk"] = True

        if filters:
            return {
                "answer": None,
                "data": self._tool_filter_cities(**filters),
                "method": "rules",
                "intent": "filter",
            }

        # Pattern: Chennai areas
        if "chennai" in q and any(w in q for w in ["area", "zone", "locality"]):
            max_price = None
            pm = re.search(r'(?:under|below|<)\s*[₹]?\s*([\d,]+)', q)
            if pm:
                max_price = float(pm.group(1).replace(",", ""))
            return {
                "answer": None,
                "data": self._tool_chennai_areas(max_price=max_price),
                "method": "rules",
                "intent": "chennai_areas",
            }

        return {
            "answer": "I couldn't understand that query. Try asking about city rankings, "
                      "price comparisons, climate analysis, or Chennai area recommendations.",
            "data": None,
            "method": "rules",
            "intent": "unknown",
        }

    def _find_city_in_query(self, query: str) -> Optional[str]:
        """Find a city name mentioned in the query."""
        if not self.cities:
            return None
        for city in self.cities:
            if city.name.lower() in query:
                return city.name
        return None

    # --- Tool implementations ---

    def _tool_city_ranking(self, top_n: int = 10, sort_by: str = "overall",
                           tier: int = None) -> List[Dict]:
        from src.scoring_engine import generate_master_ranking
        cities = self.cities
        if tier:
            cities = [c for c in cities if c.tier == tier]

        df = generate_master_ranking(cities)
        sort_col = {
            "overall": "Overall Score",
            "liveability": "Liveability",
            "sustainability": "Sustainability",
            "investment": "Investment",
        }.get(sort_by, "Overall Score")

        if sort_col in df.columns:
            df = df.sort_values(sort_col, ascending=False)

        records = df.head(top_n).to_dict("records")
        # Normalize keys to lowercase/snake_case for consistent API
        normalized = []
        for r in records:
            normalized.append({k.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_per_"): v for k, v in r.items()})
        return normalized

    def _tool_compare_cities(self, cities: List[str]) -> List[Dict]:
        cities_lower = [name.lower() for name in cities]
        city_objs = [c for c in self.cities if c.name.lower() in cities_lower]
        results = []
        for c in city_objs:
            from src.climate_analysis import climate_risk_score
            results.append({
                "city": c.name, "tier": c.tier, "state": c.state,
                "liveability": c.liveability_score,
                "sustainability": c.sustainability_score,
                "investment": c.investment_score,
                "price_2025": c.land_price.avg_price_per_sqft_2025,
                "price_2050": c.land_price.projected_price_2050,
                "population_2025": c.population.population_2025,
                "aqi": c.climate.air_quality_index,
                "climate_risk": climate_risk_score(c),
                "flood_risk": c.geo.flood_risk,
            })
        return results

    def _tool_land_price(self, city: str, year: int = 2050) -> Dict:
        city_obj = next((c for c in self.cities if c.name == city), None)
        if not city_obj:
            return {"error": f"City '{city}' not found"}

        prices = {
            2025: city_obj.land_price.avg_price_per_sqft_2025,
            2030: city_obj.land_price.projected_price_2030,
            2040: city_obj.land_price.projected_price_2040,
            2050: city_obj.land_price.projected_price_2050,
            2070: city_obj.land_price.projected_price_2070,
        }
        current = city_obj.land_price.avg_price_per_sqft_2025
        target = prices.get(year, city_obj.land_price.projected_price_2050)
        roi = round((target - current) / current * 100, 1)

        return {
            "city": city, "current_price": current,
            "projected_price": target, "year": year,
            "roi_pct": roi, "cagr": city_obj.land_price.cagr_2015_2025,
            "all_prices": prices,
        }

    def _tool_filter_cities(self, max_aqi: float = None,
                            max_price: float = None,
                            min_green_cover: float = None,
                            tier: int = None,
                            no_flood_risk: bool = False) -> List[Dict]:
        filtered = list(self.cities)
        if max_aqi:
            filtered = [c for c in filtered if c.climate.air_quality_index <= max_aqi]
        if max_price:
            filtered = [c for c in filtered if c.land_price.avg_price_per_sqft_2025 <= max_price]
        if min_green_cover:
            filtered = [c for c in filtered if c.infrastructure.green_cover_pct >= min_green_cover]
        if tier:
            filtered = [c for c in filtered if c.tier == tier]
        if no_flood_risk:
            filtered = [c for c in filtered if c.geo.flood_risk != "high"]

        return [{"city": c.name, "tier": c.tier, "aqi": c.climate.air_quality_index,
                 "price": c.land_price.avg_price_per_sqft_2025,
                 "flood_risk": c.geo.flood_risk} for c in filtered]

    def _tool_chennai_areas(self, zone: str = None, max_price: float = None,
                            top_n: int = 10) -> List[Dict]:
        areas = self.areas or []
        if zone:
            areas = [a for a in areas if zone.lower() in a.zone.lower()]
        if max_price:
            areas = [a for a in areas if a.land_price.price_per_sqft_2025 <= max_price]

        from src.chennai_area_analysis import get_top_areas_to_buy
        df = get_top_areas_to_buy(areas, top_n=top_n)
        return df.to_dict("records")

    def _tool_climate_analysis(self, city: str) -> Dict:
        city_obj = next((c for c in self.cities if c.name == city), None)
        if not city_obj:
            return {"error": f"City '{city}' not found"}

        from src.climate_analysis import climate_risk_score
        return {
            "city": city,
            "current_temp": city_obj.climate.avg_temp_c,
            "temp_2050": city_obj.climate.avg_temp_c + city_obj.climate.projected_temp_rise_2050,
            "temp_2070": city_obj.climate.avg_temp_c + city_obj.climate.projected_temp_rise_2070,
            "rainfall_mm": city_obj.climate.avg_rainfall_mm,
            "aqi_current": city_obj.climate.air_quality_index,
            "aqi_2050": city_obj.climate.projected_aqi_2050,
            "flood_risk": city_obj.geo.flood_risk,
            "cyclone_risk": city_obj.climate.cyclone_risk,
            "climate_risk_score": climate_risk_score(city_obj),
        }
