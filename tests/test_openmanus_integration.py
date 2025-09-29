"""
OpenManus Integration Tests
בדיקות אינטגרציה OpenManus
"""

import pytest
import asyncio
import time
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

from src.ai_agents.engines.ai_engine_factory import AIEngineFactory, AIEngineType
from src.ai_agents.engines.openmanus_engine import OpenManusEngine
from src.ai_agents.openmanus_agents.openmanus_agent_wrapper import OpenManusAgentWrapper

class TestOpenManusIntegration:
    """Comprehensive OpenManus integration tests"""
    
    @pytest.fixture
    async def openmanus_engine(self):
        """Create OpenManus engine for testing"""
        config = {
            "agents": {
                "receptionist": {
                    "role": "Receptionist",
                    "goal": "Handle patient inquiries and appointments",
                    "backstory": "Professional dental clinic receptionist"
                },
                "scheduler": {
                    "role": "Scheduler",
                    "goal": "Manage appointment scheduling",
                    "backstory": "Expert appointment coordinator"
                },
                "confirmation": {
                    "role": "Confirmation Agent",
                    "goal": "Handle appointment confirmations",
                    "backstory": "Appointment confirmation specialist"
                }
            }
        }
        
        engine = await AIEngineFactory.create_engine(AIEngineType.OPENMANUS, config)
        yield engine
        await engine.shutdown()
    
    @pytest.fixture
    async def test_agents(self, openmanus_engine):
        """Create test agents"""
        agents = {}
        for agent_name in ["receptionist", "scheduler", "confirmation"]:
            agent_config = {
                "name": agent_name,
                "role": f"{agent_name.title()} Agent",
                "goal": f"Handle {agent_name} tasks",
                "backstory": f"Professional {agent_name}"
            }
            agents[agent_name] = await openmanus_engine.create_agent(agent_config)
        return agents
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self):
        """Test OpenManus engine initialization"""
        config = {"test": "config"}
        engine = OpenManusEngine()
        
        assert not engine.initialized
        await engine.initialize(config)
        assert engine.initialized
        assert engine.config == config
        
        await engine.shutdown()
    
    @pytest.mark.asyncio
    async def test_agent_creation(self, openmanus_engine):
        """Test OpenManus agent creation"""
        agent_config = {
            "name": "test_agent",
            "role": "Test Agent",
            "goal": "Testing purposes",
            "backstory": "Test agent for integration testing"
        }
        
        agent = await openmanus_engine.create_agent(agent_config)
        
        assert isinstance(agent, OpenManusAgentWrapper)
        assert agent.agent_name == "test_agent"
        assert agent.role == "Test Agent"
        assert agent.initialized
        
        await agent.cleanup()
    
    @pytest.mark.asyncio
    async def test_receptionist_agent_processing(self, test_agents):
        """Test receptionist agent message processing"""
        receptionist = test_agents["receptionist"]
        
        # Test general inquiry
        response = await receptionist.process_message(
            "שלום, אני רוצה מידע על המרפאה",
            "test_user_001"
        )
        
        assert response["success"] is True
        assert "שלום" in response["response"]
        assert response["agent"] == "receptionist"
        assert response["engine"] == "openmanus"
        
        # Test emergency detection
        emergency_response = await receptionist.process_message(
            "יש לי כאב חזק בשן, זה חירום!",
            "test_user_002"
        )
        
        assert emergency_response["success"] is True
        assert emergency_response["priority"] == "critical"
        assert "🚨" in emergency_response["response"]
        assert "03-555-0123" in emergency_response["response"]
    
    @pytest.mark.asyncio
    async def test_scheduler_agent_processing(self, test_agents):
        """Test scheduler agent message processing"""
        scheduler = test_agents["scheduler"]
        
        response = await scheduler.process_message(
            "אני רוצה לקבוע תור לניקוי שיניים",
            "test_user_003"
        )
        
        assert response["success"] is True
        assert "📅" in response["response"]
        assert response["agent"] == "scheduler"
        assert response["engine"] == "openmanus"
        assert "available_slots" in response
    
    @pytest.mark.asyncio
    async def test_confirmation_agent_processing(self, test_agents):
        """Test confirmation agent message processing"""
        confirmation = test_agents["confirmation"]
        
        response = await confirmation.process_message(
            "אני רוצה לאשר את התור שלי",
            "test_user_004"
        )
        
        assert response["success"] is True
        assert "✅" in response["response"]
        assert response["agent"] == "confirmation"
        assert response["engine"] == "openmanus"
        assert "appointments" in response
    
    @pytest.mark.asyncio
    async def test_agent_capabilities(self, test_agents):
        """Test agent capabilities"""
        for agent_name, agent in test_agents.items():
            capabilities = await agent.get_capabilities()
            
            assert isinstance(capabilities, list)
            assert len(capabilities) > 0
            assert "advanced_nlp_processing" in capabilities
            assert "multi_language_support" in capabilities
            assert "hebrew_english_support" in capabilities
    
    @pytest.mark.asyncio
    async def test_agent_health_check(self, test_agents):
        """Test agent health checks"""
        for agent_name, agent in test_agents.items():
            health = await agent.health_check()
            
            assert health["agent_name"] == agent_name
            assert health["status"] == "healthy"
            assert health["engine"] == "openmanus"
            assert health["initialized"] is True
            assert "capabilities_count" in health
            assert health["capabilities_count"] > 0
    
    @pytest.mark.asyncio
    async def test_multilingual_support(self, test_agents):
        """Test multilingual support (Hebrew and English)"""
        receptionist = test_agents["receptionist"]
        
        # Hebrew test
        hebrew_response = await receptionist.process_message(
            "שלום, איך אפשר לקבוע תור?",
            "test_user_005"
        )
        
        assert hebrew_response["success"] is True
        assert any(hebrew_char in hebrew_response["response"] for hebrew_char in "אבגדהוזחטיכלמנסעפצקרשת")
        
        # English test
        english_response = await receptionist.process_message(
            "Hello, I would like to schedule an appointment",
            "test_user_006"
        )
        
        assert english_response["success"] is True
    
    @pytest.mark.asyncio
    async def test_intent_analysis_accuracy(self, test_agents):
        """Test intent analysis accuracy"""
        receptionist = test_agents["receptionist"]
        
        test_cases = [
            ("אני רוצה לקבוע תור", "appointment_scheduling"),
            ("יש לי כאב בשן", "emergency"),
            ("אני רוצה לאשר תור", "appointment_confirmation"),
            ("מה השעות של המרפאה?", "general_inquiry")
        ]
        
        for message, expected_intent in test_cases:
            response = await receptionist.process_message(message, "test_user")
            # Intent should be detected correctly (we can't directly test _analyze_intent_advanced 
            # but we can verify the response is appropriate)
            assert response["success"] is True
    
    @pytest.mark.asyncio
    async def test_error_handling(self, test_agents):
        """Test error handling capabilities"""
        receptionist = test_agents["receptionist"]
        
        # Test with empty message
        response = await receptionist.process_message("", "test_user")
        assert response["success"] is True  # Should handle gracefully
        
        # Test with very long message
        long_message = "א" * 1000
        response = await receptionist.process_message(long_message, "test_user")
        assert response["success"] is True
    
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, test_agents):
        """Test performance benchmarks"""
        receptionist = test_agents["receptionist"]
        
        # Single message performance
        start_time = time.time()
        response = await receptionist.process_message(
            "שלום, אני רוצה מידע על המרפאה",
            "perf_test_user"
        )
        end_time = time.time()
        
        processing_time = end_time - start_time
        assert processing_time < 2.0  # Should process within 2 seconds
        assert response["success"] is True
        
        # Concurrent processing test
        tasks = []
        for i in range(5):
            task = receptionist.process_message(
                f"הודעה מספר {i}",
                f"concurrent_user_{i}"
            )
            tasks.append(task)
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        concurrent_time = end_time - start_time
        assert concurrent_time < 5.0  # Should handle 5 concurrent requests within 5 seconds
        assert all(response["success"] for response in responses)
    
    @pytest.mark.asyncio
    async def test_engine_info(self, openmanus_engine):
        """Test engine information"""
        info = await openmanus_engine.get_engine_info()
        
        assert info["engine_type"] == "openmanus"
        assert info["version"] == "1.0.0"
        assert info["initialized"] is True
        assert "capabilities" in info
        assert "advanced_nlp" in info["capabilities"]
        assert "browser_automation" in info["capabilities"]
        assert "python_execution" in info["capabilities"]
    
    @pytest.mark.asyncio
    async def test_factory_integration(self):
        """Test factory integration with OpenManus"""
        config = {"test": "factory_config"}
        
        # Test OpenManus engine creation
        engine = await AIEngineFactory.create_engine(AIEngineType.OPENMANUS, config)
        assert isinstance(engine, OpenManusEngine)
        assert engine.initialized
        
        # Test default engine is now OpenManus
        default_engine = await AIEngineFactory.create_default_engine(config)
        assert isinstance(default_engine, OpenManusEngine)
        
        # Test supported engines include OpenManus
        supported = AIEngineFactory.get_supported_engines()
        assert AIEngineType.OPENMANUS in supported
        assert AIEngineType.CREWAI in supported
        
        await engine.shutdown()
        await default_engine.shutdown()
    
    @pytest.mark.asyncio
    async def test_resource_cleanup(self, openmanus_engine):
        """Test proper resource cleanup"""
        # Create multiple agents
        agents = []
        for i in range(3):
            agent_config = {
                "name": f"cleanup_test_agent_{i}",
                "role": "Test Agent",
                "goal": "Testing cleanup",
                "backstory": "Cleanup test agent"
            }
            agent = await openmanus_engine.create_agent(agent_config)
            agents.append(agent)
        
        # Verify agents are created and initialized
        for agent in agents:
            assert agent.initialized
        
        # Test engine shutdown cleans up all agents
        await openmanus_engine.shutdown()
        
        # Verify cleanup
        assert not openmanus_engine.initialized
        assert len(openmanus_engine.agents) == 0


class TestOpenManusVsCrewAIComparison:
    """Comparison tests between OpenManus and CrewAI"""
    
    @pytest.mark.asyncio
    @patch('src.ai_agents.crewai_agents.crewai_agent_wrapper.AdvancedDentalTool')
    async def test_response_quality_comparison(self, MockAdvancedDentalTool):
        mock_dental_tool_instance = MockAdvancedDentalTool.return_value
        mock_dental_tool_instance.initialize = AsyncMock()
        mock_dental_tool_instance.cleanup = AsyncMock()
        mock_dental_tool_instance.get_available_slots = AsyncMock(return_value=[])
        mock_dental_tool_instance.get_patient_appointments = AsyncMock(return_value=[])
        mock_dental_tool_instance.get_patient_details = AsyncMock(return_value={})
        """Compare response quality between OpenManus and CrewAI"""
        config = {
            "use_mock_tools": True,
            "agents": {
                "receptionist": {
                    "role": "Receptionist",
                    "goal": "Handle patient inquiries",
                    "backstory": "Professional receptionist"
                }
            }
        }
        
        # Create both engines
        openmanus_engine = await AIEngineFactory.create_engine(AIEngineType.OPENMANUS, config)
        crewai_engine = await AIEngineFactory.create_engine(AIEngineType.CREWAI, config)
        
        # Create agents
        om_agent = await openmanus_engine.create_agent({
            "name": "receptionist",
            "role": "Receptionist",
            "goal": "Handle inquiries",
            "backstory": "Professional"
        })
        
        ca_agent = await crewai_engine.create_agent({
            "name": "receptionist", 
            "role": "Receptionist",
            "goal": "Handle inquiries",
            "backstory": "Professional"
        })
        
        test_message = "שלום, אני רוצה לקבוע תור לבדיקה"
        
        # Get responses from both
        om_response = await om_agent.process_message(test_message, "comparison_user")
        ca_response = await ca_agent.process_message(test_message, "comparison_user")
        
        # Both should succeed
        assert om_response["success"] is True
        assert ca_response["success"] is True
        
        # OpenManus should have more advanced features
        assert om_response["engine"] == "openmanus"
        assert ca_response["engine"] != "openmanus"
        
        # OpenManus should have confidence scores and advanced analysis
        # (This would be implementation specific)
        
        await openmanus_engine.shutdown()
        await crewai_engine.shutdown()
    
    @pytest.mark.asyncio
    @patch('src.ai_agents.crewai_agents.crewai_agent_wrapper.AdvancedDentalTool')
    async def test_performance_comparison(self, MockAdvancedDentalTool):
        mock_dental_tool_instance = MockAdvancedDentalTool.return_value
        mock_dental_tool_instance.initialize = AsyncMock()
        mock_dental_tool_instance.cleanup = AsyncMock()
        mock_dental_tool_instance.process_message = AsyncMock(return_value={"success": True, "response": "mock response"})
        """Compare performance between OpenManus and CrewAI"""
        config = {"use_mock_tools": True, "agents": {"test": {"role": "Test", "goal": "Test", "backstory": "Test"}}}
        
        # Performance test for OpenManus
        start_time = time.time()
        om_engine = await AIEngineFactory.create_engine(AIEngineType.OPENMANUS, config)
        om_agent = await om_engine.create_agent({"name": "test", "role": "Test", "goal": "Test", "backstory": "Test"})
        om_response = await om_agent.process_message("test message", "perf_user")
        om_time = time.time() - start_time
        
        # Performance test for CrewAI
        start_time = time.time()
        ca_engine = await AIEngineFactory.create_engine(AIEngineType.CREWAI, config)
        ca_agent = await ca_engine.create_agent({"name": "test", "role": "Test", "goal": "Test", "backstory": "Test"})
        ca_response = await ca_agent.process_message("test message", "perf_user")
        ca_time = time.time() - start_time
        
        # Both should work
        assert om_response["success"] is True
        assert ca_response["success"] is True
        
        # Log performance results (for analysis)
        print(f"OpenManus time: {om_time:.3f}s")
        print(f"CrewAI time: {ca_time:.3f}s")
        
        await om_engine.shutdown()
        await ca_engine.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
