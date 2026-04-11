import joblib
import numpy as np
import pandas as pd
from pathlib import Path

MODELS_DIR = Path("models")


MODEL_FILES = {
    "Logistic Regression": "logistic_regression.pkl",
    "Decision Tree":        "decision_tree.pkl",
    "Random Forest":        "random_forest.pkl",
    "XGBoost":              "xgboost.pkl",
}