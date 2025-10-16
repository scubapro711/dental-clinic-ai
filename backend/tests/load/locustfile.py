"""
Load Testing Script for DentaFlow SaaS

This script uses Locust to simulate realistic user behavior and test the system under load.

Usage:
    locust -f locustfile.py --host=https://api.dentaflow.ai

Test Scenarios:
    1. User Authentication
    2. Dashboard Access
    3. Patient Search
    4. Appointment Booking
    5. AI Chat Conversations
"""

import json
import random
from locust import HttpUser, task, between, events
from locust.exception import RescheduleTask

# Test Data
TEST_USERS = [
    {"email": f"test{i}@dentaflow.ai", "password": "TestPassword123!"}
    for i in range(1, 11)
]

TEST_PATIENTS = [
    {"name": "John Doe", "phone": "+972501234567"},
    {"name": "Jane Smith", "phone": "+972502345678"},
    {"name": "Bob Johnson", "phone": "+972503456789"},
]

class DentaFlowUser(HttpUser):
    """
    Simulates a typical DentaFlow user (clinic staff member).
    """
    
    # Wait time between tasks (1-5 seconds)
    wait_time = between(1, 5)
    
    def on_start(self):
        """
        Called when a simulated user starts.
        Authenticates the user and stores the token.
        """
        # Select a random test user
        self.user_data = random.choice(TEST_USERS)
        
        # Login
        response = self.client.post("/api/v1/auth/login", json={
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            self.organization_id = data.get("organization_id")
        else:
            print(f"Login failed for {self.user_data['email']}: {response.status_code}")
            raise RescheduleTask()
    
    @task(5)
    def view_dashboard(self):
        """
        View the main dashboard.
        Weight: 5 (most common action)
        """
        self.client.get(
            "/api/v1/dashboard/overview",
            headers=self.headers,
            name="/dashboard/overview"
        )
    
    @task(3)
    def search_patients(self):
        """
        Search for patients.
        Weight: 3
        """
        search_term = random.choice(["John", "Jane", "Bob", "Smith", "Doe"])
        self.client.get(
            f"/api/v1/patients/search?q={search_term}",
            headers=self.headers,
            name="/patients/search"
        )
    
    @task(2)
    def view_appointments(self):
        """
        View appointments for today.
        Weight: 2
        """
        self.client.get(
            "/api/v1/appointments/today",
            headers=self.headers,
            name="/appointments/today"
        )
    
    @task(2)
    def view_patient_details(self):
        """
        View details of a random patient.
        Weight: 2
        """
        # Assume patient IDs 1-100
        patient_id = random.randint(1, 100)
        self.client.get(
            f"/api/v1/patients/{patient_id}",
            headers=self.headers,
            name="/patients/{id}"
        )
    
    @task(1)
    def create_appointment(self):
        """
        Create a new appointment.
        Weight: 1 (less common)
        """
        patient_id = random.randint(1, 100)
        doctor_id = random.randint(1, 10)
        
        appointment_data = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "start_time": "2025-10-20T10:00:00",
            "end_time": "2025-10-20T10:30:00",
            "appointment_type": "checkup",
            "notes": "Load test appointment"
        }
        
        self.client.post(
            "/api/v1/appointments",
            headers=self.headers,
            json=appointment_data,
            name="/appointments [POST]"
        )
    
    @task(3)
    def ai_chat_message(self):
        """
        Send a message to the AI chat.
        Weight: 3
        """
        messages = [
            "Show me today's appointments",
            "Who is my next patient?",
            "Search for John Doe",
            "What's the status of patient 42?",
            "Book an appointment for tomorrow at 2pm"
        ]
        
        message = random.choice(messages)
        
        self.client.post(
            "/api/v1/chat/message",
            headers=self.headers,
            json={
                "message": message,
                "agent": "alex"
            },
            name="/chat/message"
        )
    
    @task(1)
    def view_statistics(self):
        """
        View clinic statistics.
        Weight: 1
        """
        self.client.get(
            "/api/v1/dashboard/statistics",
            headers=self.headers,
            name="/dashboard/statistics"
        )
    
    @task(1)
    def view_revenue(self):
        """
        View revenue dashboard.
        Weight: 1
        """
        self.client.get(
            "/api/v1/dashboard/revenue",
            headers=self.headers,
            name="/dashboard/revenue"
        )


class PatientPortalUser(HttpUser):
    """
    Simulates a patient using the patient portal.
    """
    
    wait_time = between(2, 10)
    
    def on_start(self):
        """
        Patient login or registration.
        """
        # For simplicity, assume patient is already registered
        self.patient_data = {
            "email": f"patient{random.randint(1, 100)}@example.com",
            "password": "PatientPassword123!"
        }
        
        # Login
        response = self.client.post("/api/v1/patient-portal/login", json={
            "email": self.patient_data["email"],
            "password": self.patient_data["password"]
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            # If login fails, skip this user
            raise RescheduleTask()
    
    @task(5)
    def view_my_appointments(self):
        """
        View my appointments.
        Weight: 5 (most common)
        """
        self.client.get(
            "/api/v1/patient-portal/appointments",
            headers=self.headers,
            name="/patient-portal/appointments"
        )
    
    @task(3)
    def view_medical_records(self):
        """
        View medical records.
        Weight: 3
        """
        self.client.get(
            "/api/v1/patient-portal/medical-records",
            headers=self.headers,
            name="/patient-portal/medical-records"
        )
    
    @task(2)
    def view_billing(self):
        """
        View billing information.
        Weight: 2
        """
        self.client.get(
            "/api/v1/patient-portal/billing",
            headers=self.headers,
            name="/patient-portal/billing"
        )
    
    @task(1)
    def book_appointment(self):
        """
        Book a new appointment.
        Weight: 1
        """
        appointment_data = {
            "doctor_id": random.randint(1, 10),
            "start_time": "2025-10-25T14:00:00",
            "appointment_type": "checkup"
        }
        
        self.client.post(
            "/api/v1/patient-portal/appointments",
            headers=self.headers,
            json=appointment_data,
            name="/patient-portal/appointments [POST]"
        )


class SuperAdminUser(HttpUser):
    """
    Simulates a Super Admin user accessing the admin dashboard.
    """
    
    wait_time = between(3, 10)
    
    def on_start(self):
        """
        Super Admin login.
        """
        # Super Admin credentials
        response = self.client.post("/api/v1/auth/login", json={
            "email": "admin@dentaflow.ai",
            "password": "SuperAdminPassword123!"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            raise RescheduleTask()
    
    @task(5)
    def view_organizations(self):
        """
        View all organizations.
        Weight: 5
        """
        self.client.get(
            "/api/v1/super-admin/organizations",
            headers=self.headers,
            name="/super-admin/organizations"
        )
    
    @task(3)
    def view_revenue_dashboard(self):
        """
        View revenue dashboard.
        Weight: 3
        """
        self.client.get(
            "/api/v1/super-admin/revenue/summary",
            headers=self.headers,
            name="/super-admin/revenue/summary"
        )
    
    @task(2)
    def view_usage_dashboard(self):
        """
        View usage dashboard.
        Weight: 2
        """
        self.client.get(
            "/api/v1/super-admin/usage/summary",
            headers=self.headers,
            name="/super-admin/usage/summary"
        )
    
    @task(1)
    def view_analytics(self):
        """
        View advanced analytics.
        Weight: 1
        """
        self.client.get(
            "/api/v1/super-admin/analytics/summary",
            headers=self.headers,
            name="/super-admin/analytics/summary"
        )


# Event Listeners for Custom Metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Called when the load test starts.
    """
    print("Load test starting...")
    print(f"Target host: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Called when the load test stops.
    """
    print("Load test completed.")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Total failures: {environment.stats.total.num_failures}")
    print(f"Average response time: {environment.stats.total.avg_response_time:.2f}ms")
    print(f"Requests per second: {environment.stats.total.total_rps:.2f}")


# Custom Load Shapes (Optional)
from locust import LoadTestShape

class StepLoadShape(LoadTestShape):
    """
    A load test shape that increases users in steps.
    
    Step 1: 10 users for 2 minutes
    Step 2: 50 users for 2 minutes
    Step 3: 100 users for 2 minutes
    Step 4: 200 users for 2 minutes
    """
    
    step_time = 120  # 2 minutes per step
    step_load = 10
    spawn_rate = 10
    time_limit = 480  # 8 minutes total
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time > self.time_limit:
            return None
        
        current_step = run_time // self.step_time
        return (self.step_load * (2 ** current_step), self.spawn_rate)

