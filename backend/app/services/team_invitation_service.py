"""
Team invitation service.

Handles invitation creation, email sending, and acceptance.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.team_invitation import TeamInvitation, InvitationStatus
from app.models.organization import Organization
from app.models.user import User
from app.services.email_service import email_service


class TeamInvitationService:
    """Service for managing team invitations."""
    
    @staticmethod
    def create_invitation(
        db: Session,
        organization_id: str,
        inviter_id: str,
        invitee_email: str,
        invitee_role: str,
        invitee_name: Optional[str] = None,
        message: Optional[str] = None
    ) -> TeamInvitation:
        """
        Create a new team invitation.
        
        Args:
            db: Database session
            organization_id: Organization UUID
            inviter_id: Inviter user UUID
            invitee_email: Email of person to invite
            invitee_role: Role to assign (dentist, hygienist, etc.)
            invitee_name: Optional suggested name
            message: Optional personal message
            
        Returns:
            Created invitation
        """
        # Check if there's already a pending invitation for this email
        existing = db.query(TeamInvitation).filter(
            TeamInvitation.organization_id == organization_id,
            TeamInvitation.invitee_email == invitee_email,
            TeamInvitation.status == InvitationStatus.PENDING
        ).first()
        
        if existing and existing.is_valid():
            # Return existing valid invitation
            return existing
        
        # Create new invitation
        invitation = TeamInvitation(
            organization_id=organization_id,
            inviter_id=inviter_id,
            invitee_email=invitee_email,
            invitee_role=invitee_role,
            invitee_name=invitee_name,
            message=message
        )
        
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        return invitation
    
    @staticmethod
    def send_invitation_email(
        invitation: TeamInvitation,
        organization: Organization,
        inviter: User,
        frontend_url: str = "https://app.dentaflow.co.il"
    ) -> bool:
        """
        Send invitation email.
        
        Args:
            invitation: TeamInvitation object
            organization: Organization object
            inviter: Inviter user object
            frontend_url: Frontend URL for invitation link
            
        Returns:
            True if email sent successfully
        """
        # Build invitation link
        invitation_link = f"{frontend_url}/accept-invitation?token={invitation.token}"
        
        # Build email content
        subject = f"הזמנה להצטרף ל-{organization.name} ב-DentaFlow"
        
        html_content = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>שלום{' ' + invitation.invitee_name if invitation.invitee_name else ''}!</h2>
            
            <p><strong>{inviter.full_name or inviter.email}</strong> מזמין/ה אותך להצטרף ל<strong>{organization.name}</strong> ב-DentaFlow.</p>
            
            <p>תפקיד: <strong>{invitation.invitee_role}</strong></p>
            
            {f'<p style="background: #f5f5f5; padding: 15px; border-right: 4px solid #4CAF50;"><em>"{invitation.message}"</em></p>' if invitation.message else ''}
            
            <p>DentaFlow היא מערכת ניהול מרפאות שיניים חכמה עם סוכן AI שעוזר לך לנהל תורים, מטופלים, וטיפולים.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{invitation_link}" 
                   style="background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-size: 16px;">
                    קבל/י את ההזמנה
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                ההזמנה תפוג ב-{invitation.expires_at.strftime('%d/%m/%Y בשעה %H:%M')}
            </p>
            
            <p style="color: #666; font-size: 14px;">
                אם אינך מכיר/ה את השולח/ת, אנא התעלם/י מהודעה זו.
            </p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="color: #999; font-size: 12px; text-align: center;">
                DentaFlow - מערכת ניהול מרפאות שיניים חכמה<br>
                <a href="https://dentaflow.co.il">dentaflow.co.il</a>
            </p>
        </div>
        """
        
        text_content = f"""
שלום{' ' + invitation.invitee_name if invitation.invitee_name else ''}!

{inviter.full_name or inviter.email} מזמין/ה אותך להצטרף ל-{organization.name} ב-DentaFlow.

תפקיד: {invitation.invitee_role}

{f'הודעה: "{invitation.message}"' if invitation.message else ''}

לקבלת ההזמנה, היכנס/י לקישור הבא:
{invitation_link}

ההזמנה תפוג ב-{invitation.expires_at.strftime('%d/%m/%Y בשעה %H:%M')}

אם אינך מכיר/ה את השולח/ת, אנא התעלם/י מהודעה זו.

---
DentaFlow - מערכת ניהול מרפאות שיניים חכמה
https://dentaflow.co.il
        """
        
        # Send email
        return email_service.send_email(
            to_email=invitation.invitee_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    @staticmethod
    def validate_token(db: Session, token: str) -> Optional[TeamInvitation]:
        """
        Validate invitation token.
        
        Args:
            db: Database session
            token: Invitation token
            
        Returns:
            TeamInvitation if valid, None otherwise
        """
        invitation = db.query(TeamInvitation).filter(
            TeamInvitation.token == token
        ).first()
        
        if not invitation:
            return None
        
        if not invitation.is_valid():
            # Mark as expired if not already
            if invitation.status == InvitationStatus.PENDING:
                invitation.status = InvitationStatus.EXPIRED
                db.commit()
            return None
        
        return invitation
    
    @staticmethod
    def accept_invitation(
        db: Session,
        invitation: TeamInvitation,
        user_id: str
    ) -> bool:
        """
        Accept invitation and create membership.
        
        Args:
            db: Database session
            invitation: TeamInvitation object
            user_id: User UUID who accepted
            
        Returns:
            True if accepted successfully
        """
        if not invitation.is_valid():
            return False
        
        # Mark as accepted
        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_by_user_id = user_id
        invitation.accepted_at = datetime.utcnow()
        
        db.commit()
        
        return True
    
    @staticmethod
    def revoke_invitation(db: Session, invitation_id: str) -> bool:
        """
        Revoke invitation.
        
        Args:
            db: Database session
            invitation_id: Invitation UUID
            
        Returns:
            True if revoked successfully
        """
        invitation = db.query(TeamInvitation).filter(
            TeamInvitation.id == invitation_id
        ).first()
        
        if not invitation or invitation.status != InvitationStatus.PENDING:
            return False
        
        invitation.status = InvitationStatus.REVOKED
        invitation.revoked_at = datetime.utcnow()
        
        db.commit()
        
        return True


# Singleton instance
team_invitation_service = TeamInvitationService()
