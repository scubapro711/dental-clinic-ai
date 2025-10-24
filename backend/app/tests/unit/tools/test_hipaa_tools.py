"""
Unit Tests for HIPAA Tools

Tests for app.tools.hipaa_tools module including:
- search_hipaa_knowledge
- check_phi_compliance
- validate_baa
- assess_security_controls
- generate_breach_report
- audit_access_logs
- check_patient_rights
- evaluate_risk
- generate_compliance_report
- recommend_remediation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.tools.hipaa_tools import (
    search_hipaa_knowledge,
    check_phi_compliance,
    validate_baa,
)


@pytest.mark.unit
class TestSearchHipaaKnowledge:
    """Test search_hipaa_knowledge tool."""
    
    @patch('app.tools.hipaa_tools.vector_db')
    def test_search_success(self, mock_vector_db):
        """Test successful knowledge base search."""
        mock_vector_db.search.return_value = [
            {
                'text': 'PHI must be encrypted',
                'metadata': {'file_path': 'security_rule.md', 'category': 'security'},
                'score': 0.92
            },
            {
                'text': 'Access controls required',
                'metadata': {'file_path': 'privacy_rule.md', 'category': 'privacy'},
                'score': 0.85
            }
        ]
        
        result = search_hipaa_knowledge.invoke({"query": "encryption requirements"})
        
        assert result['status'] == 'success'
        assert result['total_results'] == 2
        assert len(result['results']) == 2
        assert result['results'][0]['content'] == 'PHI must be encrypted'
        assert result['results'][0]['score'] == 0.92
    
    @patch('app.tools.hipaa_tools.vector_db')
    def test_search_no_results(self, mock_vector_db):
        """Test search with no results."""
        mock_vector_db.search.return_value = []
        
        result = search_hipaa_knowledge.invoke({"query": "nonexistent topic"})
        
        assert result['status'] == 'no_results'
        assert result['total_results'] == 0
        assert result['results'] == []
    
    @patch('app.tools.hipaa_tools.vector_db')
    def test_search_error(self, mock_vector_db):
        """Test search with error."""
        mock_vector_db.search.side_effect = Exception("Database error")
        
        result = search_hipaa_knowledge.invoke({"query": "test query"})
        
        assert result['status'] == 'error'
        assert 'Failed to search' in result['message']
        assert result['total_results'] == 0


@pytest.mark.unit
class TestCheckPhiCompliance:
    """Test check_phi_compliance tool."""
    
    def test_fully_compliant(self):
        """Test fully compliant PHI handling."""
        result = check_phi_compliance.invoke({
            "data_description": "Patient records",
            "storage_location": "GCP Cloud SQL",
            "access_controls": "Role-based access control with MFA",
            "encryption_status": "both"
        })
        
        assert result['status'] == 'compliant'
        assert result['compliance_score'] >= 90
        assert result['total_findings'] == 0
    
    def test_no_encryption(self):
        """Test non-compliant: no encryption."""
        result = check_phi_compliance.invoke({
            "data_description": "Patient records",
            "storage_location": "GCP Cloud SQL",
            "access_controls": "Role-based access control with MFA",
            "encryption_status": "none"
        })
        
        assert result['status'] == 'non_compliant'
        assert result['compliance_score'] < 70
        assert result['total_findings'] >= 1
        assert any(f['severity'] == 'critical' for f in result['findings'])
    
    def test_partial_encryption(self):
        """Test partially compliant: only encryption at rest."""
        result = check_phi_compliance.invoke({
            "data_description": "Patient records",
            "storage_location": "GCP Cloud SQL",
            "access_controls": "Role-based access control with MFA",
            "encryption_status": "encrypted_at_rest"
        })
        
        assert result['status'] in ['compliant', 'partially_compliant']
        assert result['compliance_score'] >= 70
        assert result['total_findings'] >= 1
        assert any(f['severity'] == 'high' for f in result['findings'])
    
    def test_no_mfa(self):
        """Test non-compliant: no MFA."""
        result = check_phi_compliance.invoke({
            "data_description": "Patient records",
            "storage_location": "GCP Cloud SQL",
            "access_controls": "Basic password authentication",
            "encryption_status": "both"
        })
        
        assert result['total_findings'] >= 1
        assert any('mfa' in f['finding'].lower() for f in result['findings'])
    
    def test_no_rbac(self):
        """Test non-compliant: no RBAC."""
        result = check_phi_compliance.invoke({
            "data_description": "Patient records",
            "storage_location": "GCP Cloud SQL",
            "access_controls": "MFA enabled",
            "encryption_status": "both"
        })
        
        assert result['total_findings'] >= 1
        assert any('role' in f['finding'].lower() for f in result['findings'])
    
    def test_local_storage(self):
        """Test local storage warning."""
        result = check_phi_compliance.invoke({
            "data_description": "Patient records",
            "storage_location": "Local server",
            "access_controls": "Role-based access control with MFA",
            "encryption_status": "both"
        })
        
        assert result['total_findings'] >= 1
        assert any('local' in f['finding'].lower() for f in result['findings'])


@pytest.mark.unit
class TestValidateBaa:
    """Test validate_baa tool."""
    
    def test_compliant_baa(self):
        """Test compliant BAA."""
        result = validate_baa.invoke({
            "vendor_name": "Cloud Provider",
            "baa_signed": True,
            "baa_date": "2024-01-15",
            "services_provided": "Cloud storage",
            "phi_access": True
        })
        
        assert result['compliance_status'] in ['compliant', 'review_needed']
        assert result['baa_required'] is True
        assert result['baa_signed'] is True
    
    def test_missing_baa(self):
        """Test missing BAA when required."""
        result = validate_baa.invoke({
            "vendor_name": "Cloud Provider",
            "baa_signed": False,
            "services_provided": "Cloud storage",
            "phi_access": True
        })
        
        assert result['compliance_status'] == 'non_compliant'
        assert result['baa_required'] is True
        assert result['baa_signed'] is False
        assert result['total_issues'] >= 1
        assert any(i['severity'] == 'critical' for i in result['issues'])
    
    def test_old_baa(self):
        """Test old BAA that needs review."""
        old_date = (datetime.now() - timedelta(days=1200)).strftime('%Y-%m-%d')
        
        result = validate_baa.invoke({
            "vendor_name": "Cloud Provider",
            "baa_signed": True,
            "baa_date": old_date,
            "services_provided": "Cloud storage",
            "phi_access": True
        })
        
        assert result['compliance_status'] == 'review_needed'
        assert result['total_issues'] >= 1
        assert any('old' in i['issue'].lower() for i in result['issues'])
    
    def test_no_phi_access_no_baa_needed(self):
        """Test vendor with no PHI access doesn't need BAA."""
        result = validate_baa.invoke({
            "vendor_name": "Marketing Agency",
            "baa_signed": False,
            "services_provided": "Marketing services",
            "phi_access": False
        })
        
        assert result['baa_required'] is False
        assert result['compliance_status'] in ['compliant', 'review_needed']
    
    def test_no_phi_access_but_baa_signed(self):
        """Test vendor with no PHI access but BAA signed."""
        result = validate_baa.invoke({
            "vendor_name": "Marketing Agency",
            "baa_signed": True,
            "baa_date": "2024-01-15",
            "services_provided": "Marketing services",
            "phi_access": False
        })
        
        assert result['baa_required'] is False
        assert result['baa_signed'] is True
        # Should have an info issue about unnecessary BAA
        assert result['total_issues'] >= 1
    
    def test_invalid_baa_date(self):
        """Test invalid BAA date format."""
        result = validate_baa.invoke({
            "vendor_name": "Cloud Provider",
            "baa_signed": True,
            "baa_date": "invalid-date",
            "services_provided": "Cloud storage",
            "phi_access": True
        })
        
        # Should still return a result, possibly with a warning
        assert result['vendor_name'] == "Cloud Provider"
        assert result['baa_signed'] is True

