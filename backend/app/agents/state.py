"""
Agent state definitions for LangGraph.

This module defines the state structure for AI agents.
"""

from typing import TypedDict, Annotated, Sequence, Optional
from operator import add
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    State for dental clinic AI agents.
    
    This state is passed between nodes in the LangGraph workflow.
    """
    
    # Conversation context
    messages: Annotated[Sequence[BaseMessage], add]
    
    # User and organization context
    user_id: str
    organization_id: Optional[str]
    conversation_id: str
    
    # Agent routing
    current_agent: str  # dana, michal, yosef, sarah
    next_agent: Optional[str]
    
    # Task context
    task_type: Optional[str]  # appointment, patient_info, billing, etc.
    extracted_data: dict  # Extracted entities and data
    
    # Tool results
    tool_results: dict
    
    # Response generation
    final_response: Optional[str]
    requires_human: bool  # Flag for human handoff
