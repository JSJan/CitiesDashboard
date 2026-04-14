"""
Flood & Extreme Weather Prediction Model — predicts flood and
extreme weather event probability per city/area.

Uses gradient boosting on geographic, climate, and infrastructure features
to estimate:
  - Annual flood probability (0-1)
  - Extreme heat wave frequency
  - Cyclone exposure risk
  - Overall climate hazard score

Requires: scikit-learn
"""

import os
import json
import pickle
import numpy as np
from typing import Dict, List
from datetime import datetime

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "models")
FLOOD_MODEL_FILE = os.path.join(MODEL_DIR, "flood_model.pkl")
FLOOD_METRICS_FILE = os.path.join(MODEL_DIR, "flood_metrics.json")


class FloodPredictor:
    """
    Predicts flood probability and climate hazard for cities/areas.
    """

    FEATURE_NAMES = [
        "elevation_m", "coastal", "river_proximity", "seismic_zone",
        "avg_rainfall_mm", "humidity_pct", "cyclone_risk_num",
        "projected_rainfall_change_2050",
        "green_cover_pct", "density_per_sqkm", "terrain_type_num",
    ]

    def __init__(self):
        self.flood_model = None
        self.heat_model = None
        self.scaler = None
        self.trained = False
        self.metrics = {}

    def _extract_features(self, city) -> np.ndarray:
        """Extract features from CityProfile for flood/weather prediction."""
        cyclone_map = {"none": 0, "low": 1, "medium": 2, "high": 3}
        terrain_map = {"plain": 0, "plateau": 1, "hilly": 2, "coastal": 3, "delta": 4}

        features = [
            city.geo.elevation_m,
            int(city.geo.coastal),
            int(city.geo.river_proximity),
            city.geo.seismic_zone,
            city.climate.avg_rainfall_mm,
            city.climate.humidity_pct,
            cyclone_map.get(city.climate.cyclone_risk, 1),
            city.climate.projected_rainfall_change_2050_pct,
            city.infrastructure.green_cover_pct,
            city.population.density_per_sqkm,
            terrain_map.get(city.geo.terrain_type, 0),
        ]
        return np.array(features, dtype=np.float64)

    def _build_training_data(self, cities: list) -> tuple:
        """
        Build training data using known flood risk labels.
        Converts qualitative risk to numeric probability target.
        """
        X = []
        y_flood = []
        y_heat = []

        flood_target = {"low": 0.1, "medium": 0.4, "high": 0.7}

        for city in cities:
            features = self._extract_features(city)
            X.append(features)
            y_flood.append(flood_target.get(city.geo.flood_risk, 0.3))

            # Heat risk target based on extreme heat days
            heat_risk = min(1.0, city.climate.extreme_heat_days / 50)
            y_heat.append(heat_risk)

        return np.array(X), np.array(y_flood), np.array(y_heat)

    def train(self, cities: list):
        """Train flood and heat prediction models."""
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import cross_val_score

        X, y_flood, y_heat = self._build_training_data(cities)

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Flood model
        self.flood_model = GradientBoostingRegressor(
            n_estimators=100, max_depth=4, learning_rate=0.1,
            random_state=42
        )
        self.flood_model.fit(X_scaled, y_flood)

        # Heat model
        self.heat_model = GradientBoostingRegressor(
            n_estimators=100, max_depth=4, learning_rate=0.1,
            random_state=42
        )
        self.heat_model.fit(X_scaled, y_heat)

        flood_cv = cross_val_score(self.flood_model, X_scaled, y_flood, cv=min(5, len(X)), scoring="r2")
        heat_cv = cross_val_score(self.heat_model, X_scaled, y_heat, cv=min(5, len(X)), scoring="r2")

        self.trained = True
        self.metrics = {
            "flood_r2": round(float(np.mean(flood_cv)), 4),
            "heat_r2": round(float(np.mean(heat_cv)), 4),
            "n_samples": len(X),
            "trained_at": datetime.now().isoformat(),
            "flood_feature_importance": {
                name: round(float(imp), 4)
                for name, imp in sorted(
                    zip(self.FEATURE_NAMES, self.flood_model.feature_importances_),
                    key=lambda x: x[1], reverse=True
                )
            },
        }

        self.save()
        return self.metrics

    def predict(self, city) -> Dict:
        """Predict flood and heat risk for a city."""
        if not self.trained:
            self.load()

        features = self._extract_features(city)
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        flood_prob = float(np.clip(self.flood_model.predict(features_scaled)[0], 0, 1))
        heat_prob = float(np.clip(self.heat_model.predict(features_scaled)[0], 0, 1))

        # Composite hazard score
        hazard_score = round((flood_prob * 0.5 + heat_prob * 0.3 +
                              (city.geo.seismic_zone / 5) * 0.2) * 100, 1)

        # Risk category
        if hazard_score > 60:
            category = "high"
        elif hazard_score > 35:
            category = "moderate"
        else:
            category = "low"

        return {
            "city": city.name,
            "flood_probability": round(flood_prob, 3),
            "heat_risk": round(heat_prob, 3),
            "seismic_risk": round(city.geo.seismic_zone / 5, 2),
            "cyclone_exposure": city.climate.cyclone_risk,
            "composite_hazard_score": hazard_score,
            "risk_category": category,
            "flood_risk_label": city.geo.flood_risk,
        }

    def predict_area(self, area) -> Dict:
        """Predict flood risk for a Chennai area (simplified features)."""
        flood_prob = 0.7 if area.flood_prone else 0.15
        # Adjust by coastal proximity
        if area.coastal_proximity:
            flood_prob = min(1.0, flood_prob + 0.15)

        return {
            "area": area.name,
            "zone": area.zone,
            "flood_probability": round(flood_prob, 3),
            "flood_prone": area.flood_prone,
            "risk_category": "high" if flood_prob > 0.5 else "moderate" if flood_prob > 0.25 else "low",
        }

    def save(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        with open(FLOOD_MODEL_FILE, "wb") as f:
            pickle.dump({
                "flood_model": self.flood_model,
                "heat_model": self.heat_model,
                "scaler": self.scaler,
            }, f)
        with open(FLOOD_METRICS_FILE, "w") as f:
            json.dump(self.metrics, f, indent=2)

    def load(self) -> bool:
        if not os.path.exists(FLOOD_MODEL_FILE):
            return False
        with open(FLOOD_MODEL_FILE, "rb") as f:
            data = pickle.load(f)
            self.flood_model = data["flood_model"]
            self.heat_model = data["heat_model"]
            self.scaler = data["scaler"]
            self.trained = True
        return True


def train_and_evaluate(cities: list = None) -> Dict:
    """Train flood model and return metrics."""
    if cities is None:
        from src.seed_data import get_all_cities
        cities = get_all_cities()

    predictor = FloodPredictor()
    metrics = predictor.train(cities)
    print(f"  Flood model R²: {metrics['flood_r2']:.4f}")
    print(f"  Heat model R²: {metrics['heat_r2']:.4f}")
    return metrics
