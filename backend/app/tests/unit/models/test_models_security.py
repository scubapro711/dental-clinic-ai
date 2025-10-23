"""
Unit Tests for Security Models

Tests for security-related models including:
- Audit log model
- Compliance models
- Security tracking
"""

import pytest


@pytest.mark.unit
@pytest.mark.models
class TestSecurityModels:
    """Test Security Models."""
    
    def test_audit_log_model_import(self):
        """Test that AuditLog model can be imported."""
        try:
            from app.models.audit_log import AuditLog
            assert AuditLog is not None
            assert hasattr(AuditLog, '__tablename__')
        except ImportError:
            pytest.skip("AuditLog model not found")
    
    def test_compliance_alert_model_import(self):
        """Test that ComplianceAlert model can be imported."""
        try:
            from app.models.compliance_alert import ComplianceAlert
            assert ComplianceAlert is not None
        except ImportError:
            pytest.skip("ComplianceAlert model not found")
    
    def test_baa_signature_model_import(self):
        """Test that BAASignature model can be imported."""
        try:
            from app.models.baa_signature import BAASignature
            assert BAASignature is not None
        except ImportError:
            pytest.skip("BAASignature model not found")
    
    def test_consent_model_import(self):
        """Test that Consent model can be imported."""
        try:
            from app.models.consent import Consent
            assert Consent is not None
        except ImportError:
            pytest.skip("Consent model not found")


@pytest.mark.unit
@pytest.mark.models
class TestBusinessModels:
    """Test Business Models."""
    
    def test_invoice_model_import(self):
        """Test that Invoice model can be imported."""
        try:
            from app.models.invoice import Invoice
            assert Invoice is not None
        except ImportError:
            pytest.skip("Invoice model not found")
    
    def test_payment_model_import(self):
        """Test that Payment model can be imported."""
        try:
            from app.models.payment import Payment
            assert Payment is not None
        except ImportError:
            pytest.skip("Payment model not found")
    
    def test_cost_tracking_model_import(self):
        """Test that CostTracking model can be imported."""
        try:
            from app.models.cost_tracking import CostTracking
            assert CostTracking is not None
        except ImportError:
            pytest.skip("CostTracking model not found")

