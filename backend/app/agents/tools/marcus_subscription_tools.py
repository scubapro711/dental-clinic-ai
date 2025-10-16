"""
Marcus Subscription Tools

Subscription and billing management tools for Marcus CFO agent.
Uses MCP Client to interact with Stripe via Model Context Protocol.

Reference: Track 4 - Pricing & Trial + MCP Integration
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from langchain.tools import tool

from app.integrations.mcp_client import get_stripe_client, MCPClientError
from app.services.stripe_service import StripeService, PLAN_PRICING
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.plan_configuration import PlanConfiguration
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

# Initialize __all__ list
__all__ = [
    'get_subscription_status',
    'list_subscription_invoices',
    'analyze_subscription_usage',
    'suggest_plan_upgrade',
    'get_billing_summary',
]


@tool
def get_subscription_status(organization_id: str) -> str:
    """
    Get current subscription status for the clinic.
    
    Args:
        organization_id: Organization UUID
        
    Returns:
        Subscription status summary as formatted string
    """
    try:
        db = SessionLocal()
        
        # Get subscription
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == organization_id
        ).order_by(Subscription.created_at.desc()).first()
        
        if not subscription:
            return "❌ **אין מנוי פעיל**\n\nהמרפאה טרם נרשמה למנוי DentaFlow."
        
        # Format status
        status_emoji = {
            SubscriptionStatus.TRIALING: "🆓",
            SubscriptionStatus.ACTIVE: "✅",
            SubscriptionStatus.PAST_DUE: "⚠️",
            SubscriptionStatus.CANCELED: "❌",
            SubscriptionStatus.UNPAID: "⚠️"
        }.get(subscription.status, "❓")
        
        result = f"""
{status_emoji} **סטטוס מנוי DentaFlow**

📦 **תוכנית:** {subscription.plan_tier.value.title()}
💰 **מחיר חודשי:** {subscription.currency} {subscription.amount:,.2f}
📊 **סטטוס:** {subscription.status.value}

"""
        
        if subscription.is_in_trial:
            days_left = (subscription.trial_end - datetime.utcnow()).days
            result += f"🆓 **תקופת ניסיון:** {days_left} ימים נותרו\n"
            result += f"📅 **סיום ניסיון:** {subscription.trial_end.strftime('%d/%m/%Y')}\n\n"
        
        result += f"📅 **תקופה נוכחית:** {subscription.current_period_start.strftime('%d/%m/%Y')} - {subscription.current_period_end.strftime('%d/%m/%Y')}\n"
        
        if subscription.cancel_at_period_end:
            result += f"\n⚠️ **המנוי יבוטל ב:** {subscription.current_period_end.strftime('%d/%m/%Y')}\n"
        
        # Add plan limits
        limits = subscription.plan_limits
        result += f"\n**מגבלות תוכנית:**\n"
        result += f"👥 משתמשים: {limits['users']}\n"
        result += f"🦷 מטופלים: {limits['patients']}\n"
        
        db.close()
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error getting subscription status: {e}")
        return f"שגיאה בקבלת סטטוס מנוי: {str(e)}"


@tool
def list_subscription_invoices(organization_id: str, limit: int = 5) -> str:
    """
    List recent invoices for the clinic's subscription.
    
    Args:
        organization_id: Organization UUID
        limit: Maximum number of invoices to return (default: 5)
        
    Returns:
        Invoice list as formatted string
    """
    try:
        db = SessionLocal()
        
        # Get subscription
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == organization_id
        ).order_by(Subscription.created_at.desc()).first()
        
        if not subscription:
            db.close()
            return "❌ **אין מנוי פעיל**"
        
        # Get invoices via Stripe service
        stripe_service = StripeService(db)
        invoices = stripe_service.list_invoices(subscription, limit=limit)
        
        if not invoices:
            db.close()
            return "📄 **אין חשבוניות זמינות**"
        
        result = f"📄 **חשבוניות מנוי ({len(invoices)})**\n\n"
        
        for invoice in invoices:
            status_emoji = {
                "paid": "✅",
                "open": "⏳",
                "void": "❌",
                "uncollectible": "⚠️"
            }.get(invoice.status.value, "❓")
            
            result += f"{status_emoji} **{invoice.invoice_number or 'ממתין למספר'}**\n"
            result += f"   💰 סכום: {invoice.currency} {invoice.amount_due:,.2f}\n"
            result += f"   📅 תאריך: {invoice.created_at.strftime('%d/%m/%Y')}\n"
            
            if invoice.invoice_pdf:
                result += f"   📥 [הורד PDF]({invoice.invoice_pdf})\n"
            
            result += "\n"
        
        db.close()
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error listing invoices: {e}")
        return f"שגיאה בקבלת חשבוניות: {str(e)}"


@tool
def analyze_subscription_usage(organization_id: str) -> str:
    """
    Analyze subscription usage and provide insights.
    
    Args:
        organization_id: Organization UUID
        
    Returns:
        Usage analysis as formatted string
    """
    try:
        db = SessionLocal()
        
        # Get subscription
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == organization_id
        ).order_by(Subscription.created_at.desc()).first()
        
        if not subscription:
            db.close()
            return "❌ **אין מנוי פעיל**"
        
        # Get organization
        from app.models.organization import Organization
        from app.models.organization_membership import OrganizationMembership
        
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        
        # Count users
        user_count = db.query(OrganizationMembership).filter(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.is_active == True
        ).count()
        
        # Get patient count (from Odoo)
        # TODO: Implement patient count from Odoo
        patient_count = 0  # Placeholder
        
        # Get plan limits
        limits = subscription.plan_limits
        max_users = limits['users'] if limits['users'] != 'Unlimited' else float('inf')
        max_patients = limits['patients'] if limits['patients'] != 'Unlimited' else float('inf')
        
        result = f"""
📊 **ניתוח שימוש במנוי**

📦 **תוכנית:** {subscription.plan_tier.value.title()}

**שימוש נוכחי:**
👥 משתמשים: {user_count} / {limits['users']}
🦷 מטופלים: {patient_count} / {limits['patients']}

"""
        
        # Usage percentage
        if max_users != float('inf'):
            user_usage = (user_count / max_users) * 100
            result += f"📈 ניצול משתמשים: {user_usage:.1f}%\n"
            
            if user_usage > 80:
                result += "⚠️ **התראה:** קרוב למגבלת משתמשים!\n"
        
        if max_patients != float('inf') and patient_count > 0:
            patient_usage = (patient_count / max_patients) * 100
            result += f"📈 ניצול מטופלים: {patient_usage:.1f}%\n"
            
            if patient_usage > 80:
                result += "⚠️ **התראה:** קרוב למגבלת מטופלים!\n"
        
        # Days until renewal
        days_until_renewal = (subscription.current_period_end - datetime.utcnow()).days
        result += f"\n📅 **ימים עד חידוש:** {days_until_renewal}\n"
        
        # Cost analysis
        daily_cost = float(subscription.amount) / 30
        result += f"\n💰 **עלות יומית:** {subscription.currency} {daily_cost:.2f}\n"
        result += f"💰 **עלות חודשית:** {subscription.currency} {subscription.amount:,.2f}\n"
        
        db.close()
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error analyzing subscription usage: {e}")
        return f"שגיאה בניתוח שימוש: {str(e)}"


@tool
def suggest_plan_upgrade(organization_id: str) -> str:
    """
    Suggest plan upgrade based on usage patterns.
    
    Args:
        organization_id: Organization UUID
        
    Returns:
        Upgrade suggestions as formatted string
    """
    try:
        db = SessionLocal()
        
        # Get current subscription
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == organization_id
        ).order_by(Subscription.created_at.desc()).first()
        
        if not subscription:
            db.close()
            return "❌ **אין מנוי פעיל**"
        
        current_tier = subscription.plan_tier.value
        
        # Get all active plans
        plans = db.query(PlanConfiguration).filter(
            PlanConfiguration.is_active == True
        ).order_by(PlanConfiguration.sort_order).all()
        
        # Find current plan index
        current_plan = next((p for p in plans if p.plan_key == current_tier), None)
        if not current_plan:
            db.close()
            return "❌ **לא נמצאה תוכנית נוכחית**"
        
        # Find next tier
        current_index = plans.index(current_plan)
        if current_index >= len(plans) - 1:
            db.close()
            return "✅ **אתה כבר בתוכנית הגבוהה ביותר!**"
        
        next_plan = plans[current_index + 1]
        
        # Calculate upgrade cost
        price_diff = next_plan.amount - current_plan.amount
        
        result = f"""
🚀 **המלצה לשדרוג תוכנית**

**תוכנית נוכחית:** {current_plan.name}
💰 מחיר: {current_plan.currency} {current_plan.amount:,.2f}/חודש

**תוכנית מומלצת:** {next_plan.name}
💰 מחיר: {next_plan.currency} {next_plan.amount:,.2f}/חודש
📈 הפרש: +{next_plan.currency} {price_diff:,.2f}/חודש

**יתרונות השדרוג:**
"""
        
        # Compare features
        current_limits = current_plan.limits_display
        next_limits = next_plan.limits_display
        
        result += f"👥 משתמשים: {current_limits['users']} → {next_limits['users']}\n"
        result += f"🦷 מטופלים: {current_limits['patients']} → {next_limits['patients']}\n"
        
        # Additional features
        current_features = set(current_plan.features)
        next_features = set(next_plan.features)
        new_features = next_features - current_features
        
        if new_features:
            result += f"\n✨ **פיצ'רים חדשים:**\n"
            for feature in new_features:
                result += f"   • {feature}\n"
        
        result += f"\n💡 **המלצה:** שדרוג לתוכנית {next_plan.name} יספק יותר גמישות ופיצ'רים מתקדמים.\n"
        
        db.close()
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error suggesting plan upgrade: {e}")
        return f"שגיאה בהמלצת שדרוג: {str(e)}"


@tool
def get_billing_summary(organization_id: str) -> str:
    """
    Get comprehensive billing summary for the clinic.
    
    Args:
        organization_id: Organization UUID
        
    Returns:
        Billing summary as formatted string
    """
    try:
        db = SessionLocal()
        
        # Get subscription
        subscription = db.query(Subscription).filter(
            Subscription.organization_id == organization_id
        ).order_by(Subscription.created_at.desc()).first()
        
        if not subscription:
            db.close()
            return "❌ **אין מנוי פעיל**"
        
        # Get invoices
        stripe_service = StripeService(db)
        invoices = stripe_service.list_invoices(subscription, limit=12)  # Last 12 months
        
        # Calculate totals
        total_paid = sum(float(inv.amount_paid) for inv in invoices)
        total_due = sum(float(inv.amount_remaining) for inv in invoices)
        
        result = f"""
💰 **סיכום חיוב DentaFlow**

📦 **מנוי נוכחי:** {subscription.plan_tier.value.title()}
💵 **מחיר חודשי:** {subscription.currency} {subscription.amount:,.2f}

**סטטיסטיקות תשלום:**
✅ סה"כ שולם: {subscription.currency} {total_paid:,.2f}
⏳ סה"כ ממתין: {subscription.currency} {total_due:,.2f}
📄 מספר חשבוניות: {len(invoices)}

"""
        
        if subscription.is_in_trial:
            days_left = (subscription.trial_end - datetime.utcnow()).days
            result += f"🆓 **תקופת ניסיון:** {days_left} ימים נותרו\n"
            result += f"💳 **חיוב ראשון ב:** {subscription.trial_end.strftime('%d/%m/%Y')}\n\n"
        else:
            result += f"📅 **חיוב הבא ב:** {subscription.current_period_end.strftime('%d/%m/%Y')}\n\n"
        
        # Payment method status
        if subscription.stripe_customer_id:
            result += "✅ **אמצעי תשלום:** מוגדר\n"
        else:
            result += "⚠️ **אמצעי תשלום:** לא מוגדר\n"
        
        db.close()
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error getting billing summary: {e}")
        return f"שגיאה בקבלת סיכום חיוב: {str(e)}"



# Export tools as a list
marcus_subscription_tools = [
    get_subscription_status,
    list_subscription_invoices,
    analyze_subscription_usage,
    suggest_plan_upgrade,
    get_billing_summary,
]

