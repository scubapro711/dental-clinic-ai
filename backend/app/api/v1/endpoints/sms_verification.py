"""
SMS verification API endpoints.

Handles phone number verification via SMS codes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User
from app.models.sms_verification import SMSVerificationCode
from app.services.sms_service import sms_service
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/v1/auth")


class SendSMSCodeRequest(BaseModel):
    """Request to send SMS verification code."""
    phone_number: str


class VerifySMSCodeRequest(BaseModel):
    """Request to verify SMS code."""
    phone_number: str
    code: str


class Enable2FARequest(BaseModel):
    """Request to enable 2FA."""
    phone_number: str


@router.post("/send-sms-code")
async def send_sms_verification_code(
    request: SendSMSCodeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send SMS verification code to user's phone.
    
    Args:
        request: Phone number to send code to
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user not found or rate limited
    """
    # Get user
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="משתמש לא נמצא"
        )
    
    # Check rate limiting (max 3 codes per 10 minutes)
    recent_codes = db.query(SMSVerificationCode).filter(
        SMSVerificationCode.user_id == user.id,
        SMSVerificationCode.phone_number == request.phone_number,
        SMSVerificationCode.created_at >= datetime.utcnow() - timedelta(minutes=10)
    ).count()
    
    if recent_codes >= 3:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="נשלחו יותר מדי קודים. נסה שוב בעוד 10 דקות"
        )
    
    # Invalidate old codes for this phone
    old_codes = db.query(SMSVerificationCode).filter(
        SMSVerificationCode.user_id == user.id,
        SMSVerificationCode.phone_number == request.phone_number,
        SMSVerificationCode.is_used == False
    ).all()
    
    for code in old_codes:
        code.is_used = True
    
    # Generate new code
    verification_code = sms_service.generate_verification_code()
    
    # Create new SMS verification record
    new_code = SMSVerificationCode(
        user_id=user.id,
        phone_number=request.phone_number,
        code=verification_code
    )
    
    db.add(new_code)
    db.commit()
    
    # Send SMS
    success = await sms_service.send_verification_code(
        phone_number=request.phone_number,
        code=verification_code,
        user_name=user.full_name
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="שליחת SMS נכשלה. נסה שוב מאוחר יותר"
        )
    
    return {
        "message": "קוד אימות נשלח למספר הטלפון שלך",
        "expires_in_minutes": 10
    }


@router.post("/verify-sms-code")
async def verify_sms_code(
    request: VerifySMSCodeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify SMS code.
    
    Args:
        request: Phone number and verification code
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If code invalid, expired, or too many attempts
    """
    # Get user
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="משתמש לא נמצא"
        )
    
    # Find most recent code for this phone
    code_record = db.query(SMSVerificationCode).filter(
        SMSVerificationCode.user_id == user.id,
        SMSVerificationCode.phone_number == request.phone_number,
        SMSVerificationCode.is_used == False
    ).order_by(SMSVerificationCode.created_at.desc()).first()
    
    if not code_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="לא נמצא קוד אימות. אנא בקש קוד חדש"
        )
    
    # Check if expired
    if code_record.is_expired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="קוד האימות פג תוקף. אנא בקש קוד חדש"
        )
    
    # Increment attempts
    code_record.attempts += 1
    db.commit()
    
    # Check if too many attempts
    if code_record.attempts > 3:
        code_record.is_used = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="יותר מדי ניסיונות שגויים. אנא בקש קוד חדש"
        )
    
    # Verify code
    if code_record.code != request.code:
        remaining_attempts = 3 - code_record.attempts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"קוד שגוי. נותרו {remaining_attempts} ניסיונות"
        )
    
    # Mark as used
    code_record.is_used = True
    code_record.used_at = datetime.utcnow()
    
    # Update user's phone number if verified
    user.phone = request.phone_number
    user.phone_verified = True
    
    db.commit()
    
    return {
        "message": "מספר הטלפון אומת בהצלחה!",
        "phone_number": request.phone_number
    }


@router.post("/enable-2fa")
async def enable_2fa(
    request: Enable2FARequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enable 2FA for user account.
    
    Requires phone to be verified first.
    
    Args:
        request: Phone number for 2FA
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If phone not verified
    """
    # Get user
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="משתמש לא נמצא"
        )
    
    # Check if phone is verified
    if not user.phone_verified or user.phone != request.phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="יש לאמת את מספר הטלפון תחילה"
        )
    
    # Enable MFA
    user.mfa_enabled = True
    db.commit()
    
    return {
        "message": "אימות דו-שלבי הופעל בהצלחה!",
        "mfa_enabled": True,
        "phone_number": request.phone_number
    }


@router.post("/disable-2fa")
async def disable_2fa(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disable 2FA for user account.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    # Get user
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="משתמש לא נמצא"
        )
    
    # Disable MFA
    user.mfa_enabled = False
    db.commit()
    
    return {
        "message": "אימות דו-שלבי בוטל",
        "mfa_enabled": False
    }


@router.get("/2fa-status")
async def get_2fa_status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get 2FA status for current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        2FA status
    """
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="משתמש לא נמצא"
        )
    
    return {
        "mfa_enabled": user.mfa_enabled,
        "phone_verified": user.phone_verified,
        "phone_number": user.phone if user.phone_verified else None
    }


from datetime import timedelta  # Add this import at the top
