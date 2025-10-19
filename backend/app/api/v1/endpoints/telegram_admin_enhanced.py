"""
Telegram Admin API Endpoints - Enhanced with Message Storage

Manage Telegram integration for clinic admins:
- Generate invite codes
- View Telegram users
- Link/unlink users
- View conversations
- Send and receive messages with full history

Reference: TELEGRAM_INTEGRATION_COMPLETE_SPEC.md
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, Field
import secrets
import string

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.telegram_user import TelegramUser, TelegramUserStatus
from app.models.telegram_invite_code import TelegramInviteCode, InviteCodeStatus
from app.models.telegram_conversation import TelegramConversation
from app.models.telegram_message import TelegramMessage, MessageDirection

router = APIRouter(prefix="/telegram-admin", tags=["Telegram Admin"])
logger = logging.getLogger(__name__)


# Schemas
class InviteCodeCreate(BaseModel):
    """Schema for creating invite code."""
    max_uses: Optional[int] = Field(None, description="Maximum number of uses (null = unlimited)")
    expires_in_days: Optional[int] = Field(7, description="Days until expiration")
    notes: Optional[str] = Field(None, description="Admin notes")


class InviteCodeResponse(BaseModel):
    """Schema for invite code response."""
    id: int
    code: str
    organization_id: str
    max_uses: Optional[int]
    used_count: int
    expires_at: Optional[datetime]
    status: InviteCodeStatus
    notes: Optional[str]
    created_at: datetime
    used_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TelegramUserResponse(BaseModel):
    """Schema for Telegram user response."""
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    organization_id: Optional[str]
    odoo_patient_id: Optional[int]
    status: TelegramUserStatus
    linked_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TelegramConversationResponse(BaseModel):
    """Schema for Telegram conversation response."""
    id: str
    telegram_user_id: str
    organization_id: Optional[str]
    is_active: bool
    message_count: int
    created_at: datetime
    updated_at: datetime
    telegram_user: Optional[TelegramUserResponse] = None
    
    class Config:
        from_attributes = True


class TelegramMessageResponse(BaseModel):
    """Schema for Telegram message response."""
    id: int
    conversation_id: str
    text: Optional[str]
    message_type: str
    direction: MessageDirection
    from_clinic: bool
    sender_telegram_id: Optional[int]
    sender_name: Optional[str]
    is_sent: bool
    is_delivered: bool
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SendMessageRequest(BaseModel):
    """Schema for sending message."""
    telegram_user_id: int
    message: str


# Endpoints
@router.post("/invite-codes", response_model=InviteCodeResponse)
def create_invite_code(
    data: InviteCodeCreate,
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
    db: Session = Depends(get_db),
):
    """
    Generate a new Telegram invite code.
    
    Only owners and admins can create invite codes.
    """
    # Generate random code
    code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    
    # Calculate expiration
    expires_at = None
    if data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=data.expires_in_days)
    
    # Create invite code
    invite = TelegramInviteCode(
        code=code,
        organization_id=current_user.organization_id,
        max_uses=data.max_uses,
        expires_at=expires_at,
        status=InviteCodeStatus.ACTIVE,
        notes=data.notes,
    )
    
    db.add(invite)
    db.commit()
    db.refresh(invite)
    
    logger.info(
        f"User {current_user.id} created Telegram invite code {code} "
        f"for org {current_user.organization_id}"
    )
    
    return invite


@router.get("/invite-codes", response_model=List[InviteCodeResponse])
def list_invite_codes(
    status: Optional[InviteCodeStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
    db: Session = Depends(get_db),
):
    """
    List all Telegram invite codes for the organization.
    """
    query = db.query(TelegramInviteCode).filter(
        TelegramInviteCode.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(TelegramInviteCode.status == status)
    
    invites = query.order_by(TelegramInviteCode.created_at.desc()).all()
    
    return invites


@router.get("/users", response_model=List[TelegramUserResponse])
def list_telegram_users(
    status: Optional[TelegramUserStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
    db: Session = Depends(get_db),
):
    """
    List all Telegram users for the organization.
    """
    query = db.query(TelegramUser).filter(
        TelegramUser.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(TelegramUser.status == status)
    
    users = query.order_by(TelegramUser.created_at.desc()).all()
    
    return users


@router.get("/conversations", response_model=List[TelegramConversationResponse])
def list_conversations(
    active_only: bool = Query(False, description="Show only active conversations"),
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
    db: Session = Depends(get_db),
):
    """
    List Telegram conversations for the organization with user details.
    """
    query = db.query(TelegramConversation).options(
        joinedload(TelegramConversation.telegram_user)
    ).filter(
        TelegramConversation.organization_id == current_user.organization_id
    )
    
    if active_only:
        query = query.filter(TelegramConversation.is_active == True)
    
    conversations = query.order_by(TelegramConversation.last_message_at.desc()).limit(100).all()
    
    # Convert to response format with telegram_user included
    result = []
    for conv in conversations:
        conv_dict = {
            "id": str(conv.id),
            "telegram_user_id": str(conv.telegram_user_id),
            "organization_id": str(conv.organization_id) if conv.organization_id else None,
            "is_active": True,  # Default to active for now
            "message_count": conv.message_count,
            "created_at": conv.started_at,
            "updated_at": conv.last_message_at,
            "telegram_user": None
        }
        
        # Add telegram_user details if available
        if hasattr(conv, 'telegram_user') and conv.telegram_user:
            user = conv.telegram_user
            conv_dict["telegram_user"] = {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "organization_id": str(user.organization_id) if user.organization_id else None,
                "odoo_patient_id": user.odoo_patient_id,
                "status": user.status,
                "linked_at": user.linked_at,
                "created_at": user.created_at
            }
        
        result.append(conv_dict)
    
    return result


@router.get("/conversations/{conversation_id}/messages", response_model=List[TelegramMessageResponse])
def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(100, description="Maximum number of messages to return"),
    offset: int = Query(0, description="Number of messages to skip"),
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
    db: Session = Depends(get_db),
):
    """
    Get messages for a specific conversation.
    
    Returns messages in chronological order (oldest first).
    """
    # Verify conversation belongs to user's organization
    conversation = db.query(TelegramConversation).filter(
        TelegramConversation.id == conversation_id,
        TelegramConversation.organization_id == current_user.organization_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages
    messages = db.query(TelegramMessage).filter(
        TelegramMessage.conversation_id == conversation_id
    ).order_by(
        TelegramMessage.created_at.asc()
    ).offset(offset).limit(limit).all()
    
    return messages


@router.post("/send-message")
async def send_telegram_message(
    data: SendMessageRequest,
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
    db: Session = Depends(get_db),
):
    """
    Send a message to a Telegram user.
    
    The user must belong to the user's organization.
    """
    # Find telegram user
    telegram_user = db.query(TelegramUser).filter(
        TelegramUser.telegram_id == data.telegram_user_id,
        TelegramUser.organization_id == current_user.organization_id
    ).first()
    
    if not telegram_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram user not found or does not belong to your organization"
        )
    
    # Find or create conversation
    conversation = db.query(TelegramConversation).filter(
        TelegramConversation.telegram_user_id == telegram_user.id,
        TelegramConversation.organization_id == current_user.organization_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active conversation found with this user"
        )
    
    try:
        # Send message via Telegram client
        from app.integrations.telegram_client import telegram_client
        
        result = await telegram_client.send_message(
            chat_id=data.telegram_user_id,
            text=data.message
        )
        
        # Store message in database
        message = TelegramMessage(
            conversation_id=conversation.id,
            telegram_message_id=result.get("result", {}).get("message_id"),
            text=data.message,
            message_type="text",
            direction=MessageDirection.OUTGOING,
            from_clinic=True,
            sender_telegram_id=None,
            sender_name=f"{current_user.first_name} {current_user.last_name}",
            is_sent=True,
            is_delivered=False,
            is_read=False,
        )
        
        db.add(message)
        
        # Update conversation
        conversation.message_count += 1
        conversation.last_message_at = datetime.utcnow()
        
        db.commit()
        db.refresh(message)
        
        logger.info(f"Admin {current_user.id} sent message to telegram user {data.telegram_user_id}")
        
        return {
            "success": True,
            "message_id": message.id,
            "telegram_message_id": message.telegram_message_id,
            "created_at": message.created_at
        }
    
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get("/stats")
def get_telegram_stats(
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
    db: Session = Depends(get_db),
):
    """
    Get Telegram integration statistics.
    """
    org_id = current_user.organization_id
    
    # Count users by status
    total_users = db.query(TelegramUser).filter(
        TelegramUser.organization_id == org_id
    ).count()
    
    linked_users = db.query(TelegramUser).filter(
        TelegramUser.organization_id == org_id,
        TelegramUser.status == TelegramUserStatus.LINKED,
    ).count()
    
    # Count active conversations
    active_conversations = db.query(TelegramConversation).filter(
        TelegramConversation.organization_id == org_id,
    ).count()
    
    # Count messages
    total_messages = db.query(TelegramMessage).join(
        TelegramConversation
    ).filter(
        TelegramConversation.organization_id == org_id
    ).count()
    
    return {
        "total_users": total_users,
        "linked_users": linked_users,
        "active_conversations": active_conversations,
        "total_messages": total_messages,
    }

