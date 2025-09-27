import pytest
import requests
import time

BASE_URL = "http://127.0.0.1:8000"


class TestSecurityImprovements:

    def test_sql_injection(self):
        """Test for SQL Injection vulnerabilities."""
        malicious_payloads = [
            "' OR 1=1 --",
            "' OR '1'='1'",
            "' OR 1=1; --",
            "' OR 1=1#",
            "' OR 'a'='a'",
            "' OR 'a'='a'#",
            "' OR 'a'='a'; --",
            '" OR 1=1 --',
            '" OR "a"="a"',
            '\" OR 1=1 --',
            "' OR 1=1 -- ",
        ]
        for payload in malicious_payloads:
            response = requests.post(f"{BASE_URL}/api/search_patients", json={"query": payload})
            # The request should either be rejected (400/422) or return a safe result (not a list of all patients)
            assert response.status_code in [200, 400, 422, 429]
            if response.status_code == 200:
                assert "יוסי כהן" not in response.text

    def test_xss(self):
        """Test for Cross-Site Scripting (XSS) vulnerabilities."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "<iframe src=\"javascript:alert('XSS')\">",
        ]
        for payload in xss_payloads:
            response = requests.post(f"{BASE_URL}/api/search_patients", json={"query": payload})
            assert response.status_code in [200, 400, 422, 429]
            if response.status_code == 200:
                assert "<script>" not in response.text

    def test_rate_limiting(self):
        """Test the rate limiting on the search_patients endpoint."""
        # Burst requests to trigger rate limiting
        for i in range(15):
            response = requests.post(f"{BASE_URL}/api/search_patients", json={"query": "test"})
            if i >= 10:
                assert response.status_code == 429
        # Wait for the rate limit to reset
        time.sleep(60)
        # The next request should be successful
        response = requests.post(f"{BASE_URL}/api/search_patients", json={"query": "test"})
        assert response.status_code == 200

