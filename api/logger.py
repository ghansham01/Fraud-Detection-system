import csv
import os 
from datetime import datetime


LOG_FILE = "logs/predictions.csv"


def init_logger():
    
    os.makedirs("logs", exist_ok=True)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)

            writer.writerow([
                "timestamp", "amount", "final_verdict",
                "fraud_probability", "risk_level", "agreement"
            ])

def log_prediction(amount: float, result: dict):
    
    with open(LOG_FILE, "a", newline="") as f:
        
        writer = csv.writer(f)
        
        writer.writerow([
            datetime.now().isoformat(),
            amount,
            result["final_verdict"],
            result["fraud_probability"],
            result["risk_level"],
            result["agreement"]
        ])