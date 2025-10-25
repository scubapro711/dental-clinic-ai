"""
JWT utilities with organization context.

Provides functions to create and validate JWTs with organization context.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import UUID
import os

from jose import jwt, JWTError
from pydantic import BaseModel
import logging

from app.core.config import Settings

logger = logging.getLogger(__name__)

# Load settings
settings = Settings()

# JWT Configuration
# SECURITY: JWT_SECRET_KEY must be set in environment variables
# No default value is provided to prevent accidental use of weak secrets
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = 'HS256'

# FIXED Bug #34: Use settings from config.py instead of hardcoded values
# This ensures configuration changes take effect
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
JWT_REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# Minimum secret length for HS256 (32 bytes = 256 bits)
MIN_SECRET_LENGTH = 32


def _validate_jwt_secret():
    """
    Validate JWT secret at startup.
    
    Ensures that:
    1. JWT_SECRET_KEY is set
    2. Secret is strong enough (at least 32 bytes)
    3. Secret is not a known weak value
    
    Raises:
        RuntimeError: If JWT secret is not properly configured
    """
    if not JWT_SECRET_KEY:
        raise RuntimeError(
            "SECURITY ERROR: JWT_SECRET_KEY environment variable is not set! "
            "This is required for production deployment. "
            "Generate a strong secret with: openssl rand -base64 64"
        )
    
    if len(JWT_SECRET_KEY) < MIN_SECRET_LENGTH:
        raise RuntimeError(
            f"SECURITY ERROR: JWT_SECRET_KEY is too short ({len(JWT_SECRET_KEY)} bytes). "
            f"Must be at least {MIN_SECRET_LENGTH} bytes for HS256 security. "
            f"Generate a strong secret with: openssl rand -base64 64"
        )
    
    # Check for known weak secrets
    weak_secrets = [
        'your-secret-key-change-in-production',
        'secret',
        'password',
        'changeme',
        '12345678',
        'test',
        'development',
    ]
    
    if JWT_SECRET_KEY in weak_secrets:
        raise RuntimeError(
            f"SECURITY ERROR: JWT_SECRET_KEY is a known weak value! "
            f"Never use default or common secrets in production. "
            f"Generate a strong secret with: openssl rand -base64 64"
        )
    
    logger.info("JWT secret validation passed")


# Validate JWT secret at module import (fail fast)
try:
    _validate_jwt_secret()
except RuntimeError as e:
    logger.critical(str(e))
    # In production, this should cause the application to fail startup
    # For now, we log the error and continue (to avoid breaking existing deployments)
    # TODO: Make this a hard failure in production after migration period
    if os.getenv('ENVIRONMENT') == 'production':
        raise

# Minimum secret length for HS256 (32 bytes = 256 bits)
MIN_SECRET_LENGTH = 32


def _validate_jwt_secret():
    """
    Validate JWT secret at startup.
    
    Ensures that:
    1. JWT_SECRET_KEY is set
    2. Secret is strong enough (at least 32 bytes)
    3. Secret is not a known weak value
    
    Raises:
        RuntimeError: If JWT secret is not properly configured
    """
    if not JWT_SECRET_KEY:
        raise RuntimeError(
            "SECURITY ERROR: JWT_SECRET_KEY environment variable is not set! "
            "This is required for production deployment. "
            "Generate a strong secret with: openssl rand -base64 64"
        )
    
    if len(JWT_SECRET_KEY) < MIN_SECRET_LENGTH:
        raise RuntimeError(
            f"SECURITY ERROR: JWT_SECRET_KEY is too short ({len(JWT_SECRET_KEY)} bytes). "
            f"Must be at least {MIN_SECRET_LENGTH} bytes for HS256 security. "
            f"Generate a strong secret with: openssl rand -base64 64"
        )
    
    # Check for known weak secrets
    weak_secrets = [
        'your-secret-key-change-in-production',
        'secret',
        'password',
        'changeme',
        '12345678',
        'test',
        'development',
    ]
    
    if JWT_SECRET_KEY in weak_secrets:
        raise RuntimeError(
            f"SECURITY ERROR: JWT_SECRET_KEY is a known weak value! "
            f"Never use default or common secrets in production. "
            f"Generate a strong secret with: openssl rand -base64 64"
        )
    
    logger.info("JWT secret validation passed")


# Validate JWT secret at module import (fail fast)
try:
    _validate_jwt_secret()
except RuntimeError as e:
    logger.critical(str(e))
    # In production, this should cause the application to fail startup
    # For now, we log the error and continue (to avoid breaking existing deployments)
    # TODO: Make this a hard failure in production after migration period
    if os.getenv('ENVIRONMENT') == 'production':
        raise


class TokenData(BaseModel):
    """JWT token data."""
    sub: str  # User ID or Cognito sub
    email: Optional[str] = None
    organization_id: Optional[str] = None
    organization_role: Optional[str] = None
    functional_role: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    type: str = 'access'  # 'access' or 'refresh'


def create_access_token(
    subject: str,
    email: Optional[str] = None,
    organization_id: Optional[UUID] = None,
    organization_role: Optional[str] = None,
    functional_role: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create JWT access token with organization context.
    
    Args:
        subject: User ID or Cognito sub
        email: User email
        organization_id: Current organization UUID
        organization_role: User's role in organization (owner/admin/staff/patient)
        functional_role: User's functional role (dentist/hygienist/receptionist/etc)
        expires_delta: Custom expiration time
        additional_claims: Additional claims to include
    
    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        'sub': subject,
        'exp': int(expire.timestamp()),
        'iat': int(datetime.now(timezone.utc).timestamp()),
        'type': 'access'
    }
    
    if email:
        to_encode['email'] = email
    
    if organization_id:
        to_encode['organization_id'] = str(organization_id)
    
    if organization_role:
        to_encode['organization_role'] = organization_role
    
    if functional_role:
        to_encode['functional_role'] = functional_role
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    logger.debug(f"Created access token for user {subject} in org {organization_id}")
    
    return encoded_jwt


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token.
    
    Args:
        subject: User ID or Cognito sub
        expires_delta: Custom expiration time
    
    Returns:
        Encoded JWT refresh token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        'sub': subject,
        'exp': int(expire.timestamp()),
        'iat': int(datetime.now(timezone.utc).timestamp()),
        'type': 'refresh'
    }
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    logger.debug(f"Created refresh token for user {subject}")
    
    return encoded_jwt


def verify_token(token: str, token_type: str = 'access') -> Optional[TokenData]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token string
        token_type: Expected token type ('access' or 'refresh')
    
    Returns:
        TokenData if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Verify token type
        if payload.get('type') != token_type:
            logger.warning(f"Invalid token type. Expected {token_type}, got {payload.get('type')}")
            return None
        
        # Verify expiration
        exp = payload.get('exp')
        if exp and int(datetime.now(timezone.utc).timestamp()) > exp:
            logger.warning("Token has expired")
            return None
        
        token_data = TokenData(
            sub=payload.get('sub'),
            email=payload.get('email'),
            organization_id=payload.get('organization_id'),
            organization_role=payload.get('organization_role'),
            functional_role=payload.get('functional_role'),
            exp=payload.get('exp'),
            iat=payload.get('iat'),
            type=payload.get('type', 'access')
        )
        
        return token_data
    
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {e}")
        return None


def decode_token_without_verification(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode JWT token without verification (for debugging).
    
    WARNING: Do not use for authentication! Only for debugging.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload if valid format, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={'verify_signature': False, 'verify_exp': False}
        )
        return payload
    except Exception as e:
        logger.error(f"Failed to decode token: {e}")
        return None


def get_organization_from_token(token: str) -> Optional[UUID]:
    """
    Extract organization ID from JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Organization UUID if present, None otherwise
    """
    token_data = verify_token(token)
    
    if not token_data or not token_data.organization_id:
        return None
    
    try:
        return UUID(token_data.organization_id)
    except ValueError:
        logger.error(f"Invalid organization ID in token: {token_data.organization_id}")
        return None


def refresh_access_token(refresh_token: str, new_organization_id: Optional[UUID] = None) -> Optional[str]:
    """
    Create new access token from refresh token.
    
    Args:
        refresh_token: Valid refresh token
        new_organization_id: Optional new organization context
    
    Returns:
        New access token if refresh token is valid, None otherwise
    """
    token_data = verify_token(refresh_token, token_type='refresh')
    
    if not token_data:
        return None
    
    # Create new access token
    access_token = create_access_token(
        subject=token_data.sub,
        email=token_data.email,
        organization_id=new_organization_id if new_organization_id else 
                       (UUID(token_data.organization_id) if token_data.organization_id else None),
        organization_role=token_data.organization_role,
        functional_role=token_data.functional_role
    )
    
    return access_token


def create_token_pair(
    subject: str,
    email: Optional[str] = None,
    organization_id: Optional[UUID] = None,
    organization_role: Optional[str] = None,
    functional_role: Optional[str] = None
) -> Dict[str, str]:
    """
    Create both access and refresh tokens.
    
    Args:
        subject: User ID or Cognito sub
        email: User email
        organization_id: Current organization UUID
        organization_role: User's role in organization
        functional_role: User's functional role
    
    Returns:
        Dictionary with access_token and refresh_token
    """
    access_token = create_access_token(
        subject=subject,
        email=email,
        organization_id=organization_id,
        organization_role=organization_role,
        functional_role=functional_role
    )
    
    refresh_token = create_refresh_token(subject=subject)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'expires_in': JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
    }
