"""
Google OAuth Authentication API endpoints.

Provides:
- Google Sign-In
- Google Sign-Up
- Automatic user creation/linking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4
from typing import Optional
import secrets
from app.core.auth import get_current_user

from app.core.database import get_db
from app.core.config import Settings
from app.services.google_oauth_service import GoogleOAuthService
from app.services.auth_service import AuthService
from app.services.user_sync_service import UserSyncService
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from pydantic import BaseModel

router = APIRouter(prefix="/auth/google", tags=["Google OAuth"])

# Load settings
settings = Settings()


# ========== Schemas ==========

class GoogleAuthResponse(BaseModel):
    """Google authentication response."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    is_new_user: bool
    message: str


# ========== Helper Functions ==========

def get_google_oauth_service() -> GoogleOAuthService:
    """Get Google OAuth service instance."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured. Please contact support."
        )
    
    return GoogleOAuthService(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )


async def get_or_create_user_from_google(
    db: Session,
    google_user_info: dict,
    organization_id: Optional[str] = None
) -> tuple[User, bool]:
    """
    Get existing user or create new user from Google info.
    
    Args:
        db: Database session
        google_user_info: User info from Google
        organization_id: Optional organization ID for new users
        
    Returns:
        Tuple of (User, is_new_user)
    """
    email = google_user_info.get("email")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Google"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    
    if existing_user:
        # User exists - update Google info if needed
        if not existing_user.google_id:
            existing_user.google_id = google_user_info.get("google_id")
            existing_user.picture_url = google_user_info.get("picture")
            db.commit()
            db.refresh(existing_user)
        
        return existing_user, False
    
    # Create new user
    user = User(
        id=uuid4(),
        email=email,
        full_name=google_user_info.get("name", ""),
        google_id=google_user_info.get("google_id"),
        picture_url=google_user_info.get("picture"),
        is_active=True,
        is_verified=google_user_info.get("email_verified", True),  # Trust Google verification
        created_at=datetime.utcnow(),
        hashed_password=""  # No password for Google OAuth users
    )
    db.add(user)
    db.flush()
    
    # If organization_id provided, create membership
    if organization_id:
        # Sync with Odoo
        user_sync_service = UserSyncService(db)
        odoo_partner_id = await user_sync_service.sync_user_to_odoo(
            user_id=str(user.id),
            organization_id=organization_id
        )
        
        # Create membership
        membership = OrganizationMembership(
            id=uuid4(),
            user_id=user.id,
            organization_id=organization_id,
            role="patient",  # Default role
            odoo_partner_id=odoo_partner_id,
            is_active=True,
            joined_at=datetime.utcnow()
        )
        db.add(membership)
    else:
        # Get default organization (for MVP)
        default_org = db.query(Organization).first()
        if default_org:
            # Sync with Odoo
            user_sync_service = UserSyncService(db)
            odoo_partner_id = await user_sync_service.sync_user_to_odoo(
                user_id=str(user.id),
                organization_id=str(default_org.id)
            )
            
            # Create membership
            membership = OrganizationMembership(
                id=uuid4(),
                user_id=user.id,
                organization_id=default_org.id,
                role="patient",
                odoo_partner_id=odoo_partner_id,
                is_active=True,
                joined_at=datetime.utcnow()
            )
            db.add(membership)
    
    db.commit()
    db.refresh(user)
    
    return user, True


# ========== API Endpoints ==========

@router.get("/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth login flow.
    
    Redirects user to Google's consent screen.
    """
    google_service = get_google_oauth_service()
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state in session (in production, use Redis)
    # For now, we'll validate in callback
    
    # Get authorization URL
    auth_url = google_service.get_authorization_url(state=state)
    
    return RedirectResponse(url=auth_url)


@router.get("/callback", response_model=GoogleAuthResponse)
async def google_callback(
    code: str,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback.
    
    This endpoint is called by Google after user authorizes the app.
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided"
        )
    
    # TODO: Validate state parameter (CSRF protection)
    
    # Get Google OAuth service
    google_service = get_google_oauth_service()
    
    # Exchange code for user info
    google_user_info = await google_service.authenticate(code)
    
    # Get or create user
    user, is_new_user = await get_or_create_user_from_google(db, google_user_info)
    
    # Get user's organization membership
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User has no organization membership"
        )
    
    # Generate JWT token
    access_token = AuthService.create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": membership.role,
            "organization_id": str(membership.organization_id),
            "odoo_partner_id": membership.odoo_partner_id
        }
    )
    
    return GoogleAuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user.id),
        email=user.email,
        is_new_user=is_new_user,
        message="Successfully authenticated with Google" if not is_new_user else "Account created successfully"
    )


@router.post("/link", response_model=GoogleAuthResponse)
async def link_google_account(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Link Google account to existing user.
    
    This allows users who registered with email/password to link their Google account.
    """
    # Get Google OAuth service
    google_service = get_google_oauth_service()
    
    # Exchange code for user info
    google_user_info = await google_service.authenticate(code)
    
    # Verify email matches
    if google_user_info.get("email") != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account email does not match your account email"
        )
    
    # Link Google account
    current_user.google_id = google_user_info.get("google_id")
    current_user.picture_url = google_user_info.get("picture")
    db.commit()
    
    # Get user's organization membership
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == current_user.id,
        OrganizationMembership.is_active == True
    ).first()
    
    # Generate new JWT token
    access_token = AuthService.create_access_token(
        data={
            "sub": str(current_user.id),
            "email": current_user.email,
            "role": membership.role if membership else "patient",
            "organization_id": str(membership.organization_id) if membership else None,
            "odoo_partner_id": membership.odoo_partner_id if membership else None
        }
    )
    
    return GoogleAuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(current_user.id),
        email=current_user.email,
        is_new_user=False,
        message="Google account linked successfully"
    )
