"""
Email verification API endpoints.

Handles email verification for user registration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.models.user import User
from app.models.email_verification import EmailVerificationToken
from app.services.email_service import email_service
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/v1/auth")


class ResendVerificationRequest(BaseModel):
    """Request to resend verification email."""
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    """Request to verify email with token."""
    token: str


@router.post("/resend-verification")
async def resend_verification_email(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Resend verification email to user.
    
    Args:
        request: Email address to resend verification to
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user not found or already verified
    """
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Don't reveal if user exists for security
        return {"message": "אם האימייל קיים במערכת, נשלח אליו קישור אימות חדש"}
    
    # Check if already verified
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="האימייל כבר אומת"
        )
    
    # Invalidate old tokens
    old_tokens = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user.id,
        EmailVerificationToken.is_used == False
    ).all()
    
    for token in old_tokens:
        token.is_used = True
    
    # Create new token
    new_token = EmailVerificationToken(
        user_id=user.id,
        token=email_service.generate_verification_token()
    )
    
    db.add(new_token)
    db.commit()
    
    # Send email
    await email_service.send_verification_email(
        to_email=user.email,
        user_name=user.full_name,
        verification_token=new_token.token
    )
    
    return {"message": "קישור אימות חדש נשלח לאימייל שלך"}


@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Verify user email with token.
    
    Args:
        request: Verification token
        db: Database session
        
    Returns:
        Success message with user info
        
    Raises:
        HTTPException: If token invalid, expired, or already used
    """
    # Find token
    token = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == request.token
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="קישור אימות לא תקין"
        )
    
    # Check if already used
    if token.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="קישור אימות זה כבר נוצל"
        )
    
    # Check if expired
    if token.is_expired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="קישור אימות פג תוקף. אנא בקש קישור חדש"
        )
    
    # Mark token as used
    token.is_used = True
    token.used_at = datetime.utcnow()
    
    # Mark user as verified
    user = token.user
    user.is_verified = True
    
    db.commit()
    
    # Send welcome email
    await email_service.send_welcome_email(
        to_email=user.email,
        user_name=user.full_name
    )
    
    return {
        "message": "האימייל אומת בהצלחה!",
        "user_id": str(user.id),
        "email": user.email,
        "name": user.full_name
    }


@router.get("/verification-status")
async def get_verification_status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get email verification status for current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Verification status
    """
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="משתמש לא נמצא"
        )
    
    return {
        "is_verified": user.is_verified,
        "email": user.email
    }
