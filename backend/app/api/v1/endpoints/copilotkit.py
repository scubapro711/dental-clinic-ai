"""
CopilotKit Integration Endpoint

This endpoint connects CopilotKit frontend components to our LangGraph agent system.
It provides streaming responses and real-time agent interactions using ag_ui_langgraph.

Note: The main CopilotKit endpoint is registered directly on the FastAPI app
using add_langgraph_fastapi_endpoint() in main.py, not through this router.
"""

import logging
from typing import Any, Dict
from fastapi import APIRouter, Request
from ag_ui_langgraph import LangGraphAgent

from app.agents.agent_graph_v3 import agent_graph_v3

logger = logging.getLogger(__name__)

router = APIRouter()


# Initialize LangGraph agent for CopilotKit
# This agent wraps our existing LangGraph system
# It will be registered on the main FastAPI app in main.py
langgraph_agent = LangGraphAgent(
    name="dental_assistant",
    description="AI assistant for dental clinic management with specialized agents for patient care, financial analysis, and operations",
    graph=agent_graph_v3.graph,
)


# Alternative: Manual endpoint with direct agent integration
@router.post("/copilotkit/chat")
async def copilotkit_chat_endpoint(request: Request):
    """
    Manual chat endpoint that directly uses our agent_graph_v3.
    
    This provides a simpler interface for testing and custom integrations.
    Use this endpoint if you need custom logic for:
    - Request preprocessing
    - Response formatting
    - Custom authentication
    - Additional logging/monitoring
    """
    try:
        # Parse request body
        body = await request.json()
        
        # Extract parameters
        messages = body.get("messages", [])
        thread_id = body.get("threadId", "default")
        
        if not messages:
            return {"error": "No messages provided"}
        
        # Get last user message
        last_message = messages[-1]
        user_message = last_message.get("content", "")
        
        logger.info(f"Processing message in thread {thread_id}: {user_message[:100]}")
        
        # Process through agent graph
        result = await agent_graph_v3.process_message(
            user_id="copilotkit_user",  # TODO: Extract from auth
            organization_id="default_org",  # TODO: Extract from auth
            conversation_id=thread_id,
            message=user_message,
        )
        
        # Return response in CopilotKit format
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": result["response"],
                }
            ],
            "metadata": {
                "agent": result["agent"],
                "intent": result.get("intent"),
                "escalation_level": result.get("escalation_level"),
            }
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        return {
            "error": str(e),
            "message": "Failed to process chat request"
        }


# Health check for CopilotKit integration
@router.get("/copilotkit/health")
async def copilotkit_health():
    """
    Health check endpoint for CopilotKit integration.
    """
    return {
        "status": "healthy",
        "service": "copilotkit",
        "agents": [
            {
                "name": "dental_assistant",
                "status": "active",
                "sub_agents": ["supervisor", "alex", "cfo", "admin"]
            }
        ]
    }


# Export the agent for use in main.py
__all__ = ["router", "langgraph_agent"]
