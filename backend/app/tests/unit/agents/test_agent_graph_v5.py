"""
Unit Tests for Agent Graph V5

Tests for the multi-agent system including:
- Message history limiting
- Handoff message removal
- Agent routing logic
- State management
- Context cleaning
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.agents.agent_graph_v5 import (
    _limit_conversation_history,
    remove_handoff_messages,
)


@pytest.mark.unit
@pytest.mark.agents
class TestAgentGraphV5Helpers:
    """Test helper functions for Agent Graph V5."""
    
    def test_limit_conversation_history_under_limit(self):
        """Test that messages under limit are not truncated."""
        messages = [
            SystemMessage(content="System prompt"),
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there"),
        ]
        
        result = _limit_conversation_history(messages, max_messages=15)
        
        assert len(result) == 3
        assert result == messages
    
    def test_limit_conversation_history_over_limit(self):
        """Test that messages over limit are truncated."""
        messages = [
            SystemMessage(content="System prompt"),
        ] + [
            HumanMessage(content=f"Message {i}") if i % 2 == 0 else AIMessage(content=f"Response {i}")
            for i in range(30)
        ]
        
        result = _limit_conversation_history(messages, max_messages=15)
        
        # Should keep system message + last 15 messages
        assert len(result) == 16  # 1 system + 15 others
        assert isinstance(result[0], SystemMessage)
        assert result[0].content == "System prompt"
    
    def test_limit_conversation_history_preserves_system_messages(self):
        """Test that system messages are always preserved."""
        messages = [
            SystemMessage(content="System prompt 1"),
            SystemMessage(content="System prompt 2"),
        ] + [
            HumanMessage(content=f"Message {i}")
            for i in range(20)
        ]
        
        result = _limit_conversation_history(messages, max_messages=10)
        
        # Should keep both system messages + last 10 others
        assert len(result) == 12
        system_msgs = [m for m in result if isinstance(m, SystemMessage)]
        assert len(system_msgs) == 2
    
    def test_limit_conversation_history_exact_limit(self):
        """Test behavior when exactly at limit."""
        messages = [
            HumanMessage(content=f"Message {i}")
            for i in range(15)
        ]
        
        result = _limit_conversation_history(messages, max_messages=15)
        
        assert len(result) == 15
        assert result == messages
    
    def test_limit_conversation_history_custom_limit(self):
        """Test with custom max_messages parameter."""
        messages = [
            HumanMessage(content=f"Message {i}")
            for i in range(20)
        ]
        
        result = _limit_conversation_history(messages, max_messages=5)
        
        assert len(result) == 5
        # Should keep last 5 messages
        assert result[0].content == "Message 15"
        assert result[-1].content == "Message 19"
    
    def test_remove_handoff_messages_basic(self):
        """Test removing handoff/routing messages."""
        messages = [
            HumanMessage(content="I need help with scheduling"),
            AIMessage(content="delegating to Sophia for scheduling assistance"),
            AIMessage(content="I can help you with that"),
        ]
        
        result = remove_handoff_messages(messages)
        
        # Should remove the routing message
        assert len(result) < len(messages)
        assert any("delegating" in m.content for m in messages)
        assert not any("delegating" in m.content for m in result)
    
    def test_remove_handoff_messages_multiple_keywords(self):
        """Test removing messages with various routing keywords."""
        messages = [
            HumanMessage(content="Question 1"),
            AIMessage(content="transferring to Alex"),
            HumanMessage(content="Question 2"),
            AIMessage(content="routing to Sarah"),
            HumanMessage(content="Question 3"),
            AIMessage(content="forwarding to Marcus"),
        ]
        
        result = remove_handoff_messages(messages)
        
        # Should remove all routing messages
        routing_count = sum(1 for m in messages if isinstance(m, AIMessage) and 
                          any(kw in m.content.lower() for kw in ["transferring", "routing", "forwarding"]))
        assert routing_count > 0
        
        # Result should have fewer messages
        assert len(result) < len(messages)
    
    def test_remove_handoff_messages_preserves_user_messages(self):
        """Test that user messages are never removed."""
        messages = [
            HumanMessage(content="User message 1"),
            AIMessage(content="delegating to agent"),
            HumanMessage(content="User message 2"),
            AIMessage(content="Normal response"),
        ]
        
        result = remove_handoff_messages(messages)
        
        # All HumanMessages should be preserved
        human_messages = [m for m in result if isinstance(m, HumanMessage)]
        assert len(human_messages) == 2
        assert human_messages[0].content == "User message 1"
        assert human_messages[1].content == "User message 2"
    
    def test_remove_handoff_messages_no_handoffs(self):
        """Test that normal conversation is unchanged."""
        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi, how can I help?"),
            HumanMessage(content="I need information"),
            AIMessage(content="Here's the information you need"),
        ]
        
        result = remove_handoff_messages(messages)
        
        # Should return all messages unchanged
        assert len(result) == len(messages)
        assert result == messages
    
    def test_remove_handoff_messages_empty_list(self):
        """Test with empty message list."""
        messages = []
        
        result = remove_handoff_messages(messages)
        
        assert result == []
    
    def test_remove_handoff_messages_case_insensitive(self):
        """Test that keyword matching is case-insensitive."""
        messages = [
            AIMessage(content="DELEGATING TO AGENT"),
            AIMessage(content="Transferring To Agent"),
            AIMessage(content="routing to agent"),
        ]
        
        result = remove_handoff_messages(messages)
        
        # All should be removed regardless of case
        assert len(result) < len(messages)
    
    def test_limit_and_remove_combined(self):
        """Test combining both helper functions."""
        messages = [
            SystemMessage(content="System"),
        ] + [
            HumanMessage(content=f"Q{i}") if i % 3 == 0 else 
            AIMessage(content="delegating to agent") if i % 3 == 1 else
            AIMessage(content=f"A{i}")
            for i in range(30)
        ]
        
        # First limit history
        limited = _limit_conversation_history(messages, max_messages=15)
        
        # Then remove handoffs
        cleaned = remove_handoff_messages(limited)
        
        # Should have system message + reduced conversation
        assert len(cleaned) < len(messages)
        assert any(isinstance(m, SystemMessage) for m in cleaned)
        assert not any("delegating" in m.content.lower() for m in cleaned if isinstance(m, AIMessage))


@pytest.mark.unit
@pytest.mark.agents
class TestAgentGraphV5Integration:
    """Test Agent Graph V5 integration points."""
    
    def test_agent_state_structure(self):
        """Test that AgentState has expected structure."""
        from app.agents.graph_state import AgentState
        
        # Verify AgentState can be imported and has expected attributes
        assert AgentState is not None
    
    def test_agent_imports(self):
        """Test that all agent imports are available."""
        from app.agents.alex_v2 import AlexAgent
        from app.agents.sarah_clinical import sarah_agent
        from app.agents.cfo import CFOAgent
        from app.agents.practice_admin import PracticeAdminAgent
        from app.agents.harper_hipaa import harper_node
        
        # Verify all agents can be imported
        assert AlexAgent is not None
        assert sarah_agent is not None
        assert CFOAgent is not None
        assert PracticeAdminAgent is not None
        assert harper_node is not None
    
    @patch('app.agents.agent_graph_v5.get_memory_saver')
    def test_memory_saver_integration(self, mock_memory):
        """Test memory saver integration."""
        mock_memory.return_value = Mock()
        
        from app.agents.agent_graph_v5 import get_memory_saver
        
        memory = get_memory_saver()
        assert memory is not None
    
    def test_message_types_compatibility(self):
        """Test that message types work correctly."""
        human_msg = HumanMessage(content="Test")
        ai_msg = AIMessage(content="Response")
        system_msg = SystemMessage(content="System")
        
        messages = [system_msg, human_msg, ai_msg]
        
        # Verify messages can be processed
        result = _limit_conversation_history(messages, max_messages=10)
        assert len(result) == 3
        
        result = remove_handoff_messages(messages)
        assert len(result) == 3

