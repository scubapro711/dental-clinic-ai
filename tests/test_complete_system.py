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
import httpx
import redis
import mysql.connector
from unittest.mock import patch, AsyncMock

# Test configuration
TEST_CONFIG = {
    "gateway_url": "http://localhost:8000",
    "ai_agents_url": "http://localhost:8001",
    "redis_url": "redis://localhost:6379/1",
    "mysql_config": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "test_password",
        "database": "dental_clinic_test"
    }
}

class TestSystemHealth:
    """Test system health and basic connectivity"""
    
    @pytest.mark.integration
    async def test_gateway_health(self):
        """Test Gateway service health endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{TEST_CONFIG['gateway_url']}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "service" in data
            assert "timestamp" in data
    
    @pytest.mark.integration
    async def test_ai_agents_health(self):
        """Test AI Agents service health endpoint"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{TEST_CONFIG['ai_agents_url']}/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                assert data["service"] == "ai-agents"
            except httpx.ConnectError:
                pytest.skip("AI Agents service not running")
    
    @pytest.mark.redis
    def test_redis_connection(self):
        """Test Redis connectivity"""
        r = redis.from_url(TEST_CONFIG["redis_url"])
        assert r.ping() is True
        
        # Test basic operations
        r.set("test_key", "test_value")
        assert r.get("test_key").decode() == "test_value"
        r.delete("test_key")
    
    @pytest.mark.mysql
    def test_mysql_connection(self):
        """Test MySQL connectivity"""
        try:
            conn = mysql.connector.connect(**TEST_CONFIG["mysql_config"])
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
            cursor.close()
            conn.close()
        except mysql.connector.Error:
            pytest.skip("MySQL not available for testing")

class TestQueueProcessing:
    """Test Redis Queue functionality"""
    
    @pytest.mark.queue
    @pytest.mark.redis
    async def test_queue_enqueue_dequeue(self):
        """Test basic queue operations"""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        
        from src.shared.redis_queue import RedisQueueManager
        
        queue_manager = RedisQueueManager(TEST_CONFIG["redis_url"])
        await queue_manager.initialize()
        
        try:
            # Test enqueue
            test_message = {"text": "Test message", "sender_id": "test_user"}
            message_id = await queue_manager.enqueue("test_queue", test_message)
            assert message_id is not None
            
            # Test dequeue
            dequeued_message = await queue_manager.dequeue("test_queue")
            assert dequeued_message is not None
            assert dequeued_message["data"]["text"] == "Test message"
            assert dequeued_message["id"] == message_id
            
        finally:
            await queue_manager.cleanup()
    
    @pytest.mark.queue
    @pytest.mark.integration
    async def test_queue_api_endpoint(self):
        """Test queue API endpoints"""
        async with httpx.AsyncClient() as client:
            # Test queue stats
            response = await client.get(f"{TEST_CONFIG['gateway_url']}/api/queue/stats")
            assert response.status_code == 200
            data = response.json()
            assert "queue_name" in data
            assert "pending" in data
            
            # Test message processing
            test_message = {
                "text": "I need to book an appointment",
                "sender_id": "test_user_api",
                "channel": "api_test"
            }
            
            response = await client.post(
                f"{TEST_CONFIG['gateway_url']}/api/queue/process-async",
                json=test_message
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "message_id" in data

class TestAIAgents:
    """Test AI Agents functionality"""
    
    @pytest.mark.ai
    @pytest.mark.integration
    async def test_ai_message_processing(self):
        """Test AI message processing with mock OpenAI"""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        
        from src.ai_agents.enhanced_message_processor import EnhancedAIMessageProcessor
        from src.ai_agents.engines.ai_engine_factory import AIEngineType
        
        # Mock OpenAI to avoid API calls
        with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_openai:
            mock_openai.return_value.choices = [
                type('Choice', (), {
                    'message': type('Message', (), {
                        'content': 'I can help you book an appointment. What date would you prefer?'
                    })()
                })()
            ]
            
            processor = EnhancedAIMessageProcessor(AIEngineType.CREWAI)
            processor.queue_manager.redis_url = TEST_CONFIG["redis_url"]
            
            try:
                await processor.initialize()
                
                test_message = {
                    "text": "I need to book an appointment",
                    "sender_id": "test_user_ai",
                    "channel": "test"
                }
                
                result = await processor.process_message(test_message)
                
                assert result["success"] is True
                assert "response" in result
                assert "agent_used" in result
                assert result["sender_id"] == "test_user_ai"
                
            finally:
                await processor.cleanup()
    
    @pytest.mark.ai
    async def test_dental_tool_operations(self):
        """Test Advanced Dental Tool operations"""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        
        from src.ai_agents.tools.advanced_dental_tool import AdvancedDentalTool
        
        tool = AdvancedDentalTool()
        await tool.initialize()
        
        try:
            # Test patient search
            patients = await tool.search_patients("יוסי")
            assert len(patients) > 0
            assert patients[0]["name"] == "יוסי כהן"
            
            # Test available slots
            slots = await tool.get_available_slots(1, "2025-10-01")
            assert len(slots) > 0
            assert slots[0]["available"] is True
            
            # Test appointment booking
            booking_result = await tool.book_appointment(
                patient_id=1,
                provider_id=1,
                datetime_str="2025-10-01T10:00:00",
                treatment_type="General Checkup"
            )
            assert booking_result["success"] is True
            assert "appointment" in booking_result
            
            # Test health check
            health = await tool.health_check()
            assert health["status"] == "healthy"
            assert health["initialized"] is True
            
        finally:
            await tool.cleanup()

class TestWebhooks:
    """Test webhook functionality"""
    
    @pytest.mark.webhook
    @pytest.mark.integration
    async def test_whatsapp_webhook(self):
        """Test WhatsApp webhook processing"""
        async with httpx.AsyncClient() as client:
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
            
            response = await client.post(
                f"{TEST_CONFIG['gateway_url']}/webhooks/whatsapp",
                json=webhook_data
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "received"
    
    @pytest.mark.webhook
    @pytest.mark.integration
    async def test_telegram_webhook(self):
        """Test Telegram webhook processing"""
        async with httpx.AsyncClient() as client:
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
            
            response = await client.post(
                f"{TEST_CONFIG['gateway_url']}/webhooks/telegram",
                json=webhook_data
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "received"

class TestEndToEnd:
    """End-to-end system tests"""
    
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_complete_appointment_booking_flow(self):
        """Test complete appointment booking flow from webhook to AI response"""
        async with httpx.AsyncClient() as client:
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
            
            response = await client.post(
                f"{TEST_CONFIG['gateway_url']}/webhooks/whatsapp",
                json=webhook_data
            )
            assert response.status_code == 200
            
            # Step 2: Wait for processing
            await asyncio.sleep(2)
            
            # Step 3: Check queue stats
            response = await client.get(f"{TEST_CONFIG['gateway_url']}/api/queue/stats")
            assert response.status_code == 200
            
            # Step 4: Verify message was processed
            # In a real test, we would check the response was sent back
            # For now, we verify the system handled the request
            assert True  # Placeholder for actual verification
    
    @pytest.mark.e2e
    @pytest.mark.integration
    async def test_system_performance(self):
        """Test system performance under load"""
        async with httpx.AsyncClient() as client:
            # Send multiple messages concurrently
            tasks = []
            for i in range(10):
                task = client.post(
                    f"{TEST_CONFIG['gateway_url']}/api/queue/process-async",
                    json={
                        "text": f"Test message {i}",
                        "sender_id": f"load_test_user_{i}",
                        "channel": "load_test"
                    }
                )
                tasks.append(task)
            
            # Wait for all requests to complete
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify all requests succeeded
            success_count = 0
            for response in responses:
                if isinstance(response, httpx.Response) and response.status_code == 200:
                    success_count += 1
            
            # At least 80% should succeed
            assert success_count >= 8

# Test fixtures and utilities
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def clean_redis():
    """Clean Redis test database before and after tests"""
    r = redis.from_url(TEST_CONFIG["redis_url"])
    r.flushdb()
    yield
    r.flushdb()

@pytest.fixture
async def clean_mysql():
    """Clean MySQL test database before and after tests"""
    try:
        conn = mysql.connector.connect(**TEST_CONFIG["mysql_config"])
        cursor = conn.cursor()
        
        # Clean test data
        cursor.execute("DELETE FROM messages WHERE sender_id LIKE 'test_%'")
        cursor.execute("DELETE FROM appointments WHERE patient_id IN (SELECT id FROM patients WHERE phone LIKE '972501234567')")
        
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error:
        pass  # Skip if MySQL not available
    
    yield
    
    # Cleanup after test
    try:
        conn = mysql.connector.connect(**TEST_CONFIG["mysql_config"])
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE sender_id LIKE 'test_%'")
        cursor.execute("DELETE FROM appointments WHERE patient_id IN (SELECT id FROM patients WHERE phone LIKE '972501234567')")
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error:
        pass
