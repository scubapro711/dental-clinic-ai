"""
Test for Bug #2: Password Stored in Plain Text

This test reproduces the security bug where OdooClient stores password
in plain text in memory and sends it with EVERY request to Odoo.

Bug Report: BUG_REPORT_odoo_client.md - Bug #2
"""

import pytest
import logging
from unittest.mock import patch, MagicMock, call
from app.integrations.odoo_client import OdooClient


class TestBug2PasswordSecurity:
    """Test suite for Bug #2: Password in Plain Text"""
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_password_stored_in_memory(self, mock_proxy, mock_settings):
        """
        Test that password is stored in plain text in memory.
        
        NOTE: This is NOT a bug - it's a limitation of Odoo XML-RPC API.
        Odoo requires password for every request.
        
        Mitigation:
        - Use HTTPS to encrypt password in transit
        - Use PasswordFilter to prevent password in logs
        - Rotate passwords regularly
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"  # Use HTTPS!
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "super_secret_password_123"
        
        mock_common = MagicMock()
        mock_models = MagicMock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        
        # Password is stored (required by Odoo XML-RPC API)
        assert hasattr(client, 'password')
        assert client.password == "super_secret_password_123"
        
        # This is acceptable IF:
        # 1. HTTPS is used (password encrypted in transit)
        # 2. Password is not logged (PasswordFilter applied)
        # 3. Strong password is used
        # 4. Password is rotated regularly
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_password_sent_in_every_request(self, mock_proxy, mock_settings):
        """
        Test that password is sent with EVERY request to Odoo.
        
        NOTE: This is NOT a bug - it's how Odoo XML-RPC API works.
        Odoo does not support session tokens in XML-RPC.
        
        Mitigation:
        - HTTPS encrypts password in transit
        - PasswordFilter prevents password in logs
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"  # Use HTTPS!
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "super_secret_password_123"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = [1, 2, 3]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client and authenticate
        client = OdooClient()
        client.authenticate()
        
        # Make a search request
        client.search('res.partner', [])
        
        # Password is sent in the request (required by Odoo)
        call_args = mock_models.execute_kw.call_args
        assert call_args is not None
        
        # Check if password is in the arguments
        args = call_args[0]
        password_in_args = "super_secret_password_123" in str(args)
        
        # This is expected behavior for Odoo XML-RPC
        assert password_in_args, "Password should be sent (required by Odoo XML-RPC)"
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_password_not_in_logs(self, mock_proxy, mock_settings, caplog):
        """
        Test that password does NOT appear in logs.
        
        This test defines the EXPECTED behavior.
        Currently may FAIL if logging is enabled.
        """
        # Setup
        mock_settings.ODOO_URL = "http://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "super_secret_password_123"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = [1, 2, 3]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Enable DEBUG logging
        caplog.set_level(logging.DEBUG)
        
        # Create client and make requests
        client = OdooClient()
        client.authenticate()
        client.search('res.partner', [])
        
        # Check logs
        log_text = caplog.text.lower()
        
        # Password should NOT appear in logs!
        assert "super_secret_password_123" not in log_text, (
            "SECURITY VIOLATION: Password found in logs! "
            "This is a HIPAA violation."
        )
        
        # Password should NOT appear even in partial form
        assert "secret_password" not in log_text
        assert "password_123" not in log_text
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_https_warning_when_not_using_https(self, mock_proxy, mock_settings, caplog):
        """
        Test that client warns when not using HTTPS.
        
        This is important for security - password should be encrypted in transit.
        """
        # Setup with HTTP (not HTTPS)
        mock_settings.ODOO_URL = "http://localhost:8069"  # HTTP, not HTTPS!
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "super_secret_password_123"
        
        mock_common = MagicMock()
        mock_models = MagicMock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Enable WARNING logging
        caplog.set_level(logging.WARNING)
        
        # Create client
        client = OdooClient()
        
        # Should have warning about not using HTTPS
        assert any("SECURITY WARNING" in record.message for record in caplog.records)
        assert any("HTTPS" in record.message for record in caplog.records)
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_https_no_warning_when_using_https(self, mock_proxy, mock_settings, caplog):
        """
        Test that client does NOT warn when using HTTPS.
        
        HTTPS encrypts password in transit, which is the correct approach.
        """
        # Setup with HTTPS
        mock_settings.ODOO_URL = "https://localhost:8069"  # HTTPS!
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "super_secret_password_123"
        
        mock_common = MagicMock()
        mock_models = MagicMock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Enable WARNING logging
        caplog.set_level(logging.WARNING)
        
        # Create client
        client = OdooClient()
        
        # Should NOT have warning about HTTPS (because we're using it)
        https_warnings = [r for r in caplog.records if "HTTPS" in r.message and "WARNING" in r.levelname]
        assert len(https_warnings) == 0, "Should not warn when using HTTPS"

