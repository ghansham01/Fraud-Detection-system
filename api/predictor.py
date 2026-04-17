import joblib
import numpy as np
import pandas as pd
from pathlib import Path

MODELS_DIR = Path("models")


MODEL_FILES = {
    "Logistic Regression": "logistic_regression.pkl",
    "Decision Tree": "decision_tree.pkl",
    "Random Forest": "random_forest.pkl",
    "XGBoost": "xgboost.pkl",
}

def load_artifacts():
    models = {}
    for name, filename in MODEL_FILES.items():
        path = MODELS_DIR / filename
        if path.exists():
            models[name] = joblib.load(path)
        else:
            print(f"Warning: {filename} not found, skipping")

    scaler = joblib.load(MODELS_DIR / "scaler.pkl")
    feature_cols = joblib.load(MODELS_DIR / "feature_cols.pkl")

    return models, scaler, feature_cols

models, scaler, feature_cols = load_artifacts()

def get_confidence(probability: float) -> str:
    if probability >= 0.8:
        return "High"
    elif probability >= 0.50:
        return "Medium"
    else:
        return "Low"
    
def get_riskLevel(avgProbability: float) -> str:
    if avgProbability >= 0.75:
        return "High"
    elif avgProbability >= 0.40:
        return "Medium"
    else:
        return "Low"

def get_agreement(predictions: list) -> str:
    fraud_votes = sum(predictions)
    total = len(predictions)

    if fraud_votes == total:
        return "All models agree — Fraud"
    elif fraud_votes == 0:
        return "All models agree — Legit"
    elif fraud_votes == 3:
        return "3 of 4 models say Fraud"
    elif fraud_votes == 1:
        return "3 of 4 models say Legit"
    else:
        return "Split decision (2 vs 2)"
    

def preprocess_input(data: dict) -> pd.DataFrame:
    df = pd.DataFrame([data])

    # Scale Amount and Time together — same as training
    df[["Amount_scaled", "Time_scaled"]] = scaler.transform(df[["Amount", "Time"]])

    # Drop original columns
    df = df.drop(columns=["Amount", "Time"])

    # Match exact column order from training
    df = df[feature_cols]

    return df

def run_ensemble(transaction_data: dict) -> dict:
    
    processed = preprocess_input(transaction_data)
    predictions = []
    results = []

    for name, model in models.items():
        
        proba = model.predict_proba(processed)[0][1]  # fraud probability
        pred = int(proba >= 0.5)
        label = "Fraud" if pred == 1 else "Legit"
        confidence = get_confidence(proba)

        predictions.append(pred)
        
        results.append({
            "model_name":  name,
            "prediction":  label,
            "probability": round(proba, 4),
            "confidence":  confidence
        })

    # Ensemble logic — majority vote
    fraud_votes = sum(predictions)
    avg_probability = np.mean([r["probability"] for r in results])
   
    final_verdict = "Fraud" if fraud_votes >= 2 else "Legit"
    risk_level = get_riskLevel(avg_probability)
    agreement = get_agreement(predictions)

    return {
        "final_verdict": final_verdict,
        "fraud_probability": round(avg_probability, 4),
        "risk_level": risk_level,
        "models": results,
        "agreement": agreement,
        "transaction_amount": transaction_data["Amount"]
    }