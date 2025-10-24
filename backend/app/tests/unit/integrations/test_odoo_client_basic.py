"""
Unit Tests for Odoo Client - Basic Coverage

Tests for app.integrations.odoo_client module including:
- Connection and authentication
- Core CRUD methods (search, read, create, write, unlink)
- Error handling
- Retry logic

Note: This is a basic test suite focused on achieving coverage.
Full integration tests should be added separately.
"""

import pytest
import xmlrpc.client
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from datetime import datetime

from app.integrations.odoo_client import (
    OdooClient,
    OdooConnectionError,
    OdooValidationError,
    OdooConstraintError,
    retry_on_failure,
)


@pytest.mark.unit
@pytest.mark.integration
class TestOdooClientInit:
    """Test OdooClient initialization."""
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    def test_init_success(self, mock_proxy):
        """Test successful client initialization."""
        mock_common = Mock()
        mock_models = Mock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        
        assert client.common is mock_common
        assert client.models is mock_models
        assert client.uid is None
        assert client._authenticated is False
        # Note: No longer checking setdefaulttimeout - Bug #1 fixed!
        # Now using per-connection timeout instead of global timeout
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_init_connection_timeout(self, mock_timeout, mock_proxy):
        """Test initialization with connection timeout."""
        import socket
        mock_proxy.side_effect = socket.timeout()
        
        with pytest.raises(OdooConnectionError) as exc_info:
            OdooClient()
        
        assert "timeout" in str(exc_info.value).lower()
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_init_connection_error(self, mock_timeout, mock_proxy):
        """Test initialization with connection error."""
        mock_proxy.side_effect = Exception("Connection refused")
        
        with pytest.raises(OdooConnectionError) as exc_info:
            OdooClient()
        
        assert "cannot connect" in str(exc_info.value).lower()


@pytest.mark.unit
@pytest.mark.integration
class TestOdooClientAuthentication:
    """Test OdooClient authentication."""
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_authenticate_success(self, mock_timeout, mock_proxy):
        """Test successful authentication."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        result = client.authenticate()
        
        assert result is True
        assert client.uid == 123
        assert client._authenticated is True
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_authenticate_failure_invalid_credentials(self, mock_timeout, mock_proxy):
        """Test authentication failure with invalid credentials."""
        mock_common = Mock()
        mock_common.authenticate.return_value = None
        mock_models = Mock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        
        with pytest.raises(OdooConnectionError) as exc_info:
            client.authenticate()
        
        assert "invalid credentials" in str(exc_info.value).lower()
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_authenticate_failure_exception(self, mock_timeout, mock_proxy):
        """Test authentication failure with exception."""
        mock_common = Mock()
        mock_common.authenticate.side_effect = Exception("Network error")
        mock_models = Mock()
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        
        with pytest.raises(OdooConnectionError) as exc_info:
            client.authenticate()
        
        assert "authentication failed" in str(exc_info.value).lower()


@pytest.mark.unit
@pytest.mark.integration
class TestOdooClientExecute:
    """Test OdooClient _execute method."""
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_execute_success(self, mock_timeout, mock_proxy):
        """Test successful execute."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.return_value = [1, 2, 3]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client._execute('res.partner', 'search', [[]])
        
        assert result == [1, 2, 3]
        mock_models.execute_kw.assert_called_once()
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_execute_auto_authenticate(self, mock_timeout, mock_proxy):
        """Test execute auto-authenticates if not authenticated."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.return_value = []
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        # Don't authenticate manually
        
        result = client._execute('res.partner', 'search', [[]])
        
        assert client._authenticated is True
        assert result == []


@pytest.mark.unit
@pytest.mark.integration
class TestOdooClientSearch:
    """Test OdooClient search method."""
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_search_basic(self, mock_timeout, mock_proxy):
        """Test basic search."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.return_value = [1, 2, 3]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.search('res.partner', [['name', '=', 'Test']])
        
        assert result == [1, 2, 3]
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_search_with_limit(self, mock_timeout, mock_proxy):
        """Test search with limit."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.return_value = [1, 2]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.search('res.partner', [], limit=2)
        
        assert result == [1, 2]


@pytest.mark.unit
@pytest.mark.integration
class TestOdooClientRead:
    """Test OdooClient read method."""
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_read_basic(self, mock_timeout, mock_proxy):
        """Test basic read."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.return_value = [
            {'id': 1, 'name': 'Test'}
        ]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.read('res.partner', [1])
        
        assert result == [{'id': 1, 'name': 'Test'}]
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_read_with_fields(self, mock_timeout, mock_proxy):
        """Test read with specific fields."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.return_value = [
            {'id': 1, 'name': 'Test'}
        ]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.read('res.partner', [1], fields=['name'])
        
        assert result == [{'id': 1, 'name': 'Test'}]


@pytest.mark.unit
@pytest.mark.integration
class TestOdooClientCreate:
    """Test OdooClient create method."""
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_create_success(self, mock_timeout, mock_proxy):
        """Test successful create."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.return_value = 456
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.create('res.partner', {'name': 'New Partner'})
        
        assert result == 456


@pytest.mark.unit
@pytest.mark.integration
class TestOdooClientWrite:
    """Test OdooClient write method."""
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_write_success(self, mock_timeout, mock_proxy):
        """Test successful write."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.return_value = True
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.write('res.partner', 1, {'name': 'Updated'})
        
        assert result is True


@pytest.mark.unit
@pytest.mark.integration
class TestOdooClientUnlink:
    """Test OdooClient unlink method."""
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_unlink_success(self, mock_timeout, mock_proxy):
        """Test successful unlink."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.return_value = True
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.unlink('res.partner', [1])
        
        assert result is True


@pytest.mark.unit
@pytest.mark.integration
class TestOdooClientSearchRead:
    """Test OdooClient search_read method."""
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_search_read_basic(self, mock_timeout, mock_proxy):
        """Test basic search_read."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.return_value = [
            {'id': 1, 'name': 'Test'}
        ]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.search_read('res.partner', [])
        
        assert result == [{'id': 1, 'name': 'Test'}]


@pytest.mark.unit
@pytest.mark.integration
class TestOdooClientSearchCount:
    """Test OdooClient search_count method."""
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_search_count_basic(self, mock_timeout, mock_proxy):
        """Test basic search_count."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.return_value = 42
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.search_count('res.partner', [])
        
        assert result == 42


@pytest.mark.unit
@pytest.mark.integration
class TestRetryDecorator:
    """Test retry_on_failure decorator."""
    
    def test_retry_success_first_attempt(self):
        """Test retry decorator with success on first attempt."""
        mock_func = Mock(return_value="success")
        decorated = retry_on_failure(max_retries=3)(mock_func)
        
        result = decorated()
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_success_after_failures(self):
        """Test retry decorator with success after failures."""
        mock_func = Mock(side_effect=[
            Exception("Fail 1"),
            Exception("Fail 2"),
            "success"
        ])
        decorated = retry_on_failure(max_retries=3, delay=0.01)(mock_func)
        
        result = decorated()
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_retry_all_attempts_fail(self):
        """Test retry decorator when all attempts fail."""
        mock_func = Mock(side_effect=Exception("Always fails"))
        decorated = retry_on_failure(max_retries=3, delay=0.01)(mock_func)
        
        with pytest.raises(Exception) as exc_info:
            decorated()
        
        assert "always fails" in str(exc_info.value).lower()
        assert mock_func.call_count == 3


@pytest.mark.unit
@pytest.mark.integration
class TestOdooClientExceptions:
    """Test OdooClient exception classes."""
    
    def test_odoo_connection_error(self):
        """Test OdooConnectionError exception."""
        error = OdooConnectionError("Connection failed")
        
        assert isinstance(error, Exception)
        assert str(error) == "Connection failed"
    
    def test_odoo_validation_error(self):
        """Test OdooValidationError exception."""
        error = OdooValidationError("Validation failed")
        
        assert isinstance(error, Exception)
        assert str(error) == "Validation failed"
    
    def test_odoo_constraint_error(self):
        """Test OdooConstraintError exception."""
        error = OdooConstraintError("Constraint violated")
        
        assert isinstance(error, Exception)
        assert str(error) == "Constraint violated"





@pytest.mark.unit
@pytest.mark.integration
class TestOdooClientDentalMethods:
    """Test OdooClient dental-specific methods."""
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_get_dental_chart_success(self, mock_timeout, mock_proxy):
        """Test getting dental chart."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.side_effect = [
            [1, 2, 3],  # search results
            [  # read results
                {'id': 1, 'teeth_code': '11', 'status': 'healthy', 'last_treatment_date': '2025-01-01'},
                {'id': 2, 'teeth_code': '12', 'status': 'filled', 'last_treatment_date': '2025-01-02'},
                {'id': 3, 'teeth_code': '13', 'status': 'healthy', 'last_treatment_date': '2025-01-03'},
            ]
        ]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.get_dental_chart(patient_id=100)
        
        assert result is not None
        assert result['patient_id'] == 100
        assert len(result['teeth']) == 3
        assert result['last_updated'] == '2025-01-03'
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_get_dental_chart_not_found(self, mock_timeout, mock_proxy):
        """Test getting dental chart when not found."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.return_value = []  # No records found
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.get_dental_chart(patient_id=999)
        
        assert result is None
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_update_tooth_status_existing(self, mock_timeout, mock_proxy):
        """Test updating existing tooth status."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.side_effect = [
            [1],  # search finds existing record
            True  # write succeeds
        ]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.update_tooth_status(
            patient_id=100,
            tooth_code='11',
            status='cavity',
            notes='Needs filling'
        )
        
        assert result == 1
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_update_tooth_status_new(self, mock_timeout, mock_proxy):
        """Test creating new tooth status record."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.side_effect = [
            [],  # search finds no existing record
            456  # create returns new ID
        ]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.update_tooth_status(
            patient_id=100,
            tooth_code='21',
            status='healthy'
        )
        
        assert result == 456
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_get_treatment_history(self, mock_timeout, mock_proxy):
        """Test getting treatment history."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.side_effect = [
            [1, 2],  # search results
            [  # read results
                {'id': 1, 'treatment_type': 'Cleaning', 'treatment_date': '2025-01-01'},
                {'id': 2, 'treatment_type': 'Filling', 'treatment_date': '2025-01-02'},
            ]
        ]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.get_treatment_history(patient_id=100)
        
        assert len(result) == 2
        assert result[0]['treatment_type'] == 'Cleaning'
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_get_treatment_history_with_tooth_filter(self, mock_timeout, mock_proxy):
        """Test getting treatment history filtered by tooth."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.side_effect = [
            [1],  # search results
            [{'id': 1, 'tooth_code': '11', 'treatment_type': 'Filling'}]
        ]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.get_treatment_history(patient_id=100, tooth_code='11')
        
        assert len(result) == 1
        assert result[0]['tooth_code'] == '11'
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_create_treatment_record(self, mock_timeout, mock_proxy):
        """Test creating treatment record."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.return_value = 789
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.create_treatment_record(
            patient_id=100,
            tooth_code='11',
            treatment_type='Filling',
            doctor_id=5,
            cost=500.0,
            description='Composite filling'
        )
        
        assert result == 789
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_get_patient_prescriptions(self, mock_timeout, mock_proxy):
        """Test getting patient prescriptions."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.side_effect = [
            [1, 2],  # search results
            [  # read results
                {'id': 1, 'medication': 'Amoxicillin', 'dosage': '500mg'},
                {'id': 2, 'medication': 'Ibuprofen', 'dosage': '400mg'},
            ]
        ]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.get_patient_prescriptions(patient_id=100)
        
        assert len(result) == 2
        assert result[0]['medication'] == 'Amoxicillin'
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_create_prescription(self, mock_timeout, mock_proxy):
        """Test creating prescription."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.side_effect = [
            999,  # prescription creation
            1001  # medication line creation
        ]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.create_prescription(
            patient_id=100,
            doctor_id=5,
            medications=[
                {
                    'medication_id': 10,
                    'dosage': '500mg',
                    'frequency': '3 times daily',
                    'duration': '7 days'
                }
            ],
            diagnosis='Tooth infection'
        )
        
        assert result == 999


@pytest.mark.unit
@pytest.mark.integration
class TestOdooClientFinancialMethods:
    """Test OdooClient financial methods."""
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_get_invoices(self, mock_timeout, mock_proxy):
        """Test getting invoices."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.side_effect = [
            [1, 2],  # search results
            [  # read results
                {'id': 1, 'number': 'INV001', 'amount_total': 1000.0},
                {'id': 2, 'number': 'INV002', 'amount_total': 1500.0},
            ]
        ]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.get_invoices(patient_id=100)
        
        assert len(result) == 2
        assert result[0]['number'] == 'INV001'
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_get_payments(self, mock_timeout, mock_proxy):
        """Test getting payments."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.side_effect = [
            [1, 2],  # search results
            [  # read results
                {'id': 1, 'amount': 500.0, 'payment_date': '2025-01-01'},
                {'id': 2, 'amount': 500.0, 'payment_date': '2025-01-02'},
            ]
        ]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.get_payments(patient_id=100)
        
        assert len(result) == 2
        assert result[0]['amount'] == 500.0
    
    @patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy')
    @patch('app.integrations.odoo_client.socket.setdefaulttimeout')
    def test_get_outstanding_balance(self, mock_timeout, mock_proxy):
        """Test getting outstanding balance."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_models = Mock()
        mock_models.execute_kw.side_effect = [
            [1, 2],  # search results
            [  # read results
                {'id': 1, 'amount_residual': 400.0},
                {'id': 2, 'amount_residual': 600.0}
            ]
        ]
        mock_proxy.side_effect = [mock_common, mock_models]
        
        client = OdooClient()
        client.authenticate()
        
        result = client.get_outstanding_balance(patient_id=100)
        
        assert result['total_outstanding'] == 1000.0
        assert result['invoice_count'] == 2

