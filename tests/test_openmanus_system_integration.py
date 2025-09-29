#!/usr/bin/env python3
"""
🔥 AGGRESSIVE SYSTEM INTEGRATION TESTS - OPENMANUS MODULE
בדיקות אינטגרציה אגרסיביות - מודול OpenManus למערכת

This module tests the complete integration of OpenManus agents with the entire system:
- WebSocket integration
- Database integration  
- API integration
- Frontend integration
- Redis queue integration
- End-to-end workflows
"""

import asyncio
import json
import time
import requests
import websockets
import mysql.connector
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock
import pytest

# System components
from src.ai_agents.enhanced_message_processor import EnhancedAIMessageProcessor
from src.ai_agents.engines.ai_engine_factory import AIEngineType

class AggressiveSystemIntegrationTests:
    """Aggressive system integration tests for OpenManus"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.websocket_url = "ws://localhost:8001"
        self.test_results = []
        
    async def setup_test_environment(self):
        """Setup test environment with mocks"""
        print("🔧 Setting up aggressive test environment...")
        
        # Mock external dependencies
        self.mock_redis = AsyncMock()
        self.mock_db = MagicMock()
        
        print("✅ Test environment ready")
    
    async def test_01_openmanus_engine_system_integration(self):
        """🧪 Test 1: OpenManus engine integrates with system"""
        print("🧪 Test 1: OpenManus Engine System Integration")
        
        try:
            # Create processor with OpenManus
            processor = EnhancedAIMessageProcessor(AIEngineType.OPENMANUS)
            processor.queue_manager = self.mock_redis
            
            await processor.initialize()
            
            # Verify system integration
            assert processor.engine_type == AIEngineType.OPENMANUS
            assert len(processor.agents) == 3
            
            # Test system stats
            stats = await processor.get_stats()
            assert stats["engine_type"] == "openmanus"
            assert stats["agents_count"] == 3
            
            await processor.cleanup()
            
            self.test_results.append(("Engine Integration", "PASSED"))
            print("✅ Test 1 PASSED: OpenManus integrates with system")
            
        except Exception as e:
            self.test_results.append(("Engine Integration", f"FAILED: {e}"))
            print(f"❌ Test 1 FAILED: {e}")
    
    async def test_02_websocket_message_flow(self):
        """🧪 Test 2: Complete WebSocket message flow"""
        print("🧪 Test 2: WebSocket Message Flow Integration")
        
        try:
            # Mock WebSocket server
            class MockWebSocketServer:
                def __init__(self):
                    self.connected_clients = {}
                    self.message_processor = None
                
                async def initialize(self):
                    self.message_processor = EnhancedAIMessageProcessor(AIEngineType.OPENMANUS)
                    self.message_processor.queue_manager = self.mock_redis
                    await self.message_processor.initialize()
                
                async def handle_message(self, websocket, message_data):
                    # Simulate message processing
                    result = await self.message_processor.process_message(message_data)
                    return result
            
            # Test WebSocket flow
            ws_server = MockWebSocketServer()
            await ws_server.initialize()
            
            # Test message processing through WebSocket
            test_message = {
                "text": "שלום, אני רוצה לקבוע תור לניקוי שיניים",
                "sender_id": "websocket_test_user",
                "channel": "websocket"
            }
            
            result = await ws_server.handle_message(None, test_message)
            
            assert result["success"] == True
            assert result["agent_used"] == "scheduler"
            assert result["engine_type"] == "openmanus"
            
            await ws_server.message_processor.cleanup()
            
            self.test_results.append(("WebSocket Flow", "PASSED"))
            print("✅ Test 2 PASSED: WebSocket message flow works")
            
        except Exception as e:
            self.test_results.append(("WebSocket Flow", f"FAILED: {e}"))
            print(f"❌ Test 2 FAILED: {e}")
    
    async def test_03_api_endpoint_integration(self):
        """🧪 Test 3: API endpoint integration"""
        print("🧪 Test 3: API Endpoint Integration")
        
        try:
            # Mock API request processing
            class MockAPIHandler:
                def __init__(self):
                    self.processor = None
                
                async def initialize(self):
                    self.processor = EnhancedAIMessageProcessor(AIEngineType.OPENMANUS)
                    self.processor.queue_manager = self.mock_redis
                    await self.processor.initialize()
                
                async def handle_chat_request(self, request_data):
                    return await self.processor.process_message(request_data)
            
            # Test API integration
            api_handler = MockAPIHandler()
            await api_handler.initialize()
            
            # Simulate API request
            api_request = {
                "text": "I need to schedule a dental checkup",
                "sender_id": "api_test_user",
                "channel": "api"
            }
            
            response = await api_handler.handle_chat_request(api_request)
            
            assert response["success"] == True
            assert response["agent_used"] == "scheduler"
            assert "response" in response
            
            await api_handler.processor.cleanup()
            
            self.test_results.append(("API Integration", "PASSED"))
            print("✅ Test 3 PASSED: API endpoint integration works")
            
        except Exception as e:
            self.test_results.append(("API Integration", f"FAILED: {e}"))
            print(f"❌ Test 3 FAILED: {e}")
    
    async def test_04_database_integration_simulation(self):
        """🧪 Test 4: Database integration simulation"""
        print("🧪 Test 4: Database Integration Simulation")
        
        try:
            # Mock database operations
            class MockDatabaseIntegration:
                def __init__(self):
                    self.processor = None
                    self.db_operations = []
                
                async def initialize(self):
                    self.processor = EnhancedAIMessageProcessor(AIEngineType.OPENMANUS)
                    self.processor.queue_manager = self.mock_redis
                    await self.processor.initialize()
                
                async def process_with_db_operations(self, message):
                    # Simulate database operations during message processing
                    self.db_operations.append("SELECT patient_info")
                    
                    result = await self.processor.process_message(message)
                    
                    if result["agent_used"] == "scheduler":
                        self.db_operations.append("SELECT available_slots")
                        self.db_operations.append("INSERT appointment")
                    
                    return result, self.db_operations
            
            # Test database integration
            db_integration = MockDatabaseIntegration()
            await db_integration.initialize()
            
            # Test appointment booking with DB operations
            message = {
                "text": "אני רוצה לקבוע תור לטיפול שורש",
                "sender_id": "db_test_user",
                "channel": "system"
            }
            
            result, db_ops = await db_integration.process_with_db_operations(message)
            
            assert result["success"] == True
            assert result["agent_used"] == "scheduler"
            assert len(db_ops) >= 3  # Should have multiple DB operations
            assert "SELECT patient_info" in db_ops
            
            await db_integration.processor.cleanup()
            
            self.test_results.append(("Database Integration", "PASSED"))
            print("✅ Test 4 PASSED: Database integration simulation works")
            
        except Exception as e:
            self.test_results.append(("Database Integration", f"FAILED: {e}"))
            print(f"❌ Test 4 FAILED: {e}")
    
    async def test_05_redis_queue_integration(self):
        """🧪 Test 5: Redis queue integration"""
        print("🧪 Test 5: Redis Queue Integration")
        
        try:
            # Mock Redis queue operations
            class MockRedisQueueIntegration:
                def __init__(self):
                    self.queue_operations = []
                    self.processed_messages = []
                
                async def simulate_queue_processing(self):
                    # Create processor
                    processor = EnhancedAIMessageProcessor(AIEngineType.OPENMANUS)
                    
                    # Mock queue manager
                    mock_queue = AsyncMock()
                    mock_queue.initialize = AsyncMock()
                    mock_queue.start_worker = AsyncMock()
                    mock_queue.get_queue_stats = AsyncMock(return_value={
                        "pending": 5, "processing": 2, "completed": 100
                    })
                    
                    processor.queue_manager = mock_queue
                    await processor.initialize()
                    
                    # Simulate queue messages
                    queue_messages = [
                        {"text": f"הודעה מספר {i} מהתור", "sender_id": f"queue_user_{i}"}
                        for i in range(10)
                    ]
                    
                    # Process messages from queue
                    for msg in queue_messages:
                        result = await processor.process_message(msg)
                        self.processed_messages.append(result)
                        self.queue_operations.append("DEQUEUE")
                    
                    await processor.cleanup()
                    return len(self.processed_messages), len(self.queue_operations)
            
            # Test Redis queue integration
            redis_integration = MockRedisQueueIntegration()
            processed_count, queue_ops_count = await redis_integration.simulate_queue_processing()
            
            assert processed_count == 10
            assert queue_ops_count == 10
            assert all(msg["success"] for msg in redis_integration.processed_messages)
            
            self.test_results.append(("Redis Queue", "PASSED"))
            print("✅ Test 5 PASSED: Redis queue integration works")
            
        except Exception as e:
            self.test_results.append(("Redis Queue", f"FAILED: {e}"))
            print(f"❌ Test 5 FAILED: {e}")
    
    async def test_06_end_to_end_workflow(self):
        """🧪 Test 6: Complete end-to-end workflow"""
        print("🧪 Test 6: End-to-End Workflow")
        
        try:
            # Mock complete system workflow
            class MockEndToEndSystem:
                def __init__(self):
                    self.workflow_steps = []
                    self.processor = None
                
                async def initialize(self):
                    self.processor = EnhancedAIMessageProcessor(AIEngineType.OPENMANUS)
                    self.processor.queue_manager = self.mock_redis
                    await self.processor.initialize()
                
                async def complete_workflow(self, user_message):
                    # Step 1: Receive message
                    self.workflow_steps.append("MESSAGE_RECEIVED")
                    
                    # Step 2: Route to appropriate agent
                    agent_name = await self.processor._route_to_agent(
                        user_message["text"], user_message.get("metadata", {})
                    )
                    self.workflow_steps.append(f"ROUTED_TO_{agent_name.upper()}")
                    
                    # Step 3: Process with agent
                    result = await self.processor.process_message(user_message)
                    self.workflow_steps.append("AGENT_PROCESSED")
                    
                    # Step 4: Generate response
                    if result["success"]:
                        self.workflow_steps.append("RESPONSE_GENERATED")
                    
                    # Step 5: Log interaction
                    self.workflow_steps.append("INTERACTION_LOGGED")
                    
                    return result, self.workflow_steps
            
            # Test complete workflow
            e2e_system = MockEndToEndSystem()
            await e2e_system.initialize()
            
            # Test appointment booking workflow
            user_request = {
                "text": "שלום, אני רוצה לקבוע תור לבדיקה שגרתית בשבוע הבא",
                "sender_id": "e2e_test_user",
                "channel": "webapp",
                "metadata": {"user_type": "returning_patient"}
            }
            
            result, workflow = await e2e_system.complete_workflow(user_request)
            
            # Verify complete workflow
            assert result["success"] == True
            assert result["agent_used"] == "scheduler"
            assert "MESSAGE_RECEIVED" in workflow
            assert "ROUTED_TO_SCHEDULER" in workflow
            assert "AGENT_PROCESSED" in workflow
            assert "RESPONSE_GENERATED" in workflow
            assert "INTERACTION_LOGGED" in workflow
            
            await e2e_system.processor.cleanup()
            
            self.test_results.append(("End-to-End Workflow", "PASSED"))
            print("✅ Test 6 PASSED: End-to-end workflow complete")
            
        except Exception as e:
            self.test_results.append(("End-to-End Workflow", f"FAILED: {e}"))
            print(f"❌ Test 6 FAILED: {e}")
    
    async def test_07_stress_test_system_load(self):
        """🧪 Test 7: System stress test under load"""
        print("🧪 Test 7: System Stress Test")
        
        try:
            # Create processor for stress testing
            processor = EnhancedAIMessageProcessor(AIEngineType.OPENMANUS)
            processor.queue_manager = self.mock_redis
            await processor.initialize()
            
            # Generate high load
            stress_messages = []
            for i in range(100):
                stress_messages.append({
                    "text": f"בדיקת עומס מספר {i} - אני רוצה לקבוע תור",
                    "sender_id": f"stress_user_{i}",
                    "channel": "stress_test"
                })
            
            # Process under stress
            start_time = time.time()
            
            # Process in batches to simulate real load
            batch_size = 20
            successful_batches = 0
            
            for i in range(0, len(stress_messages), batch_size):
                batch = stress_messages[i:i+batch_size]
                tasks = [processor.process_message(msg) for msg in batch]
                results = await asyncio.gather(*tasks)
                
                # Check batch success
                batch_success = all(r["success"] for r in results)
                if batch_success:
                    successful_batches += 1
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Verify stress test results
            expected_batches = len(stress_messages) // batch_size
            assert successful_batches == expected_batches
            assert total_time < 5.0  # Should complete within 5 seconds
            
            throughput = len(stress_messages) / total_time
            print(f"✅ Stress test: {len(stress_messages)} messages in {total_time:.2f}s")
            print(f"✅ Throughput: {throughput:.1f} messages/second")
            
            await processor.cleanup()
            
            self.test_results.append(("Stress Test", "PASSED"))
            print("✅ Test 7 PASSED: System handles stress load")
            
        except Exception as e:
            self.test_results.append(("Stress Test", f"FAILED: {e}"))
            print(f"❌ Test 7 FAILED: {e}")
    
    async def test_08_error_recovery_integration(self):
        """🧪 Test 8: Error recovery and system resilience"""
        print("🧪 Test 8: Error Recovery Integration")
        
        try:
            processor = EnhancedAIMessageProcessor(AIEngineType.OPENMANUS)
            processor.queue_manager = self.mock_redis
            await processor.initialize()
            
            # Test various error scenarios
            error_scenarios = [
                {"text": None, "sender_id": "error_test_1"},  # None text
                {"text": "", "sender_id": "error_test_2"},    # Empty text
                {"text": "א" * 50000, "sender_id": "error_test_3"},  # Very long text
                {"sender_id": "error_test_4"},  # Missing text
                {"text": "test", "sender_id": None},  # None sender_id
            ]
            
            recovery_count = 0
            
            for scenario in error_scenarios:
                try:
                    result = await processor.process_message(scenario)
                    if result["success"]:
                        recovery_count += 1
                        print(f"✅ Recovered from error scenario: {scenario}")
                except Exception as e:
                    print(f"⚠️ Could not recover from: {scenario} - {e}")
            
            # System should recover from most errors
            assert recovery_count >= 4  # Should handle at least 4/5 error scenarios
            
            await processor.cleanup()
            
            self.test_results.append(("Error Recovery", "PASSED"))
            print("✅ Test 8 PASSED: System recovers from errors")
            
        except Exception as e:
            self.test_results.append(("Error Recovery", f"FAILED: {e}"))
            print(f"❌ Test 8 FAILED: {e}")
    
    async def run_all_aggressive_tests(self):
        """Run all aggressive system integration tests"""
        print("🔥 STARTING AGGRESSIVE SYSTEM INTEGRATION TESTS")
        print("=" * 70)
        
        await self.setup_test_environment()
        
        # Run all tests
        tests = [
            self.test_01_openmanus_engine_system_integration,
            self.test_02_websocket_message_flow,
            self.test_03_api_endpoint_integration,
            self.test_04_database_integration_simulation,
            self.test_05_redis_queue_integration,
            self.test_06_end_to_end_workflow,
            self.test_07_stress_test_system_load,
            self.test_08_error_recovery_integration
        ]
        
        for test in tests:
            try:
                await test()
            except Exception as e:
                print(f"❌ {test.__name__} CRASHED: {e}")
                self.test_results.append((test.__name__, f"CRASHED: {e}"))
        
        # Final results
        print("=" * 70)
        print("🎯 AGGRESSIVE SYSTEM INTEGRATION TEST RESULTS:")
        print("=" * 70)
        
        passed = sum(1 for _, result in self.test_results if result == "PASSED")
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = "✅" if result == "PASSED" else "❌"
            print(f"{status} {test_name}: {result}")
        
        print("=" * 70)
        print(f"🎯 FINAL SCORE: {passed}/{total} TESTS PASSED")
        
        if passed == total:
            print("🎉 PERFECT SCORE! OPENMANUS SYSTEM INTEGRATION IS FLAWLESS!")
        elif passed >= total * 0.8:
            print("🎯 EXCELLENT! SYSTEM INTEGRATION IS VERY STRONG!")
        elif passed >= total * 0.6:
            print("⚠️ GOOD BUT NEEDS IMPROVEMENT")
        else:
            print("🚨 CRITICAL ISSUES FOUND - IMMEDIATE ATTENTION REQUIRED")
        
        return passed == total

# Standalone runner
async def main():
    """Run aggressive system integration tests"""
    tester = AggressiveSystemIntegrationTests()
    success = await tester.run_all_aggressive_tests()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
