"""
Unit Tests for StripeService

Comprehensive tests for Stripe integration via MCP.
Tests all subscription, billing, and payment operations.

Test Coverage:
- Service initialization
- Customer management
- Subscription lifecycle
- Invoice management
- Error handling
- Edge cases
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from app.services.stripe_service import (
    StripeService,
    PLAN_PRICING,
    TRIAL_DAYS,
    EARLY_ADOPTER_DISCOUNT
)
from app.models.subscription import Subscription, SubscriptionStatus, PlanTier
from app.models.payment import Payment, PaymentStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.organization import Organization
from app.integrations.mcp_client import MCPClientError


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = Mock()
    db.add = Mock()
    db.commit = Mock()
    db.rollback = Mock()
    db.refresh = Mock()
    db.query = Mock()
    return db


@pytest.fixture
def mock_mcp_client():
    """Mock MCP client"""
    client = Mock()
    client.call_tool = Mock()
    return client


@pytest.fixture
def sample_organization():
    """Sample organization for testing"""
    org = Organization(
        id=uuid.uuid4(),
        name="Test Dental Clinic",
        email="test@clinic.com",
        phone="+972-50-123-4567",
        stripe_customer_id=None
    )
    return org


@pytest.fixture
def sample_organization_with_stripe():
    """Sample organization with Stripe customer ID"""
    org = Organization(
        id=uuid.uuid4(),
        name="Test Dental Clinic",
        email="test@clinic.com",
        phone="+972-50-123-4567",
        stripe_customer_id="cus_test123"
    )
    return org


@pytest.fixture
def sample_subscription(sample_organization_with_stripe):
    """Sample subscription for testing"""
    sub = Subscription(
        id=uuid.uuid4(),
        organization_id=sample_organization_with_stripe.id,
        stripe_subscription_id="sub_test123",
        stripe_customer_id="cus_test123",
        plan_tier=PlanTier.PROFESSIONAL,
        status=SubscriptionStatus.ACTIVE,
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
        amount=Decimal("3070.00"),
        currency="ILS"
    )
    return sub


@pytest.mark.unit
@pytest.mark.services
@pytest.mark.asyncio
class TestStripeServiceInitialization:
    """Test StripeService initialization"""
    
    def test_service_initialization(self, mock_db):
        """Test service initializes correctly"""
        with patch('app.services.stripe_service.get_stripe_client') as mock_get_client:
            mock_get_client.return_value = Mock()
            
            service = StripeService(db=mock_db)
            
            assert service.db == mock_db
            assert service.mcp_client is not None
            mock_get_client.assert_called_once()
    
    def test_service_initialization_with_mcp_client(self, mock_db, mock_mcp_client):
        """Test service stores MCP client reference"""
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            assert service.mcp_client == mock_mcp_client


@pytest.mark.unit
@pytest.mark.services
@pytest.mark.asyncio
class TestStripeServiceCustomerManagement:
    """Test customer creation and management"""
    
    async def test_create_customer_success(self, mock_db, mock_mcp_client, sample_organization):
        """Test successful customer creation"""
        # Setup
        mock_mcp_client.call_tool.return_value = {
            "id": "cus_test123",
            "email": sample_organization.email,
            "name": sample_organization.name
        }
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            # Execute
            customer_id = await service.create_customer(
                organization=sample_organization,
                email=sample_organization.email,
                name=sample_organization.name
            )
            
            # Assert
            assert customer_id == "cus_test123"
            mock_mcp_client.call_tool.assert_called_once_with(
                "create_customer",
                {
                    "email": sample_organization.email,
                    "name": sample_organization.name,
                    "metadata": {
                        "organization_id": str(sample_organization.id),
                        "organization_name": sample_organization.name
                    }
                }
            )
    
    async def test_create_customer_with_phone(self, mock_db, mock_mcp_client, sample_organization):
        """Test customer creation with phone number"""
        mock_mcp_client.call_tool.return_value = {"id": "cus_test123"}
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            customer_id = await service.create_customer(
                organization=sample_organization,
                email=sample_organization.email,
                name=sample_organization.name,
                phone=sample_organization.phone
            )
            
            # Verify phone was included in call
            call_args = mock_mcp_client.call_tool.call_args[0][1]
            assert call_args["phone"] == sample_organization.phone
    
    async def test_create_customer_without_phone(self, mock_db, mock_mcp_client, sample_organization):
        """Test customer creation without phone number"""
        mock_mcp_client.call_tool.return_value = {"id": "cus_test123"}
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            customer_id = await service.create_customer(
                organization=sample_organization,
                email=sample_organization.email,
                name=sample_organization.name,
                phone=None
            )
            
            # Verify phone was not included
            call_args = mock_mcp_client.call_tool.call_args[0][1]
            assert "phone" not in call_args
    
    async def test_create_customer_no_id_returned(self, mock_db, mock_mcp_client, sample_organization):
        """Test error when Stripe doesn't return customer ID"""
        mock_mcp_client.call_tool.return_value = {}  # No ID
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            with pytest.raises(MCPClientError, match="No customer ID returned"):
                await service.create_customer(
                    organization=sample_organization,
                    email=sample_organization.email,
                    name=sample_organization.name
                )
    
    async def test_create_customer_mcp_error(self, mock_db, mock_mcp_client, sample_organization):
        """Test handling of MCP client errors"""
        mock_mcp_client.call_tool.side_effect = MCPClientError("Stripe API error")
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            with pytest.raises(MCPClientError):
                await service.create_customer(
                    organization=sample_organization,
                    email=sample_organization.email,
                    name=sample_organization.name
                )


@pytest.mark.unit
@pytest.mark.services
@pytest.mark.asyncio
class TestStripeServiceSubscriptionCreation:
    """Test subscription creation"""
    
    async def test_create_subscription_new_customer(self, mock_db, mock_mcp_client, sample_organization):
        """Test subscription creation for new customer (no Stripe ID)"""
        # Mock customer creation
        mock_mcp_client.call_tool.side_effect = [
            {"id": "cus_new123"},  # create_customer
            {"id": "sub_new123", "status": "trialing"}  # create_subscription
        ]
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            subscription = await service.create_subscription(
                organization=sample_organization,
                plan_tier=PlanTier.STARTER,
                trial_days=30,
                apply_early_adopter_discount=False
            )
            
            # Verify customer was created
            assert mock_mcp_client.call_tool.call_count == 2
            assert sample_organization.stripe_customer_id == "cus_new123"
            
            # Verify subscription was created
            mock_db.add.assert_called()
            mock_db.commit.assert_called()
    
    async def test_create_subscription_existing_customer(self, mock_db, mock_mcp_client, sample_organization_with_stripe):
        """Test subscription creation for existing customer (has Stripe ID)"""
        mock_mcp_client.call_tool.return_value = {
            "id": "sub_test123",
            "status": "trialing"
        }
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            subscription = await service.create_subscription(
                organization=sample_organization_with_stripe,
                plan_tier=PlanTier.PROFESSIONAL,
                trial_days=30,
                apply_early_adopter_discount=False
            )
            
            # Verify only subscription was created (not customer)
            assert mock_mcp_client.call_tool.call_count == 1
            mock_db.add.assert_called()
    
    async def test_create_subscription_with_early_adopter_discount(self, mock_db, mock_mcp_client, sample_organization_with_stripe):
        """Test subscription with 20% early adopter discount"""
        mock_mcp_client.call_tool.return_value = {"id": "sub_test123"}
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            subscription = await service.create_subscription(
                organization=sample_organization_with_stripe,
                plan_tier=PlanTier.PROFESSIONAL,
                trial_days=30,
                apply_early_adopter_discount=True
            )
            
            # Verify discounted amount
            original_amount = PLAN_PRICING[PlanTier.PROFESSIONAL]["amount"]
            expected_amount = original_amount * (Decimal("1.00") - EARLY_ADOPTER_DISCOUNT)
            
            # Check the call to Stripe included discounted amount
            call_args = mock_mcp_client.call_tool.call_args[0][1]
            stripe_amount = call_args["items"][0]["price_data"]["unit_amount"]
            assert stripe_amount == int(expected_amount * 100)
    
    async def test_create_subscription_starter_tier(self, mock_db, mock_mcp_client, sample_organization_with_stripe):
        """Test subscription creation for Starter tier"""
        mock_mcp_client.call_tool.return_value = {"id": "sub_test123"}
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            subscription = await service.create_subscription(
                organization=sample_organization_with_stripe,
                plan_tier=PlanTier.STARTER,
                trial_days=30,
                apply_early_adopter_discount=False
            )
            
            # Verify correct pricing
            call_args = mock_mcp_client.call_tool.call_args[0][1]
            expected_amount = int(PLAN_PRICING[PlanTier.STARTER]["amount"] * 100)
            assert call_args["items"][0]["price_data"]["unit_amount"] == expected_amount
    
    async def test_create_subscription_enterprise_tier(self, mock_db, mock_mcp_client, sample_organization_with_stripe):
        """Test subscription creation for Enterprise tier"""
        mock_mcp_client.call_tool.return_value = {"id": "sub_test123"}
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            subscription = await service.create_subscription(
                organization=sample_organization_with_stripe,
                plan_tier=PlanTier.ENTERPRISE,
                trial_days=30,
                apply_early_adopter_discount=False
            )
            
            # Verify correct pricing
            call_args = mock_mcp_client.call_tool.call_args[0][1]
            expected_amount = int(PLAN_PRICING[PlanTier.ENTERPRISE]["amount"] * 100)
            assert call_args["items"][0]["price_data"]["unit_amount"] == expected_amount
    
    async def test_create_subscription_custom_trial_days(self, mock_db, mock_mcp_client, sample_organization_with_stripe):
        """Test subscription with custom trial period"""
        mock_mcp_client.call_tool.return_value = {"id": "sub_test123"}
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            custom_trial_days = 14
            subscription = await service.create_subscription(
                organization=sample_organization_with_stripe,
                plan_tier=PlanTier.PROFESSIONAL,
                trial_days=custom_trial_days,
                apply_early_adopter_discount=False
            )
            
            # Verify trial period in Stripe call
            call_args = mock_mcp_client.call_tool.call_args[0][1]
            trial_end_timestamp = call_args["trial_end"]
            
            # Trial end should be approximately custom_trial_days from now
            expected_trial_end = datetime.utcnow() + timedelta(days=custom_trial_days)
            actual_trial_end = datetime.fromtimestamp(trial_end_timestamp)
            
            # Allow 1 minute tolerance
            assert abs((actual_trial_end - expected_trial_end).total_seconds()) < 60
    
    async def test_create_subscription_metadata(self, mock_db, mock_mcp_client, sample_organization_with_stripe):
        """Test subscription includes correct metadata"""
        mock_mcp_client.call_tool.return_value = {"id": "sub_test123"}
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            subscription = await service.create_subscription(
                organization=sample_organization_with_stripe,
                plan_tier=PlanTier.PROFESSIONAL,
                trial_days=30,
                apply_early_adopter_discount=True
            )
            
            # Verify metadata
            call_args = mock_mcp_client.call_tool.call_args[0][1]
            metadata = call_args["metadata"]
            
            assert metadata["organization_id"] == str(sample_organization_with_stripe.id)
            assert metadata["plan_tier"] == PlanTier.PROFESSIONAL.value
            assert metadata["early_adopter"] == "True"
    
    async def test_create_subscription_db_rollback_on_error(self, mock_db, mock_mcp_client, sample_organization_with_stripe):
        """Test database rollback on subscription creation error"""
        mock_mcp_client.call_tool.side_effect = MCPClientError("Stripe error")
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            with pytest.raises(MCPClientError):
                await service.create_subscription(
                    organization=sample_organization_with_stripe,
                    plan_tier=PlanTier.PROFESSIONAL,
                    trial_days=30,
                    apply_early_adopter_discount=False
                )
            
            # Verify rollback was called
            mock_db.rollback.assert_called_once()
    
    async def test_create_subscription_no_subscription_id_returned(self, mock_db, mock_mcp_client, sample_organization_with_stripe):
        """Test error when Stripe doesn't return subscription ID"""
        mock_mcp_client.call_tool.return_value = {}  # No ID
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            with pytest.raises(MCPClientError, match="No subscription ID returned"):
                await service.create_subscription(
                    organization=sample_organization_with_stripe,
                    plan_tier=PlanTier.PROFESSIONAL,
                    trial_days=30,
                    apply_early_adopter_discount=False
                )


@pytest.mark.unit
@pytest.mark.services
@pytest.mark.asyncio
class TestStripeServiceSubscriptionCancellation:
    """Test subscription cancellation"""
    
    async def test_cancel_subscription_at_period_end(self, mock_db, mock_mcp_client, sample_subscription):
        """Test subscription cancellation at period end (default)"""
        mock_mcp_client.call_tool.return_value = {"id": sample_subscription.stripe_subscription_id}
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            result = await service.cancel_subscription(
                subscription=sample_subscription,
                cancel_immediately=False
            )
            
            # Verify Stripe was called correctly
            mock_mcp_client.call_tool.assert_called_once_with(
                "cancel_subscription",
                {
                    "subscription_id": sample_subscription.stripe_subscription_id,
                    "cancel_at_period_end": True
                }
            )
            
            # Verify subscription updated
            assert sample_subscription.cancel_at_period_end == True
            assert sample_subscription.canceled_at is not None
            assert sample_subscription.status != SubscriptionStatus.CANCELED  # Not canceled yet
            mock_db.commit.assert_called()
    
    async def test_cancel_subscription_immediately(self, mock_db, mock_mcp_client, sample_subscription):
        """Test immediate subscription cancellation"""
        mock_mcp_client.call_tool.return_value = {"id": sample_subscription.stripe_subscription_id}
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            result = await service.cancel_subscription(
                subscription=sample_subscription,
                cancel_immediately=True
            )
            
            # Verify Stripe was called correctly
            call_args = mock_mcp_client.call_tool.call_args[0][1]
            assert call_args["cancel_at_period_end"] == False
            
            # Verify subscription canceled immediately
            assert sample_subscription.cancel_at_period_end == False
            assert sample_subscription.status == SubscriptionStatus.CANCELED
            mock_db.commit.assert_called()
    
    async def test_cancel_subscription_error_handling(self, mock_db, mock_mcp_client, sample_subscription):
        """Test error handling during cancellation"""
        mock_mcp_client.call_tool.side_effect = MCPClientError("Stripe error")
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            with pytest.raises(MCPClientError):
                await service.cancel_subscription(
                    subscription=sample_subscription,
                    cancel_immediately=False
                )
            
            # Verify rollback
            mock_db.rollback.assert_called_once()


@pytest.mark.unit
@pytest.mark.services
@pytest.mark.asyncio
class TestStripeServiceSubscriptionSync:
    """Test subscription synchronization from Stripe"""
    
    async def test_sync_subscription_success(self, mock_db, mock_mcp_client, sample_subscription):
        """Test successful subscription sync from Stripe"""
        now = datetime.utcnow()
        period_end = now + timedelta(days=30)
        
        mock_mcp_client.call_tool.return_value = {
            "id": sample_subscription.stripe_subscription_id,
            "status": "active",
            "current_period_start": int(now.timestamp()),
            "current_period_end": int(period_end.timestamp()),
            "cancel_at_period_end": False
        }
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            result = await service.sync_subscription_from_stripe(
                subscription=sample_subscription
            )
            
            # Verify Stripe was called
            mock_mcp_client.call_tool.assert_called_once_with(
                "fetch_stripe_resources",
                {"id": sample_subscription.stripe_subscription_id}
            )
            
            # Verify subscription updated
            assert sample_subscription.status == SubscriptionStatus.ACTIVE
            assert sample_subscription.cancel_at_period_end == False
            mock_db.commit.assert_called()
    
    async def test_sync_subscription_status_change(self, mock_db, mock_mcp_client, sample_subscription):
        """Test subscription status change during sync"""
        sample_subscription.status = SubscriptionStatus.TRIALING
        
        mock_mcp_client.call_tool.return_value = {
            "status": "past_due",
            "current_period_start": int(datetime.utcnow().timestamp()),
            "current_period_end": int((datetime.utcnow() + timedelta(days=30)).timestamp())
        }
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            result = await service.sync_subscription_from_stripe(
                subscription=sample_subscription
            )
            
            # Verify status updated
            assert sample_subscription.status == SubscriptionStatus.PAST_DUE
    
    async def test_sync_subscription_error_handling(self, mock_db, mock_mcp_client, sample_subscription):
        """Test error handling during sync"""
        mock_mcp_client.call_tool.side_effect = MCPClientError("Stripe error")
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            with pytest.raises(MCPClientError):
                await service.sync_subscription_from_stripe(
                    subscription=sample_subscription
                )
            
            # Verify rollback
            mock_db.rollback.assert_called_once()


@pytest.mark.unit
@pytest.mark.services
@pytest.mark.asyncio
class TestStripeServiceInvoiceManagement:
    """Test invoice listing and management"""
    
    async def test_list_invoices_success(self, mock_db, mock_mcp_client, sample_subscription):
        """Test successful invoice listing"""
        now = datetime.utcnow()
        
        mock_mcp_client.call_tool.return_value = {
            "data": [
                {
                    "id": "in_test123",
                    "number": "INV-001",
                    "amount_due": 307000,  # ₪3,070 in cents
                    "amount_paid": 307000,
                    "amount_remaining": 0,
                    "currency": "ils",
                    "status": "paid",
                    "invoice_pdf": "https://stripe.com/invoice.pdf",
                    "hosted_invoice_url": "https://stripe.com/invoice",
                    "due_date": int(now.timestamp()),
                    "status_transitions": {
                        "paid_at": int(now.timestamp())
                    }
                }
            ]
        }
        
        # Mock query to return no existing invoices
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            invoices = await service.list_invoices(
                subscription=sample_subscription,
                limit=10
            )
            
            # Verify Stripe was called
            mock_mcp_client.call_tool.assert_called_once_with(
                "list_invoices",
                {
                    "customer": sample_subscription.stripe_customer_id,
                    "limit": 10
                }
            )
            
            # Verify invoice created
            assert len(invoices) == 1
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called()
    
    async def test_list_invoices_existing_invoice(self, mock_db, mock_mcp_client, sample_subscription):
        """Test listing invoices when invoice already exists in DB"""
        existing_invoice = Invoice(
            id=uuid.uuid4(),
            subscription_id=sample_subscription.id,
            stripe_invoice_id="in_test123",
            invoice_number="INV-001",
            amount_due=Decimal("3070.00"),
            amount_paid=Decimal("3070.00"),
            amount_remaining=Decimal("0.00"),
            currency="ILS",
            status=InvoiceStatus.PAID
        )
        
        mock_mcp_client.call_tool.return_value = {
            "data": [
                {
                    "id": "in_test123",
                    "number": "INV-001",
                    "amount_due": 307000,
                    "amount_paid": 307000,
                    "amount_remaining": 0,
                    "currency": "ils",
                    "status": "paid"
                }
            ]
        }
        
        # Mock query to return existing invoice
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = existing_invoice
        mock_db.query.return_value = mock_query
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            invoices = await service.list_invoices(
                subscription=sample_subscription,
                limit=10
            )
            
            # Verify existing invoice returned, no new invoice created
            assert len(invoices) == 1
            assert invoices[0] == existing_invoice
            mock_db.add.assert_not_called()
    
    async def test_list_invoices_empty(self, mock_db, mock_mcp_client, sample_subscription):
        """Test listing invoices when none exist"""
        mock_mcp_client.call_tool.return_value = {"data": []}
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            invoices = await service.list_invoices(
                subscription=sample_subscription,
                limit=10
            )
            
            assert len(invoices) == 0
            mock_db.add.assert_not_called()
    
    async def test_list_invoices_custom_limit(self, mock_db, mock_mcp_client, sample_subscription):
        """Test listing invoices with custom limit"""
        mock_mcp_client.call_tool.return_value = {"data": []}
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            invoices = await service.list_invoices(
                subscription=sample_subscription,
                limit=50
            )
            
            # Verify limit passed to Stripe
            call_args = mock_mcp_client.call_tool.call_args[0][1]
            assert call_args["limit"] == 50
    
    async def test_list_invoices_error_handling(self, mock_db, mock_mcp_client, sample_subscription):
        """Test error handling during invoice listing"""
        mock_mcp_client.call_tool.side_effect = MCPClientError("Stripe error")
        
        with patch('app.services.stripe_service.get_stripe_client', return_value=mock_mcp_client):
            service = StripeService(db=mock_db)
            
            with pytest.raises(MCPClientError):
                await service.list_invoices(
                    subscription=sample_subscription,
                    limit=10
                )
            
            # Verify rollback
            mock_db.rollback.assert_called_once()


@pytest.mark.unit
@pytest.mark.services
class TestStripeServicePricing:
    """Test pricing configuration"""
    
    def test_plan_pricing_structure(self):
        """Test PLAN_PRICING has correct structure"""
        for tier in PlanTier:
            assert tier in PLAN_PRICING
            pricing = PLAN_PRICING[tier]
            
            assert "amount" in pricing
            assert "currency" in pricing
            assert "name" in pricing
            assert "description" in pricing
            
            assert isinstance(pricing["amount"], Decimal)
            assert pricing["currency"] == "ILS"
    
    def test_trial_days_constant(self):
        """Test TRIAL_DAYS constant"""
        assert TRIAL_DAYS == 30
        assert isinstance(TRIAL_DAYS, int)
    
    def test_early_adopter_discount_constant(self):
        """Test EARLY_ADOPTER_DISCOUNT constant"""
        assert EARLY_ADOPTER_DISCOUNT == Decimal("0.20")
        assert isinstance(EARLY_ADOPTER_DISCOUNT, Decimal)
    
    def test_pricing_amounts(self):
        """Test pricing amounts match specification"""
        assert PLAN_PRICING[PlanTier.STARTER]["amount"] == Decimal("1633.00")
        assert PLAN_PRICING[PlanTier.PROFESSIONAL]["amount"] == Decimal("3070.00")
        assert PLAN_PRICING[PlanTier.ENTERPRISE]["amount"] == Decimal("6141.00")



