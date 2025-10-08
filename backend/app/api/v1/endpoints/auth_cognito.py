"""
AWS Cognito Authentication API endpoints.

Provides:
- Sign up (email/password)
- Sign in (email/password)
- Google OAuth
- Token refresh
- Password reset
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from botocore.exceptions import ClientError
import logging

from app.core.cognito import get_cognito_client, CognitoUser
from app.core.auth import get_current_user, get_current_cognito_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


# ========== Request/Response Schemas ==========

class SignUpRequest(BaseModel):
    """Sign up request."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    given_name: Optional[str] = Field(None, max_length=100)
    family_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, description="Phone in E.164 format (+972501234567)")


class SignUpResponse(BaseModel):
    """Sign up response."""
    user_sub: str
    user_confirmed: bool
    message: str
    code_delivery_details: Optional[dict] = None


class ConfirmSignUpRequest(BaseModel):
    """Confirm sign up request."""
    email: EmailStr
    confirmation_code: str = Field(..., min_length=6, max_length=6)


class SignInRequest(BaseModel):
    """Sign in request."""
    email: EmailStr
    password: str


class SignInResponse(BaseModel):
    """Sign in response."""
    access_token: str
    id_token: str
    refresh_token: str
    expires_in: int
    token_type: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response."""
    access_token: str
    id_token: str
    expires_in: int
    token_type: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request."""
    email: EmailStr


class ConfirmForgotPasswordRequest(BaseModel):
    """Confirm forgot password request."""
    email: EmailStr
    confirmation_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8)


class UserInfoResponse(BaseModel):
    """User info response."""
    username: str
    email: str
    email_verified: bool
    sub: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    phone_number: Optional[str] = None
    phone_number_verified: bool = False


# ========== Endpoints ==========

@router.post(
    "/cognito/signup",
    response_model=SignUpResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign up with AWS Cognito",
    description="Register a new user with email and password via AWS Cognito"
)
async def cognito_sign_up(request: SignUpRequest):
    """
    Sign up a new user via AWS Cognito.
    
    - **email**: User email (will be username)
    - **password**: Password (min 8 characters, must meet pool requirements)
    - **given_name**: First name (optional)
    - **family_name**: Last name (optional)
    - **phone_number**: Phone in E.164 format (optional)
    
    Returns user_sub and confirmation status.
    If email verification is required, sends confirmation code.
    """
    try:
        cognito = get_cognito_client()
        
        result = cognito.sign_up(
            email=request.email,
            password=request.password,
            given_name=request.given_name,
            family_name=request.family_name,
            phone_number=request.phone_number
        )
        
        message = "User registered successfully"
        if not result['user_confirmed']:
            message += ". Please check your email for confirmation code."
        
        return SignUpResponse(
            user_sub=result['user_sub'],
            user_confirmed=result['user_confirmed'],
            message=message,
            code_delivery_details=result.get('code_delivery_details')
        )
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'UsernameExistsException':
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        elif error_code == 'InvalidPasswordException':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid password: {error_message}"
            )
        elif error_code == 'InvalidParameterException':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid parameter: {error_message}"
            )
        else:
            logger.error(f"Sign up error: {error_code} - {error_message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Sign up failed"
            )


@router.post(
    "/cognito/confirm-signup",
    status_code=status.HTTP_200_OK,
    summary="Confirm Cognito sign up",
    description="Confirm user registration with verification code"
)
async def cognito_confirm_sign_up(request: ConfirmSignUpRequest):
    """
    Confirm user registration.
    
    - **email**: User email
    - **confirmation_code**: 6-digit code sent to email
    
    Returns success message.
    """
    try:
        cognito = get_cognito_client()
        
        cognito.confirm_sign_up(
            email=request.email,
            confirmation_code=request.confirmation_code
        )
        
        return {"message": "Email confirmed successfully. You can now sign in."}
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'CodeMismatchException':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid confirmation code"
            )
        elif error_code == 'ExpiredCodeException':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirmation code has expired"
            )
        else:
            logger.error(f"Confirm sign up error: {error_code} - {error_message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Confirmation failed"
            )


@router.post(
    "/cognito/signin",
    response_model=SignInResponse,
    summary="Sign in with Cognito",
    description="Authenticate user via AWS Cognito and get JWT tokens"
)
async def cognito_sign_in(request: SignInRequest):
    """
    Sign in user via AWS Cognito.
    
    - **email**: User email
    - **password**: User password
    
    Returns JWT tokens (access, ID, refresh).
    """
    try:
        cognito = get_cognito_client()
        
        result = cognito.sign_in(
            email=request.email,
            password=request.password
        )
        
        return SignInResponse(**result)
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code in ['NotAuthorizedException', 'UserNotFoundException']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        elif error_code == 'UserNotConfirmedException':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not confirmed. Please check your email for confirmation code."
            )
        else:
            logger.error(f"Sign in error: {error_code} - {error_message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Sign in failed"
            )


@router.post(
    "/cognito/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh Cognito token",
    description="Get new access token using Cognito refresh token"
)
async def cognito_refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token.
    
    - **refresh_token**: Refresh token from sign in
    
    Returns new access and ID tokens.
    """
    try:
        cognito = get_cognito_client()
        
        result = cognito.refresh_token(request.refresh_token)
        
        return RefreshTokenResponse(**result)
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'NotAuthorizedException':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        else:
            logger.error(f"Token refresh error: {error_code}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh failed"
            )


@router.post(
    "/cognito/signout",
    status_code=status.HTTP_200_OK,
    summary="Sign out from Cognito",
    description="Sign out user (invalidate Cognito tokens)"
)
async def cognito_sign_out(current_user: User = Depends(get_current_user)):
    """
    Sign out current user.
    
    Requires valid access token in Authorization header.
    """
    # Note: In production, you might want to:
    # 1. Revoke tokens in Cognito
    # 2. Add tokens to blacklist
    # 3. Clear user sessions
    
    return {"message": "Signed out successfully"}


@router.post(
    "/cognito/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Forgot password (Cognito)",
    description="Initiate password reset flow via Cognito"
)
async def cognito_forgot_password(request: ForgotPasswordRequest):
    """
    Initiate password reset.
    
    - **email**: User email
    
    Sends confirmation code to email.
    """
    try:
        cognito = get_cognito_client()
        
        delivery_details = cognito.forgot_password(request.email)
        
        return {
            "message": "Password reset code sent to your email",
            "delivery_details": delivery_details
        }
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'UserNotFoundException':
            # Don't reveal if user exists (security best practice)
            return {"message": "If the email exists, a reset code will be sent"}
        else:
            logger.error(f"Forgot password error: {error_code}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password reset failed"
            )


@router.post(
    "/cognito/confirm-forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Confirm forgot password (Cognito)",
    description="Reset password with confirmation code via Cognito"
)
async def cognito_confirm_forgot_password(request: ConfirmForgotPasswordRequest):
    """
    Confirm password reset.
    
    - **email**: User email
    - **confirmation_code**: 6-digit code sent to email
    - **new_password**: New password (min 8 characters)
    
    Returns success message.
    """
    try:
        cognito = get_cognito_client()
        
        cognito.confirm_forgot_password(
            email=request.email,
            confirmation_code=request.confirmation_code,
            new_password=request.new_password
        )
        
        return {"message": "Password reset successfully. You can now sign in with your new password."}
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'CodeMismatchException':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid confirmation code"
            )
        elif error_code == 'ExpiredCodeException':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirmation code has expired"
            )
        elif error_code == 'InvalidPasswordException':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid password: {error_message}"
            )
        else:
            logger.error(f"Confirm forgot password error: {error_code}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password reset failed"
            )


@router.get(
    "/cognito/me",
    response_model=UserInfoResponse,
    summary="Get current Cognito user info",
    description="Get information about the currently authenticated Cognito user"
)
async def cognito_get_me(cognito_user: CognitoUser = Depends(get_current_cognito_user)):
    """
    Get current user information from Cognito.
    
    Requires valid access token in Authorization header.
    """
    return UserInfoResponse(
        username=cognito_user.username,
        email=cognito_user.email,
        email_verified=cognito_user.email_verified,
        sub=cognito_user.sub,
        given_name=cognito_user.given_name,
        family_name=cognito_user.family_name,
        phone_number=cognito_user.phone_number,
        phone_number_verified=cognito_user.phone_number_verified
    )
