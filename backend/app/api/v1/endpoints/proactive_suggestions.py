"""
API endpoints for proactive suggestions.
"""

from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.proactive_suggestions import get_proactive_suggestions_service

router = APIRouter()


class SuggestionResponse(BaseModel):
    """Suggestion response model."""
    
    type: str
    priority: int
    title: str
    message: str
    actions: List[Dict[str, Any]]
    metadata: Dict[str, Any] = {}


class ExecuteActionRequest(BaseModel):
    """Execute action request model."""
    
    action: str
    data: Dict[str, Any] = {}


class ExecuteActionResponse(BaseModel):
    """Execute action response model."""
    
    success: bool
    message: str
    next_step: str = None
    data: Dict[str, Any] = {}


@router.get("/conversations/{conversation_id}/suggestions", response_model=List[SuggestionResponse])
def get_suggestions(
    conversation_id: UUID,
    limit: int = 3,
    db: Session = Depends(get_db)
):
    """
    Get proactive suggestions for conversation.
    
    Args:
        conversation_id: Conversation UUID
        limit: Maximum number of suggestions (default: 3)
        db: Database session
    
    Returns:
        List of suggestions
    """
    service = get_proactive_suggestions_service(db)
    
    suggestions = service.get_suggestions(
        conversation_id=conversation_id,
        limit=limit
    )
    
    return suggestions


@router.post("/conversations/{conversation_id}/suggestions/{suggestion_type}/dismiss")
def dismiss_suggestion(
    conversation_id: UUID,
    suggestion_type: str,
    db: Session = Depends(get_db)
):
    """
    Dismiss a suggestion.
    
    Args:
        conversation_id: Conversation UUID
        suggestion_type: Type of suggestion to dismiss
        db: Database session
    
    Returns:
        Success response
    """
    service = get_proactive_suggestions_service(db)
    
    success = service.dismiss_suggestion(
        conversation_id=conversation_id,
        suggestion_type=suggestion_type
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"success": True, "message": "Suggestion dismissed"}


@router.post("/conversations/{conversation_id}/suggestions/execute", response_model=ExecuteActionResponse)
def execute_suggestion_action(
    conversation_id: UUID,
    request: ExecuteActionRequest,
    db: Session = Depends(get_db)
):
    """
    Execute action from suggestion.
    
    Args:
        conversation_id: Conversation UUID
        request: Action request
        db: Database session
    
    Returns:
        Action result
    """
    service = get_proactive_suggestions_service(db)
    
    result = service.execute_suggestion_action(
        conversation_id=conversation_id,
        action=request.action,
        data=request.data
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Action failed"))
    
    return result
