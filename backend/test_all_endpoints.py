import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(name, method, endpoint, data=None, expected_status=200):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        status = "✅" if response.status_code == expected_status else "❌"
        print(f"{status} {name}: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Response keys: {list(data.keys())[:5]}")
            except:
                print(f"   Response length: {len(response.text)} bytes")
        else:
            print(f"   Error: {response.text[:100]}")
        
        return response.status_code == expected_status
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False

print("=" * 60)
print("DENTAL AI BACKEND - COMPREHENSIVE API TEST")
print("=" * 60)
print()

# Health check
print("1. HEALTH CHECK")
test_endpoint("Health", "GET", "/health")
print()

# Dashboard endpoints
print("2. DASHBOARD ENDPOINTS")
test_endpoint("Dashboard Metrics", "GET", "/api/v1/dashboard/metrics")
test_endpoint("Agent Status", "GET", "/api/v1/agents/status")
print()

# Appointments
print("3. APPOINTMENTS")
test_endpoint("Get Appointments", "GET", "/api/v1/appointments")
test_endpoint("Today's Appointments", "GET", "/api/v1/appointments/today")
print()

# Patients
print("4. PATIENTS")
test_endpoint("Get Patients", "GET", "/api/v1/patients")
test_endpoint("Search Patients", "GET", "/api/v1/patients?search=John")
print()

# Financial
print("5. FINANCIAL")
test_endpoint("Revenue Overview", "GET", "/api/v1/financial/revenue")
test_endpoint("Payments", "GET", "/api/v1/financial/payments")
print()

# Conversations
print("6. CONVERSATIONS")
test_endpoint("Get Conversations", "GET", "/api/v1/conversations")
print()

# Alerts
print("7. ALERTS")
test_endpoint("Get Alerts", "GET", "/api/v1/alerts")
print()

print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
