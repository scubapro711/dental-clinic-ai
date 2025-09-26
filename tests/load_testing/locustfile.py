"""
Locust Load Testing for AI Dental Clinic System
בדיקות עומס למערכת ניהול מרפאת שיניים AI

This file contains comprehensive load testing scenarios for all system components.
"""

import json
import random
import time
from locust import HttpUser, task, between, events
from locust.exception import RescheduleTask
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data for realistic load testing
SAMPLE_PATIENTS = [
    {"name": "יוסי כהן", "phone": "972501234567"},
    {"name": "שרה לוי", "phone": "972502345678"},
    {"name": "דוד ישראלי", "phone": "972503456789"},
    {"name": "רחל אברהם", "phone": "972504567890"},
    {"name": "משה דוד", "phone": "972505678901"},
]

SAMPLE_MESSAGES = [
    "שלום, אני רוצה לקבוע תור לבדיקה",
    "האם יש תור פנוי השבוע?",
    "אני צריך לבטל את התור שלי",
    "מתי המרפאה פתוחה?",
    "כמה עולה בדיקה?",
    "Hello, I need to book an appointment",
    "Can I reschedule my appointment?",
    "What are your opening hours?",
    "Do you accept insurance?",
    "I need an emergency appointment",
]

WHATSAPP_WEBHOOK_TEMPLATE = {
    "entry": [{
        "changes": [{
            "value": {
                "messages": [{
                    "id": "",
                    "from": "",
                    "text": {"body": ""},
                    "timestamp": ""
                }]
            }
        }]
    }]
}

TELEGRAM_WEBHOOK_TEMPLATE = {
    "update_id": 0,
    "message": {
        "message_id": 0,
        "from": {
            "id": 0,
            "first_name": "Test",
            "username": "testuser"
        },
        "chat": {
            "id": 0,
            "type": "private"
        },
        "date": 0,
        "text": ""
    }
}

class DentalClinicUser(HttpUser):
    """Base user class for dental clinic load testing"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Initialize user session"""
        self.user_id = random.randint(100000, 999999)
        self.patient_data = random.choice(SAMPLE_PATIENTS)
        logger.info(f"User {self.user_id} started session")
    
    def on_stop(self):
        """Clean up user session"""
        logger.info(f"User {self.user_id} ended session")

class HealthCheckUser(DentalClinicUser):
    """User that only performs health checks - baseline load"""
    
    weight = 1
    
    @task(10)
    def check_gateway_health(self):
        """Test Gateway health endpoint"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure(f"Unhealthy status: {data}")
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(5)
    def check_ai_agents_health(self):
        """Test AI Agents health endpoint"""
        try:
            with self.client.get("http://localhost:8001/health", catch_response=True) as response:
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy":
                        response.success()
                    else:
                        response.failure(f"AI Agents unhealthy: {data}")
                else:
                    response.failure(f"AI Agents health check failed: {response.status_code}")
        except Exception as e:
            logger.warning(f"AI Agents not accessible: {e}")

class WhatsAppUser(DentalClinicUser):
    """User simulating WhatsApp webhook traffic"""
    
    weight = 3
    
    @task(8)
    def send_whatsapp_message(self):
        """Send WhatsApp webhook message"""
        message = random.choice(SAMPLE_MESSAGES)
        webhook_data = WHATSAPP_WEBHOOK_TEMPLATE.copy()
        
        # Populate webhook data
        webhook_data["entry"][0]["changes"][0]["value"]["messages"][0].update({
            "id": f"wa_msg_{self.user_id}_{int(time.time())}",
            "from": self.patient_data["phone"],
            "text": {"body": message},
            "timestamp": str(int(time.time()))
        })
        
        with self.client.post("/webhooks/whatsapp", 
                            json=webhook_data,
                            catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "received":
                    response.success()
                else:
                    response.failure(f"WhatsApp webhook failed: {data}")
            else:
                response.failure(f"WhatsApp webhook error: {response.status_code}")
    
    @task(2)
    def check_message_status(self):
        """Check message processing status"""
        with self.client.get("/api/queue/stats", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                pending = data.get("pending", 0)
                if pending < 100:  # Reasonable queue size
                    response.success()
                else:
                    response.failure(f"Queue too large: {pending} pending messages")
            else:
                response.failure(f"Queue stats failed: {response.status_code}")

class TelegramUser(DentalClinicUser):
    """User simulating Telegram webhook traffic"""
    
    weight = 2
    
    @task(6)
    def send_telegram_message(self):
        """Send Telegram webhook message"""
        message = random.choice(SAMPLE_MESSAGES)
        webhook_data = TELEGRAM_WEBHOOK_TEMPLATE.copy()
        
        # Populate webhook data
        webhook_data.update({
            "update_id": random.randint(100000000, 999999999),
            "message": {
                "message_id": random.randint(1, 10000),
                "from": {
                    "id": self.user_id,
                    "first_name": self.patient_data["name"].split()[0],
                    "username": f"user{self.user_id}"
                },
                "chat": {
                    "id": self.user_id,
                    "type": "private"
                },
                "date": int(time.time()),
                "text": message
            }
        })
        
        with self.client.post("/webhooks/telegram",
                            json=webhook_data,
                            catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "received":
                    response.success()
                else:
                    response.failure(f"Telegram webhook failed: {data}")
            else:
                response.failure(f"Telegram webhook error: {response.status_code}")

class APIUser(DentalClinicUser):
    """User simulating direct API usage"""
    
    weight = 2
    
    @task(5)
    def send_api_message(self):
        """Send message via API"""
        message_data = {
            "text": random.choice(SAMPLE_MESSAGES),
            "sender_id": f"api_user_{self.user_id}",
            "channel": "api_test"
        }
        
        with self.client.post("/api/queue/process-async",
                            json=message_data,
                            catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"API message failed: {data}")
            else:
                response.failure(f"API error: {response.status_code}")
    
    @task(3)
    def get_patient_info(self):
        """Simulate patient information retrieval"""
        # This would typically require authentication in a real system
        patient_name = self.patient_data["name"]
        
        with self.client.get(f"/api/patients/search?name={patient_name}",
                           catch_response=True) as response:
            if response.status_code in [200, 404]:  # 404 is acceptable for test data
                response.success()
            else:
                response.failure(f"Patient search failed: {response.status_code}")

class StressTestUser(DentalClinicUser):
    """User for stress testing - aggressive load"""
    
    weight = 1
    wait_time = between(0.1, 0.5)  # Very fast requests
    
    @task(10)
    def rapid_fire_requests(self):
        """Send rapid requests to stress test the system"""
        endpoints = [
            "/health",
            "/api/queue/stats",
            "/webhooks/whatsapp",
            "/webhooks/telegram"
        ]
        
        endpoint = random.choice(endpoints)
        
        if endpoint in ["/webhooks/whatsapp", "/webhooks/telegram"]:
            # Send webhook data
            if endpoint == "/webhooks/whatsapp":
                data = WHATSAPP_WEBHOOK_TEMPLATE.copy()
                data["entry"][0]["changes"][0]["value"]["messages"][0].update({
                    "id": f"stress_{self.user_id}_{int(time.time() * 1000)}",
                    "from": self.patient_data["phone"],
                    "text": {"body": "Stress test message"},
                    "timestamp": str(int(time.time()))
                })
            else:
                data = TELEGRAM_WEBHOOK_TEMPLATE.copy()
                data["update_id"] = random.randint(100000000, 999999999)
                data["message"]["text"] = "Stress test message"
                data["message"]["from"]["id"] = self.user_id
                data["message"]["chat"]["id"] = self.user_id
            
            with self.client.post(endpoint, json=data, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Stress test failed: {response.status_code}")
        else:
            # Send GET request
            with self.client.get(endpoint, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Stress test failed: {response.status_code}")

# Event handlers for custom metrics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    """Custom request handler for detailed metrics"""
    if exception:
        logger.error(f"Request failed: {name} - {exception}")
    elif response_time > 5000:  # Log slow requests (>5 seconds)
        logger.warning(f"Slow request: {name} took {response_time}ms")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Test start handler"""
    logger.info("🚀 Starting aggressive load testing for AI Dental Clinic System")
    logger.info(f"Target host: {environment.host}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Test stop handler"""
    logger.info("🏁 Load testing completed")
    
    # Print summary statistics
    stats = environment.stats
    logger.info(f"Total requests: {stats.total.num_requests}")
    logger.info(f"Total failures: {stats.total.num_failures}")
    logger.info(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    logger.info(f"Max response time: {stats.total.max_response_time}ms")
    logger.info(f"Requests per second: {stats.total.current_rps:.2f}")

# Custom load testing scenarios
class PeakHoursScenario(DentalClinicUser):
    """Simulate peak hours traffic pattern"""
    
    weight = 4
    wait_time = between(0.5, 2)
    
    @task(15)
    def peak_appointment_requests(self):
        """High volume of appointment requests during peak hours"""
        messages = [
            "אני רוצה תור דחוף להיום",
            "יש תור פנוי מחר בבוקר?",
            "אני צריך לבטל תור ולקבוע חדש",
            "Emergency appointment needed",
            "Can I get an appointment today?"
        ]
        
        message = random.choice(messages)
        webhook_data = WHATSAPP_WEBHOOK_TEMPLATE.copy()
        webhook_data["entry"][0]["changes"][0]["value"]["messages"][0].update({
            "id": f"peak_{self.user_id}_{int(time.time())}",
            "from": self.patient_data["phone"],
            "text": {"body": message},
            "timestamp": str(int(time.time()))
        })
        
        with self.client.post("/webhooks/whatsapp",
                            json=webhook_data,
                            catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Peak hours request failed: {response.status_code}")

class ErrorRecoveryScenario(DentalClinicUser):
    """Test system recovery from errors"""
    
    weight = 1
    
    @task(5)
    def send_malformed_requests(self):
        """Send malformed requests to test error handling"""
        malformed_data = [
            {},  # Empty data
            {"invalid": "structure"},  # Wrong structure
            {"entry": []},  # Empty entry
            {"entry": [{"invalid": "data"}]},  # Invalid entry structure
        ]
        
        data = random.choice(malformed_data)
        
        with self.client.post("/webhooks/whatsapp",
                            json=data,
                            catch_response=True) as response:
            # We expect these to fail gracefully
            if response.status_code in [400, 422]:  # Bad request is expected
                response.success()
            elif response.status_code == 500:
                response.failure("Server error on malformed request")
            else:
                response.success()  # Any other response is acceptable

# Load testing configuration
if __name__ == "__main__":
    print("🧪 AI Dental Clinic Load Testing Configuration")
    print("=" * 50)
    print("User Classes:")
    print("- HealthCheckUser (weight: 1) - Basic health checks")
    print("- WhatsAppUser (weight: 3) - WhatsApp webhook simulation")
    print("- TelegramUser (weight: 2) - Telegram webhook simulation")
    print("- APIUser (weight: 2) - Direct API usage")
    print("- StressTestUser (weight: 1) - Aggressive stress testing")
    print("- PeakHoursScenario (weight: 4) - Peak traffic simulation")
    print("- ErrorRecoveryScenario (weight: 1) - Error handling testing")
    print()
    print("Run with: locust -f locustfile.py --host=http://localhost:8000")
    print("Web UI: http://localhost:8089")
    print()
    print("Recommended test scenarios:")
    print("1. Normal load: 10-50 users, 2-5 spawn rate")
    print("2. Peak load: 100-200 users, 10-20 spawn rate")
    print("3. Stress test: 500+ users, 50+ spawn rate")
