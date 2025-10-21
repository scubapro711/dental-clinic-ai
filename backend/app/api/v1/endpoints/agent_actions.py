"""
Agent Actions Endpoint

This endpoint allows the frontend to execute agent actions through the LangGraph system.
The Supervisor routes requests to the appropriate agent (Alex, Marcus, or Sophia).
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from app.agents.agent_graph_v5 import graph as agent_graph
from app.agents.graph_state import AgentState
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize agent graph (singleton)
_agent_graph = None

def get_agent_graph():
    """Get or create agent graph instance"""
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = agent_graph
        logger.info("Initialized AgentGraphV5 with Harper")
    return _agent_graph


class AgentActionRequest(BaseModel):
    """Request model for agent actions"""
    agent: str  # alex, marcus, sophia
    action: str  # call_patient, analyze_revenue, schedule_followup, etc.
    context: Dict[str, Any]  # Context data for the action


class AgentActionResponse(BaseModel):
    """Response model for agent actions"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    agent_used: str


@router.post("/execute", response_model=AgentActionResponse)
async def execute_agent_action(
    request: AgentActionRequest,
    # current_user: dict = Depends(get_current_user)  # Uncomment when auth is ready
):
    """
    Execute an agent action through LangGraph
    
    The Supervisor will route the request to the appropriate agent based on the action type.
    Each agent has access to Odoo tools and can perform actions like:
    - Alex: Call patients, handle conversations, schedule appointments
    - Marcus: Analyze financials, collect payments, generate reports
    - Sophia: Optimize schedules, manage operations, send reminders
    """
    try:
        logger.info(f"Executing agent action: {request.agent}.{request.action}")
        
        # Map frontend actions to natural language prompts
        # The Supervisor will understand these and route to the correct agent
        action_prompts = {
            # Alex actions (Patient-facing)
            "call_patient": f"Please call patient {request.context.get('patientName')} at {request.context.get('patientPhone', 'their phone number')} to discuss their inquiry. Conversation ID: {request.context.get('conversationId', 'N/A')}",
            
            "take_over": f"Take over the conversation with ID {request.context.get('conversationId')} and handle it directly.",
            
            "schedule_followup": f"Schedule a follow-up appointment for patient ID {request.context.get('patientId')}. Check available slots and book the next suitable time.",
            
            # Marcus actions (Financial)
            "analyze_revenue": f"Analyze the clinic's revenue for the period: {request.context.get('period', 'today')}. Provide insights on performance, trends, and recommendations.",
            
            "collect_payments": f"Review outstanding payments totaling ${request.context.get('amount', 0)} and initiate collection procedures. Prioritize high-value accounts.",
            
            # Sophia actions (Operations)
            "send_reminder": f"Send an appointment reminder to {request.context.get('patientName')} for their appointment (ID: {request.context.get('appointmentId')}).",
            
            "optimize_schedule": f"Optimize the schedule around appointment ID {request.context.get('appointmentId')}. Look for conflicts, gaps, and efficiency improvements.",
        }
        
        # Get the prompt for this action
        prompt = action_prompts.get(request.action)
        if not prompt:
            # If action not in predefined list, use it directly
            prompt = f"{request.action}: {request.context}"
        
        # Create initial state for LangGraph
        initial_state: AgentState = {
            "messages": [HumanMessage(content=prompt)],
            "current_agent": "supervisor",
            "next_agent": None,
            "context": request.context,
        }
        
        # Execute through LangGraph
        # The Supervisor will route to the correct agent automatically
        agent_graph = get_agent_graph()
        
        # Run the graph with a unique thread_id for this request
        thread_id = f"action_{request.agent}_{request.action}_{hash(str(request.context))}"
        config = {"configurable": {"thread_id": thread_id}}
        
        result = agent_graph.graph.invoke(initial_state, config)
        
        # Extract the response from the last message
        last_message = result["messages"][-1] if result.get("messages") else None
        response_text = last_message.content if last_message else "Action completed successfully"
        
        # Determine which agent actually handled it
        agent_used = result.get("current_agent", request.agent)
        
        logger.info(f"Action completed by {agent_used}: {response_text[:100]}...")
        
        return AgentActionResponse(
            success=True,
            message=response_text,
            data={
                "context": request.context,
                "agent_responses": result.get("agent_responses", {}),
            },
            agent_used=agent_used
        )
        
    except Exception as e:
        logger.error(f"Agent action failed: {str(e)}", exc_info=True)
        return AgentActionResponse(
            success=False,
            message=f"Action failed: {str(e)}",
            data=None,
            agent_used=request.agent
        )


@router.post("/chat")
async def chat_with_agent(
    agent: str,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    thread_id: Optional[str] = None,
    # current_user: dict = Depends(get_current_user)
):
    """
    Chat with a specific agent
    
    This endpoint allows direct conversation with Alex, Marcus, or Sophia.
    The agent will have access to the provided context and can use their tools.
    
    Supports conversation history through thread_id.
    """
    try:
        logger.info(f"Chat with {agent}: {message}")
        
        # Create initial state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=message)],
            "current_agent": "supervisor",
            "next_agent": None,
            "context": context or {},
        }
        
        # Execute through LangGraph with conversation history
        agent_graph = get_agent_graph()
        
        # Use provided thread_id or create new one
        if not thread_id:
            thread_id = f"chat_{agent}_{hash(message)}"
        
        config = {"configurable": {"thread_id": thread_id}}
        
        result = agent_graph.graph.invoke(initial_state, config)
        
        # Extract the response
        last_message = result["messages"][-1] if result.get("messages") else None
        response_text = last_message.content if last_message else "I'm here to help!"
        
        agent_used = result.get("current_agent", agent)
        
        return {
            "success": True,
            "response": response_text,
            "agent": agent_used,
            "thread_id": thread_id,  # Return thread_id for conversation continuity
            "data": result.get("agent_responses", {}),
        }
        
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}", exc_info=True)
        return {
            "success": False,
            "response": f"Sorry, I encountered an error: {str(e)}",
            "agent": agent,
            "thread_id": thread_id,
        }
