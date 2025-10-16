"""
Stripe Service

Business logic for Stripe integration via MCP.
Handles subscription management, billing, and payments.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from decimal import Decimal

from app.integrations.mcp_client import get_stripe_client, MCPClientError
from app.models.subscription import Subscription, SubscriptionStatus, PlanTier
from app.models.payment import Payment, PaymentStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.organization import Organization
import logging

logger = logging.getLogger(__name__)


# Pricing configuration (in ILS, from SAAS_PRICING_REVISED_GCP_ILS.md)
PLAN_PRICING = {
    PlanTier.STARTER: {
        "amount": Decimal("1633.00"),  # ₪1,633/month
        "currency": "ILS",
        "name": "DentaFlow Starter",
        "description": "1 user, 100 patients, basic AI features"
    },
    PlanTier.PROFESSIONAL: {
        "amount": Decimal("3070.00"),  # ₪3,070/month
        "currency": "ILS",
        "name": "DentaFlow Professional",
        "description": "5 users, 500 patients, advanced AI features"
    },
    PlanTier.ENTERPRISE: {
        "amount": Decimal("6141.00"),  # ₪6,141/month
        "currency": "ILS",
        "name": "DentaFlow Enterprise",
        "description": "Unlimited users & patients, all features"
    }
}

TRIAL_DAYS = 30
EARLY_ADOPTER_DISCOUNT = Decimal("0.20")  # 20% discount


class StripeService:
    """
    Stripe Service
    
    Handles all Stripe operations via MCP client.
    Syncs data with local database models.
    """
    
    def __init__(self, db: Session):
        """
        Initialize Stripe Service
        
        Args:
            db: Database session
        """
        self.db = db
        self.mcp_client = get_stripe_client()
    
    async def create_customer(
        self,
        organization: Organization,
        email: str,
        name: str,
        phone: Optional[str] = None
    ) -> str:
        """
        Create a Stripe customer
        
        Args:
            organization: Organization model
            email: Customer email
            name: Customer name
            phone: Customer phone (optional)
        
        Returns:
            Stripe customer ID
        
        Raises:
            MCPClientError: If customer creation fails
        """
        try:
            input_data = {
                "email": email,
                "name": name,
                "metadata": {
                    "organization_id": str(organization.id),
                    "organization_name": organization.name
                }
            }
            
            if phone:
                input_data["phone"] = phone
            
            result = self.mcp_client.call_tool("create_customer", input_data)
            
            customer_id = result.get("id")
            if not customer_id:
                raise MCPClientError("No customer ID returned from Stripe")
            
            logger.info(f"Created Stripe customer: {customer_id} for org {organization.id}")
            return customer_id
        
        except Exception as e:
            logger.error(f"Failed to create Stripe customer: {str(e)}")
            raise
    
    async def create_subscription(
        self,
        organization: Organization,
        plan_tier: PlanTier,
        trial_days: int = TRIAL_DAYS,
        apply_early_adopter_discount: bool = False
    ) -> Subscription:
        """
        Create a subscription with trial period
        
        Args:
            organization: Organization model
            plan_tier: Subscription tier
            trial_days: Trial period in days (default: 30)
            apply_early_adopter_discount: Apply 20% early adopter discount
        
        Returns:
            Subscription model
        
        Raises:
            MCPClientError: If subscription creation fails
        """
        try:
            # Get pricing
            pricing = PLAN_PRICING[plan_tier]
            amount = pricing["amount"]
            
            # Apply early adopter discount if applicable
            if apply_early_adopter_discount:
                amount = amount * (Decimal("1.00") - EARLY_ADOPTER_DISCOUNT)
                logger.info(f"Applied early adopter discount: {EARLY_ADOPTER_DISCOUNT * 100}%")
            
            # Create or get Stripe customer
            if not organization.stripe_customer_id:
                customer_id = await self.create_customer(
                    organization=organization,
                    email=organization.email,
                    name=organization.name,
                    phone=organization.phone
                )
                organization.stripe_customer_id = customer_id
                self.db.commit()
            else:
                customer_id = organization.stripe_customer_id
            
            # Create Stripe product (if not exists)
            # Note: In production, products should be pre-created
            # For now, we'll create them on-the-fly
            
            # Create Stripe subscription via MCP
            trial_end = datetime.utcnow() + timedelta(days=trial_days)
            
            input_data = {
                "customer": customer_id,
                "items": [{
                    "price_data": {
                        "currency": pricing["currency"].lower(),
                        "product_data": {
                            "name": pricing["name"],
                            "description": pricing["description"]
                        },
                        "unit_amount": int(amount * 100),  # Convert to cents
                        "recurring": {
                            "interval": "month"
                        }
                    }
                }],
                "trial_end": int(trial_end.timestamp()),
                "metadata": {
                    "organization_id": str(organization.id),
                    "plan_tier": plan_tier.value,
                    "early_adopter": str(apply_early_adopter_discount)
                }
            }
            
            result = self.mcp_client.call_tool("create_subscription", input_data)
            
            stripe_subscription_id = result.get("id")
            if not stripe_subscription_id:
                raise MCPClientError("No subscription ID returned from Stripe")
            
            # Create local subscription record
            subscription = Subscription(
                organization_id=organization.id,
                stripe_subscription_id=stripe_subscription_id,
                stripe_customer_id=customer_id,
                plan_tier=plan_tier,
                status=SubscriptionStatus.TRIALING,
                current_period_start=datetime.utcnow(),
                current_period_end=trial_end,
                trial_start=datetime.utcnow(),
                trial_end=trial_end,
                amount=amount,
                currency=pricing["currency"]
            )
            
            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)
            
            logger.info(f"Created subscription: {subscription.id} for org {organization.id}")
            return subscription
        
        except Exception as e:
            logger.error(f"Failed to create subscription: {str(e)}")
            self.db.rollback()
            raise
    
    async def cancel_subscription(
        self,
        subscription: Subscription,
        cancel_immediately: bool = False
    ) -> Subscription:
        """
        Cancel a subscription
        
        Args:
            subscription: Subscription model
            cancel_immediately: Cancel immediately (default: at period end)
        
        Returns:
            Updated subscription model
        
        Raises:
            MCPClientError: If cancellation fails
        """
        try:
            input_data = {
                "subscription_id": subscription.stripe_subscription_id,
                "cancel_at_period_end": not cancel_immediately
            }
            
            result = self.mcp_client.call_tool("cancel_subscription", input_data)
            
            # Update local record
            subscription.cancel_at_period_end = not cancel_immediately
            subscription.canceled_at = datetime.utcnow()
            
            if cancel_immediately:
                subscription.status = SubscriptionStatus.CANCELED
            
            self.db.commit()
            self.db.refresh(subscription)
            
            logger.info(f"Canceled subscription: {subscription.id}")
            return subscription
        
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {str(e)}")
            self.db.rollback()
            raise
    
    async def sync_subscription_from_stripe(
        self,
        subscription: Subscription
    ) -> Subscription:
        """
        Sync subscription data from Stripe
        
        Args:
            subscription: Subscription model
        
        Returns:
            Updated subscription model
        
        Raises:
            MCPClientError: If sync fails
        """
        try:
            input_data = {
                "id": subscription.stripe_subscription_id
            }
            
            result = self.mcp_client.call_tool("fetch_stripe_resources", input_data)
            
            # Update local record with Stripe data
            stripe_status = result.get("status")
            if stripe_status:
                subscription.status = SubscriptionStatus(stripe_status)
            
            current_period_start = result.get("current_period_start")
            if current_period_start:
                subscription.current_period_start = datetime.fromtimestamp(current_period_start)
            
            current_period_end = result.get("current_period_end")
            if current_period_end:
                subscription.current_period_end = datetime.fromtimestamp(current_period_end)
            
            cancel_at_period_end = result.get("cancel_at_period_end")
            if cancel_at_period_end is not None:
                subscription.cancel_at_period_end = cancel_at_period_end
            
            self.db.commit()
            self.db.refresh(subscription)
            
            logger.info(f"Synced subscription from Stripe: {subscription.id}")
            return subscription
        
        except Exception as e:
            logger.error(f"Failed to sync subscription: {str(e)}")
            self.db.rollback()
            raise
    
    async def list_invoices(
        self,
        subscription: Subscription,
        limit: int = 10
    ) -> list[Invoice]:
        """
        List invoices for a subscription
        
        Args:
            subscription: Subscription model
            limit: Maximum number of invoices to return
        
        Returns:
            List of Invoice models
        
        Raises:
            MCPClientError: If listing fails
        """
        try:
            input_data = {
                "customer": subscription.stripe_customer_id,
                "limit": limit
            }
            
            result = self.mcp_client.call_tool("list_invoices", input_data)
            
            invoices = []
            for stripe_invoice in result.get("data", []):
                # Check if invoice already exists
                existing = self.db.query(Invoice).filter(
                    Invoice.stripe_invoice_id == stripe_invoice["id"]
                ).first()
                
                if existing:
                    invoices.append(existing)
                    continue
                
                # Create new invoice record
                invoice = Invoice(
                    subscription_id=subscription.id,
                    stripe_invoice_id=stripe_invoice["id"],
                    invoice_number=stripe_invoice.get("number"),
                    amount_due=Decimal(stripe_invoice["amount_due"]) / 100,
                    amount_paid=Decimal(stripe_invoice["amount_paid"]) / 100,
                    amount_remaining=Decimal(stripe_invoice["amount_remaining"]) / 100,
                    currency=stripe_invoice["currency"].upper(),
                    status=InvoiceStatus(stripe_invoice["status"]),
                    invoice_pdf=stripe_invoice.get("invoice_pdf"),
                    hosted_invoice_url=stripe_invoice.get("hosted_invoice_url"),
                    due_date=datetime.fromtimestamp(stripe_invoice["due_date"]) if stripe_invoice.get("due_date") else None,
                    paid_at=datetime.fromtimestamp(stripe_invoice["status_transitions"]["paid_at"]) if stripe_invoice.get("status_transitions", {}).get("paid_at") else None
                )
                
                self.db.add(invoice)
                invoices.append(invoice)
            
            self.db.commit()
            
            logger.info(f"Listed {len(invoices)} invoices for subscription {subscription.id}")
            return invoices
        
        except Exception as e:
            logger.error(f"Failed to list invoices: {str(e)}")
            self.db.rollback()
            raise

