"""
Team invitation API endpoints.

Handles inviting team members, viewing invitations, and accepting invitations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.team_invitation import TeamInvitation, InvitationStatus
from app.services.team_invitation_service import team_invitation_service
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/v1/invitations")


class SendInvitationRequest(BaseModel):
    """Request to send team invitation."""
    organization_id: str
    invitee_email: EmailStr
    invitee_role: str
    invitee_name: Optional[str] = None
    message: Optional[str] = None


class InvitationResponse(BaseModel):
    """Invitation response."""
    id: str
    organization_id: str
    organization_name: str
    invitee_email: str
    invitee_role: str
    invitee_name: Optional[str]
    status: str
    created_at: str
    expires_at: str
    inviter_name: Optional[str]
    message: Optional[str]


@router.post("/send")
async def send_invitation(
    request: SendInvitationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send team invitation.
    
    Only organization owners and admins can send invitations.
    
    Args:
        request: Invitation details
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Invitation confirmation
        
    Raises:
        HTTPException: If validation fails or user not authorized
    """
    # Get organization
    organization = db.query(Organization).filter(
        Organization.id == request.organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ארגון לא נמצא"
        )
    
    # Check if user is owner or admin
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == current_user["user_id"],
        OrganizationMembership.organization_id == request.organization_id
    ).first()
    
    if not membership or membership.role not in ["owner", "org_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="רק בעלים או מנהלים יכולים לשלוח הזמנות"
        )
    
    # Check if invitee is already a member
    existing_member = db.query(OrganizationMembership).join(User).filter(
        User.email == request.invitee_email,
        OrganizationMembership.organization_id == request.organization_id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="משתמש זה כבר חבר בארגון"
        )
    
    # Get inviter details
    inviter = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    # Create invitation
    invitation = team_invitation_service.create_invitation(
        db=db,
        organization_id=request.organization_id,
        inviter_id=current_user["user_id"],
        invitee_email=request.invitee_email,
        invitee_role=request.invitee_role,
        invitee_name=request.invitee_name,
        message=request.message
    )
    
    # Send invitation email
    email_sent = team_invitation_service.send_invitation_email(
        invitation=invitation,
        organization=organization,
        inviter=inviter
    )
    
    return {
        "message": "הזמנה נשלחה בהצלחה!" if email_sent else "הזמנה נוצרה (שליחת אימייל נכשלה)",
        "invitation_id": str(invitation.id),
        "invitee_email": invitation.invitee_email,
        "expires_at": invitation.expires_at.isoformat(),
        "email_sent": email_sent
    }


@router.get("/organization/{organization_id}")
async def get_organization_invitations(
    organization_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[InvitationResponse]:
    """
    Get all invitations for an organization.
    
    Only organization owners and admins can view invitations.
    
    Args:
        organization_id: Organization UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of invitations
        
    Raises:
        HTTPException: If organization not found or user not authorized
    """
    # Get organization
    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ארגון לא נמצא"
        )
    
    # Check if user is owner or admin
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == current_user["user_id"],
        OrganizationMembership.organization_id == organization_id
    ).first()
    
    if not membership or membership.role not in ["owner", "org_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="רק בעלים או מנהלים יכולים לצפות בהזמנות"
        )
    
    # Get invitations
    invitations = db.query(TeamInvitation).filter(
        TeamInvitation.organization_id == organization_id
    ).order_by(TeamInvitation.created_at.desc()).all()
    
    # Build response
    result = []
    for inv in invitations:
        inviter = db.query(User).filter(User.id == inv.inviter_id).first()
        result.append({
            "id": str(inv.id),
            "organization_id": str(inv.organization_id),
            "organization_name": organization.name,
            "invitee_email": inv.invitee_email,
            "invitee_role": inv.invitee_role,
            "invitee_name": inv.invitee_name,
            "status": inv.status.value,
            "created_at": inv.created_at.isoformat(),
            "expires_at": inv.expires_at.isoformat(),
            "inviter_name": inviter.full_name if inviter else None,
            "message": inv.message
        })
    
    return result


@router.get("/validate/{token}")
async def validate_invitation(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Validate invitation token.
    
    Public endpoint - no authentication required.
    
    Args:
        token: Invitation token
        db: Database session
        
    Returns:
        Invitation details if valid
        
    Raises:
        HTTPException: If token invalid or expired
    """
    invitation = team_invitation_service.validate_token(db, token)
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="הזמנה לא נמצאה או פגה תוקפה"
        )
    
    # Get organization
    organization = db.query(Organization).filter(
        Organization.id == invitation.organization_id
    ).first()
    
    # Get inviter
    inviter = db.query(User).filter(User.id == invitation.inviter_id).first()
    
    return {
        "valid": True,
        "organization_name": organization.name if organization else "Unknown",
        "invitee_email": invitation.invitee_email,
        "invitee_role": invitation.invitee_role,
        "invitee_name": invitation.invitee_name,
        "inviter_name": inviter.full_name if inviter else None,
        "message": invitation.message,
        "expires_at": invitation.expires_at.isoformat()
    }


@router.post("/revoke/{invitation_id}")
async def revoke_invitation(
    invitation_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke invitation.
    
    Only organization owners and admins can revoke invitations.
    
    Args:
        invitation_id: Invitation UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Revocation confirmation
        
    Raises:
        HTTPException: If invitation not found or user not authorized
    """
    # Get invitation
    invitation = db.query(TeamInvitation).filter(
        TeamInvitation.id == invitation_id
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="הזמנה לא נמצאה"
        )
    
    # Check if user is owner or admin of the organization
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == current_user["user_id"],
        OrganizationMembership.organization_id == invitation.organization_id
    ).first()
    
    if not membership or membership.role not in ["owner", "org_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="רק בעלים או מנהלים יכולים לבטל הזמנות"
        )
    
    # Revoke invitation
    success = team_invitation_service.revoke_invitation(db, invitation_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="לא ניתן לבטל הזמנה זו"
        )
    
    return {
        "message": "הזמנה בוטלה בהצלחה",
        "invitation_id": str(invitation.id)
    }


@router.get("/my-invitations")
async def get_my_invitations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[InvitationResponse]:
    """
    Get invitations sent to current user's email.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of invitations
    """
    # Get user
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    # Get invitations
    invitations = db.query(TeamInvitation).filter(
        TeamInvitation.invitee_email == user.email,
        TeamInvitation.status == InvitationStatus.PENDING
    ).order_by(TeamInvitation.created_at.desc()).all()
    
    # Build response
    result = []
    for inv in invitations:
        if not inv.is_valid():
            continue
            
        organization = db.query(Organization).filter(
            Organization.id == inv.organization_id
        ).first()
        
        inviter = db.query(User).filter(User.id == inv.inviter_id).first()
        
        result.append({
            "id": str(inv.id),
            "organization_id": str(inv.organization_id),
            "organization_name": organization.name if organization else "Unknown",
            "invitee_email": inv.invitee_email,
            "invitee_role": inv.invitee_role,
            "invitee_name": inv.invitee_name,
            "status": inv.status.value,
            "created_at": inv.created_at.isoformat(),
            "expires_at": inv.expires_at.isoformat(),
            "inviter_name": inviter.full_name if inviter else None,
            "message": inv.message
        })
    
    return result
