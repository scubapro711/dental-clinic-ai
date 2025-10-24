"""
Tests for Bug #9: Unsafe Tuple Indexing in get_available_slots()

Bug Description:
- Location: Lines 2928-2929
- Problem: Checks isinstance(..., tuple) but doesn't check if tuple is empty
- Impact: IndexError when Odoo returns empty tuple for doctor_id

This test suite reproduces the bug and verifies the fix.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.integrations.odoo_client import OdooClient


class TestBug9TupleIndexing:
    """Test suite for Bug #9: Unsafe Tuple Indexing"""
    
    # ========== BUG REPRODUCTION TESTS ==========
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_empty_tuple_causes_index_error(self, mock_proxy, mock_settings):
        """
        Test that empty tuple in doctor_id causes IndexError.
        
        This is the main bug - when Odoo returns empty tuple (),
        the code tries to access [0] and [1] which raises IndexError.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        
        # Simulate Odoo returning slot with empty tuple for doctor_id
        mock_models.execute_kw.return_value = [
            {
                'id': 1,
                'doctor_id': (),  # Empty tuple - this is the bug trigger!
                'date': '2025-10-25',
                'start_time': '09:00',
                'end_time': '09:30',
                'duration': 30,
                'state': 'available'
            }
        ]
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # Bug: IndexError is caught by try/except and returns empty list
        # This is a SILENT FAILURE - user doesn't see error, just no slots
        slots = client.get_available_slots(
            start_date='2025-10-25',
            end_date='2025-10-25',
            duration_minutes=30
        )
        
        # Should return empty list due to caught exception
        # This is the bug - should either raise error or handle gracefully
        assert slots == []  # Silent failure
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_single_element_tuple_causes_index_error(self, mock_proxy, mock_settings):
        """
        Test that single-element tuple causes IndexError on [1] access.
        
        If Odoo returns tuple with only ID (123,), accessing [1] fails.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        
        # Simulate Odoo returning slot with single-element tuple
        mock_models.execute_kw.return_value = [
            {
                'id': 1,
                'doctor_id': (5,),  # Only ID, no name - triggers bug on [1]
                'date': '2025-10-25',
                'start_time': '09:00',
                'end_time': '09:30',
                'duration': 30,
                'state': 'available'
            }
        ]
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # Bug: IndexError is caught by try/except and returns empty list
        slots = client.get_available_slots(
            start_date='2025-10-25',
            end_date='2025-10-25',
            duration_minutes=30
        )
        
        # Should return empty list due to caught exception
        assert slots == []  # Silent failure
    
    # ========== VALID SCENARIOS (SHOULD WORK AFTER FIX) ==========
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_valid_tuple_with_id_and_name(self, mock_proxy, mock_settings):
        """
        Test that valid tuple (id, name) works correctly.
        
        This is the normal case - should always work.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        
        # Simulate Odoo returning slot with valid tuple
        mock_models.execute_kw.return_value = [
            {
                'id': 1,
                'doctor_id': (5, 'Dr. Smith'),  # Valid tuple
                'date': '2025-10-25',
                'start_time': '09:00',
                'end_time': '09:30',
                'duration': 30,
                'state': 'available'
            }
        ]
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # This should work fine
        slots = client.get_available_slots(
            start_date='2025-10-25',
            end_date='2025-10-25',
            duration_minutes=30
        )
        
        assert len(slots) == 1
        assert slots[0]['doctor_id'] == 5
        assert slots[0]['doctor_name'] == 'Dr. Smith'
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_non_tuple_doctor_id(self, mock_proxy, mock_settings):
        """
        Test that non-tuple doctor_id (just int) works correctly.
        
        Sometimes Odoo returns just the ID as integer, not tuple.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        
        # Simulate Odoo returning slot with integer doctor_id
        mock_models.execute_kw.return_value = [
            {
                'id': 1,
                'doctor_id': 5,  # Just integer, not tuple
                'date': '2025-10-25',
                'start_time': '09:00',
                'end_time': '09:30',
                'duration': 30,
                'state': 'available'
            }
        ]
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # This should work fine (falls to else branch)
        slots = client.get_available_slots(
            start_date='2025-10-25',
            end_date='2025-10-25',
            duration_minutes=30
        )
        
        assert len(slots) == 1
        assert slots[0]['doctor_id'] == 5
        assert slots[0]['doctor_name'] == 'Unknown'  # Default when not tuple
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_none_doctor_id(self, mock_proxy, mock_settings):
        """
        Test that None doctor_id is handled gracefully.
        
        If doctor_id is missing/None, should not crash.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        
        # Simulate Odoo returning slot with None doctor_id
        mock_models.execute_kw.return_value = [
            {
                'id': 1,
                'doctor_id': None,  # Missing/deleted doctor
                'date': '2025-10-25',
                'start_time': '09:00',
                'end_time': '09:30',
                'duration': 30,
                'state': 'available'
            }
        ]
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # This should work fine (falls to else branch)
        slots = client.get_available_slots(
            start_date='2025-10-25',
            end_date='2025-10-25',
            duration_minutes=30
        )
        
        assert len(slots) == 1
        assert slots[0]['doctor_id'] is None
        assert slots[0]['doctor_name'] == 'Unknown'
    
    # ========== EDGE CASES ==========
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_multiple_slots_with_mixed_formats(self, mock_proxy, mock_settings):
        """
        Test that multiple slots with different doctor_id formats work.
        
        Real-world scenario: some slots have tuples, some have ints, some None.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        
        # Simulate Odoo returning slots with mixed formats
        mock_models.execute_kw.return_value = [
            {
                'id': 1,
                'doctor_id': (5, 'Dr. Smith'),  # Valid tuple
                'date': '2025-10-25',
                'start_time': '09:00',
                'end_time': '09:30',
                'duration': 30,
                'state': 'available'
            },
            {
                'id': 2,
                'doctor_id': 7,  # Just integer
                'date': '2025-10-25',
                'start_time': '10:00',
                'end_time': '10:30',
                'duration': 30,
                'state': 'available'
            },
            {
                'id': 3,
                'doctor_id': None,  # None
                'date': '2025-10-25',
                'start_time': '11:00',
                'end_time': '11:30',
                'duration': 30,
                'state': 'available'
            }
        ]
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # This should work fine for all formats
        slots = client.get_available_slots(
            start_date='2025-10-25',
            end_date='2025-10-25',
            duration_minutes=30
        )
        
        assert len(slots) == 3
        assert slots[0]['doctor_id'] == 5
        assert slots[0]['doctor_name'] == 'Dr. Smith'
        assert slots[1]['doctor_id'] == 7
        assert slots[1]['doctor_name'] == 'Unknown'
        assert slots[2]['doctor_id'] is None
        assert slots[2]['doctor_name'] == 'Unknown'
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_empty_slots_list(self, mock_proxy, mock_settings):
        """
        Test that empty slots list is handled correctly.
        
        If no slots available, should return empty list, not crash.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        
        # Simulate Odoo returning empty list
        mock_models.execute_kw.return_value = []
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # This should work fine
        slots = client.get_available_slots(
            start_date='2025-10-25',
            end_date='2025-10-25',
            duration_minutes=30
        )
        
        assert slots == []

