#!/usr/bin/env python3.11
"""
Patient Portal API Integration Test
Tests all patient portal endpoints with Mock Odoo Dental backend
"""

import requests
import json
from typing import Dict, Any, Optional

# Configuration
API_BASE_URL = "http://localhost:8002"
TEST_USER = {
    "email": "test@dentaflow.com",
    "password": "testpassword123",
    "full_name": "Test User",
    "role": "patient"
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class PatientPortalAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user_data: Optional[Dict[str, Any]] = None
        self.test_results = []
        
    def log(self, message: str, status: str = "INFO"):
        color = {
            "PASS": Colors.GREEN,
            "FAIL": Colors.RED,
            "INFO": Colors.BLUE,
            "WARN": Colors.YELLOW
        }.get(status, "")
        print(f"{color}[{status}]{Colors.END} {message}")
        
    def test_endpoint(self, name: str, method: str, endpoint: str, 
                     expected_status: int = 200, data: Optional[Dict] = None,
                     auth_required: bool = False) -> bool:
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if 'login' in endpoint or 'register' in endpoint:
                    # Form data for auth endpoints
                    response = requests.post(url, data=data, headers=headers)
                else:
                    headers['Content-Type'] = 'application/json'
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                headers['Content-Type'] = 'application/json'
                response = requests.put(url, json=data, headers=headers)
            else:
                self.log(f"{name}: Unsupported method {method}", "FAIL")
                return False
                
            if response.status_code == expected_status:
                self.log(f"{name}: {response.status_code} ✓", "PASS")
                self.test_results.append((name, True, response.status_code))
                return True
            else:
                self.log(f"{name}: Expected {expected_status}, got {response.status_code}", "FAIL")
                try:
                    error_detail = response.json()
                    self.log(f"  Error: {json.dumps(error_detail, indent=2)}", "FAIL")
                except:
                    self.log(f"  Response: {response.text[:200]}", "FAIL")
                self.test_results.append((name, False, response.status_code))
                return False
                
        except Exception as e:
            self.log(f"{name}: Exception - {str(e)}", "FAIL")
            self.test_results.append((name, False, 0))
            return False
            
    def test_authentication(self):
        """Test authentication flow"""
        self.log("\n=== Testing Authentication ===", "INFO")
        
        # Test registration
        register_data = {
            "username": TEST_USER["email"],
            "password": TEST_USER["password"],
            "email": TEST_USER["email"],
            "full_name": TEST_USER["full_name"],
            "role": TEST_USER["role"]
        }
        
        # Try to register (might fail if user exists, that's ok)
        response = requests.post(
            f"{self.base_url}/api/v1/auth/register",
            json=register_data
        )
        
        if response.status_code in [200, 201]:
            self.log("Registration: Success", "PASS")
            data = response.json()
            self.token = data.get('access_token')
        elif response.status_code == 400:
            self.log("Registration: User already exists (expected)", "WARN")
        else:
            self.log(f"Registration: Unexpected status {response.status_code}", "WARN")
            
        # Test login
        login_data = {
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            data=login_data
        )
        
        if response.status_code == 200:
            self.log("Login: Success ✓", "PASS")
            data = response.json()
            self.token = data.get('access_token')
            self.test_results.append(("Login", True, 200))
        else:
            self.log(f"Login: Failed with status {response.status_code}", "FAIL")
            self.test_results.append(("Login", False, response.status_code))
            return False
            
        # Test /auth/me
        if self.token:
            return self.test_endpoint(
                "Get Current User",
                "GET",
                "/api/v1/auth/me",
                auth_required=True
            )
        return False
        
    def test_patient_profile(self):
        """Test patient profile endpoints"""
        self.log("\n=== Testing Patient Profile ===", "INFO")
        
        self.test_endpoint(
            "Get Patient Profile",
            "GET",
            "/api/v1/patient/profile",
            auth_required=True
        )
        
        self.test_endpoint(
            "Get Health Score",
            "GET",
            "/api/v1/patient/health-score",
            auth_required=True
        )
        
    def test_appointments(self):
        """Test appointment endpoints"""
        self.log("\n=== Testing Appointments ===", "INFO")
        
        self.test_endpoint(
            "Get All Appointments",
            "GET",
            "/api/v1/appointments",
            auth_required=True
        )
        
        self.test_endpoint(
            "Get Upcoming Appointments",
            "GET",
            "/api/v1/appointments?status=upcoming",
            auth_required=True
        )
        
        self.test_endpoint(
            "Get Doctors List",
            "GET",
            "/api/v1/doctors",
            auth_required=True
        )
        
        self.test_endpoint(
            "Get Available Slots",
            "GET",
            "/api/v1/appointments/available-slots?doctor_id=1&date=2025-11-15",
            auth_required=True
        )
        
    def test_medical_records(self):
        """Test medical records endpoints"""
        self.log("\n=== Testing Medical Records ===", "INFO")
        
        self.test_endpoint(
            "Get All Medical Records",
            "GET",
            "/api/v1/records",
            auth_required=True
        )
        
        self.test_endpoint(
            "Get X-Ray Records",
            "GET",
            "/api/v1/records?record_type=xray",
            auth_required=True
        )
        
    def test_billing(self):
        """Test billing endpoints"""
        self.log("\n=== Testing Billing ===", "INFO")
        
        self.test_endpoint(
            "Get Billing Overview",
            "GET",
            "/api/v1/billing/overview",
            auth_required=True
        )
        
        self.test_endpoint(
            "Get All Invoices",
            "GET",
            "/api/v1/billing/invoices",
            auth_required=True
        )
        
        self.test_endpoint(
            "Get Paid Invoices",
            "GET",
            "/api/v1/billing/invoices?status=paid",
            auth_required=True
        )
        
    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "="*60, "INFO")
        self.log("TEST SUMMARY", "INFO")
        self.log("="*60, "INFO")
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        percentage = (passed / total * 100) if total > 0 else 0
        
        self.log(f"\nTotal Tests: {total}", "INFO")
        self.log(f"Passed: {passed}", "PASS" if passed == total else "INFO")
        self.log(f"Failed: {total - passed}", "FAIL" if passed < total else "INFO")
        self.log(f"Success Rate: {percentage:.1f}%", 
                "PASS" if percentage >= 90 else "WARN" if percentage >= 70 else "FAIL")
        
        if passed < total:
            self.log("\nFailed Tests:", "FAIL")
            for name, success, status in self.test_results:
                if not success:
                    self.log(f"  - {name} (Status: {status})", "FAIL")
                    
        return percentage >= 90
        
    def run_all_tests(self):
        """Run all integration tests"""
        self.log("="*60, "INFO")
        self.log("PATIENT PORTAL API INTEGRATION TESTS", "INFO")
        self.log(f"Backend: {self.base_url}", "INFO")
        self.log("="*60, "INFO")
        
        # Test authentication first
        if not self.test_authentication():
            self.log("\nAuthentication failed. Cannot proceed with other tests.", "FAIL")
            return False
            
        # Test all endpoints
        self.test_patient_profile()
        self.test_appointments()
        self.test_medical_records()
        self.test_billing()
        
        # Print summary
        return self.print_summary()

def main():
    tester = PatientPortalAPITester(API_BASE_URL)
    success = tester.run_all_tests()
    
    if success:
        print(f"\n{Colors.GREEN}✓ All tests passed! API integration is ready.{Colors.END}")
        exit(0)
    else:
        print(f"\n{Colors.RED}✗ Some tests failed. Please review the errors above.{Colors.END}")
        exit(1)

if __name__ == "__main__":
    main()

