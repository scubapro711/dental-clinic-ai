"""
Decision Queue API Endpoints.

Provides endpoints for managing proactive suggestions and decisions.
Part of the agentic/proactive experience.

Endpoints:
- GET /decision-queue - List pending suggestions with filtering
- GET /decision-queue/{id} - Get suggestion details
- POST /decision-queue/{id}/approve - Approve suggestion
- POST /decision-queue/{id}/reject - Reject suggestion
- POST /decision-queue/{id}/feedback - Provide learning feedback
- GET /decision-queue/stats - Get queue statistics
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.proactive_suggestion import (
    ProactiveSuggestion,
    SuggestionPriority,
    SuggestionStatus,
    SuggestionCategory
)
from pydantic import BaseModel, Field


router = APIRouter()


# Pydantic schemas

class SuggestionFilter(BaseModel):
    """Filter parameters for suggestions."""
    agent_name: Optional[str] = None
    category: Optional[SuggestionCategory] = None
    priority: Optional[SuggestionPriority] = None
    status: Optional[SuggestionStatus] = None
    include_expired: bool = False


class SuggestionResponse(BaseModel):
    """Suggestion response model."""
    id: str
    organization_id: str
    agent_name: str
    title: str
    message: str
    category: str
    priority: str
    status: str
    actions: Optional[List[dict]] = None
    metadata: Optional[dict] = None
    confidence: Optional[int] = None
    patient_id: Optional[str] = None
    appointment_id: Optional[str] = None
    conversation_id: Optional[str] = None
    decided_by: Optional[str] = None
    decided_at: Optional[str] = None
    decision_notes: Optional[str] = None
    executed: bool
    executed_at: Optional[str] = None
    execution_result: Optional[dict] = None
    feedback_provided: bool
    feedback_rating: Optional[int] = None
    feedback_notes: Optional[str] = None
    created_at: str
    updated_at: str
    expires_at: Optional[str] = None
    is_expired: bool
    age_hours: float


class DecisionRequest(BaseModel):
    """Decision request model."""
    notes: Optional[str] = Field(None, description="Optional notes about the decision")


class FeedbackRequest(BaseModel):
    """Feedback request model."""
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5 stars")
    notes: Optional[str] = Field(None, description="Optional feedback notes")


class QueueStats(BaseModel):
    """Decision queue statistics."""
    total_pending: int
    by_priority: dict
    by_agent: dict
    by_category: dict
    avg_age_hours: float
    oldest_pending_hours: float


# Endpoints

@router.get(
    "/",
    response_model=List[SuggestionResponse],
    tags=["Decision Queue"],
    summary="List proactive suggestions",
    description="""
    Get a list of proactive suggestions from AI agents.
    
    **Features:**
    - Filter by agent, category, priority, status
    - Pagination support
    - Sorted by priority and age
    - Organization-scoped
    
    **Authentication:** Requires valid JWT token
    
    **Example Response:**
    ```json
    [
      {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "agent_name": "alex",
        "title": "3 patients need appointment confirmation",
        "message": "I noticed 3 patients haven't confirmed tomorrow's appointments...",
        "category": "appointment",
        "priority": "high",
        "status": "pending",
        "confidence": 95,
        "actions": [
          {"label": "Send Reminders", "action": "send_reminders"}
        ]
      }
    ]
    ```
    """,
    responses={
        200: {"description": "List of suggestions"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def list_suggestions(
    agent_name: Optional[str] = Query(None, description="Filter by agent name (alex, marcus, sarah, sophia)"),
    category: Optional[SuggestionCategory] = Query(None, description="Filter by category"),
    priority: Optional[SuggestionPriority] = Query(None, description="Filter by priority"),
    status: Optional[SuggestionStatus] = Query(SuggestionStatus.PENDING, description="Filter by status"),
    include_expired: bool = Query(False, description="Include expired suggestions"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List proactive suggestions with filtering.
    
    Returns suggestions for the current user's organization, sorted by priority and age.
    """
    # Build query
    query = db.query(ProactiveSuggestion).filter(
        ProactiveSuggestion.organization_id == current_user.organization_id
    )
    
    # Apply filters
    if agent_name:
        query = query.filter(ProactiveSuggestion.agent_name == agent_name)
    
    if category:
        query = query.filter(ProactiveSuggestion.category == category)
    
    if priority:
        query = query.filter(ProactiveSuggestion.priority == priority)
    
    if status:
        query = query.filter(ProactiveSuggestion.status == status)
    
    if not include_expired:
        query = query.filter(
            (ProactiveSuggestion.expires_at == None) | 
            (ProactiveSuggestion.expires_at > datetime.utcnow())
        )
    
    # Order by priority (urgent first) and age (oldest first)
    priority_order = {
        SuggestionPriority.URGENT: 4,
        SuggestionPriority.HIGH: 3,
        SuggestionPriority.MEDIUM: 2,
        SuggestionPriority.LOW: 1
    }
    
    # Get results
    suggestions = query.order_by(
        ProactiveSuggestion.created_at.asc()
    ).offset(offset).limit(limit).all()
    
    # Sort by priority in Python (SQLite doesn't support CASE)
    suggestions.sort(
        key=lambda s: (priority_order.get(s.priority, 0), -s.age_hours),
        reverse=True
    )
    
    # Convert to response
    return [
        SuggestionResponse(
            **s.to_dict(),
            is_expired=s.is_expired,
            age_hours=s.age_hours
        )
        for s in suggestions
    ]


@router.get("/{suggestion_id}", response_model=SuggestionResponse)
async def get_suggestion(
    suggestion_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get suggestion details by ID."""
    suggestion = db.query(ProactiveSuggestion).filter(
        ProactiveSuggestion.id == suggestion_id,
        ProactiveSuggestion.organization_id == current_user.organization_id
    ).first()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    return SuggestionResponse(
        **suggestion.to_dict(),
        is_expired=suggestion.is_expired,
        age_hours=suggestion.age_hours
    )


@router.post(
    "/{suggestion_id}/approve",
    response_model=SuggestionResponse,
    tags=["Decision Queue"],
    summary="Approve a suggestion",
    description="""
    Approve a proactive suggestion from an AI agent.
    
    This marks the suggestion as approved and optionally executes the suggested action.
    
    **Authentication:** Requires valid JWT token
    
    **Example Request:**
    ```json
    {
      "notes": "Good idea, let's send those reminders"
    }
    ```
    """,
    responses={
        200: {"description": "Suggestion approved successfully"},
        404: {"description": "Suggestion not found"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def approve_suggestion(
    suggestion_id: UUID,
    request: DecisionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve a suggestion.
    
    Marks the suggestion as approved and triggers execution.
    """
    suggestion = db.query(ProactiveSuggestion).filter(
        ProactiveSuggestion.id == suggestion_id,
        ProactiveSuggestion.organization_id == current_user.organization_id
    ).first()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    if suggestion.status != SuggestionStatus.PENDING:
        raise HTTPException(status_code=400, detail="Suggestion is not pending")
    
    if suggestion.is_expired:
        raise HTTPException(status_code=400, detail="Suggestion has expired")
    
    # Update suggestion
    suggestion.status = SuggestionStatus.APPROVED
    suggestion.decided_by = current_user.id
    suggestion.decided_at = datetime.utcnow()
    suggestion.decision_notes = request.notes
    
    db.commit()
    db.refresh(suggestion)
    
    # TODO: Trigger execution asynchronously
    # execute_suggestion_async(suggestion_id)
    
    return SuggestionResponse(
        **suggestion.to_dict(),
        is_expired=suggestion.is_expired,
        age_hours=suggestion.age_hours
    )


@router.post("/{suggestion_id}/reject", response_model=SuggestionResponse)
async def reject_suggestion(
    suggestion_id: UUID,
    request: DecisionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject a suggestion.
    
    Marks the suggestion as rejected and provides learning feedback to the agent.
    """
    suggestion = db.query(ProactiveSuggestion).filter(
        ProactiveSuggestion.id == suggestion_id,
        ProactiveSuggestion.organization_id == current_user.organization_id
    ).first()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    if suggestion.status != SuggestionStatus.PENDING:
        raise HTTPException(status_code=400, detail="Suggestion is not pending")
    
    # Update suggestion
    suggestion.status = SuggestionStatus.REJECTED
    suggestion.decided_by = current_user.id
    suggestion.decided_at = datetime.utcnow()
    suggestion.decision_notes = request.notes
    
    db.commit()
    db.refresh(suggestion)
    
    # TODO: Send feedback to agent for learning
    # send_rejection_feedback(suggestion)
    
    return SuggestionResponse(
        **suggestion.to_dict(),
        is_expired=suggestion.is_expired,
        age_hours=suggestion.age_hours
    )


@router.post("/{suggestion_id}/feedback", response_model=SuggestionResponse)
async def provide_feedback(
    suggestion_id: UUID,
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Provide learning feedback on a suggestion.
    
    Helps the agent learn and improve future suggestions.
    """
    suggestion = db.query(ProactiveSuggestion).filter(
        ProactiveSuggestion.id == suggestion_id,
        ProactiveSuggestion.organization_id == current_user.organization_id
    ).first()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    # Update feedback
    suggestion.feedback_provided = True
    suggestion.feedback_rating = request.rating
    suggestion.feedback_notes = request.notes
    
    db.commit()
    db.refresh(suggestion)
    
    # TODO: Send feedback to agent for fine-tuning
    # send_learning_feedback(suggestion)
    
    return SuggestionResponse(
        **suggestion.to_dict(),
        is_expired=suggestion.is_expired,
        age_hours=suggestion.age_hours
    )


@router.get("/stats/overview", response_model=QueueStats)
async def get_queue_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Decision Queue statistics.
    
    Provides overview of pending suggestions by priority, agent, and category.
    """
    # Get all pending suggestions
    pending = db.query(ProactiveSuggestion).filter(
        ProactiveSuggestion.organization_id == current_user.organization_id,
        ProactiveSuggestion.status == SuggestionStatus.PENDING,
        (ProactiveSuggestion.expires_at == None) | 
        (ProactiveSuggestion.expires_at > datetime.utcnow())
    ).all()
    
    if not pending:
        return QueueStats(
            total_pending=0,
            by_priority={},
            by_agent={},
            by_category={},
            avg_age_hours=0,
            oldest_pending_hours=0
        )
    
    # Calculate stats
    by_priority = {}
    by_agent = {}
    by_category = {}
    total_age = 0
    oldest_age = 0
    
    for s in pending:
        # By priority
        by_priority[s.priority.value] = by_priority.get(s.priority.value, 0) + 1
        
        # By agent
        by_agent[s.agent_name] = by_agent.get(s.agent_name, 0) + 1
        
        # By category
        by_category[s.category.value] = by_category.get(s.category.value, 0) + 1
        
        # Age
        age = s.age_hours
        total_age += age
        if age > oldest_age:
            oldest_age = age
    
    return QueueStats(
        total_pending=len(pending),
        by_priority=by_priority,
        by_agent=by_agent,
        by_category=by_category,
        avg_age_hours=total_age / len(pending) if pending else 0,
        oldest_pending_hours=oldest_age
    )

