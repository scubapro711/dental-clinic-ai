"""
BAA (Business Associate Agreement) signature API endpoints.

Handles BAA display, electronic signature, and PDF generation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.models.baa_signature import BAASignature
from app.models.organization_membership import OrganizationMembership
from app.services.baa_service import baa_service
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/v1/baa")


class SignBAARequest(BaseModel):
    """Request to sign BAA."""
    organization_id: str
    signatory_name: str
    signatory_title: str
    consent_confirmed: bool


class BAAResponse(BaseModel):
    """BAA document response."""
    baa_text: str
    baa_version: str
    consent_text: str
    organization_name: str
    already_signed: bool
    signature_date: str = None


@router.get("/document/{organization_id}")
async def get_baa_document(
    organization_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get BAA document for organization.
    
    Args:
        organization_id: Organization UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        BAA document with signature status
        
    Raises:
        HTTPException: If organization not found or user not authorized
    """
    # Get organization
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ארגון לא נמצא"
        )
    
    # Check if user is owner or admin of this organization
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == current_user["user_id"],
        OrganizationMembership.organization_id == organization_id
    ).first()
    
    if not membership or membership.role not in ["owner", "org_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="אין לך הרשאה לצפות בהסכם זה"
        )
    
    # Check if already signed
    existing_signature = db.query(BAASignature).filter(
        BAASignature.organization_id == organization_id
    ).order_by(BAASignature.signed_at.desc()).first()
    
    # Get BAA text and consent
    baa_version = "1.0"
    baa_text = baa_service.get_baa_text(version=baa_version)
    consent_text = baa_service.generate_consent_text()
    
    return {
        "baa_text": baa_text,
        "baa_version": baa_version,
        "consent_text": consent_text,
        "organization_name": organization.name,
        "already_signed": existing_signature is not None,
        "signature_date": existing_signature.signed_at.isoformat() if existing_signature else None
    }


@router.post("/sign")
async def sign_baa(
    request: SignBAARequest,
    http_request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sign BAA electronically.
    
    Args:
        request: Signature request with organization and signatory details
        http_request: FastAPI request object (for IP and user agent)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Signature confirmation
        
    Raises:
        HTTPException: If validation fails or user not authorized
    """
    # Validate consent
    if not request.consent_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="יש לאשר את תנאי ההסכם"
        )
    
    # Get organization
    organization = db.query(Organization).filter(Organization.id == request.organization_id).first()
    
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
            detail="רק בעלים או מנהלים יכולים לחתום על ההסכם"
        )
    
    # Check if already signed
    existing_signature = db.query(BAASignature).filter(
        BAASignature.organization_id == request.organization_id
    ).first()
    
    if existing_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="הסכם כבר נחתם עבור ארגון זה"
        )
    
    # Get user details
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    # Get BAA content and calculate hash
    baa_version = "1.0"
    baa_text = baa_service.get_baa_text(version=baa_version)
    content_hash = baa_service.calculate_content_hash(baa_text)
    consent_text = baa_service.generate_consent_text()
    
    # Get IP address and user agent
    ip_address = http_request.client.host if http_request.client else None
    user_agent = http_request.headers.get("user-agent", "")
    
    # Create signature record
    signature = BAASignature(
        organization_id=request.organization_id,
        signatory_user_id=user.id,
        signatory_name=request.signatory_name,
        signatory_title=request.signatory_title,
        signatory_email=user.email,
        signature_method="electronic",
        ip_address=ip_address,
        user_agent=user_agent,
        baa_version=baa_version,
        baa_content_hash=content_hash,
        consent_text=consent_text,
        signed_at=datetime.utcnow()
    )
    
    db.add(signature)
    db.commit()
    db.refresh(signature)
    
    return {
        "message": "הסכם נחתם בהצלחה!",
        "signature_id": str(signature.id),
        "signed_at": signature.signed_at.isoformat(),
        "signatory_name": signature.signatory_name,
        "organization_name": organization.name
    }


@router.get("/status/{organization_id}")
async def get_baa_status(
    organization_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get BAA signature status for organization.
    
    Args:
        organization_id: Organization UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Signature status
        
    Raises:
        HTTPException: If organization not found or user not authorized
    """
    # Get organization
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ארגון לא נמצא"
        )
    
    # Check if user is member of this organization
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == current_user["user_id"],
        OrganizationMembership.organization_id == organization_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="אין לך הרשאה לצפות במידע זה"
        )
    
    # Get signature
    signature = db.query(BAASignature).filter(
        BAASignature.organization_id == organization_id
    ).order_by(BAASignature.signed_at.desc()).first()
    
    if not signature:
        return {
            "signed": False,
            "organization_name": organization.name
        }
    
    return {
        "signed": True,
        "signature_id": str(signature.id),
        "signed_at": signature.signed_at.isoformat(),
        "signatory_name": signature.signatory_name,
        "signatory_title": signature.signatory_title,
        "baa_version": signature.baa_version,
        "organization_name": organization.name
    }


@router.get("/history/{organization_id}")
async def get_baa_history(
    organization_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get BAA signature history for organization.
    
    Useful if BAA is re-signed after amendments.
    
    Args:
        organization_id: Organization UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of all signatures
        
    Raises:
        HTTPException: If organization not found or user not authorized
    """
    # Get organization
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    
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
            detail="רק בעלים או מנהלים יכולים לצפות בהיסטוריה"
        )
    
    # Get all signatures
    signatures = db.query(BAASignature).filter(
        BAASignature.organization_id == organization_id
    ).order_by(BAASignature.signed_at.desc()).all()
    
    return {
        "organization_name": organization.name,
        "signatures": [
            {
                "signature_id": str(sig.id),
                "signed_at": sig.signed_at.isoformat(),
                "signatory_name": sig.signatory_name,
                "signatory_title": sig.signatory_title,
                "signatory_email": sig.signatory_email,
                "baa_version": sig.baa_version,
                "ip_address": sig.ip_address
            }
            for sig in signatures
        ]
    }
