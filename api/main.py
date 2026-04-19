from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import TransactionInput, EnsembleResponse
from api.predictor import run_ensemble
from api.logger import init_logger, log_prediction

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logger()
    print("Logger initialized")
    print("All models loaded and ready")
    yield

app = FastAPI(
    title="Fraud Detection API",
    description="Ensemble ML API — 4 models vote on every transaction",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — yeh middleware sabse pehle add hona chahiye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # development ke liye
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Fraud Detection API is running",
        "docs":    "/docs",
        "health":  "/health"
    }

@app.get("/health")
def health():
    return {
        "status":        "healthy",
        "models_loaded": 4,
        "version":       "1.0.0"
    }

@app.post("/predict", response_model=EnsembleResponse)
def predict(transaction: TransactionInput):
    try:
        result = run_ensemble(transaction.model_dump())
        log_prediction(transaction.Amount, result)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

@app.get("/logs/summary")
def logs_summary():
    import pandas as pd
    import os

    if not os.path.exists("logs/predictions.csv"):
        return {"message": "No predictions logged yet"}

    df = pd.read_csv("logs/predictions.csv", encoding="utf-8")

    if df.empty:
        return {"message": "No predictions logged yet"}

    return {
        "total_predictions":     len(df),
        "fraud_detected":        int((df["final_verdict"] == "Fraud").sum()),
        "legit_detected":        int((df["final_verdict"] == "Legit").sum()),
        "avg_fraud_probability": round(df["fraud_probability"].mean(), 4),
        "high_risk_count":       int((df["risk_level"] == "High").sum()),
    }