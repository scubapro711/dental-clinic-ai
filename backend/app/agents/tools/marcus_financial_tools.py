"""
Marcus Financial Tools - Enhanced with Odoo Client V3

Complete financial analysis tools using Odoo Dental financial models.

Reference: ODOO_DENTAL_MODULE_ANALYSIS.md, Phase 3
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from langchain.tools import tool

from app.integrations.odoo_client_v3 import odoo_client_v3

logger = logging.getLogger(__name__)


@tool
def get_revenue_overview(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> str:
    """
    Get comprehensive revenue overview for a time period.
    
    Args:
        date_from: Start date (YYYY-MM-DD). Defaults to 30 days ago.
        date_to: End date (YYYY-MM-DD). Defaults to today.
        
    Returns:
        Revenue overview as formatted string
    """
    try:
        # Default to last 30 days
        if not date_to:
            date_to = datetime.now().strftime("%Y-%m-%d")
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        revenue_data = odoo_client_v3.get_revenue_by_period(date_from, date_to)
        
        result = f"""
📊 **סקירת הכנסות**
תקופה: {date_from} עד {date_to}

💰 **הכנסות כוללות:** ₪{revenue_data['total_revenue']:,.2f}
📄 **מספר חשבוניות:** {revenue_data['invoice_count']}
📈 **ממוצע לחשבונית:** ₪{revenue_data['average_invoice']:,.2f}
"""
        
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error getting revenue overview: {e}")
        return f"שגיאה בקבלת סקירת הכנסות: {str(e)}"


@tool
def get_outstanding_invoices(patient_id: Optional[int] = None) -> str:
    """
    Get list of outstanding (unpaid) invoices.
    
    Args:
        patient_id: Optional patient ID to filter by specific patient
        
    Returns:
        Outstanding invoices summary as formatted string
    """
    try:
        outstanding_data = odoo_client_v3.get_outstanding_balance(patient_id=patient_id)
        
        result = f"""
⚠️ **חשבוניות ממתינות לתשלום**

💰 **סה"כ חוב:** ₪{outstanding_data['total_outstanding']:,.2f}
📄 **מספר חשבוניות:** {outstanding_data['invoice_count']}
"""
        
        if outstanding_data['invoices']:
            result += "\n**פירוט חשבוניות:**\n"
            for inv in outstanding_data['invoices'][:10]:  # Top 10
                patient_name = inv.get('partner_id', [None, 'לא ידוע'])[1] if isinstance(inv.get('partner_id'), list) else 'לא ידוע'
                result += f"- {inv.get('name', 'N/A')}: {patient_name} - ₪{inv.get('amount_residual', 0):,.2f}\n"
        
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error getting outstanding invoices: {e}")
        return f"שגיאה בקבלת חשבוניות ממתינות: {str(e)}"


@tool
def get_top_treatments_by_revenue(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 10,
) -> str:
    """
    Get top treatments by revenue.
    
    Args:
        date_from: Start date (YYYY-MM-DD). Defaults to 30 days ago.
        date_to: End date (YYYY-MM-DD). Defaults to today.
        limit: Number of top treatments to return
        
    Returns:
        Top treatments as formatted string
    """
    try:
        # Default to last 30 days
        if not date_to:
            date_to = datetime.now().strftime("%Y-%m-%d")
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        treatments = odoo_client_v3.get_treatment_revenue(
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )
        
        result = f"""
🏆 **טיפולים מובילים לפי הכנסות**
תקופה: {date_from} עד {date_to}

"""
        
        if treatments:
            for i, treatment in enumerate(treatments, 1):
                result += f"{i}. **{treatment['product_name']}**\n"
                result += f"   הכנסה: ₪{treatment['revenue']:,.2f} | כמות: {int(treatment['quantity'])}\n"
        else:
            result += "לא נמצאו טיפולים בתקופה זו."
        
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error getting top treatments: {e}")
        return f"שגיאה בקבלת טיפולים מובילים: {str(e)}"


@tool
def get_payment_collection_status(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> str:
    """
    Get payment collection status and rates.
    
    Args:
        date_from: Start date (YYYY-MM-DD). Defaults to 30 days ago.
        date_to: End date (YYYY-MM-DD). Defaults to today.
        
    Returns:
        Payment collection status as formatted string
    """
    try:
        # Default to last 30 days
        if not date_to:
            date_to = datetime.now().strftime("%Y-%m-%d")
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        payments = odoo_client_v3.get_payments(
            date_from=date_from,
            date_to=date_to
        )
        
        total_collected = sum(p.get('amount', 0) for p in payments)
        payment_count = len(payments)
        avg_payment = total_collected / payment_count if payment_count > 0 else 0
        
        result = f"""
💳 **סטטוס גביית תשלומים**
תקופה: {date_from} עד {date_to}

💰 **סה"כ נגבה:** ₪{total_collected:,.2f}
🧾 **מספר תשלומים:** {payment_count}
📊 **ממוצע לתשלום:** ₪{avg_payment:,.2f}
"""
        
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error getting payment collection status: {e}")
        return f"שגיאה בקבלת סטטוס גבייה: {str(e)}"


@tool
def get_financial_summary(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> str:
    """
    Get comprehensive financial summary including revenue, payments, and outstanding.
    
    Args:
        date_from: Start date (YYYY-MM-DD). Defaults to 30 days ago.
        date_to: End date (YYYY-MM-DD). Defaults to today.
        
    Returns:
        Financial summary as formatted string
    """
    try:
        # Default to last 30 days
        if not date_to:
            date_to = datetime.now().strftime("%Y-%m-%d")
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        summary = odoo_client_v3.get_financial_summary(date_from, date_to)
        
        result = f"""
📊 **סיכום פיננסי מקיף**
תקופה: {date_from} עד {date_to}

💰 **הכנסות**
- סה"כ: ₪{summary['revenue']['total_revenue']:,.2f}
- חשבוניות: {summary['revenue']['invoice_count']}
- ממוצע: ₪{summary['revenue']['average_invoice']:,.2f}

💳 **תשלומים שנגבו**
- סה"כ: ₪{summary['payments']['total_collected']:,.2f}
- מספר תשלומים: {summary['payments']['payment_count']}

⚠️ **חובות**
- סה"כ חוב: ₪{summary['outstanding']['total']:,.2f}
- חשבוניות ממתינות: {summary['outstanding']['invoice_count']}

🏆 **טיפולים מובילים**
"""
        
        if summary['top_treatments']:
            for i, treatment in enumerate(summary['top_treatments'][:5], 1):
                result += f"{i}. {treatment['product_name']}: ₪{treatment['revenue']:,.2f}\n"
        else:
            result += "לא נמצאו טיפולים בתקופה זו.\n"
        
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error getting financial summary: {e}")
        return f"שגיאה בקבלת סיכום פיננסי: {str(e)}"


@tool
def analyze_patient_financial_status(patient_id: int) -> str:
    """
    Analyze financial status for a specific patient.
    
    Args:
        patient_id: Patient ID
        
    Returns:
        Patient financial analysis as formatted string
    """
    try:
        # Get patient invoices
        invoices = odoo_client_v3.get_invoices(patient_id=patient_id, limit=100)
        
        # Get patient payments
        payments = odoo_client_v3.get_payments(patient_id=patient_id, limit=100)
        
        # Get outstanding balance
        outstanding = odoo_client_v3.get_outstanding_balance(patient_id=patient_id)
        
        # Calculate totals
        total_invoiced = sum(inv.get('amount_total', 0) for inv in invoices)
        total_paid = sum(p.get('amount', 0) for p in payments)
        total_outstanding = outstanding['total_outstanding']
        
        result = f"""
👤 **ניתוח פיננסי למטופל**

💰 **סיכום כספי**
- סה"כ חשבוניות: ₪{total_invoiced:,.2f}
- סה"כ שולם: ₪{total_paid:,.2f}
- יתרת חוב: ₪{total_outstanding:,.2f}

📊 **סטטיסטיקות**
- מספר חשבוניות: {len(invoices)}
- מספר תשלומים: {len(payments)}
- חשבוניות ממתינות: {outstanding['invoice_count']}
"""
        
        if total_invoiced > 0:
            payment_rate = (total_paid / total_invoiced) * 100
            result += f"\n✅ **אחוז גבייה:** {payment_rate:.1f}%"
        
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error analyzing patient financial status: {e}")
        return f"שגיאה בניתוח סטטוס פיננסי של מטופל: {str(e)}"


@tool
def get_monthly_revenue_trend(months: int = 6) -> str:
    """
    Get monthly revenue trend for the last N months.
    
    Args:
        months: Number of months to analyze (default 6)
        
    Returns:
        Monthly revenue trend as formatted string
    """
    try:
        result = f"📈 **מגמת הכנסות חודשית ({months} חודשים אחרונים)**\n\n"
        
        monthly_data = []
        for i in range(months):
            # Calculate month range
            end_date = datetime.now().replace(day=1) - timedelta(days=i*30)
            start_date = (end_date - timedelta(days=30)).replace(day=1)
            
            # Get revenue for month
            revenue_data = odoo_client_v3.get_revenue_by_period(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            
            month_name = end_date.strftime("%B %Y")
            monthly_data.append({
                'month': month_name,
                'revenue': revenue_data['total_revenue'],
                'invoices': revenue_data['invoice_count']
            })
        
        # Reverse to show oldest first
        monthly_data.reverse()
        
        for data in monthly_data:
            result += f"**{data['month']}:** ₪{data['revenue']:,.2f} ({data['invoices']} חשבוניות)\n"
        
        # Calculate trend
        if len(monthly_data) >= 2:
            first_month = monthly_data[0]['revenue']
            last_month = monthly_data[-1]['revenue']
            if first_month > 0:
                trend = ((last_month - first_month) / first_month) * 100
                trend_emoji = "📈" if trend > 0 else "📉"
                result += f"\n{trend_emoji} **מגמה:** {trend:+.1f}%"
        
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error getting monthly revenue trend: {e}")
        return f"שגיאה בקבלת מגמת הכנסות: {str(e)}"


# Export all tools
marcus_financial_tools = [
    get_revenue_overview,
    get_outstanding_invoices,
    get_top_treatments_by_revenue,
    get_payment_collection_status,
    get_financial_summary,
    analyze_patient_financial_status,
    get_monthly_revenue_trend,
]

