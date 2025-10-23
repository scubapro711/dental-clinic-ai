"""Unit Tests for Google OAuth Service"""

import pytest
from unittest.mock import Mock, patch

from app.services.google_oauth_service import GoogleOAuthService


@pytest.fixture
def oauth_service():
    return GoogleOAuthService(
        client_id="test-client-id",
        client_secret="test-secret",
        redirect_uri="http://localhost/callback"
    )


@pytest.mark.unit
@pytest.mark.services
class TestGoogleOAuthService:
    """Test Google OAuth service."""
    
    def test_init(self, oauth_service):
        """Test service initialization."""
        assert oauth_service.client_id == "test-client-id"
        assert oauth_service.client_secret == "test-secret"
        assert oauth_service.redirect_uri == "http://localhost/callback"
    
    def test_get_authorization_url_no_state(self, oauth_service):
        """Test authorization URL generation without state."""
        url = oauth_service.get_authorization_url()
        
        assert GoogleOAuthService.GOOGLE_AUTH_URL in url
        assert "client_id=test-client-id" in url
        assert "redirect_uri=" in url
    
    def test_get_authorization_url_with_state(self, oauth_service):
        """Test authorization URL generation with state."""
        url = oauth_service.get_authorization_url(state="test-state-123")
        
        assert "state=test-state-123" in url
    
    def test_oauth_urls_constants(self):
        """Test OAuth URL constants."""
        assert GoogleOAuthService.GOOGLE_AUTH_URL == "https://accounts.google.com/o/oauth2/v2/auth"
        assert GoogleOAuthService.GOOGLE_TOKEN_URL == "https://oauth2.googleapis.com/token"
        assert GoogleOAuthService.GOOGLE_USERINFO_URL == "https://www.googleapis.com/oauth2/v2/userinfo"

