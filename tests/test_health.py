from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_root_returns_200():
    response = client.get("/")
    assert response.status_code == 200

def test_root_has_message():
    response = client.get("/")
    assert "message" in response.json()

def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200

def test_health_status_is_healthy():
    response = client.get("/health")
    assert response.json()["status"] == "healthy"

def test_health_models_loaded():
    response = client.get("/health")
    assert response.json()["models_loaded"] == 4

def test_health_has_version():
    response = client.get("/health")
    assert "version" in response.json()