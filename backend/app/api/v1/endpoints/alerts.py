"""
Alerts API - Aggregate alerts from all agents

Provides unified alert management for the Mission Control dashboard.
Aggregates alerts from Alex, Marcus, and Sophia agents.

Architecture: Widget → API → Database (aggregate from all agents)
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from enum import Enum

from app.api.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# ===== Enums =====

class AlertPriority(str, Enum):
    """Alert priority levels."""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class AlertSource(str, Enum):
    """Alert source agents."""
    ALEX = "alex"
    MARCUS = "marcus"
    SOPHIA = "sophia"
    SYSTEM = "system"


class AlertStatus(str, Enum):
    """Alert status."""
    ACTIVE = "active"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"


# ===== Schemas =====

class Alert(BaseModel):
    """Alert model."""
    id: str
    source: AlertSource
    priority: AlertPriority
    status: AlertStatus
    title: str
    message: str
    created_at: str
    updated_at: str
    action_url: str | None = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class AlertActionResponse(BaseModel):
    """Response after alert action."""
    success: bool
    message: str
    alert_id: str
    new_status: AlertStatus


# ===== Endpoints =====

@router.get("/active", response_model=List[Alert])
async def get_active_alerts(
    current_user: User = Depends(get_current_user),
    source: AlertSource | None = None,
    priority: AlertPriority | None = None,
):
    """
    Get active alerts from all agents.
    
    Args:
        source: Filter by alert source (alex, marcus, sophia, system)
        priority: Filter by priority (urgent, high, normal, low)
        
    Returns:
        List of active alerts
    """
    try:
        # Mock alerts from different agents
        # TODO: Replace with real alert aggregation from database
        
        now = datetime.utcnow()
        
        # Alex alerts (patient-related)
        alex_alerts = [
            Alert(
                id="alert_alex_1",
                source=AlertSource.ALEX,
                priority=AlertPriority.URGENT,
                status=AlertStatus.ACTIVE,
                title="Patient Escalation",
                message="John Doe reported severe tooth pain. Requires immediate attention.",
                created_at=(now - timedelta(minutes=5)).isoformat(),
                updated_at=(now - timedelta(minutes=5)).isoformat(),
                action_url="/conversations/conv_123",
                metadata={"conversation_id": "conv_123", "patient_id": "patient_001"}
            ),
            Alert(
                id="alert_alex_2",
                source=AlertSource.ALEX,
                priority=AlertPriority.HIGH,
                status=AlertStatus.ACTIVE,
                title="Appointment Confirmation Needed",
                message="3 appointments tomorrow need confirmation.",
                created_at=(now - timedelta(hours=2)).isoformat(),
                updated_at=(now - timedelta(hours=2)).isoformat(),
                action_url="/appointments",
                metadata={"count": 3}
            ),
        ]
        
        # Marcus alerts (financial)
        marcus_alerts = [
            Alert(
                id="alert_marcus_1",
                source=AlertSource.MARCUS,
                priority=AlertPriority.HIGH,
                status=AlertStatus.ACTIVE,
                title="Outstanding Payments",
                message="15 invoices overdue by more than 30 days. Total: $8,450.",
                created_at=(now - timedelta(hours=1)).isoformat(),
                updated_at=(now - timedelta(hours=1)).isoformat(),
                action_url="/analytics",
                metadata={"count": 15, "total_amount": 8450}
            ),
            Alert(
                id="alert_marcus_2",
                source=AlertSource.MARCUS,
                priority=AlertPriority.NORMAL,
                status=AlertStatus.ACTIVE,
                title="Revenue Below Target",
                message="This week's revenue is 15% below target. Consider reviewing pricing.",
                created_at=(now - timedelta(hours=3)).isoformat(),
                updated_at=(now - timedelta(hours=3)).isoformat(),
                action_url="/analytics",
                metadata={"variance": -15}
            ),
        ]
        
        # Sophia alerts (operations)
        sophia_alerts = [
            Alert(
                id="alert_sophia_1",
                source=AlertSource.SOPHIA,
                priority=AlertPriority.URGENT,
                status=AlertStatus.ACTIVE,
                title="Scheduling Conflict",
                message="Double booking detected for Dr. Smith at 2:00 PM today.",
                created_at=(now - timedelta(minutes=15)).isoformat(),
                updated_at=(now - timedelta(minutes=15)).isoformat(),
                action_url="/appointments",
                metadata={"doctor": "Dr. Smith", "time": "14:00"}
            ),
            Alert(
                id="alert_sophia_2",
                source=AlertSource.SOPHIA,
                priority=AlertPriority.NORMAL,
                status=AlertStatus.ACTIVE,
                title="High No-Show Rate",
                message="No-show rate this week is 12% (above 10% threshold).",
                created_at=(now - timedelta(hours=4)).isoformat(),
                updated_at=(now - timedelta(hours=4)).isoformat(),
                action_url="/appointments",
                metadata={"rate": 12}
            ),
        ]
        
        # Combine all alerts
        all_alerts = alex_alerts + marcus_alerts + sophia_alerts
        
        # Filter by source if specified
        if source:
            all_alerts = [a for a in all_alerts if a.source == source]
        
        # Filter by priority if specified
        if priority:
            all_alerts = [a for a in all_alerts if a.priority == priority]
        
        # Sort by priority (urgent first) and then by created_at (newest first)
        priority_order = {
            AlertPriority.URGENT: 0,
            AlertPriority.HIGH: 1,
            AlertPriority.NORMAL: 2,
            AlertPriority.LOW: 3,
        }
        all_alerts.sort(key=lambda x: (priority_order[x.priority], x.created_at), reverse=True)
        
        logger.info(f"Retrieved {len(all_alerts)} active alerts")
        return all_alerts
        
    except Exception as e:
        logger.error(f"Error getting active alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alerts: {str(e)}"
        )


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific alert by ID.
    
    Args:
        alert_id: Alert ID
    """
    # Get all alerts and find the one with matching ID
    all_alerts = await get_active_alerts(current_user)
    alert = next((a for a in all_alerts if a.id == alert_id), None)
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{alert_id}' not found"
        )
    
    return alert


@router.post("/{alert_id}/dismiss", response_model=AlertActionResponse)
async def dismiss_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Dismiss an alert (hide it without resolving).
    
    Args:
        alert_id: Alert ID to dismiss
    """
    try:
        # TODO: Update alert status in database
        logger.info(f"Alert '{alert_id}' dismissed by user {current_user.id}")
        
        return AlertActionResponse(
            success=True,
            message=f"Alert '{alert_id}' has been dismissed",
            alert_id=alert_id,
            new_status=AlertStatus.DISMISSED
        )
        
    except Exception as e:
        logger.error(f"Error dismissing alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to dismiss alert: {str(e)}"
        )


@router.post("/{alert_id}/resolve", response_model=AlertActionResponse)
async def resolve_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Resolve an alert (mark as handled).
    
    Args:
        alert_id: Alert ID to resolve
    """
    try:
        # TODO: Update alert status in database
        logger.info(f"Alert '{alert_id}' resolved by user {current_user.id}")
        
        return AlertActionResponse(
            success=True,
            message=f"Alert '{alert_id}' has been resolved",
            alert_id=alert_id,
            new_status=AlertStatus.RESOLVED
        )
        
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve alert: {str(e)}"
        )


@router.get("/stats/summary", response_model=Dict[str, Any])
async def get_alerts_summary(
    current_user: User = Depends(get_current_user),
):
    """
    Get alert statistics summary.
    
    Returns:
        Summary of alerts by source, priority, and status
    """
    try:
        all_alerts = await get_active_alerts(current_user)
        
        # Count by source
        by_source = {}
        for source in AlertSource:
            by_source[source.value] = len([a for a in all_alerts if a.source == source])
        
        # Count by priority
        by_priority = {}
        for priority in AlertPriority:
            by_priority[priority.value] = len([a for a in all_alerts if a.priority == priority])
        
        return {
            "total_active": len(all_alerts),
            "by_source": by_source,
            "by_priority": by_priority,
            "urgent_count": by_priority.get("urgent", 0),
            "last_updated": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error getting alerts summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alerts summary: {str(e)}"
        )
