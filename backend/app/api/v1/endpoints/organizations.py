"""
Organization Registration API endpoints.

Handles clinic onboarding:
- Organization registration
- Owner user creation
- Default settings initialization
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import uuid4
import re

from app.core.database import get_db
from app.models.organization import Organization, SubscriptionTier
from app.models.user import User
from app.models.organization_membership import OrganizationMembership
from app.models.clinic_settings import ClinicSettings
from app.models.treatment_price import TreatmentPrice
from app.services.user_sync_service import UserSyncService
from app.services.auth_service import AuthService
from app.schemas.organization import OrganizationRegisterRequest, OrganizationResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

router = APIRouter(prefix="/organizations", tags=["Organizations"])


# ========== Schemas ==========

class OrganizationRegisterRequest(BaseModel):
    """Organization registration request."""
    # Clinic info
    clinic_name: str = Field(..., min_length=2, max_length=200)
    clinic_email: EmailStr
    clinic_phone: Optional[str] = Field(None, max_length=20)
    clinic_address: Optional[str] = Field(None, max_length=500)
    
    # Owner info
    owner_full_name: str = Field(..., min_length=2, max_length=200)
    owner_email: EmailStr
    owner_password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    owner_phone: Optional[str] = Field(None, max_length=20)


class OrganizationResponse(BaseModel):
    """Organization registration response."""
    organization_id: str
    organization_name: str
    organization_slug: str
    owner_id: str
    owner_email: str
    access_token: str
    token_type: str = "bearer"
    message: str
    
    class Config:
        from_attributes = True


# ========== Helper Functions ==========

def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from organization name."""
    # Convert to lowercase
    slug = name.lower()
    
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug


def create_default_clinic_settings(db: Session, organization_id: str) -> ClinicSettings:
    """Create default clinic settings for new organization."""
    from datetime import time
    settings = ClinicSettings(
        organization_id=organization_id,
        # Israeli work week hours
        sunday_open=time(9, 0),
        sunday_close=time(17, 0),
        monday_open=time(9, 0),
        monday_close=time(17, 0),
        tuesday_open=time(9, 0),
        tuesday_close=time(17, 0),
        wednesday_open=time(9, 0),
        wednesday_close=time(17, 0),
        thursday_open=time(9, 0),
        thursday_close=time(17, 0),
        friday_open=time(9, 0),
        friday_close=time(14, 0),
        # Saturday closed (Shabbat)
        saturday_open=None,
        saturday_close=None,
        # Appointment settings
        default_appointment_duration=30,
        buffer_between_appointments=10,
        advance_booking_days=90,
        cancellation_notice_hours=24,
        # Billing
        currency="ILS"
    )
    db.add(settings)
    return settings


def create_default_treatment_prices(db: Session, organization_id: str):
    """Create default treatment prices for new organization."""
    default_treatments = [
        {"name": "בדיקה כללית", "code": "EXAM_001", "price": 150.0, "duration": 30},
        {"name": "ניקוי אבנית", "code": "CLEAN_001", "price": 300.0, "duration": 45},
        {"name": "סתימה לבנה", "code": "FILL_001", "price": 500.0, "duration": 60},
        {"name": "עקירת שן", "code": "EXTRACT_001", "price": 400.0, "duration": 45},
        {"name": "טיפול שורש", "code": "ROOT_001", "price": 1500.0, "duration": 90},
        {"name": "כתר", "code": "CROWN_001", "price": 2500.0, "duration": 120},
        {"name": "הלבנה", "code": "WHITEN_001", "price": 1200.0, "duration": 60},
        {"name": "צילום פנורמי", "code": "XRAY_001", "price": 200.0, "duration": 15},
    ]
    
    for treatment in default_treatments:
        price = TreatmentPrice(
            organization_id=organization_id,
            treatment_name=treatment["name"],
            treatment_code=treatment["code"],
            price=treatment["price"],
            currency="ILS",
            duration_minutes=treatment["duration"],
            is_active=True
        )
        db.add(price)


# ========== API Endpoints ==========

@router.post("/register", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def register_organization(
    request: OrganizationRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new dental clinic organization.
    
    This endpoint:
    1. Creates a new organization
    2. Creates the owner user
    3. Creates organization membership (owner role)
    4. Syncs user with Odoo (creates patient record)
    5. Creates default clinic settings
    6. Seeds default treatment prices
    7. Returns access token for immediate login
    
    **Note:** Email verification is sent but not required for initial access.
    """
    
    # 1. Validate owner email not already registered
    existing_user = db.query(User).filter(User.email == request.owner_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner email already registered"
        )
    
    # 2. Generate unique slug for organization
    slug = generate_slug(request.clinic_name)
    existing_org = db.query(Organization).filter(Organization.slug == slug).first()
    if existing_org:
        # Add random suffix if slug already exists
        slug = f"{slug}-{uuid4().hex[:6]}"
    
    try:
        # 3. Create organization
        organization = Organization(
            id=uuid4(),
            name=request.clinic_name,
            slug=slug,
            email=request.clinic_email,
            phone=request.clinic_phone,
            address=request.clinic_address,
            subscription_tier=SubscriptionTier.BASIC,
            subscription_status="trial",
            subscription_start_date=datetime.utcnow(),
            subscription_end_date=datetime.utcnow() + timedelta(days=30),  # 30-day trial
            is_active=True
        )
        db.add(organization)
        db.flush()  # Get organization.id
        
        # 4. Create owner user
        from app.core.security import get_password_hash
        hashed_password = get_password_hash(request.owner_password)
        owner = User(
            id=uuid4(),
            email=request.owner_email,
            hashed_password=hashed_password,
            full_name=request.owner_full_name,
            phone=request.owner_phone,
            is_active=True,
            is_verified=False,  # Will be verified via email
            created_at=datetime.utcnow()
        )
        db.add(owner)
        db.flush()  # Get owner.id
        
        # 5. Create organization membership (owner role)
        membership = OrganizationMembership(
            id=uuid4(),
            user_id=owner.id,
            organization_id=organization.id,
            organization_role="owner",
            is_active=True,
            joined_at=datetime.utcnow()
        )
        db.add(membership)
        db.flush()
        
        # 6. Sync user with Odoo (create patient record)
        user_sync_service = UserSyncService(db)
        odoo_partner_id = user_sync_service.sync_user_to_odoo(
            user_id=owner.id,
            organization_id=organization.id
        )
        
        # Update membership with odoo_partner_id
        membership.odoo_partner_id = odoo_partner_id
        
        # 7. Create default clinic settings
        create_default_clinic_settings(db, str(organization.id))
        
        # 8. Seed default treatment prices
        create_default_treatment_prices(db, str(organization.id))
        
        # 9. Commit all changes
        db.commit()
        db.refresh(organization)
        db.refresh(owner)
        db.refresh(membership)
        
        # 10. Generate access token
        access_token = AuthService.create_access_token(
            data={
                "sub": str(owner.id),
                "email": owner.email,
                "role": "owner",
                "organization_id": str(organization.id),
                "odoo_partner_id": odoo_partner_id
            }
        )
        
        # 11. TODO: Send verification email (will be implemented in Email Verification component)
        
        return OrganizationResponse(
            organization_id=str(organization.id),
            organization_name=organization.name,
            organization_slug=organization.slug,
            owner_id=str(owner.id),
            owner_email=owner.email,
            access_token=access_token,
            token_type="bearer",
            message="Organization registered successfully! Please check your email to verify your account."
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register organization: {str(e)}"
        )


@router.get("/{organization_id}", response_model=dict)
async def get_organization(
    organization_id: str,
    db: Session = Depends(get_db)
):
    """Get organization details by ID."""
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return {
        "id": str(organization.id),
        "name": organization.name,
        "slug": organization.slug,
        "email": organization.email,
        "phone": organization.phone,
        "address": organization.address,
        "subscription_tier": organization.subscription_tier,
        "subscription_status": organization.subscription_status,
        "is_active": organization.is_active
    }
