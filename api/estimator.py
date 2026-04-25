from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd


V_COLUMNS = [f"V{i}" for i in range(1, 29)]
DATA_PATH = Path("data/creditcard.csv")


@lru_cache(maxsize=1)
def _load_profiles():
    df = pd.read_csv(DATA_PATH, usecols=[*V_COLUMNS, "Class"])
    profiles = {}

    for class_value, label in [(0, "legit"), (1, "fraud")]:
        class_df = df[df["Class"] == class_value][V_COLUMNS]
        profiles[label] = {
            "q25": class_df.quantile(0.25).to_numpy(),
            "median": class_df.median().to_numpy(),
            "q75": class_df.quantile(0.75).to_numpy(),
        }

    return profiles


def _risk_score(amount: float, hour: float) -> float:
    amount_score = np.clip(np.log1p(amount) / np.log1p(5000), 0, 1)
    odd_hour_score = 1.0 if hour < 6 or hour > 22 else 0.0
    business_hour_discount = 0.15 if 9 <= hour <= 17 else 0.0
    return float(np.clip((0.65 * amount_score) + (0.45 * odd_hour_score) - business_hour_discount, 0, 1))


def _sample_profile(label: str, rng: np.random.Generator) -> np.ndarray:
    profile = _load_profiles()[label]
    spread = np.maximum(profile["q75"] - profile["q25"], 0.05)
    values = profile["median"] + rng.normal(0, spread / 4)
    return np.clip(values, profile["q25"], profile["q75"])


def estimator(amount: float, time: float) -> dict:
    rng = np.random.default_rng(seed=int(amount * 100 + time))
    hour = (time % 86400) / 3600
    risk = _risk_score(amount, hour)

    if risk >= 0.70:
        v_values = _sample_profile("fraud", rng)
    elif risk <= 0.35:
        v_values = _sample_profile("legit", rng)
    else:
        legit_values = _sample_profile("legit", rng)
        fraud_values = _sample_profile("fraud", rng)
        fraud_weight = (risk - 0.35) / 0.35
        v_values = (1 - fraud_weight) * legit_values + fraud_weight * fraud_values

    return {column: round(float(value), 6) for column, value in zip(V_COLUMNS, v_values)}
