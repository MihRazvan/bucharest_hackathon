# app/tests/test_tokenmetrics.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_token_metrics_endpoint():
    response = client.get("/test/tokenmetrics")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success" or data["status"] == "error"