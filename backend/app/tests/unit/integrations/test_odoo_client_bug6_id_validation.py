"""
Test suite for Bug #6: No Input Validation on IDs

BUG DESCRIPTION:
Methods read(), write(), and unlink() do not validate ID parameters.
This leads to:
1. Confusing behavior (empty results instead of errors)
2. Unclear error messages from Odoo
3. Silent failures

EXPECTED BEHAVIOR:
- read() should raise ValueError if ids is empty
- write() should raise ValueError if record_id <= 0
- unlink() should raise ValueError if record_ids is empty
- Clear, actionable error messages
"""

import pytest
from unittest.mock import MagicMock, patch
from app.integrations.odoo_client import OdooClient


class TestBug6IDValidation:
    """Test suite for Bug #6: No Input Validation on IDs"""
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_read_with_empty_ids_list(self, mock_proxy, mock_settings):
        """
        Test that read() with empty IDs list should raise ValueError.
        
        Current behavior: Returns [] (confusing)
        Expected behavior: Raise ValueError with clear message
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = []  # Odoo returns empty list
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # BUG: This should raise ValueError, but currently doesn't
        with pytest.raises(ValueError, match="ids.*empty|cannot be empty"):
            client.read('res.partner', ids=[])
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_write_with_zero_id(self, mock_proxy, mock_settings):
        """
        Test that write() with ID=0 should raise ValueError.
        
        Current behavior: Odoo raises confusing exception
        Expected behavior: Raise ValueError with clear message BEFORE calling Odoo
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # BUG: This should raise ValueError BEFORE calling Odoo
        with pytest.raises(ValueError, match="record_id.*positive|must be greater than 0"):
            client.write('res.partner', record_id=0, values={'name': 'Test'})
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_write_with_negative_id(self, mock_proxy, mock_settings):
        """
        Test that write() with negative ID should raise ValueError.
        
        Current behavior: Odoo raises confusing exception
        Expected behavior: Raise ValueError with clear message
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # BUG: This should raise ValueError
        with pytest.raises(ValueError, match="record_id.*positive|must be greater than 0"):
            client.write('res.partner', record_id=-1, values={'name': 'Test'})
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_unlink_with_empty_ids_list(self, mock_proxy, mock_settings):
        """
        Test that unlink() with empty IDs list should raise ValueError.
        
        Current behavior: Silent success (returns True but does nothing)
        Expected behavior: Raise ValueError with clear message
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = True  # Odoo returns True
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # BUG: This should raise ValueError, not silently succeed
        with pytest.raises(ValueError, match="record_ids.*empty|cannot be empty"):
            client.unlink('res.partner', record_ids=[])
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_unlink_with_invalid_ids(self, mock_proxy, mock_settings):
        """
        Test that unlink() with invalid IDs (0, negative) should raise ValueError.
        
        Current behavior: Odoo raises confusing exception
        Expected behavior: Raise ValueError with clear message
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # BUG: This should raise ValueError for invalid IDs
        with pytest.raises(ValueError, match="positive.*integer|Invalid IDs"):
            client.unlink('res.partner', record_ids=[1, 0, -1])
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_read_with_valid_ids_should_work(self, mock_proxy, mock_settings):
        """
        Test that read() with valid IDs works correctly.
        
        This is a positive test to ensure we don't break valid usage.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = [{'id': 1, 'name': 'Test'}]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # This should work fine
        result = client.read('res.partner', ids=[1])
        assert result == [{'id': 1, 'name': 'Test'}]
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_write_with_valid_id_should_work(self, mock_proxy, mock_settings):
        """
        Test that write() with valid ID works correctly.
        
        This is a positive test to ensure we don't break valid usage.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = True
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # This should work fine
        result = client.write('res.partner', record_id=1, values={'name': 'Test'})
        assert result is True
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_unlink_with_valid_ids_should_work(self, mock_proxy, mock_settings):
        """
        Test that unlink() with valid IDs works correctly.
        
        This is a positive test to ensure we don't break valid usage.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = True
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # This should work fine
        result = client.unlink('res.partner', record_ids=[1, 2, 3])
        assert result is True



    # ========== ADDITIONAL COMPREHENSIVE TESTS ==========
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_read_with_zero_id(self, mock_proxy, mock_settings):
        """
        Test that read() with ID=0 should raise ValueError.
        
        Zero is not a valid Odoo record ID.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # Should raise ValueError for ID=0
        with pytest.raises(ValueError, match="positive|greater than 0|invalid"):
            client.read('res.partner', ids=[0])
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_read_with_negative_id(self, mock_proxy, mock_settings):
        """
        Test that read() with negative ID should raise ValueError.
        
        Negative IDs are not valid in Odoo.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # Should raise ValueError for negative ID
        with pytest.raises(ValueError, match="positive|greater than 0|invalid"):
            client.read('res.partner', ids=[-1])
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_read_with_mixed_valid_and_invalid_ids(self, mock_proxy, mock_settings):
        """
        Test that read() with mix of valid and invalid IDs should raise ValueError.
        
        Even if some IDs are valid, all must be valid.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # Should raise ValueError for mixed IDs
        with pytest.raises(ValueError, match="positive|greater than 0|invalid"):
            client.read('res.partner', ids=[1, 2, 0, 3])
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_write_with_empty_values(self, mock_proxy, mock_settings):
        """
        Test that write() with empty values dict should raise ValueError.
        
        No point in calling Odoo if there's nothing to update.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # Should raise ValueError for empty values
        with pytest.raises(ValueError, match="values.*empty|cannot be empty"):
            client.write('res.partner', record_id=1, values={})
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_read_with_multiple_valid_ids(self, mock_proxy, mock_settings):
        """
        Test that read() with multiple valid IDs works correctly.
        
        Positive test for bulk read operations.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = [
            {'id': 1, 'name': 'Test 1'},
            {'id': 2, 'name': 'Test 2'},
            {'id': 3, 'name': 'Test 3'}
        ]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # Should work fine with multiple IDs
        result = client.read('res.partner', ids=[1, 2, 3])
        assert len(result) == 3
        assert result[0]['id'] == 1
        assert result[1]['id'] == 2
        assert result[2]['id'] == 3
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_unlink_with_single_invalid_id_in_list(self, mock_proxy, mock_settings):
        """
        Test that unlink() with a single invalid ID in list should raise ValueError.
        
        All IDs must be valid, even if just one is invalid.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # Should raise ValueError even with one invalid ID
        with pytest.raises(ValueError, match="positive.*integer|Invalid IDs"):
            client.unlink('res.partner', record_ids=[1, 2, 3, 0])
    
    @patch('app.integrations.odoo_client.settings')
    @patch('xmlrpc.client.ServerProxy')
    def test_read_with_large_number_of_ids(self, mock_proxy, mock_settings):
        """
        Test that read() works with a large number of IDs.
        
        Positive test for bulk operations.
        """
        # Setup
        mock_settings.ODOO_URL = "https://localhost:8069"
        mock_settings.ODOO_DB = "test_db"
        mock_settings.ODOO_USERNAME = "admin"
        mock_settings.ODOO_PASSWORD = "password"
        
        mock_common = MagicMock()
        mock_common.authenticate.return_value = 123
        mock_models = MagicMock()
        mock_models.execute_kw.return_value = [{'id': i, 'name': f'Test {i}'} for i in range(1, 101)]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # Create client
        client = OdooClient()
        client.authenticate()
        
        # Should work fine with 100 IDs
        large_ids = list(range(1, 101))
        result = client.read('res.partner', ids=large_ids)
        assert len(result) == 100

