from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

# Base valid input — har test mein modify karenge
VALID_INPUT = {
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

def test_negative_amount_rejected():
    bad = {**VALID_INPUT, "Amount": -500.0}
    response = client.post("/predict", json=bad)
    assert response.status_code == 422

def test_missing_amount_rejected():
    bad = {k: v for k, v in VALID_INPUT.items() if k != "Amount"}
    response = client.post("/predict", json=bad)
    assert response.status_code == 422

def test_missing_time_rejected():
    bad = {k: v for k, v in VALID_INPUT.items() if k != "Time"}
    response = client.post("/predict", json=bad)
    assert response.status_code == 422

def test_missing_v1_rejected():
    bad = {k: v for k, v in VALID_INPUT.items() if k != "V1"}
    response = client.post("/predict", json=bad)
    assert response.status_code == 422

def test_string_amount_rejected():
    bad = {**VALID_INPUT, "Amount": "not_a_number"}
    response = client.post("/predict", json=bad)
    assert response.status_code == 422

def test_string_time_rejected():
    bad = {**VALID_INPUT, "Time": "abc"}
    response = client.post("/predict", json=bad)
    assert response.status_code == 422

def test_empty_body_rejected():
    response = client.post("/predict", json={})
    assert response.status_code == 422

def test_only_partial_fields_rejected():
    bad = {"Time": 406.0, "Amount": 100.0}
    response = client.post("/predict", json=bad)
    assert response.status_code == 422

def test_zero_amount_accepted():
    good = {**VALID_INPUT, "Amount": 0.0}
    response = client.post("/predict", json=good)
    assert response.status_code == 200

def test_large_amount_accepted():
    good = {**VALID_INPUT, "Amount": 99999.99}
    response = client.post("/predict", json=good)
    assert response.status_code == 200