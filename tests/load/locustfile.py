"""
Locust load testing for DentaFlow API.

Run with:
    locust -f locustfile.py --host=http://localhost:8000

Then open browser: http://localhost:8089
Configure: 100 users, spawn rate 10/sec, run 10 minutes
"""

from locust import HttpUser, task, between, events
import random
import json
import logging

logger = logging.getLogger(__name__)


class DentaFlowUser(HttpUser):
    """Simulate typical DentaFlow user behavior."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when user starts - login/register."""
        # Try to register (might fail if user exists, that's OK)
        email = f"loadtest{random.randint(1000, 999999)}@example.com"
        response = self.client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "LoadTest123!@#",
            "name": f"Load Test User {random.randint(1, 1000)}",
            "phone": f"+97250{random.randint(1000000, 9999999)}"
        }, catch_response=True)
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.token = data.get("access_token")
            self.user_id = data.get("user_id")
            response.success()
        elif response.status_code == 400:
            # User might already exist, try login
            response = self.client.post("/api/v1/auth/login", json={
                "email": email,
                "password": "LoadTest123!@#"
            })
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
        else:
            logger.error(f"Failed to register/login: {response.status_code}")
            self.token = None
            self.user_id = None
        
        if self.token:
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}
    
    @task(10)
    def send_message(self):
        """Send message in conversation (most common action - 50% of traffic)."""
        if not self.token:
            return
        
        # Create or get conversation
        response = self.client.post(
            "/api/v1/conversations",
            headers=self.headers,
            json={
                "channel": "web_chat",
                "primary_agent": random.choice(["alex", "marcus", "sophia"]),
                "patient_name": f"Patient {random.randint(1, 100)}",
                "patient_phone": f"+97250{random.randint(1000000, 9999999)}"
            },
            name="/api/v1/conversations [CREATE]"
        )
        
        if response.status_code in [200, 201]:
            conversation_id = response.json()["id"]
            
            # Send message
            messages = [
                "שלום, אני רוצה לקבוע תור",
                "מה המחיר של ניקוי אבנית?",
                "יש לי כאב בשן",
                "מתי יש תורים פנויים?",
                "אני רוצה לבטל תור"
            ]
            
            self.client.post(
                f"/api/v1/conversations/{conversation_id}/messages",
                headers=self.headers,
                json={
                    "role": "user",
                    "content": random.choice(messages)
                },
                name="/api/v1/conversations/{id}/messages [SEND]"
            )
    
    @task(5)
    def get_conversation_history(self):
        """Get conversation history (25% of traffic)."""
        if not self.token:
            return
        
        # Get user's conversations
        response = self.client.get(
            "/api/v1/conversations",
            headers=self.headers,
            name="/api/v1/conversations [LIST]"
        )
        
        if response.status_code == 200:
            conversations = response.json()
            if conversations and len(conversations) > 0:
                # Get messages for first conversation
                conversation_id = conversations[0]["id"]
                self.client.get(
                    f"/api/v1/conversations/{conversation_id}/messages",
                    headers=self.headers,
                    name="/api/v1/conversations/{id}/messages [GET]"
                )
    
    @task(3)
    def get_proactive_suggestions(self):
        """Get proactive suggestions (15% of traffic)."""
        if not self.token:
            return
        
        # Get conversations
        response = self.client.get(
            "/api/v1/conversations",
            headers=self.headers
        )
        
        if response.status_code == 200:
            conversations = response.json()
            if conversations and len(conversations) > 0:
                conversation_id = conversations[0]["id"]
                self.client.get(
                    f"/api/v1/proactive-suggestions/conversations/{conversation_id}/suggestions",
                    headers=self.headers,
                    name="/api/v1/proactive-suggestions [GET]"
                )
    
    @task(2)
    def get_treatment_prices(self):
        """Get treatment prices (10% of traffic)."""
        self.client.get(
            "/api/v1/treatment-prices",
            name="/api/v1/treatment-prices [LIST]"
        )
    
    @task(1)
    def get_clinic_settings(self):
        """Get clinic settings (5% of traffic)."""
        if not self.token:
            return
        
        self.client.get(
            "/api/v1/clinic-settings",
            headers=self.headers,
            name="/api/v1/clinic-settings [GET]"
        )


class StressTestUser(HttpUser):
    """Aggressive stress test - rapid fire requests."""
    
    wait_time = between(0.1, 0.5)  # Very fast - 0.1-0.5 seconds
    weight = 1  # Less common than normal users
    
    @task
    def rapid_fire_health_check(self):
        """Rapid health check requests."""
        self.client.get("/api/v1/health", name="/api/v1/health [STRESS]")
    
    @task
    def rapid_fire_prices(self):
        """Rapid price requests."""
        self.client.get("/api/v1/treatment-prices", name="/api/v1/treatment-prices [STRESS]")


class SpikeTestUser(HttpUser):
    """Simulate traffic spike - burst of requests."""
    
    wait_time = between(0, 0.1)  # Almost no wait
    weight = 1  # Rare
    
    @task
    def burst_requests(self):
        """Send burst of requests."""
        for _ in range(10):
            self.client.get("/api/v1/health")


# Event handlers for custom metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("🚀 Load test starting...")
    print(f"   Target: {environment.host}")
    print(f"   Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    print("\n✅ Load test completed!")
    
    # Print summary
    stats = environment.stats
    print(f"\n📊 Summary:")
    print(f"   Total requests: {stats.total.num_requests}")
    print(f"   Failed requests: {stats.total.num_failures}")
    print(f"   Failure rate: {stats.total.fail_ratio * 100:.2f}%")
    print(f"   Avg response time: {stats.total.avg_response_time:.2f}ms")
    print(f"   95th percentile: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"   Requests/sec: {stats.total.total_rps:.2f}")
    
    # Deployment decision
    failure_rate = stats.total.fail_ratio * 100
    avg_response_time = stats.total.avg_response_time
    p95_response_time = stats.total.get_response_time_percentile(0.95)
    
    print(f"\n🎯 Load Test Criteria:")
    
    criteria_met = 0
    criteria_total = 3
    
    # Criterion 1: Failure rate < 1%
    if failure_rate < 1.0:
        print(f"   ✅ Failure rate: {failure_rate:.2f}% (< 1%)")
        criteria_met += 1
    else:
        print(f"   ❌ Failure rate: {failure_rate:.2f}% (>= 1%)")
    
    # Criterion 2: Avg response time < 2000ms
    if avg_response_time < 2000:
        print(f"   ✅ Avg response time: {avg_response_time:.2f}ms (< 2000ms)")
        criteria_met += 1
    else:
        print(f"   ❌ Avg response time: {avg_response_time:.2f}ms (>= 2000ms)")
    
    # Criterion 3: 95th percentile < 5000ms
    if p95_response_time < 5000:
        print(f"   ✅ 95th percentile: {p95_response_time:.2f}ms (< 5000ms)")
        criteria_met += 1
    else:
        print(f"   ❌ 95th percentile: {p95_response_time:.2f}ms (>= 5000ms)")
    
    # Final verdict
    pass_rate = (criteria_met / criteria_total) * 100
    print(f"\n   Pass rate: {criteria_met}/{criteria_total} ({pass_rate:.0f}%)")
    
    if criteria_met == criteria_total:
        print(f"\n   🚀 LOAD TEST PASSED - Ready for production!")
    else:
        print(f"\n   ⚠️  LOAD TEST ISSUES - Review performance before deployment")


if __name__ == "__main__":
    # Run from command line
    import os
    os.system("locust -f locustfile.py --host=http://localhost:8000")
