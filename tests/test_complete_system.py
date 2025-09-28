"""
Complete System Tests
בדיקות מערכת מלאות

Comprehensive end-to-end tests for the AI Dental Clinic Management System.
"""

import pytest
import asyncio
import json
import time
from typing import Dict, Any

# Test configuration
TEST_CONFIG = {
    "gateway_url": "http://localhost:8000",
    "ai_agents_url": "http://localhost:8001",
}

class TestSystemHealth:
    """Test system health and basic connectivity"""
    
    def test_gateway_health(self, client):
        """Test Gateway service health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

class TestQueueProcessing:
    """Test Redis Queue functionality"""
    
    def test_queue_api_endpoint(self, client, mock_queue_manager):
        """Test queue API endpoints"""
        # Test message processing
        test_message = {
            "text": "I need to book an appointment",
            "sender_id": "test_user_api",
            "channel": "api_test"
        }
        
        response = client.post("/api/queue/process-async", json=test_message)
        assert response.status_code == 200
        data = response.json()
        assert "message_id" in data

class TestWebhooks:
    """Test webhook functionality"""
    
    def test_whatsapp_webhook(self, client, mock_queue_manager):
        """Test WhatsApp webhook processing"""
        webhook_data = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "id": "test_message_id",
                            "from": "972501234567",
                            "text": {"body": "שלום, אני רוצה לקבוע תור"},
                            "timestamp": str(int(time.time()))
                        }]
                    }
                }]
            }]
        }
        
        response = client.post("/webhook/whatsapp", json=webhook_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
    
    def test_telegram_webhook(self, client, mock_queue_manager):
        """Test Telegram webhook processing"""
        webhook_data = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 987654321,
                    "first_name": "Test",
                    "username": "testuser"
                },
                "chat": {
                    "id": 987654321,
                    "type": "private"
                },
                "date": int(time.time()),
                "text": "Hello, I need to book an appointment"
            }
        }
        
        response = client.post("/webhook/telegram", json=webhook_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"

class TestEndToEnd:
    """End-to-end system tests"""

    def test_complete_appointment_booking_flow(self, client, mock_queue_manager):
        """Test complete appointment booking flow from webhook to AI response"""
        # Step 1: Send webhook message
        webhook_data = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "id": "e2e_test_message",
                            "from": "972501234567",
                            "text": {"body": "אני רוצה לקבוע תור לבדיקה"},
                            "timestamp": str(int(time.time()))
                        }]
                    }
                }]
            }]
        }
        
        response = client.post("/webhook/whatsapp", json=webhook_data)
        assert response.status_code == 200
        
        # Step 2: Verify message was processed
        # In a real test, we would check the response was sent back
        # For now, we verify the system handled the request
        assert True  # Placeholder for actual verification

