"""
Test Security Headers Middleware

Validates that all security headers are properly set on API responses.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_security_headers_on_root():
    """Test that security headers are present on root endpoint"""
    response = client.get("/")
    
    # Content Security Policy
    assert "Content-Security-Policy" in response.headers
    csp = response.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp
    assert "upgrade-insecure-requests" in csp
    
    # X-Frame-Options
    assert response.headers.get("X-Frame-Options") == "DENY"
    
    # X-Content-Type-Options
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    
    # X-XSS-Protection
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    
    # Referrer-Policy
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    
    # Permissions-Policy
    assert "Permissions-Policy" in response.headers
    permissions = response.headers["Permissions-Policy"]
    assert "geolocation=()" in permissions
    assert "camera=()" in permissions
    
    # Server header should be removed
    assert "Server" not in response.headers


def test_security_headers_on_health():
    """Test that security headers are present on health endpoint"""
    response = client.get("/health")
    
    assert "Content-Security-Policy" in response.headers
    assert "X-Frame-Options" in response.headers
    assert "X-Content-Type-Options" in response.headers


def test_security_headers_on_api():
    """Test that security headers are present on API endpoints"""
    response = client.get("/api/v1/status")
    
    assert "Content-Security-Policy" in response.headers
    assert "X-Frame-Options" in response.headers
    assert "X-Content-Type-Options" in response.headers


def test_hsts_not_on_http():
    """Test that HSTS is not added on HTTP connections"""
    response = client.get("/")
    
    # HSTS should only be added on HTTPS
    # In test environment, we're using HTTP
    assert "Strict-Transport-Security" not in response.headers


def test_csp_directives():
    """Test specific CSP directives"""
    response = client.get("/")
    csp = response.headers["Content-Security-Policy"]
    
    # Check all required directives
    required_directives = [
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self'",
        "img-src 'self' data: https:",
        "font-src 'self' data:",
        "connect-src 'self'",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "upgrade-insecure-requests"
    ]
    
    for directive in required_directives:
        assert directive in csp, f"Missing CSP directive: {directive}"


def test_permissions_policy_directives():
    """Test specific Permissions-Policy directives"""
    response = client.get("/")
    permissions = response.headers["Permissions-Policy"]
    
    # Check all required directives
    required_permissions = [
        "geolocation=()",
        "microphone=()",
        "camera=()",
        "payment=()",
        "usb=()",
        "magnetometer=()",
        "gyroscope=()",
        "speaker=()"
    ]
    
    for permission in required_permissions:
        assert permission in permissions, f"Missing Permissions-Policy directive: {permission}"


def test_security_headers_on_404():
    """Test that security headers are present even on 404 responses"""
    response = client.get("/nonexistent-endpoint")
    
    assert response.status_code == 404
    assert "Content-Security-Policy" in response.headers
    assert "X-Frame-Options" in response.headers
    assert "X-Content-Type-Options" in response.headers


def test_security_headers_on_docs():
    """Test that security headers are present on documentation endpoints"""
    response = client.get("/docs")
    
    assert "Content-Security-Policy" in response.headers
    assert "X-Frame-Options" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

