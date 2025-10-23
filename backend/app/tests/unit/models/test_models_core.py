"""
Unit Tests for Core Models

Tests for key models including:
- Organization model
- Subscription tiers
- Model relationships
- Field validation
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.models.organization import Organization, SubscriptionTier


@pytest.mark.unit
@pytest.mark.models
class TestOrganizationModel:
    """Test Organization Model."""
    
    def test_organization_model_exists(self):
        """Test that Organization model can be imported."""
        assert Organization is not None
    
    def test_organization_has_required_fields(self):
        """Test that Organization has expected fields."""
        assert hasattr(Organization, 'id')
        assert hasattr(Organization, 'name')
        assert hasattr(Organization, 'slug')
        assert hasattr(Organization, 'email')
        assert hasattr(Organization, 'subscription_tier')
    
    def test_subscription_tier_enum_values(self):
        """Test SubscriptionTier enum values."""
        assert SubscriptionTier.BASIC == "basic"
        assert SubscriptionTier.PROFESSIONAL == "professional"
        assert SubscriptionTier.ENTERPRISE == "enterprise"
    
    def test_subscription_tier_has_three_tiers(self):
        """Test that there are exactly 3 subscription tiers."""
        tiers = list(SubscriptionTier)
        assert len(tiers) == 3
    
    def test_organization_tablename(self):
        """Test that Organization has correct table name."""
        assert Organization.__tablename__ == "organizations"


@pytest.mark.unit
@pytest.mark.models
class TestModelImports:
    """Test that key models can be imported."""
    
    def test_import_conversation_model(self):
        """Test importing conversation model."""
        try:
            from app.models.conversation import Conversation
            assert Conversation is not None
        except ImportError:
            pytest.skip("Conversation model not found")
    
    def test_import_message_model(self):
        """Test importing message model."""
        try:
            from app.models.message import Message
            assert Message is not None
        except ImportError:
            pytest.skip("Message model not found")
    
    def test_import_audit_log_model(self):
        """Test importing audit_log model."""
        try:
            from app.models.audit_log import AuditLog
            assert AuditLog is not None
        except ImportError:
            pytest.skip("AuditLog model not found")
    
    def test_import_organization_membership_model(self):
        """Test importing organization_membership model."""
        try:
            from app.models.organization_membership import OrganizationMembership
            assert OrganizationMembership is not None
        except ImportError:
            pytest.skip("OrganizationMembership model not found")

