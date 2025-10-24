"""
Tests for Bug #10: Unsafe List Indexing in get_treatment_revenue()

Bug Description:
- Location: Lines 1825-1826
- Problem: Checks isinstance(..., list) but doesn't check list length
- Impact: IndexError when Odoo returns empty list or single-element list for product_id

This test suite reproduces the bug and verifies the fix.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.integrations.odoo_client import OdooClient


class TestBug10ListIndexing:
    """Test suite for Bug #10: Unsafe List Indexing"""
    
    # ========== BUG REPRODUCTION TESTS ==========
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_empty_list_causes_index_error(self, mock_proxy, mock_settings):
        """
        Test that empty list in product_id causes IndexError.
        
        This is the main bug - when Odoo returns empty list [],
        the code tries to access [0] which raises IndexError.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        
        # Simulate Odoo returning invoice lines with empty list for product_id
        mock_models.execute_kw.return_value = [
            {
                'id': 1,
                'product_id': [],  # Empty list - this is the bug trigger!
                'quantity': 1,
                'price_unit': 100.0,
                'price_subtotal': 100.0
            }
        ]
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # Bug: IndexError is caught by try/except and returns empty list
        # This is a SILENT FAILURE - user doesn't see error, just no revenue data
        revenue = client.get_treatment_revenue(
            date_from='2025-10-01',
            date_to='2025-10-31'
        )
        
        # Should return empty list due to caught exception
        assert revenue == []  # Silent failure
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_single_element_list_causes_index_error(self, mock_proxy, mock_settings):
        """
        Test that single-element list causes IndexError on [1] access.
        
        If Odoo returns list with only ID [123], accessing [1] fails.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        
        # Simulate Odoo returning invoice lines with single-element list
        mock_models.execute_kw.return_value = [
            {
                'id': 1,
                'product_id': [5],  # Only ID, no name - triggers bug on [1]
                'quantity': 1,
                'price_unit': 100.0,
                'price_subtotal': 100.0
            }
        ]
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # Bug: IndexError is caught by try/except and returns empty list
        revenue = client.get_treatment_revenue(
            date_from='2025-10-01',
            date_to='2025-10-31'
        )
        
        # Should return empty list due to caught exception
        assert revenue == []  # Silent failure
    
    # ========== VALID SCENARIOS (SHOULD WORK AFTER FIX) ==========
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_valid_list_with_id_and_name(self, mock_proxy, mock_settings):
        """
        Test that valid list [id, name] works correctly.
        
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
        
        # Simulate Odoo returning invoice lines with valid list
        mock_models.execute_kw.return_value = [
            {
                'id': 1,
                'product_id': [5, 'Dental Cleaning'],  # Valid list
                'quantity': 1,
                'price_unit': 100.0,
                'price_subtotal': 100.0
            }
        ]
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # This should work fine
        revenue = client.get_treatment_revenue(
            date_from='2025-10-01',
            date_to='2025-10-31'
        )
        
        assert len(revenue) == 1
        assert revenue[0]['product_id'] == 5
        assert revenue[0]['product_name'] == 'Dental Cleaning'
        assert revenue[0]['revenue'] == 100.0
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_non_list_product_id(self, mock_proxy, mock_settings):
        """
        Test that non-list product_id (just int) works correctly.
        
        Sometimes Odoo returns just the ID as integer, not list.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        
        # Simulate Odoo returning invoice lines with integer product_id
        mock_models.execute_kw.return_value = [
            {
                'id': 1,
                'product_id': 5,  # Just integer, not list
                'name': 'Dental Cleaning',
                'quantity': 1,
                'price_unit': 100.0,
                'price_subtotal': 100.0
            }
        ]
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # This should work fine (falls to else branch)
        revenue = client.get_treatment_revenue(
            date_from='2025-10-01',
            date_to='2025-10-31'
        )
        
        assert len(revenue) == 1
        assert revenue[0]['product_id'] == 5
        assert revenue[0]['product_name'] == 'Dental Cleaning'
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_none_product_id_is_skipped(self, mock_proxy, mock_settings):
        """
        Test that None product_id is skipped (continue statement).
        
        If product_id is missing/None, should skip the line.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        
        # Simulate Odoo returning invoice lines with None product_id
        mock_models.execute_kw.return_value = [
            {
                'id': 1,
                'product_id': None,  # Missing/deleted product
                'quantity': 1,
                'price_unit': 100.0,
                'price_subtotal': 100.0
            },
            {
                'id': 2,
                'product_id': [5, 'Dental Cleaning'],  # Valid product
                'quantity': 1,
                'price_unit': 150.0,
                'price_subtotal': 150.0
            }
        ]
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # This should work fine, skipping None product
        revenue = client.get_treatment_revenue(
            date_from='2025-10-01',
            date_to='2025-10-31'
        )
        
        # Should only have 1 product (None was skipped)
        assert len(revenue) == 1
        assert revenue[0]['product_id'] == 5
    
    # ========== EDGE CASES ==========
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_multiple_lines_with_mixed_formats(self, mock_proxy, mock_settings):
        """
        Test that multiple lines with different product_id formats work.
        
        Real-world scenario: some lines have lists, some have ints, some None.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        
        # Simulate Odoo returning lines with mixed formats
        mock_models.execute_kw.return_value = [
            {
                'id': 1,
                'product_id': [5, 'Dental Cleaning'],  # Valid list
                'quantity': 1,
                'price_unit': 100.0,
                'price_subtotal': 100.0
            },
            {
                'id': 2,
                'product_id': 7,  # Just integer
                'name': 'X-Ray',
                'quantity': 2,
                'price_unit': 50.0,
                'price_subtotal': 100.0
            },
            {
                'id': 3,
                'product_id': None,  # None - should be skipped
                'quantity': 1,
                'price_unit': 75.0,
                'price_subtotal': 75.0
            }
        ]
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # This should work fine for all formats
        revenue = client.get_treatment_revenue(
            date_from='2025-10-01',
            date_to='2025-10-31'
        )
        
        # Should have 2 products (None was skipped)
        assert len(revenue) == 2
        assert revenue[0]['product_id'] == 5
        assert revenue[0]['product_name'] == 'Dental Cleaning'
        assert revenue[0]['revenue'] == 100.0
        assert revenue[1]['product_id'] == 7
        assert revenue[1]['product_name'] == 'X-Ray'
        assert revenue[1]['revenue'] == 100.0
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_same_product_multiple_lines(self, mock_proxy, mock_settings):
        """
        Test that same product in multiple lines is aggregated correctly.
        
        Revenue should be summed for the same product.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        
        # Simulate Odoo returning multiple lines for same product
        mock_models.execute_kw.return_value = [
            {
                'id': 1,
                'product_id': [5, 'Dental Cleaning'],
                'quantity': 1,
                'price_unit': 100.0,
                'price_subtotal': 100.0
            },
            {
                'id': 2,
                'product_id': [5, 'Dental Cleaning'],  # Same product
                'quantity': 2,
                'price_unit': 100.0,
                'price_subtotal': 200.0
            }
        ]
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # This should aggregate revenue for same product
        revenue = client.get_treatment_revenue(
            date_from='2025-10-01',
            date_to='2025-10-31'
        )
        
        # Should have 1 product with aggregated revenue
        assert len(revenue) == 1
        assert revenue[0]['product_id'] == 5
        assert revenue[0]['quantity'] == 3  # 1 + 2
        assert revenue[0]['revenue'] == 300.0  # 100 + 200
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_empty_invoice_lines(self, mock_proxy, mock_settings):
        """
        Test that empty invoice lines list is handled correctly.
        
        If no lines, should return empty list, not crash.
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
        revenue = client.get_treatment_revenue(
            date_from='2025-10-01',
            date_to='2025-10-31'
        )
        
        assert revenue == []

