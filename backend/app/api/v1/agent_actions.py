"""
Agent Actions API Endpoints

Provides agent decision queue and action approval/rejection
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import logging

from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


class AgentAction(BaseModel):
    """Agent action model"""
    id: int
    priority: str  # high, medium, low
    agent: str  # alex, marcus, sophia
    title: str
    description: str
    action: str
    timestamp: datetime
    status: str = "pending"  # pending, approved, rejected
    metadata: Optional[dict] = None


class ActionApproval(BaseModel):
    """Action approval request"""
    reason: Optional[str] = None
    execute: bool = True


class ActionRejection(BaseModel):
    """Action rejection request"""
    reason: Optional[str] = None


@router.get("/queue", response_model=List[AgentAction])
async def get_decision_queue(
    status: str = "pending",
    x_organization_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get pending agent actions that need human approval
    
    Returns list of actions organized by priority
    """
    try:
        # TODO: Query from database when agent_actions table is created
        # For now, return mock data with realistic scenarios
        
        mock_actions = [
            {
                "id": 1,
                "priority": "high",
                "agent": "alex",
                "title": "3 מטופלים ממתינים לאישור תור",
                "description": "Alex זיהה 3 מטופלים שלא אישרו תור - צריך להתקשר",
                "action": "התקשר למטופלים",
                "timestamp": datetime.now(),
                "status": "pending",
                "metadata": {
                    "patient_ids": [1, 2, 3],
                    "appointment_ids": [10, 11, 12],
                    "phone_numbers": ["050-1234567", "050-2345678", "050-3456789"]
                }
            },
            {
                "id": 2,
                "priority": "medium",
                "agent": "marcus",
                "title": "₪5,000 חובות לא נגבו",
                "description": "Marcus מצא 5 חשבונות פתוחים מעל 30 יום - צריך להחליט על תזכורות",
                "action": "שלח תזכורות",
                "timestamp": datetime.now(),
                "status": "pending",
                "metadata": {
                    "invoice_ids": [101, 102, 103, 104, 105],
                    "total_amount": 5000,
                    "oldest_invoice_days": 45
                }
            },
            {
                "id": 3,
                "priority": "low",
                "agent": "sophia",
                "title": "קונפליקט בלוח הזמנים",
                "description": "Sophia מצאה חפיפה בין 2 תורים ביום חמישי - צריך לבחור מי לשנות",
                "action": "פתור קונפליקט",
                "timestamp": datetime.now(),
                "status": "pending",
                "metadata": {
                    "appointment_id_1": 20,
                    "appointment_id_2": 21,
                    "conflict_date": "2025-10-10",
                    "conflict_time": "14:00"
                }
            },
            {
                "id": 4,
                "priority": "medium",
                "agent": "alex",
                "title": "מטופל חדש עם היסטוריה רפואית מורכבת",
                "description": "Alex ממליץ לקרוא את ההיסטוריה לפני הביקור הראשון מחר",
                "action": "סקור היסטוריה",
                "timestamp": datetime.now(),
                "status": "pending",
                "metadata": {
                    "patient_id": 15,
                    "appointment_id": 25,
                    "medical_history_url": "/patients/15/history",
                    "appointment_date": "2025-10-09"
                }
            }
        ]
        
        # Filter by status
        if status != "all":
            mock_actions = [a for a in mock_actions if a["status"] == status]
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        mock_actions.sort(key=lambda x: priority_order.get(x["priority"], 999))
        
        logger.info(f"Retrieved {len(mock_actions)} agent actions with status={status}")
        return mock_actions
        
    except Exception as e:
        logger.error(f"Error fetching decision queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{action_id}/approve")
async def approve_action(
    action_id: int,
    approval: ActionApproval,
    x_organization_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Approve an agent action
    
    If execute=True, the action will be executed immediately
    """
    try:
        # TODO: Update database and execute action
        logger.info(f"Action {action_id} approved. Execute: {approval.execute}, Reason: {approval.reason}")
        
        # Mock execution
        if approval.execute:
            # Here we would call the appropriate agent tool
            # For now, just log it
            logger.info(f"Executing action {action_id}...")
        
        return {
            "success": True,
            "action_id": action_id,
            "status": "approved",
            "executed": approval.execute,
            "message": "פעולה אושרה בהצלחה" + (" ובוצעה" if approval.execute else "")
        }
        
    except Exception as e:
        logger.error(f"Error approving action {action_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{action_id}/reject")
async def reject_action(
    action_id: int,
    rejection: ActionRejection,
    x_organization_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Reject an agent action
    """
    try:
        # TODO: Update database
        logger.info(f"Action {action_id} rejected. Reason: {rejection.reason}")
        
        return {
            "success": True,
            "action_id": action_id,
            "status": "rejected",
            "message": "פעולה נדחתה"
        }
        
    except Exception as e:
        logger.error(f"Error rejecting action {action_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{action_id}")
async def get_action(
    action_id: int,
    x_organization_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get specific action details
    """
    try:
        # TODO: Query from database
        # For now, return mock data
        
        mock_action = {
            "id": action_id,
            "priority": "high",
            "agent": "alex",
            "title": "Sample Action",
            "description": "This is a sample action",
            "action": "Do something",
            "timestamp": datetime.now(),
            "status": "pending",
            "metadata": {}
        }
        
        return mock_action
        
    except Exception as e:
        logger.error(f"Error fetching action {action_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_action_stats(
    x_organization_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get statistics about agent actions
    """
    try:
        # TODO: Calculate from database
        
        return {
            "total_pending": 4,
            "high_priority": 1,
            "medium_priority": 2,
            "low_priority": 1,
            "approved_today": 12,
            "rejected_today": 3,
            "avg_response_time_minutes": 15
        }
        
    except Exception as e:
        logger.error(f"Error fetching action stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
