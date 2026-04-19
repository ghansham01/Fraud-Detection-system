import csv
import os 
from datetime import datetime

LOG_FILE = "logs/predictions.csv"


def init_logger():

    os.makedirs("logs", exist_ok=True)
    
    header = ["timestamp", "amount", "final_verdict", "fraud_probability", "risk_level", "agreement"]
    
    # Always ensure header exists - read existing file and prepend header if missing
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                # If file is empty or doesn't start with "timestamp", add header
                if not content.startswith("timestamp"):
                    # Read all existing data
                    f.seek(0)
                    existing_data = f.read()
                    # Rewrite with header
                    with open(LOG_FILE, "w", newline="", encoding="utf-8") as wf:
                        writer = csv.writer(wf)
                        writer.writerow(header)
                        if existing_data.strip():
                            # Parse and re-write existing data
                            import io
                            reader = csv.reader(io.StringIO(existing_data))
                            for row in reader:
                                if row:
                                    writer.writerow(row)
                    return
        except Exception as e:
            print(f"Error checking header: {e}")
    
    # File doesn't exist or was just created
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

def log_prediction(amount: float, result: dict):

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
    
        writer.writerow([
            datetime.now().isoformat(),
            amount,
            result["final_verdict"],
            result["fraud_probability"],
            result["risk_level"],
            result["agreement"]
        ])