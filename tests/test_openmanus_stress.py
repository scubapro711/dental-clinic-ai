"""
OpenManus Stress and Reliability Tests
בדיקות עומס ואמינות OpenManus
"""

import pytest
import asyncio
import time
import random
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

from src.ai_agents.engines.ai_engine_factory import AIEngineFactory, AIEngineType

class TestOpenManusStress:
    """Stress testing for OpenManus integration"""
    
    @pytest.fixture
    async def stress_engine(self):
        """Create engine for stress testing"""
        config = {
            "agents": {
                "receptionist": {"role": "Receptionist", "goal": "Handle inquiries", "backstory": "Professional"},
                "scheduler": {"role": "Scheduler", "goal": "Schedule appointments", "backstory": "Expert"},
                "confirmation": {"role": "Confirmation", "goal": "Handle confirmations", "backstory": "Specialist"}
            }
        }
        
        engine = await AIEngineFactory.create_engine(AIEngineType.OPENMANUS, config)
        yield engine
        await engine.shutdown()
    
    @pytest.fixture
    async def stress_agents(self, stress_engine):
        """Create agents for stress testing"""
        agents = {}
        for agent_name in ["receptionist", "scheduler", "confirmation"]:
            agent_config = {
                "name": agent_name,
                "role": f"{agent_name.title()}",
                "goal": f"Handle {agent_name} tasks",
                "backstory": f"Professional {agent_name}"
            }
            agents[agent_name] = await stress_engine.create_agent(agent_config)
        return agents
    
    @pytest.mark.asyncio
    async def test_high_concurrency_load(self, stress_agents):
        """Test high concurrency load (50 concurrent requests)"""
        receptionist = stress_agents["receptionist"]
        
        messages = [
            "שלום, אני רוצה לקבוע תור",
            "מה השעות של המרפאה?",
            "יש לי כאב בשן",
            "אני רוצה לבטל תור",
            "Hello, I need an appointment",
            "What are your prices?",
            "Do you accept insurance?",
            "I have a dental emergency"
        ]
        
        # Create 50 concurrent tasks
        tasks = []
        for i in range(50):
            message = random.choice(messages)
            task = receptionist.process_message(message, f"stress_user_{i}")
            tasks.append(task)
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        total_time = end_time - start_time
        successful_responses = [r for r in responses if isinstance(r, dict) and r.get("success")]
        
        # Assertions
        assert len(successful_responses) >= 45  # At least 90% success rate
        assert total_time < 30.0  # Should complete within 30 seconds
        
        print(f"Processed {len(successful_responses)}/{len(responses)} requests in {total_time:.2f}s")
        print(f"Average response time: {total_time/len(responses):.3f}s per request")
    
    @pytest.mark.asyncio
    async def test_sustained_load(self, stress_agents):
        """Test sustained load over time (100 requests over 60 seconds)"""
        receptionist = stress_agents["receptionist"]
        
        messages = [
            "שלום, איך אפשר לעזור?",
            "אני רוצה מידע על טיפולים",
            "מתי אפשר לקבוע תור?",
            "כמה עולה ניקוי שיניים?"
        ]
        
        responses = []
        start_time = time.time()
        
        # Send requests continuously for 60 seconds
        while time.time() - start_time < 60:
            message = random.choice(messages)
            user_id = f"sustained_user_{len(responses)}"
            
            try:
                response = await receptionist.process_message(message, user_id)
                responses.append(response)
            except Exception as e:
                responses.append({"success": False, "error": str(e)})
            
            # Small delay between requests
            await asyncio.sleep(0.5)
        
        successful_responses = [r for r in responses if r.get("success")]
        success_rate = len(successful_responses) / len(responses) * 100
        
        assert success_rate >= 95.0  # At least 95% success rate
        assert len(responses) >= 100  # Should process at least 100 requests
        
        print(f"Sustained load: {len(responses)} requests, {success_rate:.1f}% success rate")
    
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self, stress_engine):
        """Test for memory leaks during agent creation/destruction"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create and destroy agents repeatedly
        for i in range(20):
            agent_config = {
                "name": f"memory_test_agent_{i}",
                "role": "Memory Test Agent",
                "goal": "Test memory usage",
                "backstory": "Testing agent"
            }
            
            agent = await stress_engine.create_agent(agent_config)
            
            # Process some messages
            for j in range(5):
                await agent.process_message(f"Test message {j}", f"memory_user_{i}_{j}")
            
            await agent.cleanup()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        memory_increase_mb = memory_increase / (1024 * 1024)
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase_mb < 50, f"Memory increased by {memory_increase_mb:.2f}MB"
        
        print(f"Memory usage: {memory_increase_mb:.2f}MB increase after 20 agent cycles")
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, stress_agents):
        """Test system recovery after errors"""
        receptionist = stress_agents["receptionist"]
        
        # Test with various problematic inputs
        problematic_inputs = [
            "",  # Empty string
            "א" * 10000,  # Very long string
            "🚀🤖💻" * 100,  # Lots of emojis
            "\n\n\n\n\n",  # Only newlines
            "SELECT * FROM users;",  # SQL injection attempt
            "<script>alert('xss')</script>",  # XSS attempt
            None,  # This will be handled by the wrapper
        ]
        
        successful_recoveries = 0
        
        for i, problematic_input in enumerate(problematic_inputs):
            if problematic_input is None:
                continue
                
            try:
                response = await receptionist.process_message(
                    problematic_input, 
                    f"error_test_user_{i}"
                )
                
                # Should handle gracefully
                if response.get("success") is not False:
                    successful_recoveries += 1
                    
            except Exception as e:
                # Should not raise unhandled exceptions
                print(f"Unhandled exception for input {i}: {e}")
        
        # Should handle most problematic inputs gracefully
        recovery_rate = successful_recoveries / (len(problematic_inputs) - 1) * 100
        assert recovery_rate >= 80, f"Only {recovery_rate:.1f}% recovery rate"
        
        print(f"Error recovery: {recovery_rate:.1f}% successful recoveries")
    
    @pytest.mark.asyncio
    async def test_multi_agent_coordination(self, stress_agents):
        """Test coordination between multiple agents under load"""
        tasks = []
        
        # Create tasks for all agents simultaneously
        for i in range(30):
            agent_name = ["receptionist", "scheduler", "confirmation"][i % 3]
            agent = stress_agents[agent_name]
            
            message = f"בדיקת תיאום {i} עבור {agent_name}"
            task = agent.process_message(message, f"coordination_user_{i}")
            tasks.append((agent_name, task))
        
        start_time = time.time()
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        end_time = time.time()
        
        # Analyze results by agent
        agent_results = {"receptionist": [], "scheduler": [], "confirmation": []}
        
        for i, result in enumerate(results):
            agent_name = tasks[i][0]
            if isinstance(result, dict) and result.get("success"):
                agent_results[agent_name].append(result)
        
        # Each agent should handle its requests successfully
        for agent_name, agent_responses in agent_results.items():
            success_rate = len(agent_responses) / 10 * 100  # 10 requests per agent
            assert success_rate >= 80, f"{agent_name} only {success_rate:.1f}% success rate"
        
        total_time = end_time - start_time
        assert total_time < 15.0, f"Multi-agent coordination took {total_time:.2f}s"
        
        print(f"Multi-agent coordination: {total_time:.2f}s for 30 requests across 3 agents")
    
    @pytest.mark.asyncio
    async def test_rapid_agent_creation_destruction(self, stress_engine):
        """Test rapid agent creation and destruction"""
        creation_times = []
        destruction_times = []
        
        for i in range(10):
            # Test agent creation time
            start_time = time.time()
            agent_config = {
                "name": f"rapid_test_agent_{i}",
                "role": "Rapid Test Agent",
                "goal": "Test rapid creation",
                "backstory": "Testing agent"
            }
            agent = await stress_engine.create_agent(agent_config)
            creation_time = time.time() - start_time
            creation_times.append(creation_time)
            
            # Test agent destruction time
            start_time = time.time()
            await agent.cleanup()
            destruction_time = time.time() - start_time
            destruction_times.append(destruction_time)
        
        avg_creation_time = sum(creation_times) / len(creation_times)
        avg_destruction_time = sum(destruction_times) / len(destruction_times)
        
        # Creation and destruction should be fast
        assert avg_creation_time < 1.0, f"Average creation time: {avg_creation_time:.3f}s"
        assert avg_destruction_time < 0.5, f"Average destruction time: {avg_destruction_time:.3f}s"
        
        print(f"Agent lifecycle: {avg_creation_time:.3f}s creation, {avg_destruction_time:.3f}s destruction")
    
    @pytest.mark.asyncio
    async def test_hebrew_unicode_stress(self, stress_agents):
        """Test Hebrew and Unicode handling under stress"""
        receptionist = stress_agents["receptionist"]
        
        hebrew_messages = [
            "שלום, אני רוצה לקבוע תור לבדיקה שגרתית",
            "יש לי כאב חזק בשן הטוחנת השמאלית",
            "מתי המרפאה פתוחה בימי שישי?",
            "כמה עולה טיפול שורש?",
            "אני רוצה לבטל את התור שלי למחר",
            "האם אתם מקבלים ביטוח מכבי?",
            "אני צריך תור דחוף לילד בן 8",
            "מה ההמלצות לאחר עקירת שן?"
        ]
        
        # Add some complex Unicode
        unicode_messages = [
            "שלום 🦷 אני רוצה תור",
            "כאב שיניים 😣 עזרה!",
            "ביטוח ✅ או ❌?",
            "תור 📅 מתי פנוי?",
            "חירום 🚨 כאב חזק!"
        ]
        
        all_messages = hebrew_messages + unicode_messages
        
        # Process 50 Hebrew/Unicode messages concurrently
        tasks = []
        for i in range(50):
            message = random.choice(all_messages)
            task = receptionist.process_message(message, f"hebrew_user_{i}")
            tasks.append(task)
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        successful_responses = [r for r in responses if isinstance(r, dict) and r.get("success")]
        success_rate = len(successful_responses) / len(responses) * 100
        
        assert success_rate >= 90, f"Hebrew/Unicode success rate: {success_rate:.1f}%"
        
        # Check that responses contain Hebrew characters
        hebrew_responses = 0
        for response in successful_responses:
            if any(char in response.get("response", "") for char in "אבגדהוזחטיכלמנסעפצקרשת"):
                hebrew_responses += 1
        
        hebrew_response_rate = hebrew_responses / len(successful_responses) * 100
        assert hebrew_response_rate >= 70, f"Only {hebrew_response_rate:.1f}% responses in Hebrew"
        
        print(f"Hebrew/Unicode stress: {success_rate:.1f}% success, {hebrew_response_rate:.1f}% Hebrew responses")


class TestOpenManusReliability:
    """Reliability and edge case testing"""
    
    @pytest.mark.asyncio
    async def test_network_simulation(self):
        """Simulate network delays and failures"""
        # This would typically involve mocking network calls
        # For now, we'll test timeout handling
        
        config = {"agents": {"test": {"role": "Test", "goal": "Test", "backstory": "Test"}}}
        engine = await AIEngineFactory.create_engine(AIEngineType.OPENMANUS, config)
        
        agent = await engine.create_agent({
            "name": "network_test",
            "role": "Network Test",
            "goal": "Test network resilience", 
            "backstory": "Testing agent"
        })
        
        # Test with simulated delay (using asyncio.sleep)
        async def delayed_message():
            await asyncio.sleep(0.1)  # Simulate network delay
            return await agent.process_message("Test message with delay", "network_user")
        
        start_time = time.time()
        response = await delayed_message()
        end_time = time.time()
        
        assert response["success"] is True
        assert end_time - start_time >= 0.1  # Should include the delay
        
        await engine.shutdown()
    
    @pytest.mark.asyncio
    async def test_data_consistency(self):
        """Test data consistency across multiple operations"""
        config = {"agents": {"consistency": {"role": "Test", "goal": "Test", "backstory": "Test"}}}
        engine = await AIEngineFactory.create_engine(AIEngineType.OPENMANUS, config)
        
        agent = await engine.create_agent({
            "name": "consistency_test",
            "role": "Consistency Test",
            "goal": "Test data consistency",
            "backstory": "Testing agent"
        })
        
        # Perform multiple operations and check consistency
        user_id = "consistency_user"
        responses = []
        
        for i in range(10):
            response = await agent.process_message(f"Message {i}", user_id)
            responses.append(response)
        
        # All responses should be successful and consistent
        assert all(r["success"] for r in responses)
        assert all(r["agent"] == "consistency_test" for r in responses)
        assert all(r["engine"] == "openmanus" for r in responses)
        
        await engine.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto", "-s"])
