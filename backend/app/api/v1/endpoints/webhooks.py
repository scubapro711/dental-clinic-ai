"""
Stripe Webhooks Handler

Handles Stripe webhook events for subscription lifecycle management.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.stripe_service import StripeService
from app.models.subscription import Subscription, SubscriptionStatus
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    
    Events handled:
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - customer.subscription.trial_will_end
    - invoice.payment_succeeded
    - invoice.payment_failed
    - payment_intent.succeeded
    - payment_intent.payment_failed
    """
    try:
        # Get raw body
        payload = await request.body()
        
        # Verify webhook signature (TODO: implement signature verification)
        # For now, we'll trust the webhook (NOT PRODUCTION READY!)
        # In production, use: stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        
        # Parse event
        import json
        event = json.loads(payload)
        
        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})
        
        logger.info(f"Received Stripe webhook: {event_type}")
        
        # Route to appropriate handler
        if event_type == "customer.subscription.created":
            await handle_subscription_created(data, db)
        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(data, db)
        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(data, db)
        elif event_type == "customer.subscription.trial_will_end":
            await handle_trial_will_end(data, db)
        elif event_type == "invoice.payment_succeeded":
            await handle_payment_succeeded(data, db)
        elif event_type == "invoice.payment_failed":
            await handle_payment_failed(data, db)
        elif event_type == "payment_intent.succeeded":
            await handle_payment_intent_succeeded(data, db)
        elif event_type == "payment_intent.payment_failed":
            await handle_payment_intent_failed(data, db)
        else:
            logger.info(f"Unhandled event type: {event_type}")
        
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=400, detail=str(e))


async def handle_subscription_created(data: Dict[str, Any], db: Session):
    """Handle subscription.created event."""
    stripe_subscription_id = data.get("id")
    customer_id = data.get("customer")
    status = data.get("status")
    
    logger.info(f"Subscription created: {stripe_subscription_id}")
    
    # Sync subscription from Stripe
    stripe_service = StripeService(db)
    await stripe_service.sync_subscription_from_stripe(stripe_subscription_id)


async def handle_subscription_updated(data: Dict[str, Any], db: Session):
    """Handle subscription.updated event."""
    stripe_subscription_id = data.get("id")
    status = data.get("status")
    
    logger.info(f"Subscription updated: {stripe_subscription_id}, status: {status}")
    
    # Sync subscription from Stripe
    stripe_service = StripeService(db)
    await stripe_service.sync_subscription_from_stripe(stripe_subscription_id)


async def handle_subscription_deleted(data: Dict[str, Any], db: Session):
    """Handle subscription.deleted event."""
    stripe_subscription_id = data.get("id")
    
    logger.info(f"Subscription deleted: {stripe_subscription_id}")
    
    # Find subscription in database
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_subscription_id
    ).first()
    
    if subscription:
        subscription.status = SubscriptionStatus.CANCELED
        subscription.canceled_at = datetime.utcnow()
        db.commit()
        logger.info(f"Marked subscription {subscription.id} as canceled")


async def handle_trial_will_end(data: Dict[str, Any], db: Session):
    """
    Handle subscription.trial_will_end event.
    
    This event is sent 7 days before trial ends.
    We can send a reminder email to the clinic.
    """
    stripe_subscription_id = data.get("id")
    trial_end = data.get("trial_end")
    
    logger.info(f"Trial will end for subscription: {stripe_subscription_id}")
    
    # Find subscription in database
    subscription = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == stripe_subscription_id
    ).first()
    
    if subscription and subscription.organization:
        # TODO: Send reminder email
        # email_service.send_trial_ending_reminder(
        #     to=subscription.organization.email,
        #     trial_end_date=datetime.fromtimestamp(trial_end)
        # )
        logger.info(f"Should send trial ending reminder to {subscription.organization.name}")


async def handle_payment_succeeded(data: Dict[str, Any], db: Session):
    """Handle invoice.payment_succeeded event."""
    invoice_id = data.get("id")
    subscription_id = data.get("subscription")
    amount_paid = data.get("amount_paid") / 100  # Convert from cents
    
    logger.info(f"Payment succeeded: {invoice_id}, amount: ${amount_paid}")
    
    # Sync subscription status
    if subscription_id:
        stripe_service = StripeService(db)
        await stripe_service.sync_subscription_from_stripe(subscription_id)


async def handle_payment_failed(data: Dict[str, Any], db: Session):
    """Handle invoice.payment_failed event."""
    invoice_id = data.get("id")
    subscription_id = data.get("subscription")
    
    logger.warning(f"Payment failed: {invoice_id}")
    
    # Find subscription
    if subscription_id:
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_id
        ).first()
        
        if subscription:
            # Mark as past_due
            subscription.status = SubscriptionStatus.PAST_DUE
            db.commit()
            
            # TODO: Send payment failed email
            # email_service.send_payment_failed_notification(
            #     to=subscription.organization.email
            # )
            logger.warning(f"Marked subscription {subscription.id} as past_due")


async def handle_payment_intent_succeeded(data: Dict[str, Any], db: Session):
    """Handle payment_intent.succeeded event."""
    payment_intent_id = data.get("id")
    amount = data.get("amount") / 100
    
    logger.info(f"Payment intent succeeded: {payment_intent_id}, amount: ${amount}")


async def handle_payment_intent_failed(data: Dict[str, Any], db: Session):
    """Handle payment_intent.payment_failed event."""
    payment_intent_id = data.get("id")
    
    logger.warning(f"Payment intent failed: {payment_intent_id}")

