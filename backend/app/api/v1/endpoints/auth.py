"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user
from app.models.user import User
from app.middleware.rate_limiter import limiter, get_rate_limit

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(get_rate_limit("auth_register"))
async def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **full_name**: User's full name
    - **phone**: Optional phone number
    - **invitation_token**: Optional invitation token (if joining via invitation)
    
    This endpoint now automatically:
    1. Creates a user in PostgreSQL
    2. Creates a corresponding patient in Odoo
    3. Links them via UserSyncService
    4. If invitation_token provided, accepts invitation and creates membership
    """
    # Check if user already exists
    existing_user = AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Determine organization based on invitation token or default
    from app.models.organization import Organization
    from app.models.organization_membership import OrganizationMembership
    from app.services.user_sync_service import UserSyncService
    from app.services.team_invitation_service import team_invitation_service
    
    organization_id = None
    user_role = "PATIENT"  # Default role (must be uppercase for enum)
    invitation = None
    
    # Check if registration is via invitation
    if hasattr(user_data, 'invitation_token') and user_data.invitation_token:
        invitation = team_invitation_service.validate_token(db, user_data.invitation_token)
        
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="הזמנה לא תקפה או פגה תוקפה"
            )
        
        # Verify email matches invitation
        if invitation.invitee_email != user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="האימייל לא תואם להזמנה"
            )
        
        organization_id = invitation.organization_id
        user_role = invitation.invitee_role
    else:
        # Get default organization (first one) for direct signup
        default_org = db.query(Organization).first()
        
        if not default_org:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No organization found. Please contact support.",
            )
        
        organization_id = default_org.id
    
    # Create new user
    user = AuthService.create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        organization_id=organization_id,
        role=user_role,
    )
    
    # Sync user with Odoo (create patient record)
    sync_service = UserSyncService(db)
    try:
        odoo_partner_id = sync_service.sync_user_to_odoo(
            user_id=user.id,
            organization_id=organization_id,
            user_email=user.email,
            user_name=user.full_name,
            user_phone=user.phone,
        )
        
        # Update user's membership with Odoo partner ID
        membership = db.query(OrganizationMembership).filter(
            OrganizationMembership.user_id == user.id,
            OrganizationMembership.organization_id == organization_id
        ).first()
        
        if membership:
            membership.odoo_partner_id = odoo_partner_id
            db.commit()
            
    except Exception as e:
        # Log error but don't fail registration
        # User can still use the system, sync can be retried later
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to sync user {user.id} to Odoo: {str(e)}")
    
    # If registration was via invitation, accept it
    if invitation:
        team_invitation_service.accept_invitation(db, invitation, str(user.id))

    return user


@router.post("/login", response_model=Token)
@limiter.limit(get_rate_limit("auth_login"))
async def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password.
    
    Returns JWT access and refresh tokens.
    """
    # Authenticate user
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Update last login
    AuthService.update_last_login(db, user.id)

    # Get user's membership to include organization_id and odoo_partner_id in token
    from app.models.organization_membership import OrganizationMembership
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.is_active == True
    ).first()
    
    organization_id = None
    odoo_partner_id = None
    
    if membership:
        organization_id = str(membership.organization_id)
        odoo_partner_id = membership.odoo_partner_id

    # Create tokens with organization_id and odoo_partner_id
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "organization_id": organization_id,
        "odoo_partner_id": odoo_partner_id,  # Include Odoo link
    }

    access_token = AuthService.create_access_token(token_data)
    refresh_token = AuthService.create_refresh_token(token_data)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.post("/refresh", response_model=Token)
@limiter.limit(get_rate_limit("auth_token_refresh"))
async def refresh_token(request: Request, refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    """
    # Verify refresh token
    token_data = AuthService.verify_token(refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user
    user = AuthService.get_user_by_id(db, token_data.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens
    new_token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "organization_id": str(user.organization_id) if user.organization_id else None,
    }

    access_token = AuthService.create_access_token(new_token_data)
    new_refresh_token = AuthService.create_refresh_token(new_token_data)

    return Token(access_token=access_token, refresh_token=new_refresh_token)
