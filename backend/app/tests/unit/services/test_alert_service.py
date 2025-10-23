"""
Unit Tests for Alert Service

Tests alert/notification functionality including:
- Email alert sending
- Alert type handling
- HTML email generation
- SMTP configuration
- Convenience alert methods
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from smtplib import SMTP

from app.services.alert_service import AlertService, AlertType, get_alert_service


@pytest.fixture
def service_configured():
    """Create AlertService with proper configuration."""
    with patch.dict(os.environ, {
        'SMTP_HOST': 'smtp.test.com',
        'SMTP_PORT': '587',
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'test_password',
        'ADMIN_ALERT_EMAILS': 'admin1@example.com,admin2@example.com'
    }):
        return AlertService()


@pytest.fixture
def service_unconfigured():
    """Create AlertService without configuration."""
    with patch.dict(os.environ, {}, clear=True):
        return AlertService()


@pytest.mark.unit
@pytest.mark.services
class TestAlertService:
    """Test Alert Service."""
    
    def test_init_configured(self, service_configured):
        """Test service initialization with configuration."""
        assert service_configured is not None
        assert service_configured.smtp_host == 'smtp.test.com'
        assert service_configured.smtp_port == 587
        assert service_configured.smtp_user == 'test@example.com'
        assert service_configured.smtp_password == 'test_password'
        assert len(service_configured.admin_emails) == 2
        assert 'admin1@example.com' in service_configured.admin_emails
        assert 'admin2@example.com' in service_configured.admin_emails
    
    def test_init_unconfigured(self, service_unconfigured):
        """Test service initialization without configuration."""
        assert service_unconfigured is not None
        assert service_unconfigured.smtp_host == 'smtp.gmail.com'  # Default
        assert service_unconfigured.smtp_port == 587  # Default
        assert service_unconfigured.admin_emails == []
    
    def test_init_with_whitespace_in_emails(self):
        """Test that email whitespace is properly handled."""
        with patch.dict(os.environ, {
            'ADMIN_ALERT_EMAILS': ' admin1@example.com , admin2@example.com , '
        }):
            service = AlertService()
            assert len(service.admin_emails) == 2
            assert 'admin1@example.com' in service.admin_emails
            assert 'admin2@example.com' in service.admin_emails
    
    def test_is_configured_true(self, service_configured):
        """Test is_configured returns True when properly configured."""
        assert service_configured.is_configured() is True
    
    def test_is_configured_false_no_smtp_user(self):
        """Test is_configured returns False without SMTP user."""
        with patch.dict(os.environ, {
            'SMTP_PASSWORD': 'password',
            'ADMIN_ALERT_EMAILS': 'admin@example.com'
        }):
            service = AlertService()
            assert service.is_configured() is False
    
    def test_is_configured_false_no_smtp_password(self):
        """Test is_configured returns False without SMTP password."""
        with patch.dict(os.environ, {
            'SMTP_USER': 'user@example.com',
            'ADMIN_ALERT_EMAILS': 'admin@example.com'
        }):
            service = AlertService()
            assert service.is_configured() is False
    
    def test_is_configured_false_no_admin_emails(self):
        """Test is_configured returns False without admin emails."""
        with patch.dict(os.environ, {
            'SMTP_USER': 'user@example.com',
            'SMTP_PASSWORD': 'password'
        }):
            service = AlertService()
            assert service.is_configured() is False
    
    def test_send_alert_not_configured(self, service_unconfigured):
        """Test send_alert returns False when not configured."""
        result = service_unconfigured.send_alert(
            alert_type=AlertType.SYSTEM_ERROR,
            subject="Test Alert",
            message="Test message"
        )
        assert result is False
    
    def test_send_alert_no_recipients(self, service_configured):
        """Test send_alert returns False with no recipients."""
        service_configured.admin_emails = []
        result = service_configured.send_alert(
            alert_type=AlertType.SYSTEM_ERROR,
            subject="Test Alert",
            message="Test message"
        )
        assert result is False
    
    def test_send_alert_success(self, service_configured):
        """Test successful alert sending."""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = service_configured.send_alert(
                alert_type=AlertType.NEW_SIGNUP,
                subject="Test Alert",
                message="Test message",
                data={"key": "value"}
            )
            
            assert result is True
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with('test@example.com', 'test_password')
            mock_server.send_message.assert_called_once()
    
    def test_send_alert_smtp_failure(self, service_configured):
        """Test alert sending handles SMTP failures."""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.return_value.__enter__.side_effect = Exception("SMTP Error")
            
            result = service_configured.send_alert(
                alert_type=AlertType.SYSTEM_ERROR,
                subject="Test Alert",
                message="Test message"
            )
            
            assert result is False
    
    def test_send_alert_custom_recipients(self, service_configured):
        """Test sending alert to custom recipients."""
        custom_recipients = ['custom1@example.com', 'custom2@example.com']
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = service_configured.send_alert(
                alert_type=AlertType.HIGH_USAGE,
                subject="Test Alert",
                message="Test message",
                recipients=custom_recipients
            )
            
            assert result is True
            # Verify send_message was called (recipients are in the message)
            mock_server.send_message.assert_called_once()
    
    def test_create_html_body_basic(self, service_configured):
        """Test HTML body creation."""
        html = service_configured._create_html_body(
            alert_type=AlertType.NEW_SIGNUP,
            subject="Test Subject",
            message="Test Message",
            data=None
        )
        
        assert "Test Subject" in html
        assert "Test Message" in html
        assert "DentaFlow Alert" in html
        assert "<!DOCTYPE html>" in html
    
    def test_create_html_body_with_data(self, service_configured):
        """Test HTML body creation with data table."""
        data = {
            "Organization": "Test Clinic",
            "Amount": "$100.00",
            "Status": "Active"
        }
        
        html = service_configured._create_html_body(
            alert_type=AlertType.PAYMENT_FAILED,
            subject="Payment Issue",
            message="Payment failed",
            data=data
        )
        
        assert "Test Clinic" in html
        assert "$100.00" in html
        assert "Active" in html
        assert "Details:" in html
    
    def test_create_html_body_color_coding(self, service_configured):
        """Test that different alert types have different colors."""
        html_error = service_configured._create_html_body(
            AlertType.SYSTEM_ERROR, "Error", "Message"
        )
        html_signup = service_configured._create_html_body(
            AlertType.NEW_SIGNUP, "Signup", "Message"
        )
        
        # Both should contain color codes but different ones
        assert "#dc2626" in html_error  # Red for error
        assert "#10b981" in html_signup  # Green for signup
    
    def test_alert_payment_failed(self, service_configured):
        """Test payment failed convenience method."""
        with patch.object(service_configured, 'send_alert') as mock_send:
            mock_send.return_value = True
            
            result = service_configured.alert_payment_failed(
                organization_name="Test Clinic",
                amount=99.99,
                error_message="Card declined"
            )
            
            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args[1]
            assert call_args['alert_type'] == AlertType.PAYMENT_FAILED
            assert "Test Clinic" in call_args['subject']
            assert call_args['data']['Amount'] == "$99.99"
            assert call_args['data']['Error'] == "Card declined"
    
    def test_alert_subscription_canceled(self, service_configured):
        """Test subscription canceled convenience method."""
        with patch.object(service_configured, 'send_alert') as mock_send:
            mock_send.return_value = True
            
            result = service_configured.alert_subscription_canceled(
                organization_name="Test Clinic",
                plan_tier="Professional",
                mrr_impact=299.00
            )
            
            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args[1]
            assert call_args['alert_type'] == AlertType.SUBSCRIPTION_CANCELED
            assert call_args['data']['Plan'] == "Professional"
            assert "-$299.00" in call_args['data']['MRR Impact']
    
    def test_alert_trial_ending(self, service_configured):
        """Test trial ending convenience method."""
        with patch.object(service_configured, 'send_alert') as mock_send:
            mock_send.return_value = True
            
            result = service_configured.alert_trial_ending(
                organization_name="Test Clinic",
                days_remaining=3
            )
            
            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args[1]
            assert call_args['alert_type'] == AlertType.TRIAL_ENDING
            assert call_args['data']['Days Remaining'] == 3
    
    def test_alert_high_usage(self, service_configured):
        """Test high usage convenience method."""
        with patch.object(service_configured, 'send_alert') as mock_send:
            mock_send.return_value = True
            
            result = service_configured.alert_high_usage(
                organization_name="Test Clinic",
                metric_type="API Calls",
                current_value=15000,
                threshold=10000
            )
            
            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args[1]
            assert call_args['alert_type'] == AlertType.HIGH_USAGE
            assert call_args['data']['Current Value'] == 15000
            assert call_args['data']['Threshold'] == 10000
            assert "150.0%" in call_args['data']['Percentage']
    
    def test_alert_high_cost(self, service_configured):
        """Test high cost convenience method."""
        with patch.object(service_configured, 'send_alert') as mock_send:
            mock_send.return_value = True
            
            result = service_configured.alert_high_cost(
                service_name="OpenAI API",
                current_cost=500.00,
                previous_cost=300.00,
                increase_percentage=66.7
            )
            
            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args[1]
            assert call_args['alert_type'] == AlertType.HIGH_COST
            assert "$500.00" in call_args['data']['Current Cost']
            assert "$300.00" in call_args['data']['Previous Cost']
    
    def test_alert_new_signup(self, service_configured):
        """Test new signup convenience method."""
        with patch.object(service_configured, 'send_alert') as mock_send:
            mock_send.return_value = True
            
            result = service_configured.alert_new_signup(
                organization_name="New Clinic",
                plan_tier="Starter",
                trial_days=14
            )
            
            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args[1]
            assert call_args['alert_type'] == AlertType.NEW_SIGNUP
            assert call_args['data']['Plan'] == "Starter"
            assert "14 days" in call_args['data']['Trial Duration']
    
    def test_alert_churn_risk(self, service_configured):
        """Test churn risk convenience method."""
        with patch.object(service_configured, 'send_alert') as mock_send:
            mock_send.return_value = True
            
            reasons = [
                "Low usage in past 30 days",
                "No logins in 2 weeks",
                "Support tickets unresolved"
            ]
            
            result = service_configured.alert_churn_risk(
                organization_name="At Risk Clinic",
                risk_score=85.5,
                reasons=reasons
            )
            
            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args[1]
            assert call_args['alert_type'] == AlertType.CHURN_RISK
            # Risk score is formatted as integer percentage
            assert "86%" in call_args['data']['Risk Score'] or "85%" in call_args['data']['Risk Score']
            assert "<ul>" in call_args['message']
            assert "Low usage" in call_args['message']
    
    def test_alert_type_enum_values(self):
        """Test that AlertType enum has expected values."""
        assert AlertType.PAYMENT_FAILED == "payment_failed"
        assert AlertType.SUBSCRIPTION_CANCELED == "subscription_canceled"
        assert AlertType.TRIAL_ENDING == "trial_ending"
        assert AlertType.HIGH_USAGE == "high_usage"
        assert AlertType.HIGH_COST == "high_cost"
        assert AlertType.SYSTEM_ERROR == "system_error"
        assert AlertType.NEW_SIGNUP == "new_signup"
        assert AlertType.CHURN_RISK == "churn_risk"
    
    def test_get_alert_service_singleton(self):
        """Test that get_alert_service returns singleton instance."""
        service1 = get_alert_service()
        service2 = get_alert_service()
        
        assert service1 is not None
        assert service1 is service2  # Same instance
        assert isinstance(service1, AlertService)

