import pytest


def test_sql_injection(client):
    """Test for SQL injection vulnerabilities"""
    payload = {"query": "' OR 1=1 --"}
    response = client.post("/api/search_patients", json=payload)
    assert response.status_code != 500

def test_xss(client):
    """Test for Cross-Site Scripting (XSS) vulnerabilities"""
    payload = {"query": "<script>alert('XSS')</script>"}
    response = client.post("/api/search_patients", json=payload)
    assert "<script>" not in response.text

def test_rate_limiting(client):
    """Test the rate limiting mechanism"""
    responses = []
    for _ in range(15):
        responses.append(client.post("/api/search_patients", json={"query": "test"}))
    
    status_codes = [res.status_code for res in responses]
    assert 429 in status_codes

