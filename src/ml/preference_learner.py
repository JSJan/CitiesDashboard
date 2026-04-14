"""
Preference Learning — learns optimal scoring weights from user
feedback to personalize city/area recommendations.

Approaches:
  1. Weighted preference aggregation: user rates cities they like,
     system learns which factors matter most to them
  2. Pairwise comparison: "Do you prefer City A or City B?"
     → derives implicit weights
  3. Constraint satisfaction: "I need AQI < 100 and price < ₹8000/sqft"
     → filters + re-ranks

Requires: scikit-learn
"""

import json
import os
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
PREFS_FILE = os.path.join(DATA_DIR, "user_preferences.json")


class PreferenceLearner:
    """
    Learns personalized scoring weights from user feedback.
    """

    # Default weights (same as scoring_engine.py)
    DEFAULT_WEIGHTS = {
        "liveability": 0.35,
        "sustainability": 0.35,
        "investment": 0.30,
    }

    # Sub-factor weights for liveability
    LIVEABILITY_FACTORS = [
        "climate_comfort", "infrastructure", "air_quality",
        "green_cover", "water_supply", "density", "disaster_safety",
    ]

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.weights = self.DEFAULT_WEIGHTS.copy()
        self.feedback_history = []
        self.constraints = {}
        self._load()

    def _load(self):
        """Load saved preferences."""
        if os.path.exists(PREFS_FILE):
            with open(PREFS_FILE, "r") as f:
                all_prefs = json.load(f)
            if self.user_id in all_prefs:
                prefs = all_prefs[self.user_id]
                self.weights = prefs.get("weights", self.DEFAULT_WEIGHTS.copy())
                self.feedback_history = prefs.get("feedback", [])
                self.constraints = prefs.get("constraints", {})

    def save(self):
        """Save preferences to disk."""
        os.makedirs(DATA_DIR, exist_ok=True)
        all_prefs = {}
        if os.path.exists(PREFS_FILE):
            with open(PREFS_FILE, "r") as f:
                all_prefs = json.load(f)

        all_prefs[self.user_id] = {
            "weights": self.weights,
            "feedback": self.feedback_history,
            "constraints": self.constraints,
            "updated_at": datetime.now().isoformat(),
        }

        with open(PREFS_FILE, "w") as f:
            json.dump(all_prefs, f, indent=2)

    def add_city_rating(self, city_name: str, rating: float):
        """
        User rates a city 1-10. Used to learn which factors
        correlate with what they value.
        """
        self.feedback_history.append({
            "type": "rating",
            "city": city_name,
            "rating": rating,
            "timestamp": datetime.now().isoformat(),
        })
        self.save()

    def add_pairwise_preference(self, preferred: str, over: str):
        """User prefers city A over city B."""
        self.feedback_history.append({
            "type": "pairwise",
            "preferred": preferred,
            "over": over,
            "timestamp": datetime.now().isoformat(),
        })
        self.save()

    def set_constraint(self, key: str, operator: str, value: float):
        """
        Set a hard constraint.
        Examples:
          set_constraint("aqi", "<", 100)
          set_constraint("price_per_sqft", "<", 8000)
          set_constraint("green_cover_pct", ">", 10)
        """
        self.constraints[key] = {"operator": operator, "value": value}
        self.save()

    def clear_constraints(self):
        self.constraints = {}
        self.save()

    def learn_weights(self, cities: list) -> Dict[str, float]:
        """
        Learn optimal weights from user ratings using linear regression.
        Maps city scores to user ratings to find which factors matter most.
        """
        ratings = [
            fb for fb in self.feedback_history
            if fb["type"] == "rating"
        ]

        if len(ratings) < 3:
            return self.weights  # need at least 3 ratings

        from sklearn.linear_model import Ridge

        city_map = {c.name: c for c in cities}
        X = []
        y = []

        for fb in ratings:
            city = city_map.get(fb["city"])
            if city and city.liveability_score is not None:
                X.append([
                    city.liveability_score,
                    city.sustainability_score,
                    city.investment_score,
                ])
                y.append(fb["rating"])

        if len(X) < 3:
            return self.weights

        X = np.array(X)
        y = np.array(y)

        # Ridge regression to find weight mapping
        model = Ridge(alpha=1.0, positive=True)
        model.fit(X, y)

        # Normalize coefficients to sum to 1
        coefs = np.abs(model.coef_)
        total = coefs.sum()
        if total > 0:
            coefs = coefs / total

        self.weights = {
            "liveability": round(float(coefs[0]), 3),
            "sustainability": round(float(coefs[1]), 3),
            "investment": round(float(coefs[2]), 3),
        }
        self.save()
        return self.weights

    def apply_constraints(self, cities: list) -> list:
        """Filter cities by user constraints."""
        filtered = list(cities)

        constraint_map = {
            "aqi": lambda c, v, op: _compare(c.climate.air_quality_index, v, op),
            "price_per_sqft": lambda c, v, op: _compare(c.land_price.avg_price_per_sqft_2025, v, op),
            "green_cover_pct": lambda c, v, op: _compare(c.infrastructure.green_cover_pct, v, op),
            "population": lambda c, v, op: _compare(c.population.population_2025, v, op),
            "growth_rate": lambda c, v, op: _compare(c.population.growth_rate_pct, v, op),
            "tier": lambda c, v, op: _compare(c.tier, v, op),
            "flood_risk": lambda c, v, op: c.geo.flood_risk != "high" if op == "!=" else True,
        }

        for key, constraint in self.constraints.items():
            if key in constraint_map:
                filtered = [
                    c for c in filtered
                    if constraint_map[key](c, constraint["value"], constraint["operator"])
                ]

        return filtered

    def personalized_ranking(self, cities: list) -> list:
        """
        Re-rank cities using learned weights + constraints.
        Returns sorted list of (city, personalized_score) tuples.
        """
        filtered = self.apply_constraints(cities)

        results = []
        for city in filtered:
            if city.liveability_score is None:
                continue
            score = (
                city.liveability_score * self.weights["liveability"] +
                city.sustainability_score * self.weights["sustainability"] +
                city.investment_score * self.weights["investment"]
            )
            results.append((city, round(score, 1)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def get_profile_summary(self) -> Dict:
        """Get summary of user's preference profile."""
        return {
            "user_id": self.user_id,
            "weights": self.weights,
            "constraints": self.constraints,
            "total_ratings": sum(1 for f in self.feedback_history if f["type"] == "rating"),
            "total_comparisons": sum(1 for f in self.feedback_history if f["type"] == "pairwise"),
        }


def _compare(actual, target, operator: str) -> bool:
    """Compare actual vs target using operator string."""
    ops = {
        "<": lambda a, b: a < b,
        "<=": lambda a, b: a <= b,
        ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b,
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
    }
    return ops.get(operator, lambda a, b: True)(actual, target)
