"""
Test Suite for All Agents

Tests for Dana, Michal, Yosef, and Sarah agents with error handling,
rate limiting, and routing logic.
"""

import pytest
from unittest.mock import Mock, patch
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.agents.dana import DanaAgent
from app.agents.michal import MichalAgent
from app.agents.yosef import YosefAgent
from app.agents.sarah import SarahAgent
from app.agents.graph_state import AgentState
from app.agents.error_handler import RateLimitError, LLMError


@pytest.fixture
def base_state():
    """Create a base agent state for testing."""
    return {
        "messages": [],
        "current_agent": "dana",
        "user_id": "test_user_123",
        "organization_id": "test_org_456",
        "conversation_id": "test_conv_789",
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


class TestDanaAgent:
    """Tests for Dana (Coordinator) agent."""
    
    def test_dana_initialization(self):
        """Test Dana agent initialization."""
        dana = DanaAgent()
        assert dana.llm is not None
        assert dana.SYSTEM_PROMPT is not None
    
    @patch('app.agents.dana.ChatOpenAI')
    def test_dana_process_general_inquiry(self, mock_llm, base_state):
        """Test Dana handling general inquiry."""
        # Mock LLM response
        mock_response = AIMessage(content="Hello! How can I help you today?")
        mock_llm.return_value.invoke.return_value = mock_response
        
        dana = DanaAgent()
        dana.llm = mock_llm.return_value
        
        # Add user message
        base_state["messages"] = [HumanMessage(content="Hello")]
        
        # Process
        result = dana.process(base_state)
        
        # Assertions
        assert result["current_agent"] == "dana"
        assert len(result["messages"]) == 2
        assert result["next_agent"] is None
    
    @patch('app.agents.dana.ChatOpenAI')
    def test_dana_routing_to_michal(self, mock_llm, base_state):
        """Test Dana routing medical questions to Michal."""
        # Mock LLM response with medical keywords
        mock_response = AIMessage(content="That sounds like a dental issue. Let me connect you with Dr. Michal.")
        mock_llm.return_value.invoke.return_value = mock_response
        
        dana = DanaAgent()
        dana.llm = mock_llm.return_value
        
        # Add user message
        base_state["messages"] = [HumanMessage(content="I have tooth pain")]
        
        # Process
        result = dana.process(base_state)
        
        # Assertions
        assert result["next_agent"] == "michal"
    
    @patch('app.agents.dana.ChatOpenAI')
    def test_dana_routing_to_yosef(self, mock_llm, base_state):
        """Test Dana routing billing questions to Yosef."""
        # Mock LLM response with billing keywords
        mock_response = AIMessage(content="Let me connect you with Yosef, our accountant, to discuss billing.")
        mock_llm.return_value.invoke.return_value = mock_response
        
        dana = DanaAgent()
        dana.llm = mock_llm.return_value
        
        # Add user message
        base_state["messages"] = [HumanMessage(content="What's my invoice?")]
        
        # Process
        result = dana.process(base_state)
        
        # Assertions
        assert result["next_agent"] == "yosef"
    
    @patch('app.agents.dana.ChatOpenAI')
    def test_dana_routing_to_sarah(self, mock_llm, base_state):
        """Test Dana routing scheduling questions to Sarah."""
        # Mock LLM response with scheduling keywords
        mock_response = AIMessage(content="Let me connect you with Sarah to schedule an appointment.")
        mock_llm.return_value.invoke.return_value = mock_response
        
        dana = DanaAgent()
        dana.llm = mock_llm.return_value
        
        # Add user message
        base_state["messages"] = [HumanMessage(content="I need to book an appointment")]
        
        # Process
        result = dana.process(base_state)
        
        # Assertions
        assert result["next_agent"] == "sarah"
    
    def test_dana_rate_limiting(self, base_state):
        """Test Dana rate limiting."""
        dana = DanaAgent()
        
        # Simulate rapid requests
        for i in range(15):  # Exceed burst size of 10
            base_state["messages"] = [HumanMessage(content=f"Message {i}")]
            
            if i < 10:
                # Should succeed
                result = dana.process(base_state)
                assert "rate limit" not in result["messages"][-1].content.lower()
            else:
                # Should hit rate limit
                result = dana.process(base_state)
                # Check if rate limit error was handled
                if result.get("errors"):
                    assert result["errors"][-1]["type"] == "rate_limit"


class TestMichalAgent:
    """Tests for Michal (Medical) agent."""
    
    def test_michal_initialization(self):
        """Test Michal agent initialization."""
        michal = MichalAgent()
        assert michal.llm is not None
        assert michal.SYSTEM_PROMPT is not None
    
    @patch('app.agents.michal.ChatOpenAI')
    def test_michal_process_medical_question(self, mock_llm, base_state):
        """Test Michal handling medical question."""
        # Mock LLM response
        mock_response = AIMessage(content="Tooth sensitivity can be caused by several factors...")
        mock_llm.return_value.invoke.return_value = mock_response
        
        michal = MichalAgent()
        michal.llm = mock_llm.return_value
        
        # Add user message
        base_state["messages"] = [HumanMessage(content="Why are my teeth sensitive?")]
        
        # Process
        result = michal.process(base_state)
        
        # Assertions
        assert result["current_agent"] == "michal"
        assert len(result["messages"]) == 2
        assert result["requires_human"] is False
    
    @patch('app.agents.michal.ChatOpenAI')
    def test_michal_escalation_urgent_case(self, mock_llm, base_state):
        """Test Michal escalating urgent cases."""
        # Mock LLM response with urgent keywords
        mock_response = AIMessage(content="This sounds urgent. Please see a dentist immediately.")
        mock_llm.return_value.invoke.return_value = mock_response
        
        michal = MichalAgent()
        michal.llm = mock_llm.return_value
        
        # Add user message
        base_state["messages"] = [HumanMessage(content="I have severe pain and swelling")]
        
        # Process
        result = michal.process(base_state)
        
        # Assertions
        assert result["requires_human"] is True


class TestYosefAgent:
    """Tests for Yosef (Billing) agent."""
    
    def test_yosef_initialization(self):
        """Test Yosef agent initialization."""
        yosef = YosefAgent()
        assert yosef.llm is not None
        assert yosef.SYSTEM_PROMPT is not None
    
    @patch('app.agents.yosef.ChatOpenAI')
    def test_yosef_process_billing_question(self, mock_llm, base_state):
        """Test Yosef handling billing question."""
        # Mock LLM response
        mock_response = AIMessage(content="Your invoice total is 500 NIS, which includes...")
        mock_llm.return_value.invoke.return_value = mock_response
        
        yosef = YosefAgent()
        yosef.llm = mock_llm.return_value
        
        # Add user message
        base_state["messages"] = [HumanMessage(content="What's my invoice?")]
        
        # Process
        result = yosef.process(base_state)
        
        # Assertions
        assert result["current_agent"] == "yosef"
        assert len(result["messages"]) == 2
        assert result["requires_human"] is False
    
    @patch('app.agents.yosef.ChatOpenAI')
    def test_yosef_escalation_complex_case(self, mock_llm, base_state):
        """Test Yosef escalating complex billing cases."""
        # Mock LLM response with escalation keywords
        mock_response = AIMessage(content="This is a complex billing dispute. Please contact our accountant.")
        mock_llm.return_value.invoke.return_value = mock_response
        
        yosef = YosefAgent()
        yosef.llm = mock_llm.return_value
        
        # Add user message
        base_state["messages"] = [HumanMessage(content="I was charged incorrectly")]
        
        # Process
        result = yosef.process(base_state)
        
        # Assertions
        assert result["requires_human"] is True


class TestSarahAgent:
    """Tests for Sarah (Scheduling) agent."""
    
    def test_sarah_initialization(self):
        """Test Sarah agent initialization."""
        sarah = SarahAgent()
        assert sarah.llm is not None
        assert sarah.SYSTEM_PROMPT is not None
    
    @patch('app.agents.sarah.ChatOpenAI')
    def test_sarah_process_scheduling_request(self, mock_llm, base_state):
        """Test Sarah handling scheduling request."""
        # Mock LLM response
        mock_response = AIMessage(content="I'd be happy to schedule an appointment. What date works for you?")
        mock_llm.return_value.invoke.return_value = mock_response
        
        sarah = SarahAgent()
        sarah.llm = mock_llm.return_value
        
        # Add user message
        base_state["messages"] = [HumanMessage(content="I need to schedule an appointment")]
        
        # Process
        result = sarah.process(base_state)
        
        # Assertions
        assert result["current_agent"] == "sarah"
        assert len(result["messages"]) == 2
        assert result["task_type"] == "schedule"
    
    @patch('app.agents.sarah.ChatOpenAI')
    def test_sarah_reschedule_request(self, mock_llm, base_state):
        """Test Sarah handling reschedule request."""
        # Mock LLM response
        mock_response = AIMessage(content="I can help you reschedule. What's your new preferred date?")
        mock_llm.return_value.invoke.return_value = mock_response
        
        sarah = SarahAgent()
        sarah.llm = mock_llm.return_value
        
        # Add user message
        base_state["messages"] = [HumanMessage(content="I need to reschedule my appointment")]
        
        # Process
        result = sarah.process(base_state)
        
        # Assertions
        assert result["task_type"] == "reschedule"


class TestErrorHandling:
    """Tests for error handling across all agents."""
    
    @patch('app.agents.dana.ChatOpenAI')
    def test_llm_failure_with_retry(self, mock_llm, base_state):
        """Test LLM failure triggers retry logic."""
        dana = DanaAgent()
        
        # Mock LLM to fail twice then succeed
        mock_llm.return_value.invoke.side_effect = [
            Exception("API Error"),
            Exception("API Error"),
            AIMessage(content="Hello!"),
        ]
        dana.llm = mock_llm.return_value
        
        base_state["messages"] = [HumanMessage(content="Hello")]
        
        # Process - should succeed after retries
        result = dana.process(base_state)
        
        # Should have succeeded
        assert len(result["messages"]) == 2
        assert mock_llm.return_value.invoke.call_count == 3
    
    @patch('app.agents.dana.ChatOpenAI')
    def test_llm_failure_exhausts_retries(self, mock_llm, base_state):
        """Test LLM failure after all retries."""
        dana = DanaAgent()
        
        # Mock LLM to always fail
        mock_llm.return_value.invoke.side_effect = Exception("API Error")
        dana.llm = mock_llm.return_value
        
        base_state["messages"] = [HumanMessage(content="Hello")]
        
        # Process - should handle error gracefully
        result = dana.process(base_state)
        
        # Should have error message
        assert len(result["errors"]) > 0
        assert result["errors"][-1]["type"] == "llm_error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
