"""
Test for Bug #1: Global Socket Timeout

This test reproduces the bug where OdooClient.setdefaulttimeout()
modifies the global socket timeout, affecting all connections in the system.

Bug Report: BUG_REPORT_odoo_client.md - Bug #1
"""

import socket
import pytest
from unittest.mock import patch, MagicMock
from app.integrations.odoo_client import OdooClient


class TestBug1GlobalSocketTimeout:
    """Test suite for Bug #1: Global Socket Timeout"""
    
    def test_socket_timeout_before_odoo_client(self):
        """Test that socket timeout is None before OdooClient creation."""
        # Reset to default
        socket.setdefaulttimeout(None)
        
        # Verify default is None
        assert socket.getdefaulttimeout() is None
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_socket_timeout_modified_by_odoo_client(self, mock_proxy, mock_settings):
        """
        Test that OdooClient modifies global socket timeout.
        
        This is the BUG - it should NOT modify global timeout!
        """
        # Setup
        socket.setdefaulttimeout(None)
        mock_settings.ODOO_URL = "http://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "admin"
        
        # Verify timeout is None before
        assert socket.getdefaulttimeout() is None
        
        # Create OdooClient
        try:
            client = OdooClient()
        except Exception:
            pass  # Connection may fail, that's OK
        
        # AFTER FIX: Global timeout should still be None!
        timeout_after = socket.getdefaulttimeout()
        
        # Verify the bug is FIXED
        assert timeout_after is None, (
            f"BUG STILL EXISTS: OdooClient modified global socket timeout to {timeout_after}! "
            "This affects ALL socket connections in the system."
        )
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_multiple_odoo_clients_race_condition(self, mock_proxy, mock_settings):
        """
        Test that multiple OdooClient instances cause race condition.
        
        Each instance modifies the global timeout, causing unpredictable behavior.
        """
        # Setup
        socket.setdefaulttimeout(None)
        mock_settings.ODOO_URL = "http://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "admin"
        
        # Create multiple clients
        try:
            client1 = OdooClient()
            timeout1 = socket.getdefaulttimeout()
            
            client2 = OdooClient()
            timeout2 = socket.getdefaulttimeout()
            
            # BUG: Both set the same global timeout
            if timeout1 == 10.0 and timeout2 == 10.0:
                pytest.fail(
                    "BUG CONFIRMED: Multiple OdooClient instances all modify "
                    "the same global socket timeout!"
                )
        except Exception:
            # Connection may fail, but we can still check timeout
            if socket.getdefaulttimeout() == 10.0:
                pytest.fail("BUG CONFIRMED: Global timeout modified!")
    
    @patch('app.integrations.odoo_client.settings')
    def test_socket_timeout_should_be_per_connection(self, mock_settings):
        """
        Test that socket timeout should be per-connection, not global.
        
        This test defines the EXPECTED behavior after fix.
        Currently this test will FAIL (showing the bug).
        After fix, this test should PASS.
        """
        # Setup
        socket.setdefaulttimeout(None)
        mock_settings.ODOO_URL = "http://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "admin"
        
        try:
            # Create OdooClient
            client = OdooClient()
            
            # EXPECTED: Global timeout should still be None
            # (timeout should be per-connection only)
            timeout_after = socket.getdefaulttimeout()
            
            assert timeout_after is None, (
                f"Expected global timeout to remain None, "
                f"but got {timeout_after}. "
                f"Timeout should be per-connection, not global!"
            )
            
        except Exception as e:
            # If connection fails, that's OK for this test
            # We only care about the global timeout
            timeout_after = socket.getdefaulttimeout()
            
            assert timeout_after is None, (
                f"Expected global timeout to remain None even after error, "
                f"but got {timeout_after}"
            )
    
    def teardown_method(self):
        """Reset socket timeout after each test."""
        socket.setdefaulttimeout(None)

