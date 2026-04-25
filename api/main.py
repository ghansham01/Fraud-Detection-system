from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import TransactionInput, EnsembleResponse, SimpleTransactionInput
from api.predictor import run_ensemble
from api.logger import init_logger, log_prediction
from api.estimator import estimator

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

@app.post("/predict/simple", response_model=EnsembleResponse)
def predict_simple(transaction: SimpleTransactionInput):
    try:
        # Time hour ko seconds mein convert karo
        time_seconds = transaction.time_hour * 3600

        # Transaction type se amount adjust karo
        type_multiplier = {
            "online":   1.0,
            "in-store": 0.8,
            "atm":      1.2
        }
        adjusted_amount = transaction.amount * type_multiplier[transaction.transaction_type]

        # V features estimate karo
        v_features = estimator(adjusted_amount, time_seconds)

        # Full payload banao
        full_payload = {
            "Time":   time_seconds,
            "Amount": transaction.amount,
            **v_features
        }

        result = run_ensemble(full_payload)
        log_prediction(transaction.amount, result)
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )   