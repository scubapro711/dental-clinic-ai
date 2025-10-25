"""
MFA (Multi-Factor Authentication) API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import logging
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.mfa_service import get_mfa_service
from app.core.audit_log import log_audit_event

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class MFASetupResponse(BaseModel):
    """Response for MFA setup."""
    secret: str = Field(..., description="TOTP secret key (show once)")
    qr_code: str = Field(..., description="QR code data URI")
    backup_codes: List[str] = Field(..., description="Backup codes (show once)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "secret": "JBSWY3DPEHPK3PXP",
                "qr_code": "data:image/png;base64,iVBORw0KG...",
                "backup_codes": ["A1B2C3D4", "E5F6G7H8"]
            }
        }


class MFAEnableRequest(BaseModel):
    """Request to enable MFA."""
    token: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "123456"
            }
        }


class MFAVerifyRequest(BaseModel):
    """Request to verify MFA token."""
    token: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code")
    backup_code: str | None = Field(None, description="Backup code (alternative to token)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "123456"
            }
        }


class MFADisableRequest(BaseModel):
    """Request to disable MFA."""
    token: str | None = Field(None, min_length=6, max_length=6, description="6-digit TOTP code")
    backup_code: str | None = Field(None, description="Backup code (alternative to token)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "123456"
            }
        }


class MFAStatusResponse(BaseModel):
    """Response for MFA status."""
    enabled: bool = Field(..., description="Whether MFA is enabled")
    backup_codes_remaining: int | None = Field(None, description="Number of backup codes remaining")
    
    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "backup_codes_remaining": 8
            }
        }


class MFARegenerateBackupCodesRequest(BaseModel):
    """Request to regenerate backup codes."""
    token: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "123456"
            }
        }


class MFABackupCodesResponse(BaseModel):
    """Response for backup codes."""
    backup_codes: List[str] = Field(..., description="New backup codes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "backup_codes": ["A1B2C3D4", "E5F6G7H8", "I9J0K1L2"]
            }
        }


# Endpoints
@router.get("/status", response_model=MFAStatusResponse)
async def get_mfa_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get MFA status for current user.
    
    Returns whether MFA is enabled and how many backup codes remain.
    """
    mfa_service = get_mfa_service()
    
    backup_codes_remaining = None
    if current_user.mfa_enabled and current_user.mfa_backup_codes:
        try:
            backup_codes_str = mfa_service.encryption_service.decrypt(current_user.mfa_backup_codes)
            backup_codes = backup_codes_str.split(",")
            backup_codes_remaining = len(backup_codes)
        except Exception:
            pass
    
    return MFAStatusResponse(
        enabled=current_user.mfa_enabled,
        backup_codes_remaining=backup_codes_remaining
    )


@router.post("/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initialize MFA setup for current user.
    
    Returns:
    - TOTP secret (save this securely - shown only once)
    - QR code for scanning with authenticator app
    - Backup codes (save these securely - shown only once)
    
    After setup, call /mfa/enable with a valid token to activate MFA.
    """
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled. Disable it first to set up again."
        )
    
    mfa_service = get_mfa_service()
    
    try:
        secret, qr_code, backup_codes = mfa_service.setup_mfa(db, current_user)
        
        # Audit log
        log_audit_event(
            db=db,
            user_id=current_user.id,
            action="mfa_setup_initiated",
            resource_type="user",
            resource_id=str(current_user.id),
            details={"email": current_user.email}
        )
        
        return MFASetupResponse(
            secret=secret,
            qr_code=qr_code,
            backup_codes=backup_codes
        )
    except Exception as e:
        logger.error(f"Failed to setup MFA: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again later."
        )


@router.post("/enable")
async def enable_mfa(
    request: MFAEnableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enable MFA after verifying the first token.
    
    This endpoint must be called after /mfa/setup to activate MFA.
    Provide a valid TOTP token from your authenticator app.
    """
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled"
        )
    
    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not set up. Call /mfa/setup first."
        )
    
    mfa_service = get_mfa_service()
    
    if not mfa_service.enable_mfa(db, current_user, request.token):
        # Audit log - failed attempt
        log_audit_event(
            db=db,
            user_id=current_user.id,
            action="mfa_enable_failed",
            resource_type="user",
            resource_id=str(current_user.id),
            details={"reason": "invalid_token"}
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token. Please try again."
        )
    
    # Audit log - success
    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="mfa_enabled",
        resource_type="user",
        resource_id=str(current_user.id),
        details={"email": current_user.email}
    )
    
    return {"message": "MFA enabled successfully"}


@router.post("/verify")
async def verify_mfa(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify MFA token or backup code.
    
    Used during login or for sensitive operations.
    Provide either a TOTP token or a backup code.
    """
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    mfa_service = get_mfa_service()
    verified = False
    used_backup_code = False
    
    # Try token first
    if request.token:
        try:
            secret = mfa_service.encryption_service.decrypt(current_user.mfa_secret)
            verified = mfa_service.verify_token(secret, request.token)
        except Exception:
            pass
    
    # Try backup code if token failed
    if not verified and request.backup_code:
        verified = mfa_service.use_backup_code(db, current_user, request.backup_code)
        used_backup_code = verified
    
    if not verified:
        # Audit log - failed verification
        log_audit_event(
            db=db,
            user_id=current_user.id,
            action="mfa_verification_failed",
            resource_type="user",
            resource_id=str(current_user.id),
            details={"method": "backup_code" if request.backup_code else "token"}
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or backup code"
        )
    
    # Audit log - success
    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="mfa_verified",
        resource_type="user",
        resource_id=str(current_user.id),
        details={
            "method": "backup_code" if used_backup_code else "token",
            "backup_code_used": used_backup_code
        }
    )
    
    response = {"message": "MFA verified successfully"}
    if used_backup_code:
        # Get remaining backup codes
        backup_codes_remaining = 0
        if current_user.mfa_backup_codes:
            try:
                backup_codes_str = mfa_service.encryption_service.decrypt(current_user.mfa_backup_codes)
                backup_codes = backup_codes_str.split(",")
                backup_codes_remaining = len(backup_codes)
            except Exception:
                pass
        
        response["backup_code_used"] = True
        response["backup_codes_remaining"] = backup_codes_remaining
        
        if backup_codes_remaining == 0:
            response["warning"] = "No backup codes remaining. Please regenerate them."
    
    return response


@router.post("/disable")
async def disable_mfa(
    request: MFADisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disable MFA for current user.
    
    Requires verification with either a TOTP token or backup code.
    This will remove all MFA settings including backup codes.
    """
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    if not request.token and not request.backup_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either token or backup_code is required"
        )
    
    mfa_service = get_mfa_service()
    
    if not mfa_service.disable_mfa(db, current_user, request.token, request.backup_code):
        # Audit log - failed attempt
        log_audit_event(
            db=db,
            user_id=current_user.id,
            action="mfa_disable_failed",
            resource_type="user",
            resource_id=str(current_user.id),
            details={"reason": "invalid_credentials"}
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or backup code"
        )
    
    # Audit log - success
    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="mfa_disabled",
        resource_type="user",
        resource_id=str(current_user.id),
        details={"email": current_user.email}
    )
    
    return {"message": "MFA disabled successfully"}


@router.post("/regenerate-backup-codes", response_model=MFABackupCodesResponse)
async def regenerate_backup_codes(
    request: MFARegenerateBackupCodesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate backup codes.
    
    This will invalidate all existing backup codes and generate new ones.
    Save the new codes securely - they are shown only once.
    """
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    mfa_service = get_mfa_service()
    
    backup_codes = mfa_service.regenerate_backup_codes(db, current_user, request.token)
    
    if not backup_codes:
        # Audit log - failed attempt
        log_audit_event(
            db=db,
            user_id=current_user.id,
            action="mfa_backup_codes_regeneration_failed",
            resource_type="user",
            resource_id=str(current_user.id),
            details={"reason": "invalid_token"}
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Audit log - success
    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="mfa_backup_codes_regenerated",
        resource_type="user",
        resource_id=str(current_user.id),
        details={"email": current_user.email, "codes_count": len(backup_codes)}
    )
    
    return MFABackupCodesResponse(backup_codes=backup_codes)

