# app/tests/test_api.py
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Factora+ API"}

def test_token_metrics():
    response = client.get("/test/tokenmetrics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"