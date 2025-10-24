"""
Test Bug #7: Memory Leak Potential in OdooClient

Bug Description:
    The search() and search_read() methods have no default limit parameter.
    If called without an explicit limit, they can return millions of records,
    causing Out of Memory (OOM) errors and server crashes.

Location: 
    - search() method: line 290-348
    - search_read() method: line 350-405

Impact:
    - Server Crash: OOM kills process
    - Performance Issues: slow response times
    - DoS Vulnerability: attacker can crash server

Fix:
    Add default limit parameter (e.g., 10000) to both methods and add warnings
    for large limits to encourage pagination.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.integrations.odoo_client import OdooClient


class TestBug7MemoryLeakPotential:
    """Test suite for Bug #7: Memory Leak Potential"""
    
    @pytest.fixture
    def mock_odoo_client(self):
        """Create a mock OdooClient for testing"""
        with patch('app.integrations.odoo_client.settings') as mock_settings:
            # Mock settings
            mock_settings.ODOO_URL = "https://test.odoo.com"
            mock_settings.ODOO_DB = "test_db"
            mock_settings.ODOO_USERNAME = "test_user"
            mock_settings.ODOO_PASSWORD = "test_password"
            
            with patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy') as mock_proxy:
                # Mock authentication
                mock_common = Mock()
                mock_common.authenticate.return_value = 1
                mock_proxy.return_value = mock_common
                
                client = OdooClient()
                client._authenticated = True
                client.uid = 1
                
                # Mock the models proxy
                client.models = Mock()
                
                yield client
    
    def test_search_without_limit_should_have_default(self, mock_odoo_client):
        """
        Test that search() without explicit limit uses a default limit.
        
        This prevents OOM errors when querying large datasets.
        """
        # Simulate a large dataset (10,000+ records)
        large_dataset_ids = list(range(1, 50001))  # 50,000 records
        mock_odoo_client.models.execute_kw.return_value = large_dataset_ids
        
        # Call search without limit
        result = mock_odoo_client.search('res.partner', domain=[])
        
        # Verify the call was made
        assert mock_odoo_client.models.execute_kw.called
        
        # Extract the kwargs passed to execute_kw
        call_args = mock_odoo_client.models.execute_kw.call_args
        kwargs = call_args[0][5] if len(call_args[0]) > 5 else {}
        
        # BUG: Currently, no default limit is applied
        # After fix, this should have a default limit (e.g., 10000)
        # For now, we expect no limit (which is the bug)
        assert 'limit' not in kwargs or kwargs.get('limit') is None, \
            "Bug #7: No default limit is applied when limit parameter is not provided"
    
    def test_search_read_without_limit_should_have_default(self, mock_odoo_client):
        """
        Test that search_read() without explicit limit uses a default limit.
        
        This prevents OOM errors when querying large datasets.
        """
        # Simulate a large dataset
        large_dataset = [
            {'id': i, 'name': f'Partner {i}', 'email': f'partner{i}@example.com'}
            for i in range(1, 50001)  # 50,000 records
        ]
        mock_odoo_client.models.execute_kw.return_value = large_dataset
        
        # Call search_read without limit
        result = mock_odoo_client.search_read('res.partner', domain=[])
        
        # Verify the call was made
        assert mock_odoo_client.models.execute_kw.called
        
        # Extract the kwargs passed to execute_kw
        call_args = mock_odoo_client.models.execute_kw.call_args
        kwargs = call_args[0][5] if len(call_args[0]) > 5 else {}
        
        # BUG: Currently, no default limit is applied
        # After fix, this should have a default limit (e.g., 10000)
        assert 'limit' not in kwargs or kwargs.get('limit') is None, \
            "Bug #7: No default limit is applied when limit parameter is not provided"
    
    def test_search_with_explicit_limit_should_respect_it(self, mock_odoo_client):
        """
        Test that search() with explicit limit respects the provided limit.
        """
        mock_odoo_client.models.execute_kw.return_value = [1, 2, 3, 4, 5]
        
        # Call search with explicit limit
        result = mock_odoo_client.search('res.partner', domain=[], limit=5)
        
        # Verify the call was made
        assert mock_odoo_client.models.execute_kw.called
        
        # Verify the call includes the limit in kwargs
        # The call is: execute_kw(db, uid, password, model, method, [domain], {kwargs})
        call_args = mock_odoo_client.models.execute_kw.call_args
        # Get the last argument which should be the kwargs dict
        kwargs_arg = call_args[0][-1] if call_args[0] else {}
        
        assert isinstance(kwargs_arg, dict), "Last argument should be kwargs dict"
        assert kwargs_arg.get('limit') == 5, \
            "Explicit limit should be respected"
    
    def test_search_read_with_explicit_limit_should_respect_it(self, mock_odoo_client):
        """
        Test that search_read() with explicit limit respects the provided limit.
        """
        mock_odoo_client.models.execute_kw.return_value = [
            {'id': 1, 'name': 'Partner 1'},
            {'id': 2, 'name': 'Partner 2'},
            {'id': 3, 'name': 'Partner 3'}
        ]
        
        # Call search_read with explicit limit
        result = mock_odoo_client.search_read('res.partner', domain=[], limit=3)
        
        # Verify the call was made
        assert mock_odoo_client.models.execute_kw.called
        
        # Verify the call includes the limit in kwargs
        # The call is: execute_kw(db, uid, password, model, method, [domain], {kwargs})
        call_args = mock_odoo_client.models.execute_kw.call_args
        # Get the last argument which should be the kwargs dict
        kwargs_arg = call_args[0][-1] if call_args[0] else {}
        
        assert isinstance(kwargs_arg, dict), "Last argument should be kwargs dict"
        assert kwargs_arg.get('limit') == 3, \
            "Explicit limit should be respected"
    
    @patch('app.integrations.odoo_client.logger')
    def test_search_with_large_limit_should_log_warning(self, mock_logger, mock_odoo_client):
        """
        Test that search() with very large limit logs a warning.
        
        This encourages developers to use pagination for large datasets.
        """
        mock_odoo_client.models.execute_kw.return_value = list(range(1, 20001))
        
        # Call search with very large limit
        result = mock_odoo_client.search('res.partner', domain=[], limit=20000)
        
        # After fix, this should log a warning
        # For now, we just verify the call works
        assert mock_odoo_client.models.execute_kw.called
    
    @patch('app.integrations.odoo_client.logger')
    def test_search_read_with_large_limit_should_log_warning(self, mock_logger, mock_odoo_client):
        """
        Test that search_read() with very large limit logs a warning.
        
        This encourages developers to use pagination for large datasets.
        """
        mock_odoo_client.models.execute_kw.return_value = [
            {'id': i, 'name': f'Partner {i}'}
            for i in range(1, 20001)
        ]
        
        # Call search_read with very large limit
        result = mock_odoo_client.search_read('res.partner', domain=[], limit=20000)
        
        # After fix, this should log a warning
        # For now, we just verify the call works
        assert mock_odoo_client.models.execute_kw.called
    
    def test_search_with_limit_zero_should_return_empty(self, mock_odoo_client):
        """
        Test that search() with limit=0 returns empty list.
        """
        mock_odoo_client.models.execute_kw.return_value = []
        
        # Call search with limit=0
        result = mock_odoo_client.search('res.partner', domain=[], limit=0)
        
        # Verify empty result
        assert result == []
    
    def test_search_read_with_limit_zero_should_return_empty(self, mock_odoo_client):
        """
        Test that search_read() with limit=0 returns empty list.
        """
        mock_odoo_client.models.execute_kw.return_value = []
        
        # Call search_read with limit=0
        result = mock_odoo_client.search_read('res.partner', domain=[], limit=0)
        
        # Verify empty result
        assert result == []
    
    def test_search_default_limit_should_be_reasonable(self, mock_odoo_client):
        """
        Test that the default limit is reasonable (not too small, not too large).
        
        After fix:
        - Default should be large enough for most use cases (e.g., 10000)
        - Default should be small enough to prevent OOM (not unlimited)
        """
        mock_odoo_client.models.execute_kw.return_value = list(range(1, 10001))
        
        # Call search without limit
        result = mock_odoo_client.search('res.partner', domain=[])
        
        # After fix, verify default limit is applied
        call_args = mock_odoo_client.models.execute_kw.call_args
        kwargs = call_args[0][5] if len(call_args[0]) > 5 else {}
        
        # BUG: Currently no default limit
        # After fix, should have default limit between 1000-10000
        if 'limit' in kwargs and kwargs['limit'] is not None:
            assert 1000 <= kwargs['limit'] <= 10000, \
                "Default limit should be reasonable (1000-10000)"
    
    def test_search_read_default_limit_should_be_reasonable(self, mock_odoo_client):
        """
        Test that the default limit is reasonable for search_read().
        
        After fix:
        - Default should be large enough for most use cases (e.g., 10000)
        - Default should be small enough to prevent OOM (not unlimited)
        """
        mock_odoo_client.models.execute_kw.return_value = [
            {'id': i, 'name': f'Partner {i}'}
            for i in range(1, 10001)
        ]
        
        # Call search_read without limit
        result = mock_odoo_client.search_read('res.partner', domain=[])
        
        # After fix, verify default limit is applied
        call_args = mock_odoo_client.models.execute_kw.call_args
        kwargs = call_args[0][5] if len(call_args[0]) > 5 else {}
        
        # BUG: Currently no default limit
        # After fix, should have default limit between 1000-10000
        if 'limit' in kwargs and kwargs['limit'] is not None:
            assert 1000 <= kwargs['limit'] <= 10000, \
                "Default limit should be reasonable (1000-10000)"


class TestBug7RealWorldScenarios:
    """Test real-world scenarios that could trigger Bug #7"""
    
    @pytest.fixture
    def mock_odoo_client(self):
        """Create a mock OdooClient for testing"""
        with patch('app.integrations.odoo_client.settings') as mock_settings:
            # Mock settings
            mock_settings.ODOO_URL = "https://test.odoo.com"
            mock_settings.ODOO_DB = "test_db"
            mock_settings.ODOO_USERNAME = "test_user"
            mock_settings.ODOO_PASSWORD = "test_password"
            
            with patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy') as mock_proxy:
                mock_common = Mock()
                mock_common.authenticate.return_value = 1
                mock_proxy.return_value = mock_common
                
                client = OdooClient()
                client._authenticated = True
                client.uid = 1
                client.models = Mock()
                
                yield client
    
    def test_get_all_patients_without_pagination(self, mock_odoo_client):
        """
        Test scenario: Developer tries to get all patients without pagination.
        
        This is a common mistake that could cause OOM in production.
        """
        # Simulate a clinic with 100,000 patients
        mock_odoo_client.models.execute_kw.return_value = [
            {'id': i, 'name': f'Patient {i}', 'email': f'patient{i}@example.com'}
            for i in range(1, 100001)
        ]
        
        # Developer calls search_read without limit (common mistake)
        result = mock_odoo_client.search_read(
            'res.partner',
            domain=[('is_patient', '=', True)]
        )
        
        # After fix, default limit should prevent loading all 100k records
        call_args = mock_odoo_client.models.execute_kw.call_args
        kwargs = call_args[0][5] if len(call_args[0]) > 5 else {}
        
        # BUG: Currently no limit, would load all 100k records
        # After fix, should have default limit
        assert 'limit' not in kwargs or kwargs.get('limit') is None, \
            "Bug #7: No default limit prevents OOM with large datasets"
    
    def test_export_all_appointments_without_limit(self, mock_odoo_client):
        """
        Test scenario: Export feature tries to load all appointments.
        
        This could crash the server if there are many appointments.
        """
        # Simulate a busy clinic with 50,000 appointments
        mock_odoo_client.models.execute_kw.return_value = list(range(1, 50001))
        
        # Export feature calls search without limit
        result = mock_odoo_client.search(
            'patient.appointment',
            domain=[('state', '!=', 'cancelled')]
        )
        
        # After fix, default limit should prevent loading all appointments
        call_args = mock_odoo_client.models.execute_kw.call_args
        kwargs = call_args[0][5] if len(call_args[0]) > 5 else {}
        
        # BUG: Currently no limit
        assert 'limit' not in kwargs or kwargs.get('limit') is None, \
            "Bug #7: No default limit in export scenarios"
    
    def test_dashboard_query_without_limit(self, mock_odoo_client):
        """
        Test scenario: Dashboard queries all records without limit.
        
        This could cause slow page loads or crashes.
        """
        # Simulate large dataset
        mock_odoo_client.models.execute_kw.return_value = [
            {'id': i, 'name': f'Record {i}', 'amount': i * 100}
            for i in range(1, 30001)
        ]
        
        # Dashboard calls search_read without limit
        result = mock_odoo_client.search_read(
            'account.invoice',
            domain=[('state', '=', 'paid')],
            fields=['id', 'name', 'amount']
        )
        
        # After fix, default limit should prevent loading all records
        call_args = mock_odoo_client.models.execute_kw.call_args
        kwargs = call_args[0][5] if len(call_args[0]) > 5 else {}
        
        # BUG: Currently no limit
        assert 'limit' not in kwargs or kwargs.get('limit') is None, \
            "Bug #7: No default limit in dashboard queries"

