"""
Decisions API Endpoints

Provides endpoints for managing pending decisions that require approval.
Decisions are extracted from LangGraph checkpoints where agents have flagged
items that need human review.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_async_db
from app.core.auth import get_current_membership
from app.models.user import OrganizationMembership
from app.shared.checkpoint_queries import (
    get_pending_decisions,
    approve_decision,
    reject_decision
)

router = APIRouter()


class Decision(BaseModel):
    """Pending decision model - Enhanced with context and AI metadata"""
    # Core fields
    id: str
    thread_id: str
    agent: str
    
    # Content
    title: str
    description: str
    action: str
    
    # Classification
    priority: str  # critical, high, medium, low
    category: Optional[str] = "operational"  # clinical, operational, financial, compliance
    
    # AI Metadata
    confidence: Optional[int] = None  # 0-100
    reasoning: Optional[str] = None
    
    # Context
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    
    # Impact
    impact_level: Optional[str] = "medium"  # high, medium, low
    compliance_risk: Optional[bool] = None
    
    # Timing
    timestamp: str
    due_by: Optional[str] = None


class ApprovalRequest(BaseModel):
    """Request to approve a decision"""
    execute: bool = True
    reason: Optional[str] = "Approved by user"


class RejectionRequest(BaseModel):
    """Request to reject a decision"""
    reason: Optional[str] = "Rejected by user"


class ApprovalResponse(BaseModel):
    """Response after approval/rejection"""
    success: bool
    message: str
    decision_id: str


@router.get("/pending", response_model=List[Decision])
async def get_pending_decisions_endpoint(
    membership: OrganizationMembership = Depends(get_current_membership),
    async_db: AsyncSession = Depends(get_async_db),
    limit: int = Query(default=10, ge=1, le=100, description="Maximum number of decisions to return")
):
    """
    Get pending decisions that require approval.
    
    Extracts decisions from agent checkpoints where:
    - requires_approval = true
    - approval_status = pending
    
    Decisions are sorted by priority (high → medium → low) and timestamp.
    
    **Returns:**
    - List of pending decisions with agent, title, description, action, priority
    
    **Example Response:**
    ```json
    [
        {
            "id": "thread_123_cp_456",
            "thread_id": "thread_123",
            "agent": "alex",
            "title": "3 patients waiting for appointment confirmation",
            "description": "Alex identified 3 patients who haven't confirmed",
            "action": "Call patients",
            "priority": "high",
            "timestamp": "2025-11-12T08:00:00Z"
        }
    ]
    ```
    """
    try:
        org_id = str(membership.organization_id)
        
        decisions = await get_pending_decisions(
            db=async_db,
            org_id=org_id,
            limit=limit
        )
        
        return decisions
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch pending decisions: {str(e)}"
        )


@router.post("/{decision_id}/approve", response_model=ApprovalResponse)
async def approve_decision_endpoint(
    decision_id: str,
    request: ApprovalRequest,
    membership: OrganizationMembership = Depends(get_current_membership),
    async_db: AsyncSession = Depends(get_async_db)
):
    """
    Approve a pending decision.
    
    Updates the checkpoint to mark the decision as approved.
    If execute=true, the agent will proceed with the action.
    
    **Parameters:**
    - decision_id: Decision ID (format: thread_id_checkpoint_id)
    - execute: Whether to execute the action (default: true)
    - reason: Approval reason (optional)
    
    **Returns:**
    - Success status and message
    
    **Example Request:**
    ```json
    {
        "execute": true,
        "reason": "Approved - proceed with action"
    }
    ```
    """
    try:
        org_id = str(membership.organization_id)
        
        success = await approve_decision(
            db=async_db,
            decision_id=decision_id,
            org_id=org_id,
            reason=request.reason
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Decision not found or already processed"
            )
        
        return ApprovalResponse(
            success=True,
            message=f"Decision approved: {decision_id}",
            decision_id=decision_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to approve decision: {str(e)}"
        )


@router.post("/{decision_id}/reject", response_model=ApprovalResponse)
async def reject_decision_endpoint(
    decision_id: str,
    request: RejectionRequest,
    membership: OrganizationMembership = Depends(get_current_membership),
    async_db: AsyncSession = Depends(get_async_db)
):
    """
    Reject a pending decision.
    
    Updates the checkpoint to mark the decision as rejected.
    The agent will not proceed with the action.
    
    **Parameters:**
    - decision_id: Decision ID (format: thread_id_checkpoint_id)
    - reason: Rejection reason (optional)
    
    **Returns:**
    - Success status and message
    
    **Example Request:**
    ```json
    {
        "reason": "Not needed at this time"
    }
    ```
    """
    try:
        org_id = str(membership.organization_id)
        
        success = await reject_decision(
            db=async_db,
            decision_id=decision_id,
            org_id=org_id,
            reason=request.reason
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Decision not found or already processed"
            )
        
        return ApprovalResponse(
            success=True,
            message=f"Decision rejected: {decision_id}",
            decision_id=decision_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reject decision: {str(e)}"
        )
