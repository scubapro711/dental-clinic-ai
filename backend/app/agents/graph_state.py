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
    
    Enhanced with RBAC (Role-Based Access Control) for data privacy and security.
    """
    # Conversation messages
    messages: Annotated[List[BaseMessage], add]
    
    # Current agent handling the conversation
    current_agent: str
    
    # User and organization context
    user_id: str
    organization_id: str
    conversation_id: str
    
    # RBAC - Role-Based Access Control
    user_role: str  # "patient" | "doctor" | "owner"
    user_permissions: List[str]  # List of permission strings
    
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
    
    # Agent responses (for multi-agent queries)
    agent_responses: Dict[str, str]
    
    # Error tracking
    errors: List[Dict[str, Any]]
    
    # Rate limiting counters
    rate_limit_counters: Dict[str, int]
    
    # Final response flag
    requires_human: bool
    
    # Escalation level for medical safety
    escalation_level: Optional[str]
    
    # Suggested actions from agents (Phase 7: Agentic System)
    suggested_actions: Optional[List[Dict[str, Any]]]
    """
    Actions suggested by the agent based on context and reasoning.
    
    IMPORTANT: These are decided by the agent (LLM), not by code logic!
    The agent analyzes the situation and suggests specific actions.
    
    Format: [
        {
            "id": "action_1",
            "label": "Review Pricing Strategy",
            "description": "Check if prices are competitive",
            "type": "analyze",  # analyze, schedule, contact, update, view, financial, action
            "priority": "high",  # high, medium, low
            "icon": "BarChart"  # Icon name for UI
        }
    ]
    
    The parser only extracts these from agent response, doesn't decide them!
    """
