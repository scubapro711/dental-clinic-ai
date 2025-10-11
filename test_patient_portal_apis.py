#!/usr/bin/env python3.11
"""
Comprehensive Patient Portal API Testing Script
Tests all dashboard endpoints with real Mock Odoo data
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8002/api/v1"

def login(email: str, password: str) -> str:
    """Login and return access token."""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.text}")

def test_endpoint(name: str, method: str, endpoint: str, token: str, **kwargs):
    """Test an endpoint and return result."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, **kwargs)
        elif method == "POST":
            response = requests.post(url, headers=headers, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"Status {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def run_tests():
    """Run all tests."""
    print("=" * 80)
    print("PATIENT PORTAL API TESTS")
    print("=" * 80)
    
    # Login with mapped user
    print("\n[SETUP] Logging in as mapped user...")
    try:
        token = login("searchtest@gmail.com", "TestPass123!")
        print("✅ Login successful")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Get patient profile
    print("\n[TEST 1] GET /patient/profile")
    success, result = test_endpoint("Profile", "GET", "/patient/profile", token)
    if success:
        print(f"✅ Profile retrieved")
        print(f"   Name: {result.get('name')}")
        print(f"   Email: {result.get('email')}")
        print(f"   Odoo linked: {result.get('odoo_linked')}")
        if result.get('odoo_id'):
            print(f"   Odoo ID: {result.get('odoo_id')}")
        tests_passed += 1
    else:
        print(f"❌ Failed: {result}")
        tests_failed += 1
    
    # Test 2: Get health score
    print("\n[TEST 2] GET /patient/health-score")
    success, result = test_endpoint("Health Score", "GET", "/patient/health-score", token)
    if success:
        print(f"✅ Health score retrieved")
        print(f"   Score: {result.get('score')}/100")
        print(f"   Message: {result.get('message')}")
        print(f"   Factors: {len(result.get('factors', []))}")
        print(f"   Recommendations: {len(result.get('recommendations', []))}")
        tests_passed += 1
    else:
        print(f"❌ Failed: {result}")
        tests_failed += 1
    
    # Test 3: Get all appointments
    print("\n[TEST 3] GET /appointments (all)")
    success, result = test_endpoint("Appointments All", "GET", "/appointments", token, params={"status": "all"})
    if success:
        print(f"✅ Appointments retrieved")
        print(f"   Total: {result.get('total', 0)}")
        appointments = result.get('appointments', [])
        if appointments:
            print(f"   Sample appointment:")
            apt = appointments[0]
            print(f"     - Date: {apt.get('date')} {apt.get('time')}")
            print(f"     - Doctor: {apt.get('doctor')}")
            print(f"     - Type: {apt.get('type')}")
            print(f"     - Status: {apt.get('status')}")
        tests_passed += 1
    else:
        print(f"❌ Failed: {result}")
        tests_failed += 1
    
    # Test 4: Get upcoming appointments
    print("\n[TEST 4] GET /appointments (upcoming)")
    success, result = test_endpoint("Appointments Upcoming", "GET", "/appointments", token, params={"status": "upcoming"})
    if success:
        print(f"✅ Upcoming appointments retrieved")
        print(f"   Count: {len(result.get('appointments', []))}")
        tests_passed += 1
    else:
        print(f"❌ Failed: {result}")
        tests_failed += 1
    
    # Test 5: Get past appointments
    print("\n[TEST 5] GET /appointments (past)")
    success, result = test_endpoint("Appointments Past", "GET", "/appointments", token, params={"status": "past"})
    if success:
        print(f"✅ Past appointments retrieved")
        print(f"   Count: {len(result.get('appointments', []))}")
        tests_passed += 1
    else:
        print(f"❌ Failed: {result}")
        tests_failed += 1
    
    # Test 6: Get doctors
    print("\n[TEST 6] GET /doctors")
    success, result = test_endpoint("Doctors", "GET", "/doctors", token)
    if success:
        print(f"✅ Doctors retrieved")
        print(f"   Total: {result.get('total', 0)}")
        doctors = result.get('doctors', [])
        if doctors:
            print(f"   Doctors:")
            for doc in doctors:
                print(f"     - {doc.get('name')} ({doc.get('specialization')})")
        tests_passed += 1
    else:
        print(f"❌ Failed: {result}")
        tests_failed += 1
    
    # Test 7: Get available slots
    print("\n[TEST 7] GET /patient/appointments/available-slots")
    from datetime import datetime, timedelta
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    success, result = test_endpoint(
        "Available Slots", 
        "GET", 
        "/patient/appointments/available-slots", 
        token, 
        params={"doctor_id": 1, "date": tomorrow}
    )
    if success:
        print(f"✅ Available slots retrieved")
        print(f"   Date: {result.get('date')}")
        print(f"   Slots: {len(result.get('slots', []))}")
        tests_passed += 1
    else:
        print(f"❌ Failed: {result}")
        tests_failed += 1
    
    # Test 8: Get my mapping
    print("\n[TEST 8] GET /mappings/me")
    success, result = test_endpoint("My Mapping", "GET", "/mappings/me", token)
    if success:
        print(f"✅ Mapping retrieved")
        print(f"   Patient ID: {result.get('odoo_patient_id')}")
        print(f"   Email: {result.get('email')}")
        print(f"   Full name: {result.get('full_name')}")
        tests_passed += 1
    else:
        print(f"❌ Failed: {result}")
        tests_failed += 1
    
    # Test 9-20: Multiple page refreshes (stress test)
    print("\n[TEST 9-20] Multiple page refreshes (stress test)")
    refresh_passed = 0
    for i in range(1, 13):
        success, _ = test_endpoint(f"Refresh {i}", "GET", "/patient/profile", token)
        if success:
            refresh_passed += 1
    
    print(f"✅ Passed {refresh_passed}/12 refreshes")
    tests_passed += refresh_passed
    tests_failed += (12 - refresh_passed)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    total = tests_passed + tests_failed
    print(f"📊 Success Rate: {tests_passed}/{total} ({100 * tests_passed / total:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()

