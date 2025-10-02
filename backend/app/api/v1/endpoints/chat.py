"""
Chat API endpoints for AI agent conversations.
"""

from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_organization_id
from app.models.user import User
from app.models.conversation import Conversation, ConversationStatus, ConversationChannel
from app.models.message import Message
from app.schemas.conversation import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessages,
    MessageResponse,
)
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/chat", tags=["Chat"])

# Initialize orchestrator
orchestrator = AgentOrchestrator()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a message to AI agents and get a response.
    
    If conversation_id is not provided, a new conversation will be created.
    """
    # Ensure user has an organization
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization to chat",
        )
    
    # Get or create conversation
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.organization_id == current_user.organization_id,
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
    else:
        # Create new conversation
        conversation = Conversation(
            organization_id=current_user.organization_id,
            channel=ConversationChannel.WEB_CHAT,
            status=ConversationStatus.ACTIVE,
            primary_agent="dana",
            langgraph_thread_id=str(uuid4()),
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Process message with orchestrator
    try:
        result = await orchestrator.process_message(
            db=db,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            conversation_id=conversation.id,
            message_content=request.message,
        )
        
        # Get the latest AI message ID
        latest_message = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at.desc()).first()
        
        return ChatResponse(
            conversation_id=conversation.id,
            message_id=latest_message.id,
            response=result["response"],
            agent=result["agent"],
            requires_human=result.get("requires_human", False),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}",
        )


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
):
    """
    List all conversations for the current user's organization.
    """
    if not current_user.organization_id:
        return []
    
    conversations = db.query(Conversation).filter(
        Conversation.organization_id == current_user.organization_id
    ).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()
    
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific conversation with all messages.
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.organization_id == current_user.organization_id,
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    # Get messages
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    return ConversationWithMessages(
        **conversation.__dict__,
        messages=[MessageResponse(**msg.__dict__) for msg in messages]
    )
