# Load Testing with Locust for Dental Clinic AI System
# Version: 1.0.0
# Date: 2025-12-29

from locust import HttpUser, task, between
import random
import json

class DentalClinicUser(HttpUser):
    """Simulates a user interacting with the dental clinic system."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts."""
        self.hebrew_messages = [
            "שלום, אני רוצה לקבוע תור לרופא שיניים",
            "מה השעות הפנויות השבוע הבא?",
            "אני רוצה לבטל את התור שלי",
            "איך אני יכול לשנות את התור?",
            "מה המחיר של בדיקה כללית?",
            "האם יש לכם זמינות היום?",
            "אני רוצה לדבר עם רופא",
            "מתי המרפאה פתוחה?",
            "איך מגיעים למרפאה?",
            "האם אתם מקבלים ביטוח?"
        ]
        
        self.english_messages = [
            "Hello, I need to schedule a dental appointment",
            "What times are available next week?",
            "I want to cancel my appointment",
            "How can I reschedule my appointment?",
            "What's the cost of a general checkup?",
            "Do you have availability today?",
            "I need to speak with a doctor",
            "What are your office hours?",
            "How do I get to the clinic?",
            "Do you accept insurance?"
        ]
    
    @task(3)
    def health_check(self):
        """Test health endpoint - most frequent."""
        self.client.get("/health")
    
    @task(2)
    def status_check(self):
        """Test status endpoint."""
        self.client.get("/api/status")
    
    @task(5)
    def process_hebrew_message(self):
        """Process Hebrew message - common user interaction."""
        message = random.choice(self.hebrew_messages)
        self.client.post("/api/process_message", json={"text": message})
    
    @task(3)
    def process_english_message(self):
        """Process English message."""
        message = random.choice(self.english_messages)
        self.client.post("/api/process_message", json={"text": message})
    
    @task(2)
    def search_patients(self):
        """Search for patients."""
        search_terms = ["יוסי", "מרים", "דוד", "שרה", "test", "cohen", "levi"]
        term = random.choice(search_terms)
        self.client.post("/api/search_patients", json={"query": term})
    
    @task(2)
    def get_providers(self):
        """Get list of providers."""
        self.client.post("/api/get_providers", json={})
    
    @task(3)
    def get_available_slots(self):
        """Get available appointment slots."""
        dates = ["2025-01-15", "2025-01-16", "2025-01-17", "2025-01-20", "2025-01-21"]
        date = random.choice(dates)
        self.client.post("/api/get_available_slots", json={"date": date})
    
    @task(1)
    def book_appointment(self):
        """Attempt to book an appointment."""
        self.client.post("/api/book_appointment", json={
            "patient_id": f"patient_{random.randint(1, 20)}",
            "doctor_id": f"doctor_{random.randint(1, 4)}",
            "date": "2025-01-20",
            "time": f"{random.randint(9, 16)}:00",
            "treatment": "בדיקה כללית"
        })
    
    @task(1)
    def simulation_status(self):
        """Check simulation status."""
        self.client.get("/api/simulation_status")

class HeavyUser(HttpUser):
    """Simulates a heavy user that makes many requests quickly."""
    
    wait_time = between(0.1, 0.5)  # Very short wait time
    
    @task(10)
    def rapid_health_checks(self):
        """Rapid health checks."""
        self.client.get("/health")
    
    @task(5)
    def rapid_message_processing(self):
        """Rapid message processing."""
        messages = [
            "שלום",
            "Hello",
            "תור",
            "appointment",
            "עזרה",
            "help"
        ]
        message = random.choice(messages)
        self.client.post("/api/process_message", json={"text": message})

class AdminUser(HttpUser):
    """Simulates an admin user checking system status."""
    
    wait_time = between(5, 10)  # Longer wait time
    
    @task(5)
    def detailed_status_check(self):
        """Check detailed system status."""
        self.client.get("/api/status")
    
    @task(2)
    def simulation_control(self):
        """Control simulation."""
        # Start simulation
        self.client.post("/api/start_simulation", json={
            "duration_minutes": 1,
            "speed": 2.0
        })
        
        # Check status
        self.client.get("/api/simulation_status")
        
        # Stop simulation
        self.client.post("/api/stop_simulation", json={})

# Custom load test scenarios
class StressTestUser(HttpUser):
    """Stress test user for aggressive testing."""
    
    wait_time = between(0.05, 0.2)  # Very aggressive
    
    @task
    def stress_test_endpoints(self):
        """Stress test all endpoints randomly."""
        endpoints = [
            ("GET", "/health", None),
            ("GET", "/api/status", None),
            ("POST", "/api/process_message", {"text": "stress test"}),
            ("POST", "/api/search_patients", {"query": "test"}),
            ("POST", "/api/get_providers", {}),
            ("POST", "/api/get_available_slots", {"date": "2025-01-15"}),
        ]
        
        method, url, data = random.choice(endpoints)
        
        if method == "GET":
            self.client.get(url)
        elif method == "POST":
            self.client.post(url, json=data)

# Run with: locust -f load_test_locust.py --host=http://localhost:8000
