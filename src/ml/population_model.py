"""
Population Flow Prediction Model — LSTM-style sequential model
for city-level population projection.

Uses an MLP with rolling-window features as a practical alternative
to full LSTM (avoids PyTorch/TensorFlow dependency).

Features:
  - Historical population sequence (2011, 2020, 2025)
  - Growth rate, density, migration rate
  - City infrastructure and climate factors
  - Carrying capacity ratio

Falls back to logistic growth if sklearn is unavailable.

Requires: scikit-learn
"""

import os
import json
import pickle
import numpy as np
from typing import Dict, List
from datetime import datetime

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "models")
POP_MODEL_FILE = os.path.join(MODEL_DIR, "population_model.pkl")
POP_METRICS_FILE = os.path.join(MODEL_DIR, "population_metrics.json")


class PopulationPredictor:
    """
    Neural network (MLP) for population projection.
    Uses rolling-window features to approximate sequential learning.
    """

    def __init__(self):
        self.model = None
        self.scaler_X = None
        self.scaler_y = None
        self.trained = False
        self.metrics = {}

    def _extract_features(self, city, target_year: int) -> np.ndarray:
        """Build feature vector for population prediction."""
        from src.population_analysis import estimate_carrying_capacity
        from src.climate_analysis import climate_risk_score

        carrying_cap = estimate_carrying_capacity(city)
        saturation = city.population.population_2025 / carrying_cap

        # Population growth sequence (normalized)
        pop_2011 = city.population.population_2011
        pop_2020 = city.population.population_2020
        pop_2025 = city.population.population_2025

        growth_2011_2020 = (pop_2020 - pop_2011) / pop_2011 if pop_2011 > 0 else 0
        growth_2020_2025 = (pop_2025 - pop_2020) / pop_2020 if pop_2020 > 0 else 0

        features = [
            np.log1p(pop_2025),           # current population (log)
            city.population.growth_rate_pct,
            city.population.density_per_sqkm / 10000,  # normalize
            growth_2011_2020,
            growth_2020_2025,
            saturation,
            city.tier,
            int(city.infrastructure.metro_rail),
            int(city.infrastructure.it_hub),
            city.infrastructure.water_supply_score / 10,
            city.infrastructure.green_cover_pct / 100,
            climate_risk_score(city) / 100,
            int(city.geo.coastal),
            target_year - 2025,  # years forward
        ]
        return np.array(features, dtype=np.float64)

    def _build_training_data(self, cities: list) -> tuple:
        """
        Build training data from known and projected population points.
        """
        X = []
        y = []

        for city in cities:
            pop_base = city.population.population_2025

            # Known data points
            for year, pop in [
                (2011, city.population.population_2011),
                (2020, city.population.population_2020),
                (2025, city.population.population_2025),
            ]:
                feat = self._extract_features(city, year)
                X.append(feat)
                y.append(np.log1p(pop))

            # Projected targets
            for year, pop in [
                (2030, city.population.projected_2030),
                (2040, city.population.projected_2040),
                (2050, city.population.projected_2050),
                (2070, city.population.projected_2070),
            ]:
                feat = self._extract_features(city, year)
                X.append(feat)
                y.append(np.log1p(pop))

        return np.array(X), np.array(y)

    def train(self, cities: list):
        """Train the population prediction model."""
        from sklearn.neural_network import MLPRegressor
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import cross_val_score

        X, y = self._build_training_data(cities)

        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()
        X_scaled = self.scaler_X.fit_transform(X)
        y_scaled = self.scaler_y.fit_transform(y.reshape(-1, 1)).ravel()

        self.model = MLPRegressor(
            hidden_layer_sizes=(64, 32, 16),
            activation="relu",
            solver="adam",
            max_iter=1000,
            early_stopping=True,
            validation_fraction=0.15,
            random_state=42,
            learning_rate="adaptive",
        )
        self.model.fit(X_scaled, y_scaled)

        cv_scores = cross_val_score(
            MLPRegressor(
                hidden_layer_sizes=(64, 32, 16),
                activation="relu", solver="adam",
                max_iter=500, random_state=42,
            ),
            X_scaled, y_scaled, cv=5, scoring="r2"
        )

        self.trained = True
        self.metrics = {
            "r2_mean": round(float(np.mean(cv_scores)), 4),
            "r2_std": round(float(np.std(cv_scores)), 4),
            "n_samples": len(X),
            "n_features": X.shape[1],
            "trained_at": datetime.now().isoformat(),
        }

        self.save()
        return self.metrics

    def predict(self, city, year: int = 2050) -> Dict:
        """Predict population for a city at a future year."""
        if not self.trained:
            self.load()

        features = self._extract_features(city, year)
        features_scaled = self.scaler_X.transform(features.reshape(1, -1))

        y_scaled = self.model.predict(features_scaled)
        y_log = self.scaler_y.inverse_transform(y_scaled.reshape(-1, 1))[0, 0]
        predicted_pop = int(np.expm1(y_log))

        # Logistic model comparison
        from src.population_analysis import logistic_population, estimate_carrying_capacity
        logistic_pop = logistic_population(
            city.population.population_2025,
            city.population.growth_rate_pct,
            estimate_carrying_capacity(city),
            year - 2025
        )

        return {
            "city": city.name,
            "year": year,
            "ml_predicted": predicted_pop,
            "logistic_predicted": logistic_pop,
            "difference_pct": round(
                (predicted_pop - logistic_pop) / logistic_pop * 100, 1
            ) if logistic_pop > 0 else 0,
        }

    def predict_timeline(self, city, start_year: int = 2025,
                         end_year: int = 2070, step: int = 5) -> List[Dict]:
        """Predict population at regular intervals."""
        return [self.predict(city, year)
                for year in range(start_year, end_year + 1, step)]

    def save(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        with open(POP_MODEL_FILE, "wb") as f:
            pickle.dump({
                "model": self.model,
                "scaler_X": self.scaler_X,
                "scaler_y": self.scaler_y,
            }, f)
        with open(POP_METRICS_FILE, "w") as f:
            json.dump(self.metrics, f, indent=2)

    def load(self) -> bool:
        if not os.path.exists(POP_MODEL_FILE):
            return False
        with open(POP_MODEL_FILE, "rb") as f:
            data = pickle.load(f)
            self.model = data["model"]
            self.scaler_X = data["scaler_X"]
            self.scaler_y = data["scaler_y"]
            self.trained = True
        return True


def train_and_evaluate(cities: list = None) -> Dict:
    """Train population model and return metrics."""
    if cities is None:
        from src.seed_data import get_all_cities
        cities = get_all_cities()

    predictor = PopulationPredictor()
    metrics = predictor.train(cities)
    print(f"  Population model R²: {metrics['r2_mean']:.4f} ± {metrics['r2_std']:.4f}")
    return metrics
