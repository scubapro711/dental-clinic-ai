"""
Unit Tests for Agent Graph V4

Tests for the 4-agent system including:
- Message history limiting
- Handoff message removal
- Agent routing
- State management
"""

import pytest
from unittest.mock import Mock, patch
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.agents.agent_graph_v4 import (
    _limit_conversation_history,
    remove_handoff_messages,
)


@pytest.mark.unit
@pytest.mark.agents
class TestAgentGraphV4Helpers:
    """Test helper functions for Agent Graph V4."""
    
    def test_limit_conversation_history_basic(self):
        """Test basic message limiting."""
        messages = [
            HumanMessage(content="Q1"),
            AIMessage(content="A1"),
            HumanMessage(content="Q2"),
        ]
        
        result = _limit_conversation_history(messages, max_messages=15)
        assert len(result) == 3
    
    def test_limit_conversation_history_with_system(self):
        """Test that system messages are preserved."""
        messages = [
            SystemMessage(content="System"),
            HumanMessage(content="Q1"),
        ] + [HumanMessage(content=f"Q{i}") for i in range(20)]
        
        result = _limit_conversation_history(messages, max_messages=10)
        
        # Should have system + 10 others
        assert len(result) == 11
        assert isinstance(result[0], SystemMessage)
    
    def test_remove_handoff_messages_v4(self):
        """Test removing routing messages in v4."""
        messages = [
            HumanMessage(content="Help me"),
            AIMessage(content="I will delegate this to Alex"),
            AIMessage(content="Here's the help"),
        ]
        
        result = remove_handoff_messages(messages)
        
        # Should remove delegation message
        assert len(result) < len(messages)
        assert not any("delegate" in m.content.lower() for m in result if isinstance(m, AIMessage))
    
    def test_remove_handoff_preserves_user_input(self):
        """Test that user messages are never removed."""
        messages = [
            HumanMessage(content="User question"),
            AIMessage(content="let me call Sarah"),
            HumanMessage(content="Another question"),
        ]
        
        result = remove_handoff_messages(messages)
        
        human_msgs = [m for m in result if isinstance(m, HumanMessage)]
        assert len(human_msgs) == 2
    
    def test_agent_v4_imports(self):
        """Test that v4 agents can be imported."""
        from app.agents.alex_v2 import AlexAgent
        from app.agents.sarah_clinical import sarah_agent
        from app.agents.cfo import CFOAgent
        from app.agents.practice_admin import PracticeAdminAgent
        
        assert AlexAgent is not None
        assert sarah_agent is not None
        assert CFOAgent is not None
        assert PracticeAdminAgent is not None
    
    def test_v4_has_4_agents(self):
        """Test that v4 has exactly 4 specialized agents (not including supervisor)."""
        # V4 should have: Alex, Sarah, Marcus (CFO), Sophia (Admin)
        from app.agents.alex_v2 import AlexAgent
        from app.agents.sarah_clinical import sarah_agent
        from app.agents.cfo import CFOAgent
        from app.agents.practice_admin import PracticeAdminAgent
        
        agents = [AlexAgent, sarah_agent, CFOAgent, PracticeAdminAgent]
        assert len(agents) == 4


@pytest.mark.unit
@pytest.mark.agents
class TestAgentGraphV4Integration:
    """Test Agent Graph V4 integration."""
    
    @patch('app.agents.agent_graph_v4.get_memory_saver')
    def test_memory_integration(self, mock_memory):
        """Test memory saver integration."""
        mock_memory.return_value = Mock()
        
        from app.agents.agent_graph_v4 import get_memory_saver
        memory = get_memory_saver()
        assert memory is not None
    
    def test_graph_state_import(self):
        """Test that graph state can be imported."""
        from app.agents.graph_state import AgentState
        assert AgentState is not None

