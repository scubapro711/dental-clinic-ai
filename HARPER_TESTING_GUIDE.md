# Harper Testing Guide
## Comprehensive Testing & Quality Assurance

**Version:** 1.0  
**Date:** October 19, 2025

---

## Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Automated Tests](#automated-tests)
3. [Manual Testing](#manual-testing)
4. [Integration Testing](#integration-testing)
5. [Performance Testing](#performance-testing)
6. [Security Testing](#security-testing)
7. [User Acceptance Testing](#user-acceptance-testing)

---

## Testing Strategy

### Test Pyramid

```
         ┌─────────────────┐
         │   E2E Tests     │  ← 10% (Manual UAT)
         ├─────────────────┤
         │ Integration     │  ← 30% (API + DB)
         ├─────────────────┤
         │  Unit Tests     │  ← 60% (Tools + Services)
         └─────────────────┘
```

### Coverage Goals

- **Unit Tests:** 80%+
- **Integration Tests:** 70%+
- **E2E Tests:** Critical paths only
- **Regression Tests:** 100% (all domains)

---

## Automated Tests

### 1. Regression Tests (Pinecone Migration)

**File:** `backend/scripts/test_pinecone_migration.py`

**What it tests:**
- All 5 domains (clinical, financial, operational, general, hipaa)
- 2 queries per domain
- Vector retrieval accuracy
- Response quality

**Run:**
```bash
cd backend
export PINECONE_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
python scripts/test_pinecone_migration.py
```

**Expected Output:**
```
============================================================
PINECONE MIGRATION REGRESSION TESTS
============================================================

Testing Clinical Domain...
✅ Query 1: What are the clinical protocols?
   Found 2 results
✅ Query 2: How to handle patient records?
   Found 2 results

Testing Financial Domain...
✅ Query 1: What are the billing procedures?
   Found 1 results
✅ Query 2: How to handle insurance claims?
   Found 1 results

Testing Operational Domain...
✅ Query 1: What are the operational guidelines?
   Found 1 results
✅ Query 2: How to manage staff scheduling?
   Found 1 results

Testing General Domain...
✅ Query 1: What are the general policies?
   Found 1 results
✅ Query 2: How to handle patient inquiries?
   Found 1 results

Testing HIPAA Domain...
✅ Query 1: What is the HIPAA Privacy Rule?
   Found 3 results
✅ Query 2: What are the requirements for PHI encryption?
   Found 3 results

============================================================
TEST SUMMARY
============================================================
Total tests: 10
✅ Passed: 10
❌ Failed: 0
Success rate: 100.0%
============================================================
```

### 2. Unit Tests (Tools)

**Create:** `backend/tests/test_hipaa_tools.py`

```python
import pytest
from app.tools.hipaa_tools import (
    search_hipaa_knowledge,
    check_phi_compliance,
    validate_baa,
    # ... other tools
)

class TestHIPAATools:
    def test_search_hipaa_knowledge(self):
        """Test HIPAA knowledge search."""
        result = search_hipaa_knowledge("What is PHI?")
        assert "Protected Health Information" in result
        assert len(result) > 0
    
    def test_check_phi_compliance(self):
        """Test PHI compliance checker."""
        result = check_phi_compliance(
            data_type="patient_records",
            storage_location="encrypted_database",
            access_controls=["role_based", "mfa"],
            encryption_at_rest=True,
            encryption_in_transit=True
        )
        assert "compliance_score" in result
        assert result["compliance_score"] >= 80
    
    def test_validate_baa(self):
        """Test BAA validation."""
        result = validate_baa(
            vendor_name="Test Vendor",
            baa_signed_date="2024-01-01",
            services_provided=["cloud_storage"],
            phi_access=True
        )
        assert "is_valid" in result
        assert "findings" in result
    
    # Add tests for all 10 tools...

# Run tests
pytest backend/tests/test_hipaa_tools.py -v
```

### 3. Integration Tests (API Endpoints)

**Create:** `backend/tests/test_compliance_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestComplianceAPI:
    def test_chat_endpoint(self, auth_token):
        """Test Harper chat endpoint."""
        response = client.post(
            "/api/v1/compliance/chat",
            json={"message": "What is HIPAA?"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "suggested_actions" in data
    
    def test_get_compliance_score(self, auth_token):
        """Test compliance score endpoint."""
        response = client.get(
            "/api/v1/compliance/score",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data
        assert 0 <= data["overall_score"] <= 100
    
    def test_get_alerts(self, auth_token):
        """Test alerts endpoint."""
        response = client.get(
            "/api/v1/compliance/alerts",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access."""
        response = client.get("/api/v1/compliance/score")
        assert response.status_code == 401

# Run tests
pytest backend/tests/test_compliance_api.py -v
```

### 4. Database Tests

**Create:** `backend/tests/test_compliance_models.py`

```python
import pytest
from app.models.compliance_alert import ComplianceAlert, AlertType, AlertSeverity
from app.models.compliance_metric import ComplianceMetric

class TestComplianceModels:
    def test_create_alert(self, db_session):
        """Test creating a compliance alert."""
        alert = ComplianceAlert(
            organization_id=1,
            alert_type=AlertType.BAA_EXPIRING,
            severity=AlertSeverity.MEDIUM,
            title="BAA Expiring Soon",
            description="Vendor BAA expires in 15 days"
        )
        db_session.add(alert)
        db_session.commit()
        
        assert alert.id is not None
        assert alert.status == "open"
    
    def test_alert_workflow(self, db_session):
        """Test alert status workflow."""
        alert = ComplianceAlert(
            organization_id=1,
            alert_type=AlertType.PHI_COMPLIANCE_ISSUE,
            severity=AlertSeverity.HIGH,
            title="PHI Compliance Issue"
        )
        db_session.add(alert)
        db_session.commit()
        
        # Acknowledge
        alert.acknowledge(user_id=1)
        assert alert.status == "acknowledged"
        assert alert.acknowledged_at is not None
        
        # Start progress
        alert.start_progress()
        assert alert.status == "in_progress"
        
        # Resolve
        alert.resolve(user_id=1, notes="Fixed encryption")
        assert alert.status == "resolved"
        assert alert.resolved_at is not None
    
    def test_create_metric(self, db_session):
        """Test creating a compliance metric."""
        metric = ComplianceMetric(
            organization_id=1,
            metric_type="overall_compliance",
            value=87.5
        )
        db_session.add(metric)
        db_session.commit()
        
        assert metric.id is not None
        assert metric.value == 87.5

# Run tests
pytest backend/tests/test_compliance_models.py -v
```

---

## Manual Testing

### Test Case 1: Harper Chat (Basic)

**Objective:** Verify Harper can answer basic HIPAA questions

**Steps:**
1. Login as Clinic Admin
2. Navigate to `/clinic/compliance`
3. Click "Ask Harper" tab
4. Type: "What is the HIPAA Privacy Rule?"
5. Click Send

**Expected Result:**
- Response mentions Privacy Rule
- Response includes key points (patient rights, permitted uses, etc.)
- Suggested actions appear
- Sources are cited

**Pass Criteria:**
- ✅ Response is relevant and accurate
- ✅ Response time < 5 seconds
- ✅ Sources are provided
- ✅ Suggested actions are actionable

---

### Test Case 2: Harper Chat (Complex)

**Objective:** Verify Harper can handle complex multi-part questions

**Steps:**
1. Login as Clinic Admin
2. Navigate to `/clinic/compliance`
3. Click "Ask Harper" tab
4. Type: "We're implementing a new EHR system. What HIPAA requirements do we need to consider for data migration, and do we need a BAA with the vendor?"
5. Click Send

**Expected Result:**
- Response addresses both data migration and BAA requirements
- Response is structured (numbered points or sections)
- Specific regulations cited (e.g., Security Rule, Privacy Rule)
- Suggested actions include:
  - Review vendor's security practices
  - Obtain BAA before migration
  - Ensure encryption during transfer
  - Document the process

**Pass Criteria:**
- ✅ All parts of question addressed
- ✅ Specific, actionable guidance
- ✅ Relevant regulations cited
- ✅ Suggested actions are comprehensive

---

### Test Case 3: Compliance Score Display

**Objective:** Verify compliance score is calculated and displayed correctly

**Steps:**
1. Login as Clinic Admin
2. Navigate to `/clinic/compliance`
3. View "Overview" tab

**Expected Result:**
- Overall compliance score displayed (0-100)
- Category scores displayed:
  - PHI Handling
  - Security Controls
  - BAA Compliance
  - Patient Rights
  - Breach Preparedness
- Trend indicator (up/down arrow)
- Last updated timestamp

**Pass Criteria:**
- ✅ All scores are realistic (0-100)
- ✅ Scores match backend calculation
- ✅ Trend is accurate
- ✅ UI is clear and readable

---

### Test Case 4: Alert Management

**Objective:** Verify alerts can be created, acknowledged, and resolved

**Steps:**
1. Login as Super Admin
2. Navigate to `/super-admin/compliance`
3. Click "Alerts" tab
4. View existing alerts
5. Click "Acknowledge" on an open alert
6. Add notes
7. Click "Start Progress"
8. Add resolution notes
9. Click "Resolve"

**Expected Result:**
- Alert status changes: Open → Acknowledged → In Progress → Resolved
- Timestamps are recorded
- Notes are saved
- Alert disappears from "Open" filter

**Pass Criteria:**
- ✅ Status transitions work correctly
- ✅ Timestamps are accurate
- ✅ Notes are persisted
- ✅ Filters work correctly

---

### Test Case 5: Proactive Monitoring

**Objective:** Verify monitoring system generates alerts

**Steps:**
1. Login as Super Admin
2. Navigate to `/super-admin/compliance`
3. Click "Run Checks" button (or wait for scheduled run)
4. Wait for completion
5. Check "Alerts" tab

**Expected Result:**
- Checks complete successfully
- New alerts generated (if issues found)
- Alert types match check results:
  - BAA_EXPIRING (if BAAs expiring soon)
  - PHI_COMPLIANCE_ISSUE (if PHI issues found)
  - SECURITY_GAP (if security controls missing)
  - etc.

**Pass Criteria:**
- ✅ Checks complete without errors
- ✅ Alerts are accurate
- ✅ Severity levels are appropriate
- ✅ Action items are helpful

---

### Test Case 6: RBAC (Role-Based Access Control)

**Objective:** Verify only authorized users can access Harper

**Steps:**
1. **Test 1: Clinic Admin**
   - Login as Clinic Admin
   - Navigate to `/clinic/compliance`
   - Expected: Access granted ✅

2. **Test 2: Super Admin**
   - Login as Super Admin
   - Navigate to `/super-admin/compliance`
   - Expected: Access granted ✅

3. **Test 3: Doctor (org_staff)**
   - Login as Doctor
   - Try to navigate to `/clinic/compliance`
   - Expected: Access denied ❌ or limited view

4. **Test 4: Patient (org_viewer)**
   - Login as Patient
   - Try to navigate to `/clinic/compliance`
   - Expected: Access denied ❌

**Pass Criteria:**
- ✅ Clinic Admin has full access
- ✅ Super Admin has full access
- ✅ Doctors have limited/no access
- ✅ Patients have no access

---

## Integration Testing

### Test Scenario 1: End-to-End Compliance Workflow

**Objective:** Test complete workflow from alert generation to resolution

**Steps:**
1. **Setup:**
   - Create test organization
   - Create test BAA expiring in 10 days

2. **Trigger Monitoring:**
   - Run daily checks
   - Verify BAA_EXPIRING alert created

3. **Alert Handling:**
   - Login as Clinic Admin
   - View alert in dashboard
   - Ask Harper: "What do I need to do about this expiring BAA?"
   - Follow suggested actions

4. **Resolution:**
   - Renew BAA with vendor
   - Update BAA in system
   - Resolve alert with notes

5. **Verification:**
   - Verify alert is resolved
   - Verify compliance score improved
   - Verify metrics updated

**Pass Criteria:**
- ✅ Alert generated correctly
- ✅ Harper provides helpful guidance
- ✅ Alert can be resolved
- ✅ Metrics reflect resolution

---

### Test Scenario 2: Multi-Organization Compliance

**Objective:** Verify Super Admin can monitor multiple organizations

**Steps:**
1. **Setup:**
   - Create 3 test organizations (Org A, B, C)
   - Create different alerts for each:
     - Org A: BAA_EXPIRING
     - Org B: PHI_COMPLIANCE_ISSUE
     - Org C: SECURITY_GAP

2. **Super Admin View:**
   - Login as Super Admin
   - Navigate to `/super-admin/compliance`
   - View aggregated dashboard

3. **Filtering:**
   - Filter by organization
   - Filter by severity
   - Filter by status

4. **Drill-down:**
   - Click on Org A
   - View Org A specific compliance
   - Ask Harper about Org A issues

**Pass Criteria:**
- ✅ All organizations visible
- ✅ Alerts correctly attributed
- ✅ Filters work correctly
- ✅ Drill-down provides org-specific data

---

## Performance Testing

### Test 1: Harper Response Time

**Objective:** Verify Harper responds within acceptable time

**Method:**
```bash
# Use Apache Bench
ab -n 100 -c 10 -p query.json -T application/json \
  -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/compliance/chat
```

**query.json:**
```json
{"message": "What is HIPAA?"}
```

**Expected Results:**
- Mean response time: < 3 seconds
- 95th percentile: < 5 seconds
- 99th percentile: < 8 seconds
- No timeouts

**Pass Criteria:**
- ✅ 95% of requests < 5 seconds
- ✅ No 500 errors
- ✅ No timeouts

---

### Test 2: Concurrent Users

**Objective:** Verify system handles multiple concurrent users

**Method:**
```bash
# Simulate 50 concurrent users
ab -n 500 -c 50 -p query.json -T application/json \
  -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/compliance/chat
```

**Expected Results:**
- All requests complete successfully
- No database deadlocks
- No memory leaks
- Response time degradation < 20%

**Pass Criteria:**
- ✅ 100% success rate
- ✅ No errors
- ✅ Acceptable performance degradation

---

### Test 3: Large Knowledge Base Query

**Objective:** Verify performance with complex queries

**Method:**
```python
import time
from app.services.vector_db import vector_db

queries = [
    "Explain all HIPAA Privacy Rule requirements",
    "What are the complete Security Rule technical safeguards?",
    "Describe the entire breach notification process",
]

for query in queries:
    start = time.time()
    results = vector_db.search('hipaa', query, top_k=10)
    elapsed = time.time() - start
    print(f"Query: {query[:50]}... - Time: {elapsed:.2f}s")
```

**Expected Results:**
- All queries < 2 seconds
- Results are relevant
- No errors

**Pass Criteria:**
- ✅ All queries complete
- ✅ Response time acceptable
- ✅ Results are accurate

---

## Security Testing

### Test 1: Authentication

**Objective:** Verify all endpoints require authentication

**Method:**
```bash
# Test without token
curl -X GET http://localhost:8000/api/v1/compliance/score

# Expected: 401 Unauthorized
```

**Test all endpoints:**
- `/api/v1/compliance/chat` → 401
- `/api/v1/compliance/score` → 401
- `/api/v1/compliance/alerts` → 401
- `/api/v1/compliance/metrics` → 401

**Pass Criteria:**
- ✅ All endpoints return 401 without token
- ✅ Valid token grants access

---

### Test 2: Authorization (RBAC)

**Objective:** Verify role-based access control

**Method:**
```python
# Test with different roles
roles = ['org_viewer', 'org_staff', 'org_admin', 'super_admin']

for role in roles:
    token = get_token_for_role(role)
    response = client.get(
        "/api/v1/compliance/score",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"{role}: {response.status_code}")
```

**Expected Results:**
- `org_viewer` (Patient): 403 Forbidden
- `org_staff` (Doctor): 403 Forbidden
- `org_admin` (Clinic Admin): 200 OK
- `super_admin`: 200 OK

**Pass Criteria:**
- ✅ Only authorized roles can access
- ✅ Proper error messages

---

### Test 3: Input Validation

**Objective:** Verify input validation prevents injection attacks

**Method:**
```bash
# Test SQL injection
curl -X POST http://localhost:8000/api/v1/compliance/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "'; DROP TABLE compliance_alerts; --"}'

# Expected: Sanitized input, no SQL execution

# Test XSS
curl -X POST http://localhost:8000/api/v1/compliance/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "<script>alert(\"XSS\")</script>"}'

# Expected: Escaped output
```

**Pass Criteria:**
- ✅ No SQL injection possible
- ✅ No XSS possible
- ✅ Input is sanitized

---

## User Acceptance Testing (UAT)

### UAT Checklist

**Clinic Admin Perspective:**

- [ ] Can access compliance dashboard
- [ ] Can view compliance score
- [ ] Can view and manage alerts
- [ ] Can chat with Harper
- [ ] Harper provides helpful answers
- [ ] Suggested actions are actionable
- [ ] Can acknowledge alerts
- [ ] Can resolve alerts
- [ ] Can view compliance metrics
- [ ] Can view trends over time
- [ ] UI is intuitive
- [ ] Response times are acceptable

**Super Admin Perspective:**

- [ ] Can access super admin compliance dashboard
- [ ] Can view all organizations
- [ ] Can filter by organization
- [ ] Can view aggregated metrics
- [ ] Can drill down to specific org
- [ ] Can run manual compliance checks
- [ ] Can view system-wide trends
- [ ] Can export reports
- [ ] Harper provides platform-level insights

**General:**

- [ ] No errors or crashes
- [ ] Data is accurate
- [ ] UI is responsive (mobile/desktop)
- [ ] Help text is clear
- [ ] Error messages are helpful

---

## Continuous Testing

### Pre-Deployment Checklist

Before deploying to production:

- [ ] All automated tests pass (100%)
- [ ] Manual test cases pass
- [ ] Performance tests meet criteria
- [ ] Security tests pass
- [ ] UAT approved by stakeholders
- [ ] Documentation is complete
- [ ] Rollback plan is ready
- [ ] Monitoring is configured
- [ ] Alerts are configured
- [ ] Backup is verified

### Post-Deployment Monitoring

After deployment:

- [ ] Monitor error rates (< 0.1%)
- [ ] Monitor response times (< 5s p95)
- [ ] Monitor database performance
- [ ] Monitor Pinecone usage
- [ ] Monitor OpenAI API usage
- [ ] Check user feedback
- [ ] Review logs for errors
- [ ] Verify scheduled jobs run

---

## Conclusion

This testing guide ensures Harper is:

✅ **Functionally correct** - All features work as expected  
✅ **Performant** - Meets response time requirements  
✅ **Secure** - Protected against common attacks  
✅ **Reliable** - Handles edge cases gracefully  
✅ **User-friendly** - Intuitive and helpful

**Test Coverage:** Comprehensive  
**Quality Assurance:** Production-ready

---

**For questions or issues:**
- Review test results
- Check logs
- Run regression tests
- Consult documentation

**Maintained by:** Manus AI Agent  
**Last Updated:** October 19, 2025

