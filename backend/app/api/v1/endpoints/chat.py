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
from app.models.message import Message, MessageRole
from app.schemas.conversation import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessages,
    MessageResponse,
)
from app.agents.agent_graph import AgentGraphV2

router = APIRouter(prefix="/chat", tags=["Chat"])

# Initialize Alex agent graph
agent_graph = AgentGraphV2()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a message to Alex AI agent and get a response.
    
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
            primary_agent="alex",
            langgraph_thread_id=str(uuid4()),
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Save user message to database
    user_message = Message(
        conversation_id=conversation.id,
        organization_id=current_user.organization_id,
        role=MessageRole.USER,
        content=request.message,
    )
    db.add(user_message)
    db.commit()
    
    # Process message with Alex agent graph
    try:
        result = await agent_graph.process_message(
            user_id=str(current_user.id),
            organization_id=str(current_user.organization_id),
            conversation_id=str(conversation.id),
            message=request.message,
        )
        
        # Save AI response to database
        ai_message = Message(
            conversation_id=conversation.id,
            organization_id=current_user.organization_id,
            role=MessageRole.ASSISTANT,
            content=result["response"],
            agent_name="alex",
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
        
        return ChatResponse(
            conversation_id=conversation.id,
            message_id=ai_message.id,
            response=result["response"],
            agent="alex",
            requires_human=result.get("escalation_level") in ["EMERGENCY", "DOCTOR_REQUIRED"],
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
