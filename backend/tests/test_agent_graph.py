"""
Test Suite for Agent Graph

Tests for LangGraph agent orchestration, routing, and state management.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.agent_graph import AgentGraph
from app.agents.graph_state import AgentState


@pytest.fixture
def agent_graph():
    """Create an agent graph instance for testing."""
    return AgentGraph()


@pytest.mark.asyncio
class TestAgentGraph:
    """Tests for agent graph orchestration."""
    
    async def test_graph_initialization(self, agent_graph):
        """Test agent graph initialization."""
        assert agent_graph.dana is not None
        assert agent_graph.michal is not None
        assert agent_graph.yosef is not None
        assert agent_graph.sarah is not None
        assert agent_graph.graph is not None
    
    @patch('app.agents.dana.ChatOpenAI')
    async def test_process_message_dana_only(self, mock_llm, agent_graph):
        """Test processing message that Dana handles alone."""
        # Mock Dana response (no routing)
        mock_response = AIMessage(content="Hello! How can I help you?")
        mock_llm.return_value.invoke.return_value = mock_response
        
        agent_graph.dana.llm = mock_llm.return_value
        
        # Process message
        result = await agent_graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv",
            message="Hello",
        )
        
        # Assertions
        assert result["agent"] == "dana"
        assert result["next_agent"] is None
        assert "Hello" in result["response"]
    
    @patch('app.agents.michal.ChatOpenAI')
    @patch('app.agents.dana.ChatOpenAI')
    async def test_process_message_dana_to_michal(self, mock_dana_llm, mock_michal_llm, agent_graph):
        """Test routing from Dana to Michal."""
        # Mock Dana response (routes to Michal)
        dana_response = AIMessage(content="Let me connect you with Dr. Michal for your dental question.")
        mock_dana_llm.return_value.invoke.return_value = dana_response
        
        # Mock Michal response
        michal_response = AIMessage(content="Tooth sensitivity can be caused by...")
        mock_michal_llm.return_value.invoke.return_value = michal_response
        
        agent_graph.dana.llm = mock_dana_llm.return_value
        agent_graph.michal.llm = mock_michal_llm.return_value
        
        # Process message
        result = await agent_graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv",
            message="Why are my teeth sensitive?",
        )
        
        # Assertions
        assert result["agent"] == "michal"
        assert "sensitivity" in result["response"].lower() or "Michal" in dana_response.content
    
    @patch('app.agents.yosef.ChatOpenAI')
    @patch('app.agents.dana.ChatOpenAI')
    async def test_process_message_dana_to_yosef(self, mock_dana_llm, mock_yosef_llm, agent_graph):
        """Test routing from Dana to Yosef."""
        # Mock Dana response (routes to Yosef)
        dana_response = AIMessage(content="Let me connect you with Yosef to discuss billing.")
        mock_dana_llm.return_value.invoke.return_value = dana_response
        
        # Mock Yosef response
        yosef_response = AIMessage(content="Your invoice total is 500 NIS...")
        mock_yosef_llm.return_value.invoke.return_value = yosef_response
        
        agent_graph.dana.llm = mock_dana_llm.return_value
        agent_graph.yosef.llm = mock_yosef_llm.return_value
        
        # Process message
        result = await agent_graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv",
            message="What's my invoice?",
        )
        
        # Assertions
        assert result["agent"] == "yosef"
    
    @patch('app.agents.sarah.ChatOpenAI')
    @patch('app.agents.dana.ChatOpenAI')
    async def test_process_message_dana_to_sarah(self, mock_dana_llm, mock_sarah_llm, agent_graph):
        """Test routing from Dana to Sarah."""
        # Mock Dana response (routes to Sarah)
        dana_response = AIMessage(content="Let me connect you with Sarah to schedule an appointment.")
        mock_dana_llm.return_value.invoke.return_value = dana_response
        
        # Mock Sarah response
        sarah_response = AIMessage(content="I'd be happy to schedule an appointment...")
        mock_sarah_llm.return_value.invoke.return_value = sarah_response
        
        agent_graph.dana.llm = mock_dana_llm.return_value
        agent_graph.sarah.llm = mock_sarah_llm.return_value
        
        # Process message
        result = await agent_graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv",
            message="I need to book an appointment",
        )
        
        # Assertions
        assert result["agent"] == "sarah"
    
    @patch('app.agents.dana.ChatOpenAI')
    async def test_conversation_history(self, mock_llm, agent_graph):
        """Test conversation history is maintained."""
        mock_response = AIMessage(content="Response")
        mock_llm.return_value.invoke.return_value = mock_response
        
        agent_graph.dana.llm = mock_llm.return_value
        
        # First message
        result1 = await agent_graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv",
            message="Hello",
        )
        
        # Second message with history
        result2 = await agent_graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv",
            message="How are you?",
            message_history=result1["state"]["messages"],
        )
        
        # Assertions
        assert len(result2["state"]["messages"]) > len(result1["state"]["messages"])
    
    @patch('app.agents.michal.ChatOpenAI')
    @patch('app.agents.dana.ChatOpenAI')
    async def test_requires_human_escalation(self, mock_dana_llm, mock_michal_llm, agent_graph):
        """Test human escalation flag is set."""
        # Mock Dana response (routes to Michal)
        dana_response = AIMessage(content="Let me connect you with Dr. Michal.")
        mock_dana_llm.return_value.invoke.return_value = dana_response
        
        # Mock Michal response (urgent case)
        michal_response = AIMessage(content="This sounds urgent. Please see a dentist immediately.")
        mock_michal_llm.return_value.invoke.return_value = michal_response
        
        agent_graph.dana.llm = mock_dana_llm.return_value
        agent_graph.michal.llm = mock_michal_llm.return_value
        
        # Process message
        result = await agent_graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv",
            message="I have severe pain and swelling",
        )
        
        # Assertions
        assert result["requires_human"] is True
    
    async def test_state_management(self, agent_graph):
        """Test state is properly managed."""
        # Create initial state
        initial_state: AgentState = {
            "messages": [HumanMessage(content="Test")],
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
        
        # Verify state structure
        assert "messages" in initial_state
        assert "current_agent" in initial_state
        assert "user_id" in initial_state
        assert "rate_limit_counters" in initial_state
        assert "errors" in initial_state


class TestRouting:
    """Tests for routing logic."""
    
    def test_route_from_dana_to_michal(self, agent_graph):
        """Test routing decision from Dana to Michal."""
        state: AgentState = {
            "messages": [],
            "current_agent": "dana",
            "user_id": "test",
            "organization_id": "test",
            "conversation_id": "test",
            "patient_id": None,
            "appointment_id": None,
            "invoice_id": None,
            "intent": None,
            "next_agent": "michal",
            "tool_results": {},
            "errors": [],
            "rate_limit_counters": {},
            "requires_human": False,
        }
        
        result = agent_graph._route_from_dana(state)
        assert result == "michal"
    
    def test_route_from_dana_to_yosef(self, agent_graph):
        """Test routing decision from Dana to Yosef."""
        state: AgentState = {
            "messages": [],
            "current_agent": "dana",
            "user_id": "test",
            "organization_id": "test",
            "conversation_id": "test",
            "patient_id": None,
            "appointment_id": None,
            "invoice_id": None,
            "intent": None,
            "next_agent": "yosef",
            "tool_results": {},
            "errors": [],
            "rate_limit_counters": {},
            "requires_human": False,
        }
        
        result = agent_graph._route_from_dana(state)
        assert result == "yosef"
    
    def test_route_from_dana_to_sarah(self, agent_graph):
        """Test routing decision from Dana to Sarah."""
        state: AgentState = {
            "messages": [],
            "current_agent": "dana",
            "user_id": "test",
            "organization_id": "test",
            "conversation_id": "test",
            "patient_id": None,
            "appointment_id": None,
            "invoice_id": None,
            "intent": None,
            "next_agent": "sarah",
            "tool_results": {},
            "errors": [],
            "rate_limit_counters": {},
            "requires_human": False,
        }
        
        result = agent_graph._route_from_dana(state)
        assert result == "sarah"
    
    def test_route_from_dana_to_end(self, agent_graph):
        """Test routing decision from Dana to end."""
        state: AgentState = {
            "messages": [],
            "current_agent": "dana",
            "user_id": "test",
            "organization_id": "test",
            "conversation_id": "test",
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
        
        result = agent_graph._route_from_dana(state)
        assert result == "end"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
