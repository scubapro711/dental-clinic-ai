"""
Test Suite for Bug #3: SQL Injection via Domain Parameter

This test suite verifies that domain validation prevents:
1. Invalid domain structures
2. SQL injection attempts
3. Malicious operators
4. Invalid field names
5. Type mismatches

While Odoo's ORM prevents SQL injection, this validation layer provides
Defense in Depth security and enforces best practices.

Bug Report: BUG_REPORT_odoo_client.md - Bug #3
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.integrations.odoo_client import OdooClient, OdooValidationError


class TestBug3DomainValidation:
    """Test domain validation for Bug #3 - SQL Injection Prevention"""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for OdooClient"""
        with patch('app.integrations.odoo_client.settings') as mock_settings:
            mock_settings.ODOO_URL = "http://localhost:8069"
            mock_settings.ODOO_DB = "test_db"
            mock_settings.ODOO_USERNAME = "admin"
            mock_settings.ODOO_PASSWORD = "admin"
            yield mock_settings
    
    @pytest.fixture
    def client(self, mock_settings):
        """Create OdooClient with mocked authentication"""
        with patch('app.integrations.odoo_client.xmlrpc.client.ServerProxy') as mock_proxy:
            # Mock authentication
            mock_common = Mock()
            mock_common.authenticate.return_value = 1
            mock_proxy.return_value = mock_common
            
            client = OdooClient()
            client.uid = 1
            client.models = Mock()
            
            yield client


class TestValidDomains(TestBug3DomainValidation):
    """Test that valid domains pass validation"""
    
    def test_empty_domain(self, client):
        """Empty domain should be valid"""
        with patch.object(client, '_execute', return_value=[]):
            result = client.search('res.partner', domain=[])
            assert result == []
    
    def test_simple_equality(self, client):
        """Simple equality domain should be valid"""
        domain = [('name', '=', 'John')]
        with patch.object(client, '_execute', return_value=[1]):
            result = client.search('res.partner', domain=domain)
            assert result == [1]
    
    def test_multiple_clauses(self, client):
        """Multiple clauses should be valid"""
        domain = [
            ('age', '>', 18),
            ('active', '=', True),
            ('customer_rank', '>=', 1)
        ]
        with patch.object(client, '_execute', return_value=[1, 2]):
            result = client.search('res.partner', domain=domain)
            assert result == [1, 2]
    
    def test_logical_operators(self, client):
        """Logical operators should be valid"""
        domain = [
            '|',
            ('name', '=', 'John'),
            ('name', '=', 'Jane')
        ]
        with patch.object(client, '_execute', return_value=[1, 2]):
            result = client.search('res.partner', domain=domain)
            assert result == [1, 2]
    
    def test_complex_logical_domain(self, client):
        """Complex logical domain should be valid"""
        domain = [
            '&',
            ('active', '=', True),
            '|',
            ('type', '=', 'patient'),
            ('type', '=', 'doctor')
        ]
        with patch.object(client, '_execute', return_value=[1, 2, 3]):
            result = client.search('res.partner', domain=domain)
            assert result == [1, 2, 3]
    
    def test_list_operator_in(self, client):
        """'in' operator with list should be valid"""
        domain = [('id', 'in', [1, 2, 3])]
        with patch.object(client, '_execute', return_value=[1, 2, 3]):
            result = client.search('res.partner', domain=domain)
            assert result == [1, 2, 3]
    
    def test_list_operator_not_in(self, client):
        """'not in' operator with list should be valid"""
        domain = [('id', 'not in', [4, 5, 6])]
        with patch.object(client, '_execute', return_value=[1, 2, 3]):
            result = client.search('res.partner', domain=domain)
            assert result == [1, 2, 3]
    
    def test_string_operator_like(self, client):
        """'like' operator should be valid"""
        domain = [('name', 'like', '%John%')]
        with patch.object(client, '_execute', return_value=[1]):
            result = client.search('res.partner', domain=domain)
            assert result == [1]
    
    def test_string_operator_ilike(self, client):
        """'ilike' operator should be valid"""
        domain = [('name', 'ilike', '%john%')]
        with patch.object(client, '_execute', return_value=[1]):
            result = client.search('res.partner', domain=domain)
            assert result == [1]
    
    def test_related_field(self, client):
        """Related field (dot notation) should be valid"""
        domain = [('partner_id.name', '=', 'John')]
        with patch.object(client, '_execute', return_value=[1]):
            result = client.search('patient.patient', domain=domain)
            assert result == [1]
    
    def test_all_comparison_operators(self, client):
        """All comparison operators should be valid"""
        operators = ['=', '!=', '>', '>=', '<', '<=']
        for op in operators:
            domain = [('age', op, 18)]
            with patch.object(client, '_execute', return_value=[1]):
                result = client.search('res.partner', domain=domain)
                assert result == [1]


class TestInvalidStructure(TestBug3DomainValidation):
    """Test that invalid domain structures are rejected"""
    
    def test_domain_not_list(self, client):
        """Domain must be a list"""
        with pytest.raises(OdooValidationError, match="Domain must be a list"):
            client.search('res.partner', domain="invalid")
    
    def test_domain_is_dict(self, client):
        """Domain cannot be a dict"""
        with pytest.raises(OdooValidationError, match="Domain must be a list"):
            client.search('res.partner', domain={'name': 'John'})
    
    def test_clause_invalid_type(self, client):
        """Clause must be tuple/list or logical operator"""
        domain = [123]  # Invalid: number
        with pytest.raises(OdooValidationError, match="must be tuple/list or logical operator"):
            client.search('res.partner', domain=domain)
    
    def test_clause_wrong_length(self, client):
        """Clause must have exactly 3 elements"""
        domain = [('name', '=')]  # Missing value
        with pytest.raises(OdooValidationError, match="must have 3 elements"):
            client.search('res.partner', domain=domain)
    
    def test_clause_too_many_elements(self, client):
        """Clause cannot have more than 3 elements"""
        domain = [('name', '=', 'John', 'extra')]
        with pytest.raises(OdooValidationError, match="must have 3 elements"):
            client.search('res.partner', domain=domain)
    
    def test_empty_field_name(self, client):
        """Field name cannot be empty"""
        domain = [('', '=', 'value')]
        with pytest.raises(OdooValidationError, match="Field name cannot be empty"):
            client.search('res.partner', domain=domain)


class TestSQLInjectionAttempts(TestBug3DomainValidation):
    """Test that SQL injection attempts are blocked"""
    
    def test_sql_injection_in_operator(self, client):
        """SQL injection in operator should be blocked"""
        domain = [('name', "OR 1=1; --", 'value')]
        with pytest.raises(OdooValidationError, match="Invalid operator"):
            client.search('res.partner', domain=domain)
    
    def test_sql_injection_in_field_name(self, client):
        """SQL injection in field name should be blocked"""
        domain = [('name; DROP TABLE users; --', '=', 'value')]
        with pytest.raises(OdooValidationError, match="Field name contains invalid characters"):
            client.search('res.partner', domain=domain)
    
    def test_sql_comment_in_field(self, client):
        """SQL comment in field name should be blocked"""
        domain = [('name--comment', '=', 'value')]
        with pytest.raises(OdooValidationError, match="Field name contains invalid characters"):
            client.search('res.partner', domain=domain)
    
    def test_sql_union_in_field(self, client):
        """SQL UNION in field name should be blocked"""
        domain = [('name UNION SELECT', '=', 'value')]
        with pytest.raises(OdooValidationError, match="Field name contains invalid characters"):
            client.search('res.partner', domain=domain)
    
    def test_script_tag_in_field(self, client):
        """Script tag in field name should be blocked"""
        domain = [('name<script>alert(1)</script>', '=', 'value')]
        with pytest.raises(OdooValidationError, match="Field name contains invalid characters"):
            client.search('res.partner', domain=domain)
    
    def test_semicolon_in_field(self, client):
        """Semicolon in field name should be blocked"""
        domain = [('name;', '=', 'value')]
        with pytest.raises(OdooValidationError, match="Field name contains invalid characters"):
            client.search('res.partner', domain=domain)
    
    def test_sql_keywords_in_field(self, client):
        """SQL keywords with spaces in field name should be blocked"""
        domain = [('SELECT * FROM users', '=', 'value')]
        with pytest.raises(OdooValidationError, match="Field name contains invalid characters"):
            client.search('res.partner', domain=domain)


class TestInvalidOperators(TestBug3DomainValidation):
    """Test that invalid operators are rejected"""
    
    def test_unknown_operator(self, client):
        """Unknown operator should be rejected"""
        domain = [('name', 'EQUALS', 'value')]
        with pytest.raises(OdooValidationError, match="Invalid operator"):
            client.search('res.partner', domain=domain)
    
    def test_operator_not_string(self, client):
        """Operator must be a string"""
        domain = [('name', 123, 'value')]
        with pytest.raises(OdooValidationError, match="Operator must be string"):
            client.search('res.partner', domain=domain)
    
    def test_invalid_logical_operator(self, client):
        """Invalid logical operator should be rejected"""
        domain = ['AND', ('name', '=', 'John')]
        with pytest.raises(OdooValidationError, match="Invalid logical operator"):
            client.search('res.partner', domain=domain)
    
    def test_sql_operator(self, client):
        """SQL operators should be rejected"""
        domain = [('id', 'BETWEEN', [1, 10])]
        with pytest.raises(OdooValidationError, match="Invalid operator"):
            client.search('res.partner', domain=domain)


class TestInvalidFieldNames(TestBug3DomainValidation):
    """Test that invalid field names are rejected"""
    
    def test_field_not_string(self, client):
        """Field name must be a string"""
        domain = [(123, '=', 'value')]
        with pytest.raises(OdooValidationError, match="Field name must be string"):
            client.search('res.partner', domain=domain)
    
    def test_field_with_special_chars(self, client):
        """Field name with special characters should be rejected"""
        domain = [('name@domain', '=', 'value')]
        with pytest.raises(OdooValidationError, match="Field name contains invalid characters"):
            client.search('res.partner', domain=domain)
    
    def test_field_with_parentheses(self, client):
        """Field name with parentheses should be rejected"""
        domain = [('name()', '=', 'value')]
        with pytest.raises(OdooValidationError, match="Field name contains invalid characters"):
            client.search('res.partner', domain=domain)
    
    def test_field_with_brackets(self, client):
        """Field name with brackets should be rejected"""
        domain = [('name[0]', '=', 'value')]
        with pytest.raises(OdooValidationError, match="Field name contains invalid characters"):
            client.search('res.partner', domain=domain)


class TestTypeMismatches(TestBug3DomainValidation):
    """Test that type mismatches are caught"""
    
    def test_in_operator_with_non_list(self, client):
        """'in' operator requires list/tuple value"""
        domain = [('id', 'in', 123)]
        with pytest.raises(OdooValidationError, match="requires list/tuple value"):
            client.search('res.partner', domain=domain)
    
    def test_not_in_operator_with_string(self, client):
        """'not in' operator requires list/tuple value"""
        domain = [('id', 'not in', 'invalid')]
        with pytest.raises(OdooValidationError, match="requires list/tuple value"):
            client.search('res.partner', domain=domain)
    
    def test_comparison_operator_with_list(self, client):
        """Comparison operators cannot be used with lists"""
        domain = [('id', '>', [1, 2, 3])]
        with pytest.raises(OdooValidationError, match="cannot be used with list"):
            client.search('res.partner', domain=domain)
    
    def test_comparison_operator_with_dict(self, client):
        """Comparison operators cannot be used with dicts"""
        domain = [('id', '>', {'key': 'value'})]
        with pytest.raises(OdooValidationError, match="cannot be used with dict"):
            client.search('res.partner', domain=domain)


class TestRealWorldScenarios(TestBug3DomainValidation):
    """Test real-world domain usage scenarios"""
    
    def test_patient_search_by_id(self, client):
        """Patient search by ID (existing code pattern)"""
        patient_id = 123
        domain = [('patient_id', '=', patient_id)]
        with patch.object(client, '_execute', return_value=[1]):
            result = client.search('patient.appointment', domain=domain)
            assert result == [1]
    
    def test_patient_search_by_name(self, client):
        """Patient search by name"""
        domain = [('name', 'ilike', '%John%')]
        with patch.object(client, '_execute', return_value=[1, 2]):
            result = client.search('res.partner', domain=domain)
            assert result == [1, 2]
    
    def test_date_range_search(self, client):
        """Date range search (common in reports)"""
        domain = [
            ('date', '>=', '2024-01-01'),
            ('date', '<=', '2024-12-31')
        ]
        with patch.object(client, '_execute', return_value=[1, 2, 3]):
            result = client.search('patient.appointment', domain=domain)
            assert result == [1, 2, 3]
    
    def test_active_patients_only(self, client):
        """Active patients only (common filter)"""
        domain = [('active', '=', True)]
        with patch.object(client, '_execute', return_value=[1, 2, 3, 4, 5]):
            result = client.search('res.partner', domain=domain)
            assert result == [1, 2, 3, 4, 5]
    
    def test_multiple_ids_search(self, client):
        """Search by multiple IDs (bulk operations)"""
        domain = [('id', 'in', [1, 2, 3, 4, 5])]
        with patch.object(client, '_execute', return_value=[1, 2, 3, 4, 5]):
            result = client.search('res.partner', domain=domain)
            assert result == [1, 2, 3, 4, 5]
    
    def test_complex_patient_query(self, client):
        """Complex patient query with multiple conditions"""
        domain = [
            '&',
            ('active', '=', True),
            '&',
            ('customer_rank', '>', 0),
            '|',
            ('name', 'ilike', '%clinic%'),
            ('email', 'ilike', '%clinic%')
        ]
        with patch.object(client, '_execute', return_value=[1, 2]):
            result = client.search('res.partner', domain=domain)
            assert result == [1, 2]


class TestSearchReadDomainValidation(TestBug3DomainValidation):
    """Test domain validation in search_read method"""
    
    def test_search_read_valid_domain(self, client):
        """search_read should validate domain"""
        domain = [('name', '=', 'John')]
        with patch.object(client, '_execute', return_value=[{'id': 1, 'name': 'John'}]):
            result = client.search_read('res.partner', domain=domain, fields=['name'])
            assert result == [{'id': 1, 'name': 'John'}]
    
    def test_search_read_invalid_domain(self, client):
        """search_read should reject invalid domain"""
        domain = [('name; DROP TABLE', '=', 'value')]
        with pytest.raises(OdooValidationError, match="Field name contains invalid characters"):
            client.search_read('res.partner', domain=domain, fields=['name'])


class TestSearchCountDomainValidation(TestBug3DomainValidation):
    """Test domain validation in search_count method"""
    
    def test_search_count_valid_domain(self, client):
        """search_count should validate domain"""
        domain = [('active', '=', True)]
        with patch.object(client, '_execute', return_value=10):
            result = client.search_count('res.partner', domain=domain)
            assert result == 10
    
    def test_search_count_invalid_domain(self, client):
        """search_count should reject invalid domain"""
        domain = [('name', 'INVALID_OP', 'value')]
        with pytest.raises(OdooValidationError, match="Invalid operator"):
            client.search_count('res.partner', domain=domain)


class TestEdgeCases(TestBug3DomainValidation):
    """Test edge cases and corner scenarios"""
    
    def test_none_domain(self, client):
        """None domain should be converted to empty list"""
        with patch.object(client, '_execute', return_value=[]):
            result = client.search('res.partner', domain=None)
            assert result == []
    
    def test_very_long_domain(self, client):
        """Very long domain should be valid"""
        domain = [('field' + str(i), '=', i) for i in range(100)]
        with patch.object(client, '_execute', return_value=[]):
            result = client.search('res.partner', domain=domain)
            assert result == []
    
    def test_nested_logical_operators(self, client):
        """Deeply nested logical operators should be valid"""
        domain = [
            '&',
            '|',
            ('a', '=', 1),
            ('b', '=', 2),
            '|',
            ('c', '=', 3),
            ('d', '=', 4)
        ]
        with patch.object(client, '_execute', return_value=[]):
            result = client.search('res.partner', domain=domain)
            assert result == []
    
    def test_unicode_in_value(self, client):
        """Unicode in value should be valid"""
        domain = [('name', '=', 'שלום')]
        with patch.object(client, '_execute', return_value=[1]):
            result = client.search('res.partner', domain=domain)
            assert result == [1]
    
    def test_special_odoo_operators(self, client):
        """Special Odoo operators should be valid"""
        operators = ['=?', 'child_of', 'parent_of']
        for op in operators:
            domain = [('id', op, 1)]
            with patch.object(client, '_execute', return_value=[1]):
                result = client.search('res.partner', domain=domain)
                assert result == [1]

