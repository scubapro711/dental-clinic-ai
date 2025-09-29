#!/usr/bin/env python3
"""
🧪 AGGRESSIVE TESTING SUITE - SYNTHESIZER + OPENMANUS INTEGRATION
בדיקות אגרסיביות - אינטגרציה מסנתז + OpenManus

This module contains comprehensive tests to ensure the Enhanced Message Processor
(synthesizer) works perfectly with OpenManus agents.
"""

import pytest
import asyncio
import time
import random
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock

# Import the components we're testing
from src.ai_agents.enhanced_message_processor import EnhancedAIMessageProcessor
from src.ai_agents.engines.ai_engine_factory import AIEngineType, AIEngineConfig
from src.ai_agents.engines.openmanus_engine import OpenManusEngine
from src.ai_agents.openmanus_agents.openmanus_agent_wrapper import OpenManusAgentWrapper

class TestSynthesizerOpenManusIntegration:
    """Comprehensive integration tests for synthesizer + OpenManus"""
    
    @pytest.fixture
    async def mock_processor(self):
        """Create a mock processor for testing without Redis"""
        processor = EnhancedAIMessageProcessor(AIEngineType.OPENMANUS)
        
        # Mock Redis queue manager to avoid connection issues
        processor.queue_manager = AsyncMock()
        processor.queue_manager.initialize = AsyncMock()
        processor.queue_manager.start_worker = AsyncMock()
        processor.queue_manager.stop_workers = AsyncMock()
        processor.queue_manager.get_queue_stats = AsyncMock(return_value={
            "pending": 0, "processing": 0, "completed": 100
        })
        processor.queue_manager.cleanup = AsyncMock()
        
        await processor.initialize()
        return processor
    
    @pytest.mark.asyncio
    async def test_01_processor_initialization_with_openmanus(self, mock_processor):
        """🧪 Test 1: Processor initializes correctly with OpenManus"""
        print("🧪 Test 1: Processor initialization with OpenManus")
        
        # Check engine type
        assert mock_processor.engine_type == AIEngineType.OPENMANUS
        assert mock_processor.ai_engine is not None
        assert isinstance(mock_processor.ai_engine, OpenManusEngine)
        
        # Check agents created
        assert len(mock_processor.agents) == 3
        assert "receptionist" in mock_processor.agents
        assert "scheduler" in mock_processor.agents
        assert "confirmation" in mock_processor.agents
        
        print("✅ Test 1 PASSED: Processor initialized with OpenManus")
    
    @pytest.mark.asyncio
    async def test_02_message_routing_logic(self, mock_processor):
        """🧪 Test 2: Message routing works correctly"""
        print("🧪 Test 2: Message routing logic")
        
        # Test appointment routing
        agent = await mock_processor._route_to_agent("אני רוצה לקבוע תור", {})
        assert agent == "scheduler"
        
        agent = await mock_processor._route_to_agent("I want to book an appointment", {})
        assert agent == "scheduler"
        
        # Test confirmation routing  
        agent = await mock_processor._route_to_agent("אישור תור", {})
        assert agent == "confirmation"
        
        agent = await mock_processor._route_to_agent("cancel appointment", {})
        assert agent == "confirmation"
        
        # Test general routing
        agent = await mock_processor._route_to_agent("שלום", {})
        assert agent == "receptionist"
        
        agent = await mock_processor._route_to_agent("hello", {})
        assert agent == "receptionist"
        
        print("✅ Test 2 PASSED: Message routing works correctly")
    
    @pytest.mark.asyncio
    async def test_03_hebrew_message_processing(self, mock_processor):
        """🧪 Test 3: Hebrew message processing"""
        print("🧪 Test 3: Hebrew message processing")
        
        hebrew_messages = [
            "שלום, אני רוצה לקבוע תור לטיפול שורש",
            "האם יש מקום פנוי מחר?",
            "אני צריך לבטל את התור שלי",
            "כמה עולה ניקוי אבנית?",
            "יש לי כאב שיניים חזק!"
        ]
        
        for msg in hebrew_messages:
            result = await mock_processor.process_message({
                "text": msg,
                "sender_id": "test_hebrew_user",
                "channel": "test"
            })
            
            assert result["success"] == True
            assert "response" in result
            assert result["engine_type"] == "openmanus"
            assert result["agent_used"] in ["receptionist", "scheduler", "confirmation"]
            
            print(f"✅ Hebrew message processed: '{msg[:20]}...' → {result['agent_used']}")
        
        print("✅ Test 3 PASSED: Hebrew messages processed correctly")
    
    @pytest.mark.asyncio
    async def test_04_english_message_processing(self, mock_processor):
        """🧪 Test 4: English message processing"""
        print("🧪 Test 4: English message processing")
        
        english_messages = [
            "Hello, I need to schedule a dental cleaning",
            "Can I book an appointment for next week?",
            "I need to cancel my appointment",
            "What are your office hours?",
            "I have severe tooth pain!"
        ]
        
        for msg in english_messages:
            result = await mock_processor.process_message({
                "text": msg,
                "sender_id": "test_english_user", 
                "channel": "test"
            })
            
            assert result["success"] == True
            assert "response" in result
            assert result["engine_type"] == "openmanus"
            
            print(f"✅ English message processed: '{msg[:20]}...' → {result['agent_used']}")
        
        print("✅ Test 4 PASSED: English messages processed correctly")
    
    @pytest.mark.asyncio
    async def test_05_concurrent_message_processing(self, mock_processor):
        """🧪 Test 5: Concurrent message processing stress test"""
        print("🧪 Test 5: Concurrent message processing")
        
        messages = [
            {"text": f"שלום, אני רוצה תור מספר {i}", "sender_id": f"user_{i}", "channel": "test"}
            for i in range(20)
        ]
        
        # Process all messages concurrently
        start_time = time.time()
        tasks = [mock_processor.process_message(msg) for msg in messages]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all succeeded
        successful = sum(1 for r in results if r["success"])
        assert successful == 20
        
        processing_time = end_time - start_time
        print(f"✅ Processed 20 concurrent messages in {processing_time:.2f} seconds")
        print(f"✅ Average: {processing_time/20:.3f} seconds per message")
        
        print("✅ Test 5 PASSED: Concurrent processing works")
    
    @pytest.mark.asyncio
    async def test_06_agent_health_checks(self, mock_processor):
        """🧪 Test 6: All agents are healthy"""
        print("🧪 Test 6: Agent health checks")
        
        stats = await mock_processor.get_stats()
        
        assert stats["processor_running"] == False  # Not started in test
        assert stats["engine_type"] == "openmanus"
        assert stats["agents_count"] == 3
        
        # Check each agent health
        agent_health = stats["agent_health"]
        for agent_name in ["receptionist", "scheduler", "confirmation"]:
            assert agent_name in agent_health
            health = agent_health[agent_name]
            assert health["status"] == "healthy"
            assert health["initialized"] == True
            
            print(f"✅ Agent {agent_name}: {health['status']}")
        
        print("✅ Test 6 PASSED: All agents are healthy")
    
    @pytest.mark.asyncio
    async def test_07_error_handling(self, mock_processor):
        """🧪 Test 7: Error handling and recovery"""
        print("🧪 Test 7: Error handling")
        
        # Test with malformed message
        result = await mock_processor.process_message({})
        assert result["success"] == True  # Should handle gracefully
        
        # Test with None text
        result = await mock_processor.process_message({
            "text": None,
            "sender_id": "test_user"
        })
        assert result["success"] == True  # Should handle gracefully
        
        # Test with very long message
        long_text = "א" * 10000
        result = await mock_processor.process_message({
            "text": long_text,
            "sender_id": "test_user"
        })
        assert result["success"] == True
        
        print("✅ Test 7 PASSED: Error handling works correctly")
    
    @pytest.mark.asyncio
    async def test_08_agent_specialization(self, mock_processor):
        """🧪 Test 8: Each agent handles its specialty correctly"""
        print("🧪 Test 8: Agent specialization")
        
        # Test scheduler specialization
        scheduler_msgs = [
            "אני רוצה לקבוע תור",
            "I need to schedule an appointment",
            "book me a slot next week"
        ]
        
        for msg in scheduler_msgs:
            result = await mock_processor.process_message({
                "text": msg, "sender_id": "test", "channel": "test"
            })
            assert result["agent_used"] == "scheduler"
            print(f"✅ Scheduler handled: '{msg[:20]}...'")
        
        # Test confirmation specialization
        confirm_msgs = [
            "אישור תור",
            "cancel my appointment", 
            "reminder for tomorrow"
        ]
        
        for msg in confirm_msgs:
            result = await mock_processor.process_message({
                "text": msg, "sender_id": "test", "channel": "test"
            })
            assert result["agent_used"] == "confirmation"
            print(f"✅ Confirmation handled: '{msg[:20]}...'")
        
        print("✅ Test 8 PASSED: Agent specialization works")
    
    @pytest.mark.asyncio
    async def test_09_performance_benchmark(self, mock_processor):
        """🧪 Test 9: Performance benchmark"""
        print("🧪 Test 9: Performance benchmark")
        
        # Warm up
        for _ in range(5):
            await mock_processor.process_message({
                "text": "warmup", "sender_id": "warmup", "channel": "test"
            })
        
        # Benchmark single message processing
        iterations = 100
        start_time = time.time()
        
        for i in range(iterations):
            await mock_processor.process_message({
                "text": f"בדיקת ביצועים מספר {i}",
                "sender_id": f"perf_user_{i}",
                "channel": "benchmark"
            })
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / iterations
        
        print(f"✅ Processed {iterations} messages in {total_time:.2f} seconds")
        print(f"✅ Average processing time: {avg_time:.3f} seconds per message")
        print(f"✅ Throughput: {iterations/total_time:.1f} messages per second")
        
        # Performance assertions
        assert avg_time < 0.1  # Should be under 100ms per message
        assert iterations/total_time > 10  # Should handle 10+ messages per second
        
        print("✅ Test 9 PASSED: Performance meets requirements")
    
    @pytest.mark.asyncio
    async def test_10_cleanup_and_shutdown(self, mock_processor):
        """🧪 Test 10: Proper cleanup and shutdown"""
        print("🧪 Test 10: Cleanup and shutdown")
        
        # Test cleanup
        await mock_processor.cleanup()
        
        # Verify cleanup
        assert mock_processor.running == False
        
        # Verify agents are cleaned up (mocked, so just check it doesn't crash)
        try:
            stats = await mock_processor.get_stats()
            print("✅ Stats still accessible after cleanup")
        except Exception as e:
            print(f"⚠️ Expected behavior: {e}")
        
        print("✅ Test 10 PASSED: Cleanup completed successfully")

# Standalone test runner
async def run_aggressive_tests():
    """Run all aggressive tests"""
    print("🚀 STARTING AGGRESSIVE INTEGRATION TESTS")
    print("=" * 60)
    
    test_suite = TestSynthesizerOpenManusIntegration()
    
    # Create mock processor
    processor = EnhancedAIMessageProcessor(AIEngineType.OPENMANUS)
    processor.queue_manager = AsyncMock()
    processor.queue_manager.initialize = AsyncMock()
    processor.queue_manager.start_worker = AsyncMock()
    processor.queue_manager.stop_workers = AsyncMock()
    processor.queue_manager.get_queue_stats = AsyncMock(return_value={
        "pending": 0, "processing": 0, "completed": 100
    })
    processor.queue_manager.cleanup = AsyncMock()
    
    await processor.initialize()
    
    # Run all tests
    tests = [
        test_suite.test_01_processor_initialization_with_openmanus,
        test_suite.test_02_message_routing_logic,
        test_suite.test_03_hebrew_message_processing,
        test_suite.test_04_english_message_processing,
        test_suite.test_05_concurrent_message_processing,
        test_suite.test_06_agent_health_checks,
        test_suite.test_07_error_handling,
        test_suite.test_08_agent_specialization,
        test_suite.test_09_performance_benchmark,
        test_suite.test_10_cleanup_and_shutdown
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test(processor)
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"🎯 FINAL RESULTS: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! SYNTHESIZER + OPENMANUS INTEGRATION IS PERFECT!")
    else:
        print("⚠️ SOME TESTS FAILED - NEEDS ATTENTION")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_aggressive_tests())
    exit(0 if success else 1)
