"""
Test Issue #8: Unsafe Error Parsing

Issue Description:
    The _execute() method uses string matching to detect error types.
    This is fragile and breaks if Odoo changes error message format.
    
    Current code (lines 274-282):
        if 'constraint' in error_msg.lower():
            raise OdooConstraintError(...)
        elif 'required' in error_msg.lower():
            raise OdooValidationError(...)

Location: Lines 270-282 in odoo_client.py

Impact:
    - Incorrect Error Handling: wrong exception type if format changes
    - Debugging Difficulty: unclear errors
    - False Positives: "constraint" might appear in other contexts

Fix:
    Use Odoo faultCode or structured error detection instead of string matching.
"""

import pytest
from unittest.mock import Mock, patch
import xmlrpc.client
from app.integrations.odoo_client import (
    OdooClient, 
    OdooConstraintError, 
    OdooValidationError
)


class TestIssue8ErrorParsing:
    """Test suite for Issue #8: Unsafe Error Parsing"""
    
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
    
    def test_constraint_error_detected_by_string_matching(self, mock_odoo_client):
        """
        Test that constraint errors are detected via string matching.
        
        This demonstrates the current (fragile) implementation.
        """
        # Mock a constraint violation error
        error = xmlrpc.client.Fault(
            1,
            "psycopg2.IntegrityError: duplicate key value violates unique constraint"
        )
        mock_odoo_client.models.execute_kw.side_effect = error
        
        # Should raise OdooConstraintError
        with pytest.raises(OdooConstraintError) as exc_info:
            mock_odoo_client._execute('res.partner', 'create', [{'name': 'Test'}])
        
        assert 'constraint' in str(exc_info.value).lower()
    
    def test_validation_error_detected_by_string_matching(self, mock_odoo_client):
        """
        Test that validation errors are detected via string matching.
        
        This demonstrates the current (fragile) implementation.
        """
        # Mock a required field error
        error = xmlrpc.client.Fault(
            1,
            "ValidationError: Field 'name' is required"
        )
        mock_odoo_client.models.execute_kw.side_effect = error
        
        # Should raise OdooValidationError
        with pytest.raises(OdooValidationError) as exc_info:
            mock_odoo_client._execute('res.partner', 'create', [{}])
        
        assert 'required' in str(exc_info.value).lower()
    
    def test_string_matching_fails_with_different_format(self, mock_odoo_client):
        """
        Test that improved error detection handles different formats.
        
        AFTER FIX: Now correctly detects IntegrityError even without "constraint" keyword.
        """
        # Mock a constraint error with different format (no "constraint" word)
        error = xmlrpc.client.Fault(
            1,
            "IntegrityError: unique_violation on table res_partner"
        )
        mock_odoo_client.models.execute_kw.side_effect = error
        
        # AFTER FIX: Should raise OdooConstraintError (detects "integrityerror" and "unique_violation")
        with pytest.raises(OdooConstraintError) as exc_info:
            mock_odoo_client._execute('res.partner', 'create', [{'name': 'Test'}])
        
        assert 'IntegrityError' in str(exc_info.value)
    
    def test_string_matching_false_positive(self, mock_odoo_client):
        """
        Test that improved error detection avoids false positives.
        
        AFTER FIX: Now correctly identifies this as NOT a constraint error,
        even though "constraint" appears in the message.
        """
        # Mock an error that mentions "constraint" but isn't a constraint error
        error = xmlrpc.client.Fault(
            1,
            "AccessError: You don't have permission to create records. "
            "This is a security constraint imposed by the system."
        )
        mock_odoo_client.models.execute_kw.side_effect = error
        
        # AFTER FIX: Should re-raise as generic Fault (no specific constraint patterns)
        with pytest.raises(xmlrpc.client.Fault) as exc_info:
            mock_odoo_client._execute('res.partner', 'create', [{'name': 'Test'}])
        
        assert 'AccessError' in str(exc_info.value)
    
    def test_generic_error_without_keywords(self, mock_odoo_client):
        """
        Test that errors without keywords are re-raised as-is.
        """
        # Mock a generic error
        error = xmlrpc.client.Fault(1, "Something went wrong")
        mock_odoo_client.models.execute_kw.side_effect = error
        
        # Should re-raise the original Fault
        with pytest.raises(xmlrpc.client.Fault) as exc_info:
            mock_odoo_client._execute('res.partner', 'search', [[]])
        
        assert "Something went wrong" in str(exc_info.value)
    
    def test_case_insensitive_matching(self, mock_odoo_client):
        """
        Test that error detection is case-insensitive.
        
        AFTER FIX: Generic "CONSTRAINT" word alone is not enough,
        needs specific patterns like "integrityerror" or "unique constraint".
        """
        # Mock error with uppercase "CONSTRAINT" but no specific pattern
        error = xmlrpc.client.Fault(1, "CONSTRAINT violation detected")
        mock_odoo_client.models.execute_kw.side_effect = error
        
        # AFTER FIX: Should re-raise as generic Fault (no specific constraint patterns)
        with pytest.raises(xmlrpc.client.Fault):
            mock_odoo_client._execute('res.partner', 'create', [{'name': 'Test'}])


class TestIssue8EdgeCases:
    """Test edge cases for Issue #8"""
    
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
    
    def test_multiple_keywords_in_error(self, mock_odoo_client):
        """
        Test error with both "constraint" and "required" keywords.
        
        AFTER FIX: Should match ValidationError because "required field" is more specific.
        Priority is given to more specific patterns.
        """
        error = xmlrpc.client.Fault(
            1,
            "Constraint violation: required field 'email' is missing"
        )
        mock_odoo_client.models.execute_kw.side_effect = error
        
        # AFTER FIX: Should raise OdooValidationError ("required field" is more specific)
        with pytest.raises(OdooValidationError) as exc_info:
            mock_odoo_client._execute('res.partner', 'create', [{}])
        
        assert 'required field' in str(exc_info.value).lower()
    
    def test_empty_error_message(self, mock_odoo_client):
        """
        Test error with empty message.
        """
        error = xmlrpc.client.Fault(1, "")
        mock_odoo_client.models.execute_kw.side_effect = error
        
        # Should re-raise as generic Fault
        with pytest.raises(xmlrpc.client.Fault):
            mock_odoo_client._execute('res.partner', 'search', [[]])
    
    def test_non_xmlrpc_exception(self, mock_odoo_client):
        """
        Test that non-xmlrpc exceptions are handled correctly.
        """
        # Mock a generic Python exception
        mock_odoo_client.models.execute_kw.side_effect = ValueError("Invalid input")
        
        # Should re-raise as-is
        with pytest.raises(ValueError) as exc_info:
            mock_odoo_client._execute('res.partner', 'search', [[]])
        
        assert "Invalid input" in str(exc_info.value)
    
    def test_unicode_in_error_message(self, mock_odoo_client):
        """
        Test error message with unicode characters.
        
        AFTER FIX: Generic "constraint" word alone is not enough,
        needs specific patterns.
        """
        error = xmlrpc.client.Fault(
            1,
            "Constraint violation: שם חובה (name required)"
        )
        mock_odoo_client.models.execute_kw.side_effect = error
        
        # AFTER FIX: Should re-raise as generic Fault (no specific constraint patterns)
        # The word "constraint" alone is not sufficient
        with pytest.raises(xmlrpc.client.Fault):
            mock_odoo_client._execute('res.partner', 'create', [{}])


class TestIssue8RealWorldScenarios:
    """Test real-world scenarios for Issue #8"""
    
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
    
    def test_duplicate_patient_email(self, mock_odoo_client):
        """
        Real-world: Duplicate patient email constraint violation.
        """
        error = xmlrpc.client.Fault(
            1,
            "psycopg2.IntegrityError: duplicate key value violates unique constraint \"res_partner_email_uniq\""
        )
        mock_odoo_client.models.execute_kw.side_effect = error
        
        with pytest.raises(OdooConstraintError) as exc_info:
            mock_odoo_client._execute('res.partner', 'create', [{'email': 'test@example.com'}])
        
        assert 'constraint' in str(exc_info.value).lower()
    
    def test_missing_required_field(self, mock_odoo_client):
        """
        Real-world: Missing required field in patient creation.
        """
        error = xmlrpc.client.Fault(
            1,
            "odoo.exceptions.ValidationError: The following fields are required: name"
        )
        mock_odoo_client.models.execute_kw.side_effect = error
        
        with pytest.raises(OdooValidationError) as exc_info:
            mock_odoo_client._execute('res.partner', 'create', [{}])
        
        assert 'required' in str(exc_info.value).lower()
    
    def test_access_denied_error(self, mock_odoo_client):
        """
        Real-world: Access denied error (should not be misclassified).
        """
        error = xmlrpc.client.Fault(
            1,
            "odoo.exceptions.AccessError: You do not have the rights to access this document"
        )
        mock_odoo_client.models.execute_kw.side_effect = error
        
        # Should re-raise as generic Fault (no "constraint" or "required")
        with pytest.raises(xmlrpc.client.Fault):
            mock_odoo_client._execute('res.partner', 'read', [[1]])

