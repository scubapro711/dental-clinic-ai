"""
AWS Cognito integration for authentication.

Provides:
- User registration with email/password
- Google OAuth integration
- JWT token validation
- User management
"""
import os
import json
import time
import hmac
import hashlib
import base64
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError
import requests
from jose import jwt, JWTError
from jose.backends import RSAKey
from pydantic import BaseModel, EmailStr, Field
import logging

logger = logging.getLogger(__name__)


class CognitoConfig(BaseModel):
    """AWS Cognito configuration."""
    region: str = Field(..., description="AWS region")
    user_pool_id: str = Field(..., description="Cognito User Pool ID")
    client_id: str = Field(..., description="App Client ID")
    client_secret: Optional[str] = Field(None, description="App Client Secret (if configured)")
    identity_pool_id: Optional[str] = Field(None, description="Identity Pool ID (for federated identities)")
    
    # Google OAuth
    google_client_id: Optional[str] = Field(None, description="Google OAuth Client ID")
    google_client_secret: Optional[str] = Field(None, description="Google OAuth Client Secret")
    
    # JWT validation
    token_use: str = Field("id", description="Token use: 'id' or 'access'")
    
    @property
    def issuer(self) -> str:
        """Get JWT issuer URL."""
        return f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"
    
    @property
    def jwks_url(self) -> str:
        """Get JWKS URL for token validation."""
        return f"{self.issuer}/.well-known/jwks.json"


class CognitoUser(BaseModel):
    """Cognito user representation."""
    username: str
    email: EmailStr
    email_verified: bool = False
    sub: str  # Cognito UUID
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    phone_number: Optional[str] = None
    phone_number_verified: bool = False
    
    # OAuth provider info
    identities: Optional[list] = None  # For federated identities
    
    # Custom attributes
    custom_attributes: Dict[str, Any] = {}


class CognitoClient:
    """
    AWS Cognito client for user authentication and management.
    
    Features:
    - Email/password authentication
    - Google OAuth integration
    - JWT token validation
    - User CRUD operations
    - Multi-factor authentication (MFA)
    """
    
    def __init__(self, config: CognitoConfig):
        """Initialize Cognito client."""
        self.config = config
        self.client = boto3.client(
            'cognito-idp',
            region_name=config.region
        )
        
        # Cache for JWKS keys
        self._jwks_cache: Optional[Dict] = None
        self._jwks_cache_time: Optional[datetime] = None
        self._jwks_cache_ttl = timedelta(hours=1)
    
    def _get_secret_hash(self, username: str) -> str:
        """
        Calculate secret hash for Cognito client secret.
        
        Required when client secret is configured.
        """
        if not self.config.client_secret:
            raise ValueError("Client secret not configured")
        
        message = username + self.config.client_id
        dig = hmac.new(
            self.config.client_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(dig).decode()
    
    def sign_up(
        self,
        email: str,
        password: str,
        given_name: Optional[str] = None,
        family_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        custom_attributes: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Register a new user with email and password.
        
        Args:
            email: User email
            password: User password (must meet pool requirements)
            given_name: First name
            family_name: Last name
            phone_number: Phone number (E.164 format: +972501234567)
            custom_attributes: Custom user attributes
        
        Returns:
            Registration response with user_sub and confirmation status
        
        Raises:
            ClientError: If registration fails
        """
        user_attributes = [
            {'Name': 'email', 'Value': email}
        ]
        
        if given_name:
            user_attributes.append({'Name': 'given_name', 'Value': given_name})
        
        if family_name:
            user_attributes.append({'Name': 'family_name', 'Value': family_name})
        
        if phone_number:
            user_attributes.append({'Name': 'phone_number', 'Value': phone_number})
        
        if custom_attributes:
            for key, value in custom_attributes.items():
                user_attributes.append({'Name': f'custom:{key}', 'Value': value})
        
        try:
            params = {
                'ClientId': self.config.client_id,
                'Username': email,
                'Password': password,
                'UserAttributes': user_attributes
            }
            
            if self.config.client_secret:
                params['SecretHash'] = self._get_secret_hash(email)
            
            response = self.client.sign_up(**params)
            
            logger.info(f"User signed up: {email}")
            
            return {
                'user_sub': response['UserSub'],
                'user_confirmed': response['UserConfirmed'],
                'code_delivery_details': response.get('CodeDeliveryDetails')
            }
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Sign up failed for {email}: {error_code}")
            raise
    
    def confirm_sign_up(self, email: str, confirmation_code: str) -> bool:
        """
        Confirm user registration with verification code.
        
        Args:
            email: User email
            confirmation_code: 6-digit code sent to email
        
        Returns:
            True if confirmation successful
        """
        try:
            params = {
                'ClientId': self.config.client_id,
                'Username': email,
                'ConfirmationCode': confirmation_code
            }
            
            if self.config.client_secret:
                params['SecretHash'] = self._get_secret_hash(email)
            
            self.client.confirm_sign_up(**params)
            
            logger.info(f"User confirmed: {email}")
            return True
        
        except ClientError as e:
            logger.error(f"Confirmation failed for {email}: {e}")
            raise
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Sign in user with email and password.
        
        Args:
            email: User email
            password: User password
        
        Returns:
            Authentication result with tokens
        """
        try:
            params = {
                'ClientId': self.config.client_id,
                'AuthFlow': 'USER_PASSWORD_AUTH',
                'AuthParameters': {
                    'USERNAME': email,
                    'PASSWORD': password
                }
            }
            
            if self.config.client_secret:
                params['AuthParameters']['SECRET_HASH'] = self._get_secret_hash(email)
            
            response = self.client.initiate_auth(**params)
            
            logger.info(f"User signed in: {email}")
            
            return {
                'access_token': response['AuthenticationResult']['AccessToken'],
                'id_token': response['AuthenticationResult']['IdToken'],
                'refresh_token': response['AuthenticationResult']['RefreshToken'],
                'expires_in': response['AuthenticationResult']['ExpiresIn'],
                'token_type': response['AuthenticationResult']['TokenType']
            }
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Sign in failed for {email}: {error_code}")
            raise
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token from sign in
        
        Returns:
            New authentication tokens
        """
        try:
            params = {
                'ClientId': self.config.client_id,
                'AuthFlow': 'REFRESH_TOKEN_AUTH',
                'AuthParameters': {
                    'REFRESH_TOKEN': refresh_token
                }
            }
            
            if self.config.client_secret:
                # For refresh, we need to use a placeholder username
                params['AuthParameters']['SECRET_HASH'] = self._get_secret_hash('refresh')
            
            response = self.client.initiate_auth(**params)
            
            return {
                'access_token': response['AuthenticationResult']['AccessToken'],
                'id_token': response['AuthenticationResult']['IdToken'],
                'expires_in': response['AuthenticationResult']['ExpiresIn'],
                'token_type': response['AuthenticationResult']['TokenType']
            }
        
        except ClientError as e:
            logger.error(f"Token refresh failed: {e}")
            raise
    
    def sign_out(self, access_token: str) -> bool:
        """
        Sign out user (global sign out).
        
        Args:
            access_token: User's access token
        
        Returns:
            True if sign out successful
        """
        try:
            self.client.global_sign_out(AccessToken=access_token)
            logger.info("User signed out")
            return True
        
        except ClientError as e:
            logger.error(f"Sign out failed: {e}")
            raise
    
    def _get_jwks(self) -> Dict:
        """Get JWKS keys for token validation (with caching)."""
        now = datetime.utcnow()
        
        # Check cache
        if (self._jwks_cache and self._jwks_cache_time and 
            now - self._jwks_cache_time < self._jwks_cache_ttl):
            return self._jwks_cache
        
        # Fetch new keys
        response = requests.get(self.config.jwks_url, timeout=10)
        response.raise_for_status()
        
        self._jwks_cache = response.json()
        self._jwks_cache_time = now
        
        return self._jwks_cache
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token (ID token or Access token)
        
        Returns:
            Decoded token claims
        
        Raises:
            JWTError: If token is invalid
        """
        try:
            # Get token header
            headers = jwt.get_unverified_header(token)
            kid = headers['kid']
            
            # Get JWKS
            jwks = self._get_jwks()
            
            # Find matching key
            key = None
            for jwk in jwks['keys']:
                if jwk['kid'] == kid:
                    key = jwk
                    break
            
            if not key:
                raise JWTError("Public key not found in JWKS")
            
            # Verify and decode token
            claims = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=self.config.client_id,
                issuer=self.config.issuer,
                options={
                    'verify_signature': True,
                    'verify_aud': True,
                    'verify_iss': True,
                    'verify_exp': True
                }
            )
            
            # Verify token_use
            if claims.get('token_use') != self.config.token_use:
                raise JWTError(f"Invalid token_use. Expected {self.config.token_use}")
            
            return claims
        
        except JWTError as e:
            logger.error(f"Token verification failed: {e}")
            raise
    
    def get_user_from_token(self, token: str) -> CognitoUser:
        """
        Get user information from JWT token.
        
        Args:
            token: JWT ID token
        
        Returns:
            CognitoUser object
        """
        claims = self.verify_token(token)
        
        return CognitoUser(
            username=claims.get('cognito:username'),
            email=claims.get('email'),
            email_verified=claims.get('email_verified', False),
            sub=claims.get('sub'),
            given_name=claims.get('given_name'),
            family_name=claims.get('family_name'),
            phone_number=claims.get('phone_number'),
            phone_number_verified=claims.get('phone_number_verified', False),
            identities=claims.get('identities'),
            custom_attributes={
                k.replace('custom:', ''): v 
                for k, v in claims.items() 
                if k.startswith('custom:')
            }
        )
    
    def get_user(self, access_token: str) -> CognitoUser:
        """
        Get user information using access token.
        
        Args:
            access_token: User's access token
        
        Returns:
            CognitoUser object
        """
        try:
            response = self.client.get_user(AccessToken=access_token)
            
            # Parse attributes
            attributes = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
            
            return CognitoUser(
                username=response['Username'],
                email=attributes.get('email'),
                email_verified=attributes.get('email_verified') == 'true',
                sub=attributes.get('sub'),
                given_name=attributes.get('given_name'),
                family_name=attributes.get('family_name'),
                phone_number=attributes.get('phone_number'),
                phone_number_verified=attributes.get('phone_number_verified') == 'true',
                custom_attributes={
                    k.replace('custom:', ''): v 
                    for k, v in attributes.items() 
                    if k.startswith('custom:')
                }
            )
        
        except ClientError as e:
            logger.error(f"Get user failed: {e}")
            raise
    
    def forgot_password(self, email: str) -> Dict[str, Any]:
        """
        Initiate forgot password flow.
        
        Args:
            email: User email
        
        Returns:
            Code delivery details
        """
        try:
            params = {
                'ClientId': self.config.client_id,
                'Username': email
            }
            
            if self.config.client_secret:
                params['SecretHash'] = self._get_secret_hash(email)
            
            response = self.client.forgot_password(**params)
            
            logger.info(f"Password reset initiated for: {email}")
            
            return response.get('CodeDeliveryDetails', {})
        
        except ClientError as e:
            logger.error(f"Forgot password failed for {email}: {e}")
            raise
    
    def confirm_forgot_password(
        self,
        email: str,
        confirmation_code: str,
        new_password: str
    ) -> bool:
        """
        Confirm forgot password with code and new password.
        
        Args:
            email: User email
            confirmation_code: Code sent to email
            new_password: New password
        
        Returns:
            True if password reset successful
        """
        try:
            params = {
                'ClientId': self.config.client_id,
                'Username': email,
                'ConfirmationCode': confirmation_code,
                'Password': new_password
            }
            
            if self.config.client_secret:
                params['SecretHash'] = self._get_secret_hash(email)
            
            self.client.confirm_forgot_password(**params)
            
            logger.info(f"Password reset confirmed for: {email}")
            return True
        
        except ClientError as e:
            logger.error(f"Confirm forgot password failed for {email}: {e}")
            raise


# Initialize global Cognito client (configured via environment variables)
def get_cognito_client() -> Optional[CognitoClient]:
    """Get configured Cognito client. Returns None if not configured."""
    user_pool_id = os.getenv('AWS_COGNITO_USER_POOL_ID')
    client_id = os.getenv('AWS_COGNITO_CLIENT_ID')
    
    # If Cognito is not configured, return None
    if not user_pool_id or not client_id:
        return None
    
    try:
        config = CognitoConfig(
            region=os.getenv('AWS_COGNITO_REGION', 'us-east-1'),
            user_pool_id=user_pool_id,
            client_id=client_id,
            client_secret=os.getenv('AWS_COGNITO_CLIENT_SECRET'),
            identity_pool_id=os.getenv('AWS_COGNITO_IDENTITY_POOL_ID'),
            google_client_id=os.getenv('GOOGLE_CLIENT_ID'),
            google_client_secret=os.getenv('GOOGLE_CLIENT_SECRET')
        )
        
        return CognitoClient(config)
    except Exception as e:
        logger.error(f"Failed to initialize Cognito client: {e}")
        return None
