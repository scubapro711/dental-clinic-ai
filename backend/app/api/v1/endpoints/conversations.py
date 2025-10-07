"""
Conversations API endpoints for Mission Control Dashboard.

Provides real-time conversation monitoring and management for doctors.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_organization_id
from app.models.user import User
from app.models.conversation import Conversation, ConversationStatus, ConversationChannel
from app.models.message import Message, MessageRole
from pydantic import BaseModel

router = APIRouter(prefix="/conversations", tags=["Conversations"])


# ===== Schemas =====

class ActiveConversationResponse(BaseModel):
    """Active conversation summary for dashboard widget."""
    conversation_id: str
    patient_name: Optional[str]
    status: str
    last_message: str
    last_message_time: datetime
    message_count: int
    requires_handoff: bool
    escalation_level: Optional[str]
    agent_name: str
    
    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    """Detailed conversation for doctor review."""
    conversation_id: str
    patient_name: Optional[str]
    status: str
    channel: str
    created_at: datetime
    updated_at: datetime
    agent_name: str
    escalation_level: Optional[str]
    requires_handoff: bool
    messages: List[dict]
    
    class Config:
        from_attributes = True


class HandoffRequest(BaseModel):
    """Request to handoff conversation to doctor."""
    reason: Optional[str] = None


class HandoffResponse(BaseModel):
    """Response after handoff request."""
    success: bool
    message: str
    conversation_id: str


# ===== Endpoints =====

@router.get("/active", response_model=List[ActiveConversationResponse])
async def get_active_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all active conversations for the dashboard widget.
    
    Returns conversations that are:
    - Currently active (not closed)
    - From the last 24 hours
    - Ordered by most recent activity
    """
    # Demo mode: return mock conversations
    from datetime import datetime, timedelta
    import random
    
    mock_conversations = []
    patient_names = ["Sarah Johnson", "Michael Chen", "Emma Davis", "James Wilson", "Lisa Anderson"]
    topics = ["Appointment scheduling", "Tooth pain inquiry", "Insurance question", "Treatment follow-up", "Emergency consultation"]
    
    for i in range(8):  # 8 active conversations
        mock_conversations.append(ActiveConversationResponse(
            conversation_id=f"conv_{i+1}",
            patient_name=patient_names[i % len(patient_names)],
            last_message=topics[i % len(topics)],
            last_message_time=datetime.utcnow() - timedelta(minutes=random.randint(5, 120)),
            message_count=random.randint(3, 15),
            requires_handoff=i < 2,  # First 2 require handoff
            channel="web",
            status="active",
            escalation_level="normal" if i >= 2 else "urgent",
            agent_name="Alex"
        ))
    
    return mock_conversations
    
    # Original code (commented out for demo):
    # if not current_user.organization_id:
    #     return []
    
    # Query active conversations from last 24 hours
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    
    conversations = db.query(Conversation).filter(
        and_(
            Conversation.organization_id == current_user.organization_id,
            Conversation.status == ConversationStatus.ACTIVE,
            Conversation.updated_at >= cutoff_time
        )
    ).order_by(Conversation.updated_at.desc()).limit(50).all()
    
    # Build response with last message for each conversation
    results = []
    for conv in conversations:
        # Get last message
        last_message = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(Message.created_at.desc()).first()
        
        # Get message count
        message_count = db.query(func.count(Message.id)).filter(
            Message.conversation_id == conv.id
        ).scalar()
        
        # Determine if handoff is required
        requires_handoff = (
            conv.status == ConversationStatus.WAITING or
            conv.escalation_level in ["EMERGENCY", "DOCTOR_REQUIRED"]
        )
        
        results.append(ActiveConversationResponse(
            conversation_id=str(conv.id),
            patient_name=conv.patient_name or "Unknown Patient",
            status=conv.status.value if hasattr(conv.status, 'value') else str(conv.status),
            last_message=last_message.content[:100] if last_message else "No messages",
            last_message_time=last_message.created_at if last_message else conv.created_at,
            message_count=message_count or 0,
            requires_handoff=requires_handoff,
            escalation_level=conv.escalation_level,
            agent_name=conv.primary_agent or "alex",
        ))
    
    return results


@router.get("/{conversation_id}/details", response_model=ConversationDetailResponse)
async def get_conversation_details(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed conversation information including full message history.
    
    Used when doctor clicks on a conversation to review it.
    """
    # Get conversation
    conversation = db.query(Conversation).filter(
        and_(
            Conversation.id == conversation_id,
            Conversation.organization_id == current_user.organization_id
        )
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get all messages
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    # Format messages
    formatted_messages = [
        {
            "id": str(msg.id),
            "role": msg.role.value if hasattr(msg.role, 'value') else str(msg.role),
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
            "agent_name": msg.agent_name,
        }
        for msg in messages
    ]
    
    # Determine if handoff is required
    requires_handoff = (
        conversation.status == ConversationStatus.WAITING or
        conversation.escalation_level in ["EMERGENCY", "DOCTOR_REQUIRED"]
    )
    
    return ConversationDetailResponse(
        conversation_id=str(conversation.id),
        patient_name=conversation.patient_name or "Unknown Patient",
        status=conversation.status.value if hasattr(conversation.status, 'value') else str(conversation.status),
        channel=conversation.channel.value if hasattr(conversation.channel, 'value') else str(conversation.channel),
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        agent_name=conversation.primary_agent or "alex",
        escalation_level=conversation.escalation_level,
        requires_handoff=requires_handoff,
        messages=formatted_messages,
    )


@router.post("/{conversation_id}/handoff", response_model=HandoffResponse)
async def request_conversation_handoff(
    conversation_id: str,
    request: HandoffRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Request human handoff for a conversation.
    
    This marks the conversation as waiting for doctor review.
    """
    # Get conversation
    conversation = db.query(Conversation).filter(
        and_(
            Conversation.id == conversation_id,
            Conversation.organization_id == current_user.organization_id
        )
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Update conversation status
    conversation.status = ConversationStatus.WAITING
    conversation.escalation_level = "DOCTOR_REQUIRED"
    conversation.updated_at = datetime.utcnow()
    
    # Add system message about handoff
    handoff_message = Message(
        conversation_id=conversation.id,
        organization_id=current_user.organization_id,
        role=MessageRole.SYSTEM,
        content=f"🔔 Handoff requested by {current_user.full_name or current_user.email}. Reason: {request.reason or 'Doctor review needed'}",
        agent_name="system",
    )
    db.add(handoff_message)
    
    db.commit()
    
    return HandoffResponse(
        success=True,
        message="Conversation marked for doctor review",
        conversation_id=str(conversation.id)
    )


@router.post("/{conversation_id}/takeover", response_model=HandoffResponse)
async def doctor_takeover_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Doctor takes over a conversation from AI agent.
    
    This changes the conversation to human-handled mode.
    """
    # Get conversation
    conversation = db.query(Conversation).filter(
        and_(
            Conversation.id == conversation_id,
            Conversation.organization_id == current_user.organization_id
        )
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Update conversation to human-handled
    conversation.status = ConversationStatus.ACTIVE
    conversation.escalation_level = "HUMAN_HANDLING"
    conversation.updated_at = datetime.utcnow()
    
    # Add system message about takeover
    takeover_message = Message(
        conversation_id=conversation.id,
        organization_id=current_user.organization_id,
        role=MessageRole.SYSTEM,
        content=f"👨‍⚕️ Dr. {current_user.full_name or current_user.email} has taken over this conversation.",
        agent_name="system",
    )
    db.add(takeover_message)
    
    db.commit()
    
    return HandoffResponse(
        success=True,
        message="You are now handling this conversation",
        conversation_id=str(conversation.id)
    )


@router.get("/stats", response_model=dict)
async def get_conversation_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get conversation statistics for the dashboard.
    
    Returns:
    - Active conversations count
    - Total conversations today
    - Conversations requiring handoff
    - Average response time
    """
    if not current_user.organization_id:
        return {
            "active_count": 0,
            "today_count": 0,
            "handoff_required": 0,
            "avg_response_time_seconds": 0,
        }
    
    # Active conversations
    active_count = db.query(func.count(Conversation.id)).filter(
        and_(
            Conversation.organization_id == current_user.organization_id,
            Conversation.status == ConversationStatus.ACTIVE
        )
    ).scalar() or 0
    
    # Today's conversations
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = db.query(func.count(Conversation.id)).filter(
        and_(
            Conversation.organization_id == current_user.organization_id,
            Conversation.created_at >= today_start
        )
    ).scalar() or 0
    
    # Conversations requiring handoff
    handoff_count = db.query(func.count(Conversation.id)).filter(
        and_(
            Conversation.organization_id == current_user.organization_id,
            Conversation.status == ConversationStatus.WAITING
        )
    ).scalar() or 0
    
    return {
        "active_count": active_count,
        "today_count": today_count,
        "handoff_required": handoff_count,
        "avg_response_time_seconds": 2.3,  # TODO: Calculate from actual data
    }
