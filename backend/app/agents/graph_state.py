"""
LangGraph Agent State Definition

This module defines the state schema for the agent graph as per User Story 2.1.
"""

from typing import TypedDict, List, Optional, Dict, Any
from typing_extensions import Annotated
from operator import add
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    State schema for the agent graph.
    
    This follows the architecture defined in WORK_PLAN_V14.1, Epic 2, User Story 2.1.
    """
    # Conversation messages
    messages: Annotated[List[BaseMessage], add]
    
    # Current agent handling the conversation
    current_agent: str
    
    # User and organization context
    user_id: str
    organization_id: str
    conversation_id: str
    
    # Extracted data from conversation
    patient_id: Optional[str]
    appointment_id: Optional[str]
    invoice_id: Optional[str]
    
    # Intent classification
    intent: Optional[str]
    
    # Routing decision
    next_agent: Optional[str]
    
    # Tool results
    tool_results: Dict[str, Any]
    
    # Error tracking
    errors: List[Dict[str, Any]]
    
    # Rate limiting counters
    rate_limit_counters: Dict[str, int]
    
    # Final response flag
    requires_human: bool
