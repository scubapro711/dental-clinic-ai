"""
Telegram Admin API Endpoints

Manage Telegram integration for clinic admins:
- Generate invite codes
- View Telegram users
- Link/unlink users
- View conversations

Reference: TELEGRAM_INTEGRATION_COMPLETE_SPEC.md
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import secrets
import string

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.telegram_user import TelegramUser, TelegramUserStatus
from app.models.telegram_invite_code import TelegramInviteCode, InviteCodeStatus
from app.models.telegram_conversation import TelegramConversation

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
    id: int
    telegram_user_id: int
    chat_id: int
    organization_id: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


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


@router.delete("/invite-codes/{code}")
def deactivate_invite_code(
    code: str,
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
    db: Session = Depends(get_db),
):
    """
    Deactivate an invite code.
    """
    invite = db.query(TelegramInviteCode).filter(
        TelegramInviteCode.code == code,
        TelegramInviteCode.organization_id == current_user.organization_id,
    ).first()
    
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite code not found"
        )
    
    invite.status = InviteCodeStatus.REVOKED
    db.commit()
    
    logger.info(f"User {current_user.id} deactivated invite code {code}")
    
    return {"message": "Invite code deactivated"}


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


@router.get("/users/{telegram_user_id}", response_model=TelegramUserResponse)
def get_telegram_user(
    telegram_user_id: int,
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
    db: Session = Depends(get_db),
):
    """
    Get details of a specific Telegram user.
    """
    user = db.query(TelegramUser).filter(
        TelegramUser.id == telegram_user_id,
        TelegramUser.organization_id == current_user.organization_id,
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram user not found"
        )
    
    return user


@router.delete("/users/{telegram_user_id}")
def unlink_telegram_user(
    telegram_user_id: int,
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
    db: Session = Depends(get_db),
):
    """
    Unlink a Telegram user from patient.
    """
    user = db.query(TelegramUser).filter(
        TelegramUser.id == telegram_user_id,
        TelegramUser.organization_id == current_user.organization_id,
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram user not found"
        )
    
    # Unlink
    user.odoo_patient_id = None
    user.status = TelegramUserStatus.NEW
    user.linked_at = None
    user.updated_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"User {current_user.id} unlinked Telegram user {telegram_user_id}")
    
    return {"message": "Telegram user unlinked"}


@router.get("/conversations", response_model=List[TelegramConversationResponse])
def list_conversations(
    active_only: bool = Query(True, description="Show only active conversations"),
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
    db: Session = Depends(get_db),
):
    """
    List Telegram conversations for the organization.
    """
    query = db.query(TelegramConversation).filter(
        TelegramConversation.organization_id == current_user.organization_id
    )
    
    if active_only:
        query = query.filter(TelegramConversation.is_active == True)
    
    conversations = query.order_by(TelegramConversation.updated_at.desc()).limit(100).all()
    
    return conversations


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
    
    new_users = db.query(TelegramUser).filter(
        TelegramUser.organization_id == org_id,
        TelegramUser.status == TelegramUserStatus.NEW,
    ).count()
    
    # Count active conversations
    active_conversations = db.query(TelegramConversation).filter(
        TelegramConversation.organization_id == org_id,
        TelegramConversation.is_active == True,
    ).count()
    
    # Count invite codes
    active_invites = db.query(TelegramInviteCode).filter(
        TelegramInviteCode.organization_id == org_id,
        TelegramInviteCode.status == InviteCodeStatus.ACTIVE,
    ).count()
    
    return {
        "total_users": total_users,
        "linked_users": linked_users,
        "pending_users": total_users - linked_users - new_users,
        "active_conversations": active_conversations,
        "messages_today": 0,  # TODO: Implement message counting
        "messages_week": 0,   # TODO: Implement message counting
        "messages_month": 0,  # TODO: Implement message counting
        "avg_response_time": 0,  # TODO: Implement response time tracking
        "users": {
            "total": total_users,
            "linked": linked_users,
            "new": new_users,
            "pending": total_users - linked_users - new_users,
        },
        "conversations": {
            "active": active_conversations,
        },
        "invite_codes": {
            "active": active_invites,
        },
    }


@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: int,
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
    
    # TODO: Implement message storage and retrieval
    # For now, return empty list
    # In production, you would query a telegram_messages table
    
    return {
        "messages": [],
        "conversation_id": conversation_id,
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@router.post("/send")
async def send_telegram_message(
    chat_id: int,
    message: str,
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
    db: Session = Depends(get_db),
):
    """
    Send a message to a Telegram chat.
    
    The chat must belong to the user's organization.
    """
    # Verify chat belongs to user's organization
    conversation = db.query(TelegramConversation).filter(
        TelegramConversation.chat_id == chat_id,
        TelegramConversation.organization_id == current_user.organization_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found or does not belong to your organization"
        )
    
    try:
        # Send message via Telegram client
        from app.integrations.telegram_client import telegram_client
        
        result = await telegram_client.send_message(
            chat_id=chat_id,
            text=message
        )
        
        logger.info(f"Admin {current_user.id} sent message to chat {chat_id}")
        
        return {
            "success": True,
            "message_id": result.get("result", {}).get("message_id"),
            "chat_id": chat_id
        }
    
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        logger.error(f"Failed to send message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again later."
        )

