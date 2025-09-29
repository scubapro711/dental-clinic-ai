# Test Monitoring Endpoint
# Version: 1.0.0
# Date: 2025-12-29

import pytest
from fastapi.testclient import TestClient
from src.gateway.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_status_endpoint():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {
        "gateway": "ok",
        "database": "ok",
        "redis": "ok"
    }

