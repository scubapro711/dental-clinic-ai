"""Quick test for new OdooClient methods."""
import sys
import os
sys.path.insert(0, 'app')

from unittest.mock import Mock, patch
from app.integrations.odoo_client import OdooClient

def test_search_patients():
    """Test search_patients method."""
    with patch('app.integrations.odoo_client.settings') as mock_settings:
        mock_settings.ODOO_URL = 'https://test.odoo.com'
        mock_settings.ODOO_DB = 'test_db'
        mock_settings.ODOO_USERNAME = 'test_user'
        mock_settings.ODOO_PASSWORD = 'test_pass'
        
        with patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy'):
            client = OdooClient()
            client._authenticated = True
            client.uid = 1
            
            # Mock the search method
            client.search = Mock(return_value=[12, 45, 67])
            
            # Test search_patients
            result = client.search_patients(name="Cohen", limit=5)
            
            assert result == [12, 45, 67], f"Expected [12, 45, 67], got {result}"
            client.search.assert_called_once_with('res.partner', [('name', 'ilike', 'Cohen')], limit=5)
            print("✅ test_search_patients PASSED")

def test_get_patient():
    """Test get_patient method."""
    with patch('app.integrations.odoo_client.settings') as mock_settings:
        mock_settings.ODOO_URL = 'https://test.odoo.com'
        mock_settings.ODOO_DB = 'test_db'
        mock_settings.ODOO_USERNAME = 'test_user'
        mock_settings.ODOO_PASSWORD = 'test_pass'
        
        with patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy'):
            client = OdooClient()
            client._authenticated = True
            client.uid = 1
            
            # Mock the read method
            mock_patient = {'id': 12, 'name': 'David Cohen', 'phone': '052-1234567'}
            client.read = Mock(return_value=[mock_patient])
            
            # Test get_patient
            result = client.get_patient(12)
            
            assert result == mock_patient, f"Expected {mock_patient}, got {result}"
            print("✅ test_get_patient PASSED")

def test_get_doctors():
    """Test get_doctors method."""
    with patch('app.integrations.odoo_client.settings') as mock_settings:
        mock_settings.ODOO_URL = 'https://test.odoo.com'
        mock_settings.ODOO_DB = 'test_db'
        mock_settings.ODOO_USERNAME = 'test_user'
        mock_settings.ODOO_PASSWORD = 'test_pass'
        
        with patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy'):
            client = OdooClient()
            client._authenticated = True
            client.uid = 1
            
            # Mock the get_physicians method
            mock_doctors = [
                {'id': 1, 'name': 'Dr. Smith'},
                {'id': 2, 'name': 'Dr. Jones'}
            ]
            client.get_physicians = Mock(return_value=mock_doctors)
            
            # Test get_doctors
            result = client.get_doctors(limit=10)
            
            assert result == mock_doctors, f"Expected {mock_doctors}, got {result}"
            print("✅ test_get_doctors PASSED")

if __name__ == '__main__':
    test_search_patients()
    test_get_patient()
    test_get_doctors()
    print("\n🎉 All new methods tests PASSED!")
