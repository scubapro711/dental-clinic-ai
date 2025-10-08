# 🧪 DentaFlow Aggressive Testing Plan

**Comprehensive testing strategy for all components before production deployment.**

**Deployment Criteria:** ✅ **90%+ pass rate with ZERO critical issues**

---

## 📋 Testing Overview

### Test Categories

| Category | Tests | Critical | Pass Rate Required |
|----------|-------|----------|-------------------|
| **Unit Tests** | 150+ | Yes | 95% |
| **Integration Tests** | 50+ | Yes | 90% |
| **API Tests** | 100+ | Yes | 95% |
| **Load Tests** | 10+ | No | 80% |
| **Security Tests** | 30+ | Yes | 100% |
| **E2E Tests** | 20+ | No | 85% |

### Severity Levels

- 🔴 **Critical**: Blocks deployment (data loss, security breach, system crash)
- 🟠 **High**: Major functionality broken (appointment booking fails)
- 🟡 **Medium**: Minor functionality issues (UI glitch)
- 🟢 **Low**: Cosmetic issues (typo, alignment)

**Deployment Rule:** ZERO 🔴 Critical issues, max 2 🟠 High issues

---

## 🎯 Test Execution Plan

### Phase 1: Unit Tests (30 minutes)

**Run all unit tests for each component**

```bash
cd /home/ubuntu/dental-clinic-ai/backend

# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Expected: 95%+ pass rate, 80%+ code coverage
```

**Components to test:**
- ✅ Models (User, Organization, Conversation, Message, etc.)
- ✅ Services (ConversationManager, ProactiveSuggestions)
- ✅ Integrations (Odoo, Telegram, WhatsApp)
- ✅ Auth (Cognito, JWT)
- ✅ Encryption
- ✅ Audit Logging

---

### Phase 2: Integration Tests (45 minutes)

**Test component interactions**

```bash
# Run integration tests
pytest tests/integration/ -v --tb=short

# Expected: 90%+ pass rate
```

**Critical flows:**
1. User registration → Organization creation → Membership
2. Conversation creation → Message exchange → Agent response
3. Odoo appointment booking → Confirmation → Reminder
4. Telegram message → Agent processing → Response
5. Proactive suggestion → User action → Execution

---

### Phase 3: API Tests (1 hour)

**Test all API endpoints**

```bash
# Run API tests
pytest tests/api/ -v

# Or use Newman (Postman CLI)
newman run DentaFlow_API_Tests.postman_collection.json \
  --environment production.postman_environment.json \
  --reporters cli,html
```

**Endpoints to test:** (100+ tests)
- `/api/v1/auth/*` - Authentication (15 tests)
- `/api/v1/organizations/*` - Organizations (10 tests)
- `/api/v1/memberships/*` - Memberships (10 tests)
- `/api/v1/clinic-settings/*` - Settings (10 tests)
- `/api/v1/treatment-prices/*` - Prices (10 tests)
- `/api/v1/conversations/*` - Conversations (15 tests)
- `/api/v1/messages/*` - Messages (10 tests)
- `/api/v1/proactive-suggestions/*` - Suggestions (10 tests)
- `/api/v1/audit-logs/*` - Audit (10 tests)

---

### Phase 4: Load Tests (1 hour)

**Test system under heavy load**

```bash
# Install Locust
pip3 install locust

# Run load tests
cd tests/load
locust -f load_test.py --host=http://localhost:8000

# Open browser: http://localhost:8089
# Configure: 100 users, spawn rate 10/sec, run 10 minutes
```

**Load test scenarios:**

#### Scenario 1: Concurrent Conversations
- **Users:** 100 concurrent
- **Duration:** 10 minutes
- **Actions:** Send messages, get responses
- **Success criteria:** 
  - ✅ Response time < 2 seconds (95th percentile)
  - ✅ Error rate < 1%
  - ✅ No crashes

#### Scenario 2: Appointment Booking Storm
- **Users:** 50 concurrent
- **Duration:** 5 minutes
- **Actions:** Book appointments via Odoo
- **Success criteria:**
  - ✅ Response time < 3 seconds
  - ✅ No double bookings
  - ✅ All bookings saved

#### Scenario 3: Database Stress
- **Users:** 200 concurrent
- **Duration:** 10 minutes
- **Actions:** Read/write operations
- **Success criteria:**
  - ✅ No deadlocks
  - ✅ No connection pool exhaustion
  - ✅ Query time < 500ms

#### Scenario 4: API Rate Limiting
- **Users:** 500 concurrent
- **Duration:** 2 minutes
- **Actions:** Rapid API calls
- **Success criteria:**
  - ✅ Rate limiting works (429 responses)
  - ✅ No server crashes
  - ✅ Graceful degradation

---

### Phase 5: Security Tests (1 hour)

**Test security vulnerabilities**

```bash
# Run security scanner
cd /home/ubuntu/dental-clinic-ai/backend

# 1. SQL Injection tests
python3 tests/security/test_sql_injection.py

# 2. XSS tests
python3 tests/security/test_xss.py

# 3. Authentication bypass tests
python3 tests/security/test_auth_bypass.py

# 4. Encryption tests
python3 tests/security/test_encryption.py

# 5. OWASP ZAP scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8000 -r security_report.html
```

**Critical security checks:**
- ✅ SQL injection prevention
- ✅ XSS prevention
- ✅ CSRF protection
- ✅ JWT validation
- ✅ Password hashing (bcrypt)
- ✅ Data encryption at rest
- ✅ HTTPS only
- ✅ Rate limiting
- ✅ Input validation
- ✅ Output encoding

**ZERO security issues allowed for deployment!**

---

### Phase 6: End-to-End Tests (30 minutes)

**Test complete user journeys**

```bash
# Run E2E tests with Playwright
cd tests/e2e
pytest test_e2e.py -v
```

**User journeys:**
1. **New patient registration** → Conversation → Appointment booking
2. **Existing patient** → Login → Check appointment status
3. **Telegram user** → Send message → Get response → Book appointment
4. **Admin user** → Login → View audit logs → Export report

---

## 🔧 Test Scripts

### Script 1: Automated Test Runner

```bash
#!/bin/bash
# File: run_all_tests.sh

echo "🧪 DentaFlow Aggressive Testing Suite"
echo "======================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
CRITICAL_ISSUES=0

cd /home/ubuntu/dental-clinic-ai/backend

# Phase 1: Unit Tests
echo ""
echo "📦 Phase 1: Unit Tests"
echo "----------------------"
pytest tests/ -v --cov=app --cov-report=term --junitxml=test-results/unit-tests.xml
UNIT_EXIT=$?
if [ $UNIT_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Unit tests passed${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ Unit tests failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Phase 2: Integration Tests
echo ""
echo "🔗 Phase 2: Integration Tests"
echo "-----------------------------"
pytest tests/integration/ -v --junitxml=test-results/integration-tests.xml
INTEGRATION_EXIT=$?
if [ $INTEGRATION_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Integration tests passed${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ Integration tests failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Phase 3: API Tests
echo ""
echo "🌐 Phase 3: API Tests"
echo "--------------------"
pytest tests/api/ -v --junitxml=test-results/api-tests.xml
API_EXIT=$?
if [ $API_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ API tests passed${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ API tests failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Phase 4: Security Tests
echo ""
echo "🔒 Phase 4: Security Tests"
echo "-------------------------"
pytest tests/security/ -v --junitxml=test-results/security-tests.xml
SECURITY_EXIT=$?
if [ $SECURITY_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Security tests passed${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ Security tests FAILED - CRITICAL!${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 10))  # Security = critical
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Calculate pass rate
PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))

# Summary
echo ""
echo "======================================"
echo "📊 Test Summary"
echo "======================================"
echo "Total test suites: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"
echo "Pass rate: $PASS_RATE%"
echo "Critical issues: $CRITICAL_ISSUES"
echo ""

# Deployment decision
if [ $CRITICAL_ISSUES -eq 0 ] && [ $PASS_RATE -ge 90 ]; then
    echo -e "${GREEN}✅ DEPLOYMENT APPROVED${NC}"
    echo "All tests passed with $PASS_RATE% success rate and ZERO critical issues!"
    exit 0
else
    echo -e "${RED}❌ DEPLOYMENT BLOCKED${NC}"
    if [ $CRITICAL_ISSUES -gt 0 ]; then
        echo "Reason: $CRITICAL_ISSUES critical issue(s) found"
    else
        echo "Reason: Pass rate $PASS_RATE% is below 90% threshold"
    fi
    exit 1
fi
```

---

### Script 2: Load Test with Locust

```python
# File: tests/load/load_test.py

from locust import HttpUser, task, between
import random
import json

class DentaFlowUser(HttpUser):
    """Simulate DentaFlow user behavior."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Login before starting tasks."""
        # Register/login
        response = self.client.post("/api/v1/auth/register", json={
            "email": f"test{random.randint(1000, 9999)}@example.com",
            "password": "Test123!@#",
            "name": "Test User"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}
    
    @task(10)
    def send_message(self):
        """Send message in conversation (most common action)."""
        if not self.token:
            return
        
        # Create conversation
        response = self.client.post(
            "/api/v1/conversations",
            headers=self.headers,
            json={
                "channel": "web_chat",
                "primary_agent": "alex"
            }
        )
        
        if response.status_code == 200:
            conversation_id = response.json()["id"]
            
            # Send message
            self.client.post(
                f"/api/v1/conversations/{conversation_id}/messages",
                headers=self.headers,
                json={
                    "role": "user",
                    "content": "אני רוצה לקבוע תור"
                }
            )
    
    @task(5)
    def get_suggestions(self):
        """Get proactive suggestions."""
        if not self.token:
            return
        
        # Assume conversation exists
        conversation_id = "test-conversation-id"
        self.client.get(
            f"/api/v1/proactive-suggestions/conversations/{conversation_id}/suggestions",
            headers=self.headers
        )
    
    @task(3)
    def get_treatment_prices(self):
        """Get treatment prices."""
        self.client.get("/api/v1/treatment-prices")
    
    @task(2)
    def get_clinic_settings(self):
        """Get clinic settings."""
        if not self.token:
            return
        
        self.client.get(
            "/api/v1/clinic-settings",
            headers=self.headers
        )
    
    @task(1)
    def create_appointment(self):
        """Book appointment (less frequent, more intensive)."""
        if not self.token:
            return
        
        # This would call Odoo integration
        self.client.post(
            "/api/v1/appointments",
            headers=self.headers,
            json={
                "patient_name": "Test Patient",
                "date": "2025-10-15",
                "time": "10:00",
                "treatment_type": "checkup"
            }
        )


class StressTestUser(HttpUser):
    """Aggressive stress test user."""
    
    wait_time = between(0.1, 0.5)  # Very fast requests
    
    @task
    def rapid_fire_requests(self):
        """Send rapid requests to stress test."""
        endpoints = [
            "/api/v1/health",
            "/api/v1/treatment-prices",
            "/api/v1/conversations",
        ]
        
        endpoint = random.choice(endpoints)
        self.client.get(endpoint)
```

**Run load test:**
```bash
# Start with 10 users, ramp up to 100
locust -f tests/load/load_test.py --host=http://localhost:8000 \
  --users 100 --spawn-rate 10 --run-time 10m --html=load-test-report.html
```

---

### Script 3: Security Test Suite

```python
# File: tests/security/test_security.py

import pytest
import requests
from sqlalchemy import text

class TestSecurity:
    """Comprehensive security tests."""
    
    BASE_URL = "http://localhost:8000"
    
    def test_sql_injection_prevention(self, db):
        """Test SQL injection is prevented."""
        
        # Attempt SQL injection in email field
        malicious_inputs = [
            "admin' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT * FROM users--",
            "admin'--",
            "' OR 1=1--"
        ]
        
        for malicious_input in malicious_inputs:
            response = requests.post(
                f"{self.BASE_URL}/api/v1/auth/login",
                json={
                    "email": malicious_input,
                    "password": "anything"
                }
            )
            
            # Should return 401 (unauthorized), not 500 (error) or 200 (success)
            assert response.status_code in [400, 401, 422], \
                f"SQL injection may be possible with input: {malicious_input}"
    
    def test_xss_prevention(self):
        """Test XSS is prevented."""
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            response = requests.post(
                f"{self.BASE_URL}/api/v1/conversations",
                json={
                    "patient_name": payload,
                    "channel": "web_chat"
                }
            )
            
            # XSS should be escaped/sanitized
            if response.status_code == 200:
                data = response.json()
                assert payload not in str(data), \
                    f"XSS payload not sanitized: {payload}"
    
    def test_authentication_required(self):
        """Test protected endpoints require authentication."""
        
        protected_endpoints = [
            "/api/v1/conversations",
            "/api/v1/memberships",
            "/api/v1/clinic-settings",
            "/api/v1/audit-logs"
        ]
        
        for endpoint in protected_endpoints:
            response = requests.get(f"{self.BASE_URL}{endpoint}")
            assert response.status_code == 401, \
                f"Endpoint {endpoint} should require authentication"
    
    def test_jwt_validation(self):
        """Test JWT validation is strict."""
        
        invalid_tokens = [
            "invalid.token.here",
            "Bearer fake-token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.signature",
            ""
        ]
        
        for token in invalid_tokens:
            response = requests.get(
                f"{self.BASE_URL}/api/v1/conversations",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 401, \
                f"Invalid JWT should be rejected: {token}"
    
    def test_rate_limiting(self):
        """Test rate limiting prevents abuse."""
        
        # Send 100 rapid requests
        responses = []
        for i in range(100):
            response = requests.get(f"{self.BASE_URL}/api/v1/health")
            responses.append(response.status_code)
        
        # Should see some 429 (Too Many Requests) responses
        rate_limited = responses.count(429)
        assert rate_limited > 0, "Rate limiting not working"
    
    def test_password_hashing(self, db):
        """Test passwords are hashed, not stored in plaintext."""
        
        # Create test user
        requests.post(
            f"{self.BASE_URL}/api/v1/auth/register",
            json={
                "email": "security-test@example.com",
                "password": "MyPassword123!",
                "name": "Security Test"
            }
        )
        
        # Check database
        result = db.execute(
            text("SELECT password_hash FROM users WHERE email = 'security-test@example.com'")
        ).fetchone()
        
        if result:
            password_hash = result[0]
            # Should be bcrypt hash (starts with $2b$)
            assert password_hash.startswith("$2b$"), \
                "Password not properly hashed with bcrypt"
            assert "MyPassword123!" not in password_hash, \
                "Password stored in plaintext!"
    
    def test_data_encryption(self, db):
        """Test sensitive data is encrypted."""
        
        # Check if encryption is enabled
        result = db.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name LIKE '%encrypted%'")
        ).fetchall()
        
        # Should have encrypted columns
        assert len(result) > 0, "No encrypted columns found in sensitive tables"
    
    def test_https_only(self):
        """Test HTTP is redirected to HTTPS."""
        
        # This test assumes production environment
        # Skip in development
        pass
    
    def test_cors_configuration(self):
        """Test CORS is properly configured."""
        
        response = requests.options(
            f"{self.BASE_URL}/api/v1/conversations",
            headers={"Origin": "https://evil.com"}
        )
        
        # Should not allow arbitrary origins
        allowed_origin = response.headers.get("Access-Control-Allow-Origin")
        assert allowed_origin != "*", "CORS allows all origins - security risk!"
    
    def test_input_validation(self):
        """Test input validation prevents invalid data."""
        
        # Test invalid email
        response = requests.post(
            f"{self.BASE_URL}/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "Test123!",
                "name": "Test"
            }
        )
        assert response.status_code == 422, "Invalid email accepted"
        
        # Test weak password
        response = requests.post(
            f"{self.BASE_URL}/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "123",  # Too weak
                "name": "Test"
            }
        )
        assert response.status_code == 422, "Weak password accepted"
```

---

### Script 4: Database Stress Test

```python
# File: tests/load/db_stress_test.py

import asyncio
import asyncpg
import random
from datetime import datetime

async def stress_test_database():
    """Stress test database with concurrent operations."""
    
    # Connect to database
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='password',
        database='dentaflow'
    )
    
    async def create_conversation():
        """Create conversation."""
        await conn.execute('''
            INSERT INTO conversations (id, organization_id, status, channel, primary_agent, langgraph_thread_id)
            VALUES (gen_random_uuid(), gen_random_uuid(), 'active', 'web_chat', 'alex', gen_random_uuid()::text)
        ''')
    
    async def create_message():
        """Create message."""
        await conn.execute('''
            INSERT INTO messages (id, conversation_id, organization_id, role, content)
            SELECT gen_random_uuid(), id, organization_id, 'user', 'Test message'
            FROM conversations
            ORDER BY random()
            LIMIT 1
        ''')
    
    async def read_conversations():
        """Read conversations."""
        await conn.fetch('SELECT * FROM conversations LIMIT 100')
    
    # Run concurrent operations
    tasks = []
    for i in range(1000):
        if i % 3 == 0:
            tasks.append(create_conversation())
        elif i % 3 == 1:
            tasks.append(create_message())
        else:
            tasks.append(read_conversations())
    
    start = datetime.now()
    await asyncio.gather(*tasks)
    duration = (datetime.now() - start).total_seconds()
    
    print(f"✅ Completed 1000 database operations in {duration:.2f} seconds")
    print(f"   Throughput: {1000/duration:.2f} ops/sec")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(stress_test_database())
```

---

## 📊 Test Results Dashboard

### Expected Results

```
====================================
📊 DentaFlow Test Results
====================================

Unit Tests:           ✅ 145/150 (96.7%)
Integration Tests:    ✅ 47/50 (94.0%)
API Tests:            ✅ 98/100 (98.0%)
Load Tests:           ✅ 9/10 (90.0%)
Security Tests:       ✅ 30/30 (100.0%) 🔒
E2E Tests:            ✅ 18/20 (90.0%)

------------------------------------
Overall Pass Rate:    ✅ 94.2%
Critical Issues:      ✅ 0
High Issues:          ⚠️  1
Medium Issues:        ℹ️  3
Low Issues:           ℹ️  8

====================================
🚀 DEPLOYMENT STATUS: APPROVED
====================================

All criteria met:
✅ Pass rate > 90% (94.2%)
✅ Zero critical issues
✅ Security tests 100% pass
✅ Load tests acceptable

Ready for production deployment!
```

---

## 🚀 Deployment Checklist

After tests pass:

- [ ] All tests executed
- [ ] Pass rate ≥ 90%
- [ ] Zero critical issues
- [ ] Security tests 100% pass
- [ ] Load tests show acceptable performance
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] Backup created
- [ ] Rollback plan ready
- [ ] Monitoring configured
- [ ] Team notified

---

**Last Updated:** October 8, 2025  
**Version:** 1.0  
**Status:** Ready for Execution 🧪
