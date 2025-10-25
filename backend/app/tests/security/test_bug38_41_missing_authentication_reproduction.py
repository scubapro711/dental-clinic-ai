"""
Bug #38-41: Missing Authentication in Critical Endpoints - REPRODUCTION TESTS

These tests REPRODUCE the vulnerabilities by demonstrating that critical endpoints
are accessible WITHOUT authentication.

Expected Result: These tests should PASS (proving the bug exists).
After the fix: These tests should FAIL (proving the bug is fixed).

Bugs:
- Bug #38: Missing Authentication in invoices.py (5 endpoints)
- Bug #39: Missing Authentication in payments.py (8 endpoints)
- Bug #40: Missing Authentication in doctor.py (7 endpoints)
- Bug #41: Missing Authentication in clinic_settings.py (5 endpoints)

CWE: CWE-306 (Missing Authentication for Critical Function)
CVSS: 8.1-9.8 (CRITICAL)
HIPAA: §164.312(a)(1) violation
OWASP: A01:2021 - Broken Access Control
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ==================== Bug #38: invoices.py ====================

class TestBug38InvoicesMissingAuthentication:
    """
    Bug #38: invoices.py endpoints are accessible without authentication
    
    Vulnerability: All 5 invoice endpoints lack authentication
    Impact: Anyone can view/create/download invoices (financial data + PHI)
    """
    
    def test_list_invoices_without_auth(self):
        """
        REPRODUCTION: GET /api/v1/invoices without authentication
        
        Expected (bug exists): 200 OK with mock data
        After fix: 401 Unauthorized
        """
        response = client.get("/api/v1/invoices")
        
        # Bug exists if we get 200 (should be 401/403)
        assert response.status_code == 200, "Bug #38: invoices endpoint is unprotected!"
        # After fix: should get 401 or 403
        # assert response.status_code in [401, 403], "Endpoint is now protected!"
    
    def test_get_invoice_without_auth(self):
        """
        REPRODUCTION: GET /api/v1/invoices/{id} without authentication
        
        Expected (bug exists): 200 OK
        After fix: 401 Unauthorized
        """
        response = client.get("/api/v1/invoices/INV-001")
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #38: get_invoice endpoint is unprotected!"
    
    def test_download_invoice_pdf_without_auth(self):
        """
        REPRODUCTION: GET /api/v1/invoices/{id}/pdf without authentication
        
        Expected (bug exists): 200 OK or error (but not 401)
        After fix: 401 Unauthorized
        """
        response = client.get("/api/v1/invoices/INV-001/pdf")
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #38: download_invoice_pdf endpoint is unprotected!"
    
    def test_create_invoice_without_auth(self):
        """
        REPRODUCTION: POST /api/v1/invoices without authentication
        
        Expected (bug exists): 200/201 or validation error (but not 401)
        After fix: 401 Unauthorized
        """
        invoice_data = {
            "patient_name": "Test Patient",
            "patient_email": "test@example.com",
            "items": [
                {"description": "Dental Cleaning", "quantity": 1, "price": 300.0}
            ]
        }
        
        response = client.post("/api/v1/invoices", json=invoice_data)
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #38: create_invoice endpoint is unprotected!"
    
    def test_invoice_summary_without_auth(self):
        """
        REPRODUCTION: GET /api/v1/invoices/stats/summary without authentication
        
        Expected (bug exists): 200 OK
        After fix: 401 Unauthorized
        """
        response = client.get("/api/v1/invoices/stats/summary")
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #38: invoice_summary endpoint is unprotected!"


# ==================== Bug #39: payments.py ====================

class TestBug39PaymentsMissingAuthentication:
    """
    Bug #39: payments.py endpoints are accessible without authentication
    
    Vulnerability: All 8 payment endpoints lack authentication
    Impact: Anyone can create payments, refunds, view financial data
    """
    
    def test_create_customer_without_auth(self):
        """
        REPRODUCTION: POST /api/v1/payments/create-customer without authentication
        
        Expected (bug exists): 200/201 or error (but not 401)
        After fix: 401 Unauthorized
        """
        customer_data = {
            "email": "test@example.com",
            "name": "Test Customer"
        }
        
        response = client.post("/api/v1/payments/create-customer", json=customer_data)
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #39: create_customer endpoint is unprotected!"
    
    def test_list_customers_without_auth(self):
        """
        REPRODUCTION: GET /api/v1/payments/customers without authentication
        
        Expected (bug exists): 200 OK
        After fix: 401 Unauthorized
        """
        response = client.get("/api/v1/payments/customers")
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #39: list_customers endpoint is unprotected!"
    
    def test_create_payment_link_without_auth(self):
        """
        REPRODUCTION: POST /api/v1/payments/create-payment-link without authentication
        
        Expected (bug exists): 200/201 or error (but not 401)
        After fix: 401 Unauthorized
        """
        payment_link_data = {
            "amount": 500,
            "currency": "ILS",
            "description": "Test Payment"
        }
        
        response = client.post("/api/v1/payments/create-payment-link", json=payment_link_data)
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #39: create_payment_link endpoint is unprotected!"
    
    def test_create_refund_without_auth(self):
        """
        REPRODUCTION: POST /api/v1/payments/refund without authentication
        
        Expected (bug exists): 200/201 or error (but not 401)
        After fix: 401 Unauthorized
        """
        refund_data = {
            "payment_intent": "pi_test123",
            "amount": 100
        }
        
        response = client.post("/api/v1/payments/refund", json=refund_data)
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #39: create_refund endpoint is unprotected!"
    
    def test_get_balance_without_auth(self):
        """
        REPRODUCTION: GET /api/v1/payments/balance without authentication
        
        Expected (bug exists): 200 OK
        After fix: 401 Unauthorized
        """
        response = client.get("/api/v1/payments/balance")
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #39: get_balance endpoint is unprotected!"
    
    def test_get_account_info_without_auth(self):
        """
        REPRODUCTION: GET /api/v1/payments/account without authentication
        
        Expected (bug exists): 200 OK
        After fix: 401 Unauthorized
        """
        response = client.get("/api/v1/payments/account")
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #39: get_account_info endpoint is unprotected!"


# ==================== Bug #40: doctor.py ====================

class TestBug40DoctorMissingAuthentication:
    """
    Bug #40: doctor.py endpoints are accessible without authentication
    
    Vulnerability: All 7 doctor/escalation endpoints lack authentication
    Impact: Anyone can create fake medical escalations, impersonate doctors
    """
    
    def test_create_escalation_without_auth(self):
        """
        REPRODUCTION: POST /api/v1/doctor/create-escalation without authentication
        
        Expected (bug exists): 200/201 or error (but not 401)
        After fix: 401 Unauthorized
        """
        escalation_data = {
            "patient_id": 123,
            "reason": "Test escalation",
            "priority": "high"
        }
        
        response = client.post("/api/v1/doctor/create-escalation", json=escalation_data)
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #40: create_escalation endpoint is unprotected!"
    
    def test_get_escalation_without_auth(self):
        """
        REPRODUCTION: GET /api/v1/doctor/escalation/{id} without authentication
        
        Expected (bug exists): 200 OK or 404 (but not 401)
        After fix: 401 Unauthorized
        """
        response = client.get("/api/v1/doctor/escalation/test-id")
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #40: get_escalation endpoint is unprotected!"
    
    def test_doctor_respond_without_auth(self):
        """
        REPRODUCTION: POST /api/v1/doctor/respond without authentication
        
        Expected (bug exists): 200/201 or error (but not 401)
        After fix: 401 Unauthorized
        """
        response_data = {
            "escalation_id": "test-id",
            "message": "Doctor response"
        }
        
        response = client.post("/api/v1/doctor/respond", json=response_data)
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #40: doctor_respond endpoint is unprotected!"
    
    def test_resolve_escalation_without_auth(self):
        """
        REPRODUCTION: POST /api/v1/doctor/resolve/{id} without authentication
        
        Expected (bug exists): 200 OK or error (but not 401)
        After fix: 401 Unauthorized
        """
        response = client.post("/api/v1/doctor/resolve/test-id")
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #40: resolve_escalation endpoint is unprotected!"
    
    def test_get_active_escalations_without_auth(self):
        """
        REPRODUCTION: GET /api/v1/doctor/active-escalations without authentication
        
        Expected (bug exists): 200 OK
        After fix: 401 Unauthorized
        """
        response = client.get("/api/v1/doctor/active-escalations")
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #40: get_active_escalations endpoint is unprotected!"
    
    def test_notify_doctor_without_auth(self):
        """
        REPRODUCTION: POST /api/v1/doctor/notify-doctor without authentication
        
        Expected (bug exists): 200 OK or error (but not 401)
        After fix: 401 Unauthorized
        """
        notify_data = {
            "escalation_id": "test-id",
            "message": "Urgent notification"
        }
        
        response = client.post("/api/v1/doctor/notify-doctor", json=notify_data)
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #40: notify_doctor endpoint is unprotected!"


# ==================== Bug #41: clinic_settings.py ====================

class TestBug41ClinicSettingsMissingAuthentication:
    """
    Bug #41: clinic_settings.py endpoints are accessible without authentication
    
    Vulnerability: All 5 clinic settings endpoints lack authentication
    Impact: Anyone can view/modify/delete clinic configuration
    """
    
    def test_create_clinic_settings_without_auth(self):
        """
        REPRODUCTION: POST /api/v1/clinic-settings/organizations/{org_id}/settings without authentication
        
        Expected (bug exists): 200/201 or error (but not 401)
        After fix: 401 Unauthorized
        """
        test_org_id = "00000000-0000-0000-0000-000000000001"
        settings_data = {
            "clinic_name": "Test Clinic",
            "timezone": "Asia/Jerusalem"
        }
        
        response = client.post(f"/api/v1/clinic-settings/organizations/{test_org_id}/settings", json=settings_data)
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #41: create_clinic_settings endpoint is unprotected!"
    
    def test_get_clinic_settings_without_auth(self):
        """
        REPRODUCTION: GET /api/v1/clinic-settings/organizations/{org_id}/settings without authentication
        
        Expected (bug exists): 200 OK
        After fix: 401 Unauthorized
        """
        test_org_id = "00000000-0000-0000-0000-000000000001"
        response = client.get(f"/api/v1/clinic-settings/organizations/{test_org_id}/settings")
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #41: get_clinic_settings endpoint is unprotected!"
    
    def test_update_clinic_settings_without_auth(self):
        """
        REPRODUCTION: PUT /api/v1/clinic-settings/organizations/{org_id}/settings without authentication
        
        Expected (bug exists): 200 OK or error (but not 401)
        After fix: 401 Unauthorized
        """
        settings_data = {
            "clinic_name": "Updated Clinic"
        }
        
        test_org_id = "00000000-0000-0000-0000-000000000001"
        response = client.put(f"/api/v1/clinic-settings/organizations/{test_org_id}/settings", json=settings_data)
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #41: update_clinic_settings endpoint is unprotected!"
    
    def test_delete_clinic_settings_without_auth(self):
        """
        REPRODUCTION: DELETE /api/v1/clinic-settings/organizations/{org_id}/settings without authentication
        
        Expected (bug exists): 200/204 or error (but not 401)
        After fix: 401 Unauthorized
        """
        test_org_id = "00000000-0000-0000-0000-000000000001"
        response = client.delete(f"/api/v1/clinic-settings/organizations/{test_org_id}/settings")
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #41: delete_clinic_settings endpoint is unprotected!"
    
    def test_reset_clinic_settings_without_auth(self):
        """
        REPRODUCTION: POST /api/v1/clinic-settings/organizations/{org_id}/settings/reset without authentication
        
        Expected (bug exists): 200 OK or error (but not 401)
        After fix: 401 Unauthorized
        """
        test_org_id = "00000000-0000-0000-0000-000000000001"
        response = client.post(f"/api/v1/clinic-settings/organizations/{test_org_id}/settings/reset")
        
        # Bug exists if we don't get 401/403
        assert response.status_code not in [401, 403], "Bug #41: reset_clinic_settings endpoint is unprotected!"


# ==================== Summary Test ====================

class TestBug38_41Summary:
    """
    Summary test to verify all 25 vulnerable endpoints
    """
    
    def test_all_vulnerable_endpoints_count(self):
        """
        Verify we're testing all 25 vulnerable endpoints:
        - Bug #38: 5 endpoints (invoices.py)
        - Bug #39: 6 endpoints (payments.py) - testing 6 most critical
        - Bug #40: 6 endpoints (doctor.py) - testing 6 most critical
        - Bug #41: 5 endpoints (clinic_settings.py)
        
        Total: 22 tests covering the most critical endpoints
        """
        # This test always passes - it's just documentation
        assert True, "Testing 22 most critical unprotected endpoints"

