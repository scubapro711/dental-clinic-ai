"""
Tests for AgentGraphV3 - Multi-Agent System with Supervisor

Tests the supervisor routing logic, agent delegation, and message forwarding.
"""

import pytest
from unittest.mock import Mock, patch
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.agent_graph_v3 import AgentGraphV3, remove_handoff_messages
from app.agents.graph_state import AgentState


class TestRemoveHandoffMessages:
    """Test the remove_handoff_messages utility function."""
    
    def test_removes_routing_messages(self):
        """Should remove messages containing routing keywords."""
        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="I will delegate this to the CFO agent"),
            AIMessage(content="Here is the response"),
        ]
        
        clean_messages = remove_handoff_messages(messages)
        
        assert len(clean_messages) == 2
        assert clean_messages[0].content == "Hello"
        assert clean_messages[1].content == "Here is the response"
    
    def test_keeps_all_messages_without_routing_keywords(self):
        """Should keep all messages if no routing keywords present."""
        messages = [
            HumanMessage(content="What's my revenue?"),
            AIMessage(content="Your revenue is $10,000"),
        ]
        
        clean_messages = remove_handoff_messages(messages)
        
        assert len(clean_messages) == 2
    
    def test_handles_empty_list(self):
        """Should handle empty message list."""
        messages = []
        
        clean_messages = remove_handoff_messages(messages)
        
        assert len(clean_messages) == 0


class TestAgentGraphV3:
    """Test AgentGraphV3 multi-agent system."""
    
    @pytest.fixture
    def mock_memory(self):
        """Create mock causal memory."""
        memory = Mock()
        memory.get_similar_interactions.return_value = []
        return memory
    
    @pytest.fixture
    def graph(self, mock_memory):
        """Create AgentGraphV3 instance with mock memory."""
        return AgentGraphV3(memory=mock_memory)
    
    @pytest.mark.asyncio
    async def test_graph_initialization(self, graph):
        """Should initialize graph with supervisor and agents."""
        assert graph.alex is not None
        assert graph.supervisor_llm is not None
        assert graph.graph is not None
    
    @pytest.mark.asyncio
    async def test_supervisor_routes_to_alex(self, graph, mock_memory):
        """Should route patient-related queries to Alex."""
        message = "I need to schedule an appointment"
        
        response = await graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv",
            message=message
        )
        
        # Should route to Alex
        assert response["agent"] == "alex"
        assert response["response"] is not None
        assert "intent" in response
    
    @pytest.mark.asyncio
    async def test_supervisor_handles_financial_query(self, graph, mock_memory):
        """Should route financial queries to CFO (or Alex for now)."""
        message = "What's our revenue this month?"
        
        response = await graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv",
            message=message
        )
        
        # CFO not implemented yet, should route to Alex
        assert response["agent"] == "alex"
        assert response["intent"] == "financial_inquiry"
    
    @pytest.mark.asyncio
    async def test_supervisor_handles_operations_query(self, graph, mock_memory):
        """Should route operations queries to Admin (or Alex for now)."""
        message = "There's a scheduling conflict at 3pm"
        
        response = await graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv",
            message=message
        )
        
        # Admin not implemented yet, should route to Alex
        assert response["agent"] == "alex"
        assert response["intent"] == "operations_inquiry"
    
    @pytest.mark.asyncio
    async def test_escalation_handling(self, graph, mock_memory):
        """Should handle escalations from agents."""
        message = "I have severe pain, level 9!"
        
        response = await graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv",
            message=message
        )
        
        # Should escalate
        assert response.get("requires_human") == True or response.get("escalation_level") is not None
    
    @pytest.mark.asyncio
    async def test_stores_interaction_in_memory(self, graph, mock_memory):
        """Should store interaction in causal memory."""
        message = "Hello"
        
        await graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv",
            message=message
        )
        
        # Should call store_interaction
        mock_memory.store_interaction.assert_called_once()
        
        # Check metadata includes supervisor_routed flag
        call_args = mock_memory.store_interaction.call_args
        metadata = call_args.kwargs["metadata"]
        assert metadata["supervisor_routed"] == True
    
    @pytest.mark.asyncio
    async def test_intent_classification(self, graph):
        """Should classify intents correctly."""
        test_cases = [
            ("What's our revenue?", "financial_inquiry"),
            ("There's a scheduling conflict", "operations_inquiry"),
            ("I have tooth pain", "medical_question"),
            ("I need an appointment", "appointment_scheduling"),
            ("Hello", "general_inquiry"),
        ]
        
        for message, expected_intent in test_cases:
            intent = graph._classify_intent(message)
            assert intent == expected_intent, f"Failed for message: {message}"
    
    @pytest.mark.asyncio
    async def test_response_not_paraphrased(self, graph, mock_memory):
        """Should forward agent response without paraphrasing."""
        message = "Hello"
        
        response = await graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv",
            message=message
        )
        
        # Response should come directly from agent, not supervisor
        assert response["response"] is not None
        assert len(response["response"]) > 0
        
        # Should not contain supervisor routing language
        routing_keywords = ["delegating to", "routing to", "calling"]
        assert not any(keyword in response["response"].lower() for keyword in routing_keywords)
    
    @pytest.mark.asyncio
    async def test_agent_responses_stored(self, graph, mock_memory):
        """Should store agent responses for multi-agent queries."""
        message = "Hello"
        
        response = await graph.process_message(
            user_id="test_user",
            organization_id="test_org",
            conversation_id="test_conv",
            message=message
        )
        
        # Should have agent_responses dict
        assert "agent_responses" in response
        assert "alex" in response["agent_responses"]


@pytest.mark.asyncio
async def test_graph_v3_end_to_end():
    """End-to-end test of AgentGraphV3."""
    graph = AgentGraphV3()
    
    # Test patient query
    response = await graph.process_message(
        user_id="test_user",
        organization_id="test_org",
        conversation_id="test_conv",
        message="I need to book an appointment"
    )
    
    assert response["agent"] == "alex"
    assert response["response"] is not None
    assert response["intent"] == "appointment_scheduling"
    assert "agent_responses" in response
