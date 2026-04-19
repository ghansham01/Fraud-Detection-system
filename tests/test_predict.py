from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

# Real fraud transaction from dataset (row 0)
FRAUD_TRANSACTION = {
    "Time": 406.0, "Amount": 149.62,
    "V1": -1.359807, "V2": -0.072781, "V3": 2.536347,
    "V4": 1.378155,  "V5": -0.338321, "V6": 0.462388,
    "V7": 0.239599,  "V8": 0.098698,  "V9": 0.363787,
    "V10": 0.090794, "V11": -0.551600, "V12": -0.617801,
    "V13": -0.991390, "V14": -0.311169, "V15": 1.468177,
    "V16": -0.470401, "V17": 0.207971, "V18": 0.025791,
    "V19": 0.403993, "V20": 0.251412,  "V21": -0.018307,
    "V22": 0.277838, "V23": -0.110474, "V24": 0.066928,
    "V25": 0.128539, "V26": -0.189115, "V27": 0.133558,
    "V28": -0.021053
}

# Real legit transaction from dataset
LEGIT_TRANSACTION = {
    "Time": 1000.0, "Amount": 25.00,
    "V1": 1.191857,  "V2": 0.266151,  "V3": 0.166480,
    "V4": 0.448154,  "V5": 0.060018,  "V6": -0.082361,
    "V7": -0.078803, "V8": 0.085102,  "V9": -0.255425,
    "V10": -0.166974, "V11": 1.612727, "V12": 1.065235,
    "V13": 0.489095, "V14": -0.143772, "V15": 0.635558,
    "V16": 0.463917, "V17": -0.114805, "V18": -0.183361,
    "V19": -0.145783, "V20": -0.069083, "V21": -0.225775,
    "V22": -0.638672, "V23": 0.101288, "V24": -0.339846,
    "V25": 0.167170, "V26": 0.125895,  "V27": -0.008983,
    "V28": 0.014724
}

def test_predict_status_200():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    assert response.status_code == 200

def test_predict_has_final_verdict():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    assert "final_verdict" in response.json()

def test_predict_has_fraud_probability():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    assert "fraud_probability" in response.json()

def test_predict_has_risk_level():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    assert "risk_level" in response.json()

def test_predict_has_models_list():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    assert "models" in response.json()

def test_predict_has_agreement():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    assert "agreement" in response.json()

def test_predict_all_4_models_respond():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    assert len(response.json()["models"]) == 4

def test_each_model_has_required_fields():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    for model in response.json()["models"]:
        assert "model_name"  in model
        assert "prediction"  in model
        assert "probability" in model
        assert "confidence"  in model

def test_fraud_probability_between_0_and_1():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    prob = response.json()["fraud_probability"]
    assert 0.0 <= prob <= 1.0

def test_each_model_probability_between_0_and_1():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    for model in response.json()["models"]:
        assert 0.0 <= model["probability"] <= 1.0

def test_final_verdict_valid_value():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    assert response.json()["final_verdict"] in ["Fraud", "Legit"]

def test_risk_level_valid_value():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    assert response.json()["risk_level"] in ["High", "Medium", "Low"]

def test_confidence_valid_value():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    for model in response.json()["models"]:
        assert model["confidence"] in ["High", "Medium", "Low"]

def test_prediction_valid_value():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    for model in response.json()["models"]:
        assert model["prediction"] in ["Fraud", "Legit"]

def test_legit_transaction_returns_200():
    response = client.post("/predict", json=LEGIT_TRANSACTION)
    assert response.status_code == 200

def test_legit_verdict_valid():
    response = client.post("/predict", json=LEGIT_TRANSACTION)
    assert response.json()["final_verdict"] in ["Fraud", "Legit"]

def test_transaction_amount_in_response():
    response = client.post("/predict", json=FRAUD_TRANSACTION)
    assert "transaction_amount" in response.json()

def test_logs_summary_returns_200():
    # Pehle ek prediction karo taaki log file empty na rahe
    client.post("/predict", json=FRAUD_TRANSACTION)
    response = client.get("/logs/summary")
    assert response.status_code == 200