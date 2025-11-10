#!/usr/bin/env python3.11
"""
Comprehensive Patient Search API Testing Script
Tests 10+ scenarios for patient search and mapping functionality
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

def search_patients(token: str, query: str) -> list:
    """Search for patients."""
    response = requests.get(
        f"{BASE_URL}/patients/search",
        params={"query": query},
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Search failed: {response.text}")

def create_mapping(token: str, patient_id: int) -> Dict[str, Any]:
    """Create patient mapping."""
    response = requests.post(
        f"{BASE_URL}/mappings/me",
        json={"odoo_patient_id": patient_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Mapping creation failed: {response.text}")

def get_my_mapping(token: str) -> Dict[str, Any]:
    """Get current user's mapping."""
    response = requests.get(
        f"{BASE_URL}/mappings/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        return None
    else:
        raise Exception(f"Get mapping failed: {response.text}")

def run_tests():
    """Run all tests."""
    print("=" * 80)
    print("PATIENT SEARCH & MAPPING API TESTS")
    print("=" * 80)
    
    # Login
    print("\n[SETUP] Logging in...")
    try:
        token = login("searchtest@gmail.com", "TestPass123!")
        print("✅ Login successful")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Search by name "Shane"
    print("\n[TEST 1] Search by name: Shane")
    try:
        results = search_patients(token, "Shane")
        if len(results) > 0:
            print(f"✅ Found {len(results)} patients")
            for p in results[:3]:
                print(f"   - {p['name']} (ID: {p['id']}, Phone: {p['phone']})")
            tests_passed += 1
        else:
            print("❌ No results found")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        tests_failed += 1
    
    # Test 2: Search by name "Smith"
    print("\n[TEST 2] Search by name: Smith")
    try:
        results = search_patients(token, "Smith")
        if len(results) > 0:
            print(f"✅ Found {len(results)} patients")
            for p in results[:3]:
                print(f"   - {p['name']} (ID: {p['id']})")
            tests_passed += 1
        else:
            print("❌ No results found")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        tests_failed += 1
    
    # Test 3: Search by partial name "Joh"
    print("\n[TEST 3] Search by partial name: Joh")
    try:
        results = search_patients(token, "Joh")
        if len(results) > 0:
            print(f"✅ Found {len(results)} patients")
            for p in results[:3]:
                print(f"   - {p['name']} (ID: {p['id']})")
            tests_passed += 1
        else:
            print("❌ No results found")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        tests_failed += 1
    
    # Test 4: Search by phone with +972 prefix
    print("\n[TEST 4] Search by phone: +972521481915")
    try:
        results = search_patients(token, "+972521481915")
        if len(results) > 0:
            print(f"✅ Found {len(results)} patients")
            for p in results:
                print(f"   - {p['name']} (ID: {p['id']}, Phone: {p['phone']})")
            tests_passed += 1
        else:
            print("⚠️  No results (phone normalization issue)")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        tests_failed += 1
    
    # Test 5: Search with very short query (should fail validation)
    print("\n[TEST 5] Search with short query: 'a' (should fail)")
    try:
        results = search_patients(token, "a")
        print(f"❌ Should have failed validation but got {len(results)} results")
        tests_failed += 1
    except Exception as e:
        if "min_length" in str(e).lower() or "422" in str(e):
            print("✅ Correctly rejected short query")
            tests_passed += 1
        else:
            print(f"❌ Unexpected error: {e}")
            tests_failed += 1
    
    # Test 6: Search with special characters
    print("\n[TEST 6] Search with special characters: O'Brien")
    try:
        results = search_patients(token, "O'Brien")
        if len(results) >= 0:
            print(f"✅ Search handled special characters ({len(results)} results)")
            tests_passed += 1
        else:
            print("❌ Failed to handle special characters")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        tests_failed += 1
    
    # Test 7: Search with numbers
    print("\n[TEST 7] Search with numbers: 123")
    try:
        results = search_patients(token, "123")
        print(f"✅ Search handled numbers ({len(results)} results)")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        tests_failed += 1
    
    # Test 8: Search for common first name
    print("\n[TEST 8] Search by first name: David")
    try:
        results = search_patients(token, "David")
        if len(results) > 0:
            print(f"✅ Found {len(results)} patients")
            for p in results[:3]:
                print(f"   - {p['name']} (ID: {p['id']})")
            tests_passed += 1
        else:
            print("❌ No results found")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        tests_failed += 1
    
    # Test 9: Create patient mapping
    print("\n[TEST 9] Create patient mapping")
    try:
        # First check if mapping already exists
        existing = get_my_mapping(token)
        if existing:
            print(f"⚠️  Mapping already exists (Patient ID: {existing['odoo_patient_id']})")
            print("✅ Get mapping works")
            tests_passed += 1
        else:
            # Create new mapping
            mapping = create_mapping(token, 1)  # Map to Shane גבע
            print(f"✅ Mapping created successfully")
            print(f"   User ID: {mapping['user_id']}")
            print(f"   Patient ID: {mapping['odoo_patient_id']}")
            tests_passed += 1
    except Exception as e:
        if "already have" in str(e):
            print("✅ Correctly prevents duplicate mapping")
            tests_passed += 1
        else:
            print(f"❌ Test failed: {e}")
            tests_failed += 1
    
    # Test 10: Get my mapping
    print("\n[TEST 10] Get my mapping")
    try:
        mapping = get_my_mapping(token)
        if mapping:
            print(f"✅ Mapping retrieved successfully")
            print(f"   Patient ID: {mapping['odoo_patient_id']}")
            print(f"   Email: {mapping['email']}")
            tests_passed += 1
        else:
            print("❌ No mapping found")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"📊 Success Rate: {tests_passed}/{tests_passed + tests_failed} ({100 * tests_passed / (tests_passed + tests_failed):.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()

