"""
Load Testing for DentalAI Backend
Uses Locust for stress testing and performance benchmarking
"""

from locust import HttpUser, task, between
import json
import random


class DentalAIUser(HttpUser):
    """Simulates a user interacting with DentalAI system"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a simulated user starts"""
        self.conversation_id = f"load_test_{random.randint(1000, 9999)}"
        self.patient_names = [
            "David Cohen", "Sarah Levi", "Michael Ben-David",
            "Rachel Mizrahi", "Yosef Katz", "Miriam Goldstein"
        ]
    
    @task(3)
    def health_check(self):
        """Test health endpoint (frequent)"""
        self.client.get("/health")
    
    @task(10)
    def chat_greeting(self):
        """Test chat with greeting"""
        self.client.post(
            "/api/v1/chat",
            json={
                "message": "שלום",
                "conversation_id": self.conversation_id
            }
        )
    
    @task(8)
    def chat_appointment_inquiry(self):
        """Test appointment inquiry"""
        messages = [
            "מתי יש תורים פנויים?",
            "אני רוצה לקבוע תור",
            "יש תור למחר?",
            "מה השעות הפנויות השבוע?"
        ]
        self.client.post(
            "/api/v1/chat",
            json={
                "message": random.choice(messages),
                "conversation_id": self.conversation_id
            }
        )
    
    @task(6)
    def chat_price_inquiry(self):
        """Test price inquiry"""
        treatments = [
            "כמה עולה ניקוי אבנית?",
            "מה המחיר של סתימה?",
            "כמה עולה הלבנת שיניים?",
            "מה עולה עקירת שן?"
        ]
        self.client.post(
            "/api/v1/chat",
            json={
                "message": random.choice(treatments),
                "conversation_id": self.conversation_id
            }
        )
    
    @task(5)
    def chat_medical_question(self):
        """Test medical question"""
        questions = [
            "יש לי כאב בשן, מה לעשות?",
            "השן שלי רגישה לקר",
            "יש לי דימום מהחניכיים",
            "כמה זמן לוקח טיפול שורש?"
        ]
        self.client.post(
            "/api/v1/chat",
            json={
                "message": random.choice(questions),
                "conversation_id": self.conversation_id
            }
        )
    
    @task(4)
    def chat_patient_search(self):
        """Test patient search"""
        self.client.post(
            "/api/v1/chat",
            json={
                "message": f"מצא מטופל בשם {random.choice(self.patient_names)}",
                "conversation_id": self.conversation_id
            }
        )
    
    @task(2)
    def chat_multilingual(self):
        """Test multilingual support"""
        messages = [
            "Hello, I need an appointment",
            "What are your prices?",
            "I have a toothache",
            "When are you open?"
        ]
        self.client.post(
            "/api/v1/chat",
            json={
                "message": random.choice(messages),
                "conversation_id": self.conversation_id
            }
        )


class AdminUser(HttpUser):
    """Simulates an admin user"""
    
    wait_time = between(2, 5)
    
    @task(1)
    def view_dashboard(self):
        """Test dashboard endpoint"""
        # This would require authentication
        pass
    
    @task(1)
    def view_analytics(self):
        """Test analytics endpoint"""
        # This would require authentication
        pass


# Run with:
# locust -f tests/load_test.py --host=http://localhost:8000
# 
# Then open http://localhost:8089 and configure:
# - Number of users: 100
# - Spawn rate: 10 users/second
# 
# Targets:
# - 100 concurrent users
# - < 500ms average response time
# - < 1% error rate
# - > 100 requests/second
