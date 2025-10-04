"""
Agents Status API - Monitor and control AI agents

Provides agent health monitoring and control for the Mission Control dashboard.

Architecture:
- Widget → API → LangGraph State (query internal state, no full agent call)
- Fast, efficient, no LLM calls
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["Agents"])


# ===== Schemas =====

class AgentStatus(BaseModel):
    """Agent health and status information."""
    name: str
    display_name: str
    status: str  # online, offline, paused
    uptime_seconds: int
    requests_handled: int
    avg_response_time: float
    success_rate: float
    last_active: str
    description: str
    
    class Config:
        from_attributes = True


class AgentControlResponse(BaseModel):
    """Response after agent control action."""
    success: bool
    message: str
    agent_name: str
    new_status: str


# ===== Endpoints =====

@router.get("/status", response_model=List[AgentStatus])
async def get_all_agents_status(
    current_user: User = Depends(get_current_user),
):
    """
    Get status of all AI agents.
    
    Returns health and performance metrics for:
    - Alex (Patient Agent)
    - Marcus (CFO Agent)
    - Sophia (Admin Agent)
    
    Architecture:
    - Queries LangGraph internal state (no LLM call)
    - Fast, efficient
    - Returns mock metrics for now (TODO: track real metrics)
    """
    try:
        # Import agent graph to check initialization
        # This is a state query, not a full agent call!
        from app.agents.agent_graph_v3 import AgentGraphV3
        
        # Try to get global instance if exists
        # For now, we'll return mock data since agents are always initialized
        # TODO: Track real agent metrics in database or in-memory store
        
        # Calculate uptime (mock - would track actual start time)
        uptime_seconds = 84600  # ~23.5 hours
        
        agents = [
            AgentStatus(
                name="alex",
                display_name="Alex",
                status="online",
                uptime_seconds=uptime_seconds,
                requests_handled=127,
                avg_response_time=2.3,
                success_rate=94.5,
                last_active=datetime.utcnow().isoformat(),
                description="Patient-facing agent for appointments and medical triage"
            ),
            AgentStatus(
                name="marcus",
                display_name="Marcus",
                status="online",
                uptime_seconds=uptime_seconds,
                requests_handled=45,
                avg_response_time=1.8,
                success_rate=98.2,
                last_active=datetime.utcnow().isoformat(),
                description="CFO agent for financial analysis and insights"
            ),
            AgentStatus(
                name="sophia",
                display_name="Sophia",
                status="online",
                uptime_seconds=uptime_seconds,
                requests_handled=89,
                avg_response_time=2.1,
                success_rate=96.7,
                last_active=datetime.utcnow().isoformat(),
                description="Practice admin agent for scheduling and operations"
            ),
        ]
        
        logger.info(f"Retrieved status for {len(agents)} agents")
        return agents
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent status: {str(e)}"
        )


@router.get("/{agent_name}/status", response_model=AgentStatus)
async def get_agent_status(
    agent_name: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get status of a specific agent.
    
    Args:
        agent_name: Name of agent (alex, marcus, sophia)
    """
    # Validate agent name
    valid_agents = ["alex", "marcus", "sophia"]
    if agent_name.lower() not in valid_agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found. Valid agents: {', '.join(valid_agents)}"
        )
    
    # Get all agents and filter
    all_agents = await get_all_agents_status(current_user)
    agent = next((a for a in all_agents if a.name == agent_name.lower()), None)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found"
        )
    
    return agent


@router.post("/{agent_name}/pause", response_model=AgentControlResponse)
async def pause_agent(
    agent_name: str,
    current_user: User = Depends(get_current_user),
):
    """
    Pause an agent (stop processing new requests).
    
    Args:
        agent_name: Name of agent to pause (alex, marcus, sophia)
        
    Note: This is a mock implementation for now.
    TODO: Implement actual agent pause mechanism.
    """
    # Validate agent name
    valid_agents = ["alex", "marcus", "sophia"]
    if agent_name.lower() not in valid_agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found"
        )
    
    # TODO: Implement actual pause mechanism
    # For now, return success (mock)
    logger.info(f"Agent '{agent_name}' paused by user {current_user.id}")
    
    return AgentControlResponse(
        success=True,
        message=f"Agent '{agent_name}' has been paused",
        agent_name=agent_name,
        new_status="paused"
    )


@router.post("/{agent_name}/resume", response_model=AgentControlResponse)
async def resume_agent(
    agent_name: str,
    current_user: User = Depends(get_current_user),
):
    """
    Resume a paused agent.
    
    Args:
        agent_name: Name of agent to resume (alex, marcus, sophia)
    """
    # Validate agent name
    valid_agents = ["alex", "marcus", "sophia"]
    if agent_name.lower() not in valid_agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found"
        )
    
    # TODO: Implement actual resume mechanism
    logger.info(f"Agent '{agent_name}' resumed by user {current_user.id}")
    
    return AgentControlResponse(
        success=True,
        message=f"Agent '{agent_name}' has been resumed",
        agent_name=agent_name,
        new_status="online"
    )


@router.post("/{agent_name}/restart", response_model=AgentControlResponse)
async def restart_agent(
    agent_name: str,
    current_user: User = Depends(get_current_user),
):
    """
    Restart an agent (reinitialize).
    
    Args:
        agent_name: Name of agent to restart (alex, marcus, sophia)
        
    Note: This is a mock implementation for now.
    TODO: Implement actual agent restart mechanism.
    """
    # Validate agent name
    valid_agents = ["alex", "marcus", "sophia"]
    if agent_name.lower() not in valid_agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found"
        )
    
    # TODO: Implement actual restart mechanism
    # This would reinitialize the agent
    logger.info(f"Agent '{agent_name}' restarted by user {current_user.id}")
    
    return AgentControlResponse(
        success=True,
        message=f"Agent '{agent_name}' has been restarted",
        agent_name=agent_name,
        new_status="online"
    )


@router.get("/health", response_model=Dict[str, Any])
async def get_agents_health():
    """
    Get overall health status of the agent system.
    
    Returns:
    - Total agents
    - Online agents
    - Offline agents
    - System status
    """
    # Mock health data
    # TODO: Calculate from real agent status
    
    return {
        "total_agents": 3,
        "online_agents": 3,
        "offline_agents": 0,
        "paused_agents": 0,
        "system_status": "healthy",
        "last_check": datetime.utcnow().isoformat(),
    }
