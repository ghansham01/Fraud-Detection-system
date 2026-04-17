from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import TransactionInput, EnsembleResponse
from api.predictor import run_ensemble
from api.logger import init_logger, log_prediction

import pandas as pd
import os


app = FastAPI(
    title="Fraud Detection API",
    description="Ensemble ML API — 4 models vote on every transaction",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    
    init_logger()
    print("Logger initialized")
    print("All models loaded and ready")

@app.get("/")
def root():
    
    return {
        "message": "Fraud Detection API is running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health():
    
    return {
        "status": "healthy",
        "models_loaded": 4,
        "version": "1.0.0"
    }

@app.post("/predict", response_model=EnsembleResponse)
def predict(transaction: TransactionInput):
    try:
        
        result = run_ensemble(transaction.dict())
        log_prediction(transaction.Amount, result)
        return result

    except Exception as e:
        
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )
    
@app.get("/logs/summary")
def logs_summary():
    
    if not os.path.exists("logs/predictions.csv"):
    
        return {"message": "No predictions logged yet"}

    df = pd.read_csv("logs/predictions.csv")
    
    return {
        "total_predictions": len(df),
        "fraud_detected": int((df["final_verdict"] == "Fraud").sum()),
        "legit_detected": int((df["final_verdict"] == "Legit").sum()),
        "avg_fraud_probability": round(df["fraud_probability"].mean(), 4),
        "high_risk_count": int((df["risk_level"] == "High").sum()),
    }