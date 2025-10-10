"""
End-to-End Tests for Patient Portal

Tests all user flows from login to data retrieval.
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# Test user credentials (you'll need to create this user)
TEST_USER = {
    "email": "test@example.com",
    "password": "TestPassword123!"
}

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_test(name):
    """Print test name."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}TEST: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")


def print_success(message):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message):
    """Print error message."""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message):
    """Print info message."""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")


class E2ETestRunner:
    """End-to-end test runner."""
    
    def __init__(self):
        self.token = None
        self.user_id = None
        self.patient_id = None
        self.tests_passed = 0
        self.tests_failed = 0
    
    def run_all_tests(self):
        """Run all E2E tests."""
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BLUE}DENTAFLOW PATIENT PORTAL - E2E TESTS{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"Base URL: {BASE_URL}")
        print(f"Test User: {TEST_USER['email']}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Flow 1: Authentication
            self.test_health_check()
            self.test_login()
            
            # Flow 2: Patient Profile
            self.test_get_profile()
            self.test_get_health_score()
            
            # Flow 3: Appointments
            self.test_get_appointments()
            self.test_get_available_slots()
            
            # Flow 4: Doctors
            self.test_get_doctors()
            
            # Flow 5: User-Patient Mapping
            self.test_get_my_mapping()
            self.test_sync_mapping()
            
            # Summary
            self.print_summary()
            
        except Exception as e:
            print_error(f"Test suite failed with error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def test_health_check(self):
        """Test health check endpoint."""
        print_test("Health Check")
        
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Health check passed: {data}")
                self.tests_passed += 1
            else:
                print_error(f"Health check failed: {response.status_code}")
                self.tests_failed += 1
                
        except Exception as e:
            print_error(f"Health check error: {e}")
            self.tests_failed += 1
    
    def test_login(self):
        """Test user login."""
        print_test("User Login")
        
        try:
            response = requests.post(
                f"{API_URL}/auth/login",
                json=TEST_USER,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.user_id = data.get('user', {}).get('id')
                print_success(f"Login successful")
                print_info(f"User ID: {self.user_id}")
                print_info(f"Token: {self.token[:20]}...")
                self.tests_passed += 1
            else:
                print_error(f"Login failed: {response.status_code}")
                print_error(f"Response: {response.text}")
                self.tests_failed += 1
                raise Exception("Login failed - cannot continue tests")
                
        except Exception as e:
            print_error(f"Login error: {e}")
            self.tests_failed += 1
            raise
    
    def get_headers(self):
        """Get authorization headers."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_get_profile(self):
        """Test get patient profile."""
        print_test("Get Patient Profile")
        
        try:
            response = requests.get(
                f"{API_URL}/patient/profile",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.patient_id = data.get('odoo_id')
                print_success("Profile retrieved successfully")
                print_info(f"Name: {data.get('name')}")
                print_info(f"Email: {data.get('email')}")
                print_info(f"Odoo ID: {self.patient_id}")
                print_info(f"Odoo Linked: {data.get('odoo_linked')}")
                self.tests_passed += 1
            else:
                print_error(f"Get profile failed: {response.status_code}")
                print_error(f"Response: {response.text}")
                self.tests_failed += 1
                
        except Exception as e:
            print_error(f"Get profile error: {e}")
            self.tests_failed += 1
    
    def test_get_health_score(self):
        """Test get health score."""
        print_test("Get Health Score")
        
        try:
            response = requests.get(
                f"{API_URL}/patient/health-score",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Health score retrieved successfully")
                print_info(f"Score: {data.get('score')}/100")
                print_info(f"Status: {data.get('status')}")
                print_info(f"Last Visit: {data.get('last_visit_date')}")
                self.tests_passed += 1
            else:
                print_error(f"Get health score failed: {response.status_code}")
                print_error(f"Response: {response.text}")
                self.tests_failed += 1
                
        except Exception as e:
            print_error(f"Get health score error: {e}")
            self.tests_failed += 1
    
    def test_get_appointments(self):
        """Test get appointments."""
        print_test("Get Appointments")
        
        try:
            # Test different filters
            filters = ['upcoming', 'past', 'cancelled', 'all']
            
            for filter_type in filters:
                response = requests.get(
                    f"{API_URL}/appointments?filter={filter_type}",
                    headers=self.get_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    appointments = data.get('appointments', [])
                    print_success(f"Filter '{filter_type}': {len(appointments)} appointments")
                else:
                    print_error(f"Filter '{filter_type}' failed: {response.status_code}")
            
            self.tests_passed += 1
                
        except Exception as e:
            print_error(f"Get appointments error: {e}")
            self.tests_failed += 1
    
    def test_get_available_slots(self):
        """Test get available slots."""
        print_test("Get Available Slots")
        
        try:
            # Get slots for next 7 days
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=7)
            
            response = requests.get(
                f"{API_URL}/appointments/available-slots",
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                slots = data.get('slots', [])
                print_success(f"Found {len(slots)} available slots")
                if slots:
                    print_info(f"First slot: {slots[0]}")
                self.tests_passed += 1
            else:
                print_error(f"Get available slots failed: {response.status_code}")
                print_error(f"Response: {response.text}")
                self.tests_failed += 1
                
        except Exception as e:
            print_error(f"Get available slots error: {e}")
            self.tests_failed += 1
    
    def test_get_doctors(self):
        """Test get doctors."""
        print_test("Get Doctors")
        
        try:
            response = requests.get(
                f"{API_URL}/doctors",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                doctors = data.get('doctors', [])
                print_success(f"Found {len(doctors)} doctors")
                for doctor in doctors[:3]:  # Show first 3
                    print_info(f"  - {doctor.get('name')} ({doctor.get('specialization')})")
                self.tests_passed += 1
            else:
                print_error(f"Get doctors failed: {response.status_code}")
                print_error(f"Response: {response.text}")
                self.tests_failed += 1
                
        except Exception as e:
            print_error(f"Get doctors error: {e}")
            self.tests_failed += 1
    
    def test_get_my_mapping(self):
        """Test get my mapping."""
        print_test("Get My Mapping")
        
        try:
            response = requests.get(
                f"{API_URL}/mappings/me",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Mapping retrieved successfully")
                print_info(f"User ID: {data.get('user_id')}")
                print_info(f"Odoo Patient ID: {data.get('odoo_patient_id')}")
                print_info(f"Email: {data.get('email')}")
                print_info(f"Full Name: {data.get('full_name')}")
                print_info(f"Last Synced: {data.get('last_synced_at')}")
                self.tests_passed += 1
            elif response.status_code == 404:
                print_info("No mapping found (this is OK for new users)")
                self.tests_passed += 1
            else:
                print_error(f"Get mapping failed: {response.status_code}")
                print_error(f"Response: {response.text}")
                self.tests_failed += 1
                
        except Exception as e:
            print_error(f"Get mapping error: {e}")
            self.tests_failed += 1
    
    def test_sync_mapping(self):
        """Test sync mapping."""
        print_test("Sync Mapping")
        
        try:
            response = requests.post(
                f"{API_URL}/mappings/sync",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Mapping synced successfully")
                print_info(f"Message: {data.get('message')}")
                self.tests_passed += 1
            elif response.status_code == 404:
                print_info("No mapping to sync (this is OK for new users)")
                self.tests_passed += 1
            else:
                print_error(f"Sync mapping failed: {response.status_code}")
                print_error(f"Response: {response.text}")
                self.tests_failed += 1
                
        except Exception as e:
            print_error(f"Sync mapping error: {e}")
            self.tests_failed += 1
    
    def print_summary(self):
        """Print test summary."""
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BLUE}TEST SUMMARY{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        
        total = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print_success(f"Passed: {self.tests_passed}")
        print_error(f"Failed: {self.tests_failed}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.tests_failed == 0:
            print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
            print(f"{Colors.GREEN}ALL TESTS PASSED! ✓{Colors.END}")
            print(f"{Colors.GREEN}{'='*60}{Colors.END}")
        else:
            print(f"\n{Colors.RED}{'='*60}{Colors.END}")
            print(f"{Colors.RED}SOME TESTS FAILED! ✗{Colors.END}")
            print(f"{Colors.RED}{'='*60}{Colors.END}")
            sys.exit(1)


if __name__ == "__main__":
    runner = E2ETestRunner()
    runner.run_all_tests()

