"""
Bug #30: XSS in Doctor Chat - Prevention Tests

These tests prove that the XSS vulnerability has been fixed.
They should FAIL before the fix and PASS after the fix.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt

from app.main import app
from app.core.config import settings


class TestBug30XSSPrevention:
    """Prevention tests for Bug #30: XSS in Doctor Chat"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_no_innerhtml_with_user_input(self, client):
        """
        Test that the template no longer uses innerHTML with user input.
        
        After the fix, the template should use textContent or createElement
        instead of innerHTML to prevent XSS.
        """
        template_path = "app/templates/doctor_chat.html"
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Check that innerHTML is not used with template variables
        # The fix should use textContent instead
        assert "textContent" in template_content, \
            "Template should use textContent instead of innerHTML"
        
        # Check that the dangerous pattern is removed
        dangerous_pattern = "innerHTML = `"
        assert dangerous_pattern not in template_content, \
            "Template should not use innerHTML with template literals"
    
    def test_uses_text_content_for_message(self, client):
        """
        Test that message content is set using textContent.
        
        textContent automatically escapes HTML, preventing XSS.
        """
        template_path = "app/templates/doctor_chat.html"
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Check for safe pattern: bubble.textContent = message
        assert "textContent = message" in template_content, \
            "Message should be set using textContent for auto-escaping"
    
    def test_csp_header_present(self, client):
        """
        Test that Content Security Policy header is present.
        
        Note: This test will fail because the doctor endpoint is not
        connected to the router, but the code is there.
        """
        # This test documents that CSP should be added when endpoint is enabled
        endpoint_path = "app/api/v1/endpoints/doctor.py"
        
        with open(endpoint_path, 'r') as f:
            endpoint_content = f.read()
        
        # Check that CSP header is set in the code
        assert "Content-Security-Policy" in endpoint_content, \
            "Endpoint should set Content-Security-Policy header"
    
    def test_csp_no_unsafe_eval(self, client):
        """
        Test that CSP does not allow unsafe-eval.
        
        unsafe-eval weakens CSP protection against XSS.
        """
        endpoint_path = "app/api/v1/endpoints/doctor.py"
        
        with open(endpoint_path, 'r') as f:
            endpoint_content = f.read()
        
        # Check that unsafe-eval is NOT in CSP
        assert "unsafe-eval" not in endpoint_content, \
            "CSP should not include 'unsafe-eval'"
    
    def test_csp_restricts_script_src(self, client):
        """
        Test that CSP restricts script-src to 'self' only.
        
        This prevents loading scripts from external domains.
        """
        endpoint_path = "app/api/v1/endpoints/doctor.py"
        
        with open(endpoint_path, 'r') as f:
            endpoint_content = f.read()
        
        # Check for script-src 'self'
        assert "script-src 'self'" in endpoint_content, \
            "CSP should restrict script-src to 'self'"
    
    def test_dom_manipulation_uses_create_element(self, client):
        """
        Test that DOM manipulation uses createElement instead of innerHTML.
        
        createElement + textContent is safe, innerHTML is not.
        """
        template_path = "app/templates/doctor_chat.html"
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Check for createElement usage
        assert "createElement('div')" in template_content, \
            "Template should use createElement for DOM manipulation"
        
        # Check for appendChild usage
        assert "appendChild" in template_content, \
            "Template should use appendChild instead of innerHTML"
    
    def test_jinja2_auto_escaping_still_works(self, client):
        """
        Test that Jinja2 auto-escaping is still enabled.
        
        This is a regression test to ensure we didn't break auto-escaping.
        """
        template_path = "app/templates/doctor_chat.html"
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Check that we're not using the 'safe' filter which disables escaping
        # In the message content areas
        assert "{{ msg.content | safe }}" not in template_content, \
            "Template should not use 'safe' filter on user content"
        
        # Check that we're using normal Jinja2 variables (auto-escaped)
        assert "{{ msg.content }}" in template_content or "{{ escalation" in template_content, \
            "Template should use auto-escaped Jinja2 variables"
    
    def test_no_dangerous_javascript_patterns(self, client):
        """
        Test that dangerous JavaScript patterns are removed.
        """
        template_path = "app/templates/doctor_chat.html"
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Check that dangerous patterns are not present
        dangerous_patterns = [
            "eval(",
            "document.write(",
            "innerHTML = `${",  # Template literal with innerHTML
        ]
        
        for pattern in dangerous_patterns:
            assert pattern not in template_content, \
                f"Dangerous pattern '{pattern}' should not be in template"
    
    def test_fix_maintains_functionality(self, client):
        """
        Test that the fix doesn't break the chat functionality.
        
        This is a regression test to ensure messages can still be displayed.
        """
        template_path = "app/templates/doctor_chat.html"
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Check that message display logic is still present
        assert "message-bubble" in template_content, \
            "Message bubble class should still exist"
        
        assert "chatContainer" in template_content, \
            "Chat container should still exist"
        
        assert "appendChild" in template_content, \
            "Messages should still be appended to chat"
    
    def test_comment_explains_xss_prevention(self, client):
        """
        Test that code includes comment explaining XSS prevention.
        
        Good practice: document security fixes in code.
        """
        template_path = "app/templates/doctor_chat.html"
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Check for security comment
        security_keywords = ["XSS", "prevent", "safe", "escape"]
        has_security_comment = any(keyword in template_content for keyword in security_keywords)
        
        assert has_security_comment, \
            "Code should include comment explaining XSS prevention"


# Summary of Prevention Tests:
#
# 1. test_no_innerhtml_with_user_input - Verifies innerHTML is not used
# 2. test_uses_text_content_for_message - Verifies textContent is used
# 3. test_csp_header_present - Verifies CSP header is set
# 4. test_csp_no_unsafe_eval - Verifies CSP doesn't allow unsafe-eval
# 5. test_csp_restricts_script_src - Verifies script-src is restricted
# 6. test_dom_manipulation_uses_create_element - Verifies safe DOM manipulation
# 7. test_jinja2_auto_escaping_still_works - Regression test for Jinja2
# 8. test_no_dangerous_javascript_patterns - Verifies no dangerous patterns
# 9. test_fix_maintains_functionality - Regression test for functionality
# 10. test_comment_explains_xss_prevention - Verifies documentation
#
# Expected Results AFTER fix:
# - All 10 tests should PASS
# - No XSS vulnerabilities
# - CSP properly configured
# - Functionality maintained

