"""
Unit Tests for Email Service

Tests email sending functionality including:
- Verification emails
- Welcome emails
- AWS SES integration
- Development mode (console logging)
- Token generation
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import os

from app.services.email_service import EmailService


@pytest.fixture
def service_dev_mode():
    """Create EmailService instance in development mode."""
    with patch.dict(os.environ, {'USE_AWS_SES': 'false'}):
        return EmailService()


@pytest.fixture
def service_ses_mode():
    """Create EmailService instance with SES enabled."""
    with patch.dict(os.environ, {'USE_AWS_SES': 'true', 'AWS_REGION': 'us-east-1'}):
        with patch('boto3.client') as mock_boto:
            mock_ses = Mock()
            mock_boto.return_value = mock_ses
            service = EmailService()
            service.ses_client = mock_ses
            return service


@pytest.mark.unit
@pytest.mark.services
class TestEmailService:
    """Test Email Service."""
    
    def test_init_dev_mode(self, service_dev_mode):
        """Test service initialization in development mode."""
        assert service_dev_mode is not None
        assert service_dev_mode.use_ses is False
        assert service_dev_mode.from_email == "noreply@dentaflow.ai"
        assert service_dev_mode.frontend_url == "http://localhost:3000"
    
    def test_init_ses_mode(self, service_ses_mode):
        """Test service initialization with SES enabled."""
        assert service_ses_mode is not None
        assert service_ses_mode.use_ses is True
        assert hasattr(service_ses_mode, 'ses_client')
    
    def test_init_with_custom_env_vars(self):
        """Test initialization with custom environment variables."""
        with patch.dict(os.environ, {
            'FROM_EMAIL': 'custom@example.com',
            'FRONTEND_URL': 'https://example.com',
            'USE_AWS_SES': 'false'
        }):
            service = EmailService()
            assert service.from_email == 'custom@example.com'
            assert service.frontend_url == 'https://example.com'
    
    def test_generate_verification_token(self, service_dev_mode):
        """Test verification token generation."""
        token1 = service_dev_mode.generate_verification_token()
        token2 = service_dev_mode.generate_verification_token()
        
        # Tokens should be strings
        assert isinstance(token1, str)
        assert isinstance(token2, str)
        
        # Tokens should be non-empty
        assert len(token1) > 0
        assert len(token2) > 0
        
        # Tokens should be unique
        assert token1 != token2
        
        # Tokens should be URL-safe
        assert all(c.isalnum() or c in '-_' for c in token1)
    
    @pytest.mark.asyncio
    async def test_send_verification_email_dev_mode(self, service_dev_mode):
        """Test sending verification email in development mode."""
        result = await service_dev_mode.send_verification_email(
            to_email="test@example.com",
            user_name="Test User",
            verification_token="test_token_123"
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_send_verification_email_ses_mode(self, service_ses_mode):
        """Test sending verification email via AWS SES."""
        # Mock SES response
        service_ses_mode.ses_client.send_email.return_value = {
            'MessageId': 'test-message-id-123'
        }
        
        result = await service_ses_mode.send_verification_email(
            to_email="test@example.com",
            user_name="Test User",
            verification_token="test_token_123"
        )
        
        assert result is True
        service_ses_mode.ses_client.send_email.assert_called_once()
        
        # Verify call arguments
        call_args = service_ses_mode.ses_client.send_email.call_args[1]
        assert call_args['Destination']['ToAddresses'] == ['test@example.com']
        assert 'test_token_123' in call_args['Message']['Body']['Html']['Data']
    
    @pytest.mark.asyncio
    async def test_send_verification_email_ses_failure(self, service_ses_mode):
        """Test handling SES send failure."""
        # Mock SES to raise exception
        service_ses_mode.ses_client.send_email.side_effect = Exception("SES Error")
        
        result = await service_ses_mode.send_verification_email(
            to_email="test@example.com",
            user_name="Test User",
            verification_token="test_token_123"
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_welcome_email_dev_mode(self, service_dev_mode):
        """Test sending welcome email in development mode."""
        result = await service_dev_mode.send_welcome_email(
            to_email="test@example.com",
            user_name="Test User"
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_send_welcome_email_ses_mode(self, service_ses_mode):
        """Test sending welcome email via AWS SES."""
        service_ses_mode.ses_client.send_email.return_value = {
            'MessageId': 'welcome-message-id-456'
        }
        
        result = await service_ses_mode.send_welcome_email(
            to_email="test@example.com",
            user_name="Test User"
        )
        
        assert result is True
        service_ses_mode.ses_client.send_email.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_verification_email_contains_user_name(self, service_dev_mode):
        """Test that verification email includes user name."""
        with patch.object(service_dev_mode, '_send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            await service_dev_mode.send_verification_email(
                to_email="test@example.com",
                user_name="John Doe",
                verification_token="token123"
            )
            
            # Verify _send_email was called
            mock_send.assert_called_once()
            
            # Check that user name is in the email body
            call_args = mock_send.call_args[0]
            html_body = call_args[2]
            text_body = call_args[3]
            
            assert "John Doe" in html_body
            assert "John Doe" in text_body
    
    @pytest.mark.asyncio
    async def test_verification_email_contains_token_url(self, service_dev_mode):
        """Test that verification email includes token in URL."""
        with patch.object(service_dev_mode, '_send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            token = "secure_token_xyz"
            await service_dev_mode.send_verification_email(
                to_email="test@example.com",
                user_name="Test User",
                verification_token=token
            )
            
            call_args = mock_send.call_args[0]
            html_body = call_args[2]
            text_body = call_args[3]
            
            expected_url = f"{service_dev_mode.frontend_url}/auth/verify-email?token={token}"
            assert expected_url in html_body
            assert expected_url in text_body
    
    @pytest.mark.asyncio
    async def test_welcome_email_contains_login_link(self, service_dev_mode):
        """Test that welcome email includes login link."""
        with patch.object(service_dev_mode, '_send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            await service_dev_mode.send_welcome_email(
                to_email="test@example.com",
                user_name="Test User"
            )
            
            call_args = mock_send.call_args[0]
            html_body = call_args[2]
            text_body = call_args[3]
            
            login_url = f"{service_dev_mode.frontend_url}/login"
            assert login_url in html_body
            assert login_url in text_body
    
    @pytest.mark.asyncio
    async def test_email_subjects_are_in_hebrew(self, service_dev_mode):
        """Test that email subjects are in Hebrew."""
        with patch.object(service_dev_mode, '_send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            
            # Test verification email
            await service_dev_mode.send_verification_email(
                to_email="test@example.com",
                user_name="Test",
                verification_token="token"
            )
            
            subject = mock_send.call_args[0][1]
            # Should contain Hebrew characters
            assert any('\u0590' <= c <= '\u05FF' for c in subject)
            
            # Test welcome email
            mock_send.reset_mock()
            await service_dev_mode.send_welcome_email(
                to_email="test@example.com",
                user_name="Test"
            )
            
            subject = mock_send.call_args[0][1]
            assert any('\u0590' <= c <= '\u05FF' for c in subject)
    
    @pytest.mark.asyncio
    async def test_send_email_internal_method_dev_mode(self, service_dev_mode):
        """Test internal _send_email method in dev mode."""
        result = await service_dev_mode._send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_body="<p>Test HTML</p>",
            text_body="Test Text"
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_send_email_internal_method_ses_mode(self, service_ses_mode):
        """Test internal _send_email method with SES."""
        service_ses_mode.ses_client.send_email.return_value = {
            'MessageId': 'msg-123'
        }
        
        result = await service_ses_mode._send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_body="<p>Test HTML</p>",
            text_body="Test Text"
        )
        
        assert result is True
        
        # Verify SES was called with correct parameters
        call_kwargs = service_ses_mode.ses_client.send_email.call_args[1]
        assert call_kwargs['Source'] == service_ses_mode.from_email
        assert call_kwargs['Destination']['ToAddresses'] == ['test@example.com']
        assert call_kwargs['Message']['Subject']['Data'] == 'Test Subject'
        assert call_kwargs['Message']['Body']['Html']['Data'] == '<p>Test HTML</p>'
        assert call_kwargs['Message']['Body']['Text']['Data'] == 'Test Text'
    
    def test_singleton_instance_exists(self):
        """Test that singleton email_service instance exists."""
        from app.services.email_service import email_service
        assert email_service is not None
        assert isinstance(email_service, EmailService)

