"""
Agent Activity API Endpoints

Provides endpoints for real-time agent activity metrics and monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Dict, Any

from app.core.database import get_async_db
from app.core.auth import get_current_membership
from app.models.user import OrganizationMembership
from app.shared.checkpoint_queries import get_agent_activity_metrics

router = APIRouter()


class AgentMetrics(BaseModel):
    """Individual agent metrics"""
    id: str
    name: str
    role: str
    status: str
    tasksToday: int
    tasksCompleted: int
    avgResponseTime: str
    successRate: int


class AgentActivityResponse(BaseModel):
    """Agent activity response model"""
    agents: List[AgentMetrics]
    totalTasks: int
    totalCompleted: int
    systemHealth: int


@router.get("/activity", response_model=AgentActivityResponse)
async def get_agent_activity(
    membership: OrganizationMembership = Depends(get_current_membership),
    async_db: AsyncSession = Depends(get_async_db),
    period_hours: int = Query(default=24, ge=1, le=168, description="Time period in hours")
):
    """
    Get comprehensive agent activity metrics.
    
    Returns real-time activity data for all AI agents including:
    - Task counts and completion rates
    - Response times
    - Success rates
    - Agent status (active/idle)
    - Overall system health
    
    **Parameters:**
    - period_hours: Time period to analyze (1-168 hours, default: 24)
    
    **Returns:**
    - List of agents with detailed metrics
    - Total tasks and completions
    - System health score (0-100)
    
    **Example Response:**
    ```json
    {
        "agents": [
            {
                "id": "alex",
                "name": "Alex",
                "role": "Patient Coordinator",
                "status": "active",
                "tasksToday": 24,
                "tasksCompleted": 18,
                "avgResponseTime": "2.3s",
                "successRate": 94
            }
        ],
        "totalTasks": 65,
        "totalCompleted": 56,
        "systemHealth": 97
    }
    ```
    """
    try:
        org_id = str(membership.organization_id)
        
        metrics = await get_agent_activity_metrics(
            db=async_db,
            org_id=org_id,
            period_hours=period_hours
        )
        
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch agent activity: {str(e)}"
        )
