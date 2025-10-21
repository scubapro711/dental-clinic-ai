"""
Business Associate Agreement (BAA) API Endpoints
Handles BAA document retrieval, signing, and verification.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.api.dependencies import get_db, get_current_user, get_current_organization_id, get_current_organization
from app.models.user import User
from app.models.organization import Organization
from app.models.baa_signature import BAASignature
from app.services.baa_service import BAAService

router = APIRouter()


# ==================== Request/Response Models ====================

class BAASignatureRequest(BaseModel):
    """Request to sign the BAA."""
    signature_name: str = Field(..., description="Full name of the person signing")
    signature_title: str = Field(..., description="Title of the person signing")
    confirm: bool = Field(..., description="Confirmation of agreement to terms")


class BAASignatureResponse(BaseModel):
    """Response after BAA signature."""
    success: bool
    organization_id: int
    signed_at: str
    signature_name: str
    message: str

class BAAStatusResponse(BaseModel):
    """BAA signature status for a clinic."""
    is_signed: bool
    signed_at: str | None
    signed_by: str | None
    signature_name: str | None
    signature_title: str | None


# ==================== Endpoints ====================

@router.get(
    "/template",
    response_model=str,
    summary="Get BAA Template for Clinic",
    description="Retrieve the personalized BAA template for the current clinic."
)
async def get_baa_template(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_organization: Organization = Depends(get_current_organization)
):
    """
    Get the personalized BAA template for the current clinic.
    
    **Permissions:** Authenticated user in an organization
    
    Returns:
        The BAA template with clinic-specific information.
    """
    try:
        service = BAAService(db)
        template = service.get_clinic_baa_template(current_organization)
        return template
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving BAA template: {str(e)}"
        )

@router.post(
    "/sign",
    response_model=BAASignatureResponse,
    summary="Sign the Business Associate Agreement",
    description="Record the BAA signature for the current clinic."
)
async def sign_baa(
    request: Request,
    signature_request: BAASignatureRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_organization: Organization = Depends(get_current_organization)
):
    """
    Sign the Business Associate Agreement for the clinic.
    
    **Permissions:** Authenticated user in an organization
    
    **HIPAA Compliance:**
    - Records digital signature with timestamp and IP address.
    - Links signature to user and organization.
    
    Args:
        request: The incoming request object to get client IP.
        signature_request: The signature details.
        
    Returns:
        A summary of the BAA signature.
    """
    if not signature_request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must confirm your agreement to the BAA terms."
        )
    
    try:
        service = BAAService(db)
        
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        signature = service.record_baa_signature(
            organization_id=current_organization.id,
            user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            signature_name=signature_request.signature_name,
            signature_title=signature_request.signature_title
        )
        
        return BAASignatureResponse(
            success=True,
            organization_id=signature.organization_id,
            signed_at=signature.signed_at.isoformat(),
            signature_name=signature.signature_name,
            message="BAA successfully signed."
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error signing BAA: {str(e)}"
        )

@router.get(
    "/status",
    response_model=BAAStatusResponse,
    summary="Get BAA Signature Status",
    description="Check if the BAA has been signed for the current clinic."
)
async def get_baa_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_organization: Organization = Depends(get_current_organization)
):
    """
    Get the BAA signature status for the current clinic.
    
    **Permissions:** Authenticated user in an organization
    
    Returns:
        The BAA signature status, including who signed it and when.
    """
    service = BAAService(db)
    signature = service.get_baa_signature_status(current_organization.id)
    
    if signature:
        return BAAStatusResponse(
            is_signed=True,
            signed_at=signature.signed_at.isoformat(),
            signed_by=signature.user.email, # Assuming relationship is loaded
            signature_name=signature.signature_name,
            signature_title=signature.signature_title
        )
    else:
        return BAAStatusResponse(is_signed=False)

