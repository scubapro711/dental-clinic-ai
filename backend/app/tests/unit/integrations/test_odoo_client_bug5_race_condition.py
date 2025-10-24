"""
Test Bug #5: Race Condition in get_dental_chart

Bug Description:
    The get_dental_chart() method has a race condition when calculating last_updated.
    If all last_treatment_date values are None, max([]) raises ValueError.
    If charts is empty, max([None]) raises TypeError.

Location: Line 628 in odoo_client.py

Impact:
    - Crash: unexpected exception
    - Data Loss: transaction rollback
    - User Experience: error page

Fix:
    Handle empty list case properly:
    dates = [c.get('last_treatment_date') for c in charts if c.get('last_treatment_date')]
    'last_updated': max(dates) if dates else None
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.integrations.odoo_client import OdooClient


class TestBug5RaceCondition:
    """Test suite for Bug #5: Race Condition in get_dental_chart"""
    
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
                client.models = Mock()
                
                yield client
    
    def test_dental_chart_with_all_none_dates_should_not_crash(self, mock_odoo_client):
        """
        Test that get_dental_chart() doesn't crash when all treatment dates are None.
        
        This is the main bug - max([]) or max([None]) raises exception.
        """
        # Mock search to return chart IDs
        mock_odoo_client.models.execute_kw.side_effect = [
            [1, 2, 3],  # search returns 3 chart IDs
            [  # read returns charts with all None dates
                {'id': 1, 'patient_id': 100, 'teeth_code': '11', 'teeth_name': 'Upper Right Central Incisor',
                 'status': 'healthy', 'notes': None, 'last_treatment_date': None},
                {'id': 2, 'patient_id': 100, 'teeth_code': '12', 'teeth_name': 'Upper Right Lateral Incisor',
                 'status': 'healthy', 'notes': None, 'last_treatment_date': None},
                {'id': 3, 'patient_id': 100, 'teeth_code': '13', 'teeth_name': 'Upper Right Canine',
                 'status': 'healthy', 'notes': None, 'last_treatment_date': None}
            ]
        ]
        
        # This should NOT crash
        result = mock_odoo_client.get_dental_chart(patient_id=100)
        
        # Verify result structure
        assert result is not None
        assert result['patient_id'] == 100
        assert len(result['teeth']) == 3
        
        # BUG: Currently crashes with ValueError or TypeError
        # After fix, last_updated should be None
        assert result['last_updated'] is None, \
            "Bug #5: last_updated should be None when all dates are None"
    
    def test_dental_chart_with_empty_charts_should_return_none(self, mock_odoo_client):
        """
        Test that get_dental_chart() returns None when no charts exist.
        """
        # Mock search to return empty list
        mock_odoo_client.models.execute_kw.return_value = []
        
        # Should return None, not crash
        result = mock_odoo_client.get_dental_chart(patient_id=100)
        
        assert result is None
    
    def test_dental_chart_with_mixed_dates_should_return_max(self, mock_odoo_client):
        """
        Test that get_dental_chart() returns the maximum date when some dates exist.
        """
        # Mock search and read
        mock_odoo_client.models.execute_kw.side_effect = [
            [1, 2, 3],  # search returns 3 chart IDs
            [  # read returns charts with mixed dates
                {'id': 1, 'patient_id': 100, 'teeth_code': '11', 'teeth_name': 'Upper Right Central Incisor',
                 'status': 'filled', 'notes': 'Cavity filled', 'last_treatment_date': '2024-01-15'},
                {'id': 2, 'patient_id': 100, 'teeth_code': '12', 'teeth_name': 'Upper Right Lateral Incisor',
                 'status': 'healthy', 'notes': None, 'last_treatment_date': None},
                {'id': 3, 'patient_id': 100, 'teeth_code': '13', 'teeth_name': 'Upper Right Canine',
                 'status': 'crown', 'notes': 'Crown placed', 'last_treatment_date': '2024-02-20'}
            ]
        ]
        
        result = mock_odoo_client.get_dental_chart(patient_id=100)
        
        assert result is not None
        assert result['patient_id'] == 100
        assert len(result['teeth']) == 3
        # Should return the maximum date (2024-02-20)
        assert result['last_updated'] == '2024-02-20'
    
    def test_dental_chart_with_single_date_should_return_that_date(self, mock_odoo_client):
        """
        Test that get_dental_chart() returns the single date when only one exists.
        """
        # Mock search and read
        mock_odoo_client.models.execute_kw.side_effect = [
            [1, 2],  # search returns 2 chart IDs
            [  # read returns charts with one date
                {'id': 1, 'patient_id': 100, 'teeth_code': '11', 'teeth_name': 'Upper Right Central Incisor',
                 'status': 'healthy', 'notes': None, 'last_treatment_date': None},
                {'id': 2, 'patient_id': 100, 'teeth_code': '12', 'teeth_name': 'Upper Right Lateral Incisor',
                 'status': 'filled', 'notes': 'Recent filling', 'last_treatment_date': '2024-03-10'}
            ]
        ]
        
        result = mock_odoo_client.get_dental_chart(patient_id=100)
        
        assert result is not None
        assert result['last_updated'] == '2024-03-10'
    
    def test_dental_chart_with_all_dates_should_return_max(self, mock_odoo_client):
        """
        Test that get_dental_chart() returns the maximum date when all have dates.
        """
        # Mock search and read
        mock_odoo_client.models.execute_kw.side_effect = [
            [1, 2, 3],  # search returns 3 chart IDs
            [  # read returns charts with all dates
                {'id': 1, 'patient_id': 100, 'teeth_code': '11', 'teeth_name': 'Upper Right Central Incisor',
                 'status': 'filled', 'notes': 'Old filling', 'last_treatment_date': '2023-06-15'},
                {'id': 2, 'patient_id': 100, 'teeth_code': '12', 'teeth_name': 'Upper Right Lateral Incisor',
                 'status': 'crown', 'notes': 'Crown', 'last_treatment_date': '2023-12-20'},
                {'id': 3, 'patient_id': 100, 'teeth_code': '13', 'teeth_name': 'Upper Right Canine',
                 'status': 'filled', 'notes': 'Recent filling', 'last_treatment_date': '2024-01-05'}
            ]
        ]
        
        result = mock_odoo_client.get_dental_chart(patient_id=100)
        
        assert result is not None
        assert result['last_updated'] == '2024-01-05'
    
    def test_dental_chart_exception_handling(self, mock_odoo_client):
        """
        Test that get_dental_chart() handles exceptions gracefully.
        """
        # Mock search to raise exception
        mock_odoo_client.models.execute_kw.side_effect = Exception("Database connection failed")
        
        # Should return None, not crash
        result = mock_odoo_client.get_dental_chart(patient_id=100)
        
        assert result is None


class TestBug5EdgeCases:
    """Test edge cases for Bug #5"""
    
    @pytest.fixture
    def mock_odoo_client(self):
        """Create a mock OdooClient for testing"""
        with patch('app.integrations.odoo_client.settings') as mock_settings:
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
    
    def test_dental_chart_with_empty_string_dates(self, mock_odoo_client):
        """
        Test that get_dental_chart() handles empty string dates.
        """
        # Mock search and read
        mock_odoo_client.models.execute_kw.side_effect = [
            [1, 2],  # search returns 2 chart IDs
            [  # read returns charts with empty string dates
                {'id': 1, 'patient_id': 100, 'teeth_code': '11', 'teeth_name': 'Upper Right Central Incisor',
                 'status': 'healthy', 'notes': None, 'last_treatment_date': ''},
                {'id': 2, 'patient_id': 100, 'teeth_code': '12', 'teeth_name': 'Upper Right Lateral Incisor',
                 'status': 'healthy', 'notes': None, 'last_treatment_date': None}
            ]
        ]
        
        result = mock_odoo_client.get_dental_chart(patient_id=100)
        
        assert result is not None
        # Empty strings are falsy, so should be filtered out
        assert result['last_updated'] is None or result['last_updated'] == ''
    
    def test_dental_chart_with_false_dates(self, mock_odoo_client):
        """
        Test that get_dental_chart() handles False dates (Odoo sometimes returns False for null).
        """
        # Mock search and read
        mock_odoo_client.models.execute_kw.side_effect = [
            [1, 2],  # search returns 2 chart IDs
            [  # read returns charts with False dates (Odoo convention for null)
                {'id': 1, 'patient_id': 100, 'teeth_code': '11', 'teeth_name': 'Upper Right Central Incisor',
                 'status': 'healthy', 'notes': None, 'last_treatment_date': False},
                {'id': 2, 'patient_id': 100, 'teeth_code': '12', 'teeth_name': 'Upper Right Lateral Incisor',
                 'status': 'healthy', 'notes': None, 'last_treatment_date': False}
            ]
        ]
        
        result = mock_odoo_client.get_dental_chart(patient_id=100)
        
        assert result is not None
        # False is falsy, so should be filtered out
        assert result['last_updated'] is None or result['last_updated'] is False
    
    def test_dental_chart_with_single_chart_no_date(self, mock_odoo_client):
        """
        Test that get_dental_chart() handles single chart with no date.
        """
        # Mock search and read
        mock_odoo_client.models.execute_kw.side_effect = [
            [1],  # search returns 1 chart ID
            [  # read returns single chart with no date
                {'id': 1, 'patient_id': 100, 'teeth_code': '11', 'teeth_name': 'Upper Right Central Incisor',
                 'status': 'healthy', 'notes': None, 'last_treatment_date': None}
            ]
        ]
        
        result = mock_odoo_client.get_dental_chart(patient_id=100)
        
        assert result is not None
        assert result['patient_id'] == 100
        assert len(result['teeth']) == 1
        assert result['last_updated'] is None

