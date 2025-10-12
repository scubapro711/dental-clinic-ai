"""
Google OAuth 2.0 Service.

Handles Google Sign-In integration.
"""

import httpx
from typing import Optional, Dict
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class GoogleOAuthService:
    """Service for Google OAuth 2.0 authentication."""
    
    # Google OAuth URLs
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize Google OAuth service.
        
        Args:
            client_id: Google OAuth Client ID
            client_secret: Google OAuth Client Secret
            redirect_uri: Redirect URI after authentication
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate Google OAuth authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL to redirect user to
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        if state:
            params["state"] = state
        
        # Build URL
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.GOOGLE_AUTH_URL}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, str]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from Google
            
        Returns:
            Dictionary containing access_token, id_token, etc.
            
        Raises:
            HTTPException: If token exchange fails
        """
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.GOOGLE_TOKEN_URL,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Google token exchange failed: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to exchange code for token"
                    )
                
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during token exchange: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google authentication service unavailable"
            )
    
    async def get_user_info(self, access_token: str) -> Dict[str, any]:
        """
        Get user information from Google using access token.
        
        Args:
            access_token: Google access token
            
        Returns:
            Dictionary containing user info (email, name, picture, etc.)
            
        Raises:
            HTTPException: If user info retrieval fails
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.GOOGLE_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Google userinfo request failed: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to get user information"
                    )
                
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during userinfo request: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google authentication service unavailable"
            )
    
    async def authenticate(self, code: str) -> Dict[str, any]:
        """
        Complete Google OAuth flow: exchange code and get user info.
        
        Args:
            code: Authorization code from Google
            
        Returns:
            Dictionary containing user info
        """
        # Exchange code for tokens
        token_data = await self.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token received"
            )
        
        # Get user information
        user_info = await self.get_user_info(access_token)
        
        return {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "given_name": user_info.get("given_name"),
            "family_name": user_info.get("family_name"),
            "picture": user_info.get("picture"),
            "email_verified": user_info.get("verified_email", False),
            "google_id": user_info.get("id")
        }
