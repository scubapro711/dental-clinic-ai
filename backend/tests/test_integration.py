"""
Integration Tests for Agent System

End-to-end tests with real LLM calls to validate the complete agent system.
"""

import pytest
import asyncio
from langchain_core.messages import HumanMessage

from app.agents.agent_graph import AgentGraph
from app.agents.dana import DanaAgent
from app.agents.michal import MichalAgent
from app.agents.yosef import YosefAgent
from app.agents.sarah import SarahAgent


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests with real LLM calls."""
    
    def test_dana_general_inquiry(self):
        """Test Dana handling a general inquiry."""
        dana = DanaAgent()
        
        state = {
            "messages": [HumanMessage(content="Hello, what services do you offer?")],
            "current_agent": "dana",
            "user_id": "test_user",
            "organization_id": "test_org",
            "conversation_id": "test_conv",
            "patient_id": None,
            "appointment_id": None,
            "invoice_id": None,
            "intent": None,
            "next_agent": None,
            "tool_results": {},
            "errors": [],
            "rate_limit_counters": {},
            "requires_human": False,
        }
        
        result = dana.process(state)
        
        # Assertions
        assert result["current_agent"] == "dana"
        assert len(result["messages"]) == 2
        assert len(result["messages"][-1].content) > 0
        print(f"\nDana response: {result['messages'][-1].content}")
    
    def test_michal_medical_question(self):
        """Test Michal handling a medical question."""
        michal = MichalAgent()
        
        state = {
            "messages": [HumanMessage(content="What are the benefits of regular dental cleanings?")],
            "current_agent": "michal",
            "user_id": "test_user",
            "organization_id": "test_org",
            "conversation_id": "test_conv",
            "patient_id": None,
            "appointment_id": None,
            "invoice_id": None,
            "intent": None,
            "next_agent": None,
            "tool_results": {},
            "errors": [],
            "rate_limit_counters": {},
            "requires_human": False,
        }
        
        result = michal.process(state)
        
        # Assertions
        assert result["current_agent"] == "michal"
        assert len(result["messages"]) == 2
        assert len(result["messages"][-1].content) > 0
        # Note: requires_human may be True or False depending on response
        print(f"\nMichal response: {result['messages'][-1].content}")
        print(f"Requires human: {result['requires_human']}")
    
    def test_yosef_billing_question(self):
        """Test Yosef handling a billing question."""
        yosef = YosefAgent()
        
        state = {
            "messages": [HumanMessage(content="How much does a dental cleaning cost?")],
            "current_agent": "yosef",
            "user_id": "test_user",
            "organization_id": "test_org",
            "conversation_id": "test_conv",
            "patient_id": None,
            "appointment_id": None,
            "invoice_id": None,
            "intent": None,
            "next_agent": None,
            "tool_results": {},
            "errors": [],
            "rate_limit_counters": {},
            "requires_human": False,
        }
        
        result = yosef.process(state)
        
        # Assertions
        assert result["current_agent"] == "yosef"
        assert len(result["messages"]) == 2
        assert len(result["messages"][-1].content) > 0
        print(f"\nYosef response: {result['messages'][-1].content}")
    
    def test_sarah_scheduling_question(self):
        """Test Sarah handling a scheduling question."""
        sarah = SarahAgent()
        
        state = {
            "messages": [HumanMessage(content="I'd like to schedule an appointment for next week")],
            "current_agent": "sarah",
            "user_id": "test_user",
            "organization_id": "test_org",
            "conversation_id": "test_conv",
            "patient_id": None,
            "appointment_id": None,
            "invoice_id": None,
            "intent": None,
            "next_agent": None,
            "tool_results": {},
            "errors": [],
            "rate_limit_counters": {},
            "requires_human": False,
        }
        
        result = sarah.process(state)
        
        # Assertions
        assert result["current_agent"] == "sarah"
        assert len(result["messages"]) == 2
        assert len(result["messages"][-1].content) > 0
        print(f"\nSarah response: {result['messages'][-1].content}")
    
    @pytest.mark.asyncio
    async def test_agent_graph_end_to_end(self):
        """Test complete agent graph with routing."""
        graph = AgentGraph()
        
        # Test 1: General inquiry
        result1 = await graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv_1",
            message="Hello, tell me about your dental services",
        )
        
        assert result1["agent"] in ["dana", "michal", "yosef", "sarah"]
        assert len(result1["response"]) > 0
        print(f"\n\nTest 1 - General inquiry:")
        print(f"Agent: {result1['agent']}")
        print(f"Response: {result1['response']}")
        
        # Test 2: Medical question (Dana -> Michal)
        result2 = await graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv_2",
            message="I have sensitive teeth, what should I do?",
        )
        
        print(f"\n\nTest 2 - Medical question:")
        print(f"Agent: {result2['agent']}")
        print(f"Response: {result2['response']}")
        
        # Test 3: Billing question (Dana -> Yosef)
        result3 = await graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv_3",
            message="How much will a root canal cost?",
        )
        
        print(f"\n\nTest 3 - Billing question:")
        print(f"Agent: {result3['agent']}")
        print(f"Response: {result3['response']}")
        
        # Test 4: Scheduling question (Dana -> Sarah)
        result4 = await graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv_4",
            message="I need to book an appointment for a cleaning",
        )
        
        print(f"\n\nTest 4 - Scheduling question:")
        print(f"Agent: {result4['agent']}")
        print(f"Response: {result4['response']}")
    
    def test_error_handling(self):
        """Test error handling with invalid state."""
        dana = DanaAgent()
        
        # Test with empty messages (should handle gracefully)
        state = {
            "messages": [],
            "current_agent": "dana",
            "user_id": "test_user",
            "organization_id": "test_org",
            "conversation_id": "test_conv",
            "patient_id": None,
            "appointment_id": None,
            "invoice_id": None,
            "intent": None,
            "next_agent": None,
            "tool_results": {},
            "errors": [],
            "rate_limit_counters": {},
            "requires_human": False,
        }
        
        # Should not crash
        result = dana.process(state)
        assert "errors" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
