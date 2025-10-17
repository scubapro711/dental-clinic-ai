"""
Marcus Financial Tools - Enhanced with Odoo Client V3

Complete financial analysis tools using Odoo Dental financial models.

Reference: ODOO_DENTAL_MODULE_ANALYSIS.md, Phase 3
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from langchain.tools import tool

from app.integrations.odoo_client import OdooClient
odoo_client = OdooClient()

logger = logging.getLogger(__name__)

# Initialize __all__ list
__all__ = [
    'get_revenue_overview',
    'get_outstanding_invoices',
    'get_top_treatments_by_revenue',
    'get_payment_collection_status',
    'get_financial_summary',
    'analyze_patient_financial_status',
    'get_monthly_revenue_trend',
]


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
        
        revenue_data = odoo_client.get_revenue_by_period(date_from, date_to)
        
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
        outstanding_data = odoo_client.get_outstanding_balance(patient_id=patient_id)
        
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
        
        treatments = odoo_client.get_treatment_revenue(
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
        
        payments = odoo_client.get_payments(
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
        
        summary = odoo_client.get_financial_summary(date_from, date_to)
        
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
        invoices = odoo_client.get_invoices(patient_id=patient_id, limit=100)
        
        # Get patient payments
        payments = odoo_client.get_payments(patient_id=patient_id, limit=100)
        
        # Get outstanding balance
        outstanding = odoo_client.get_outstanding_balance(patient_id=patient_id)
        
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
            revenue_data = odoo_client.get_revenue_by_period(
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




@tool
def create_invoice_tool(patient_id: int, treatment_ids: list[int]) -> str:
    """
    Create an invoice using Green Invoice integration.

    Args:
        patient_id: Patient ID in Odoo
        treatment_ids: List of treatment IDs to include in the invoice.

    Returns:
        A success message with the invoice details.
    """
    try:
        odoo = OdooClient()
        green_invoice = GreenInvoiceClient()

        patient = odoo.get_patient(patient_id)
        if not patient:
            return f"❌ Patient {patient_id} not found"

        # In a real implementation, this would call the Green Invoice API
        invoice_data = green_invoice.create_invoice(patient, treatment_ids)

        note = f"🧾 **חשבונית נוצרה (Green Invoice)**\n\n**מספר חשבונית:** {invoice_data['invoice_number']}\n**סכום:** {invoice_data['amount']}"
        odoo.create_patient_note(patient_id, note, note_type="invoice")

        return f"✅ **חשבונית נוצרה בהצלחה**\n\n**מטופל:** {patient.get('name')}\n**מספר חשבונית:** {invoice_data['invoice_number']}\n**קישור לחשבונית:** {invoice_data['pdf_url']}"
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        return f"❌ שגיאה ביצירת חשבונית: {str(e)}"


@tool
def send_invoice_tool(invoice_id: int, method: str = "email") -> str:
    """
    Send an invoice to the patient.

    Args:
        invoice_id: The ID of the invoice to send.
        method: The method to send the invoice - "email" or "sms".

    Returns:
        A success message.
    """
    try:
        green_invoice = GreenInvoiceClient()
        # In a real implementation, this would call the Green Invoice API
        status = green_invoice.send_invoice(invoice_id, method)
        return f"✅ חשבונית {invoice_id} נשלחה בהצלחה באמצעות {method}."
    except Exception as e:
        logger.error(f"Error sending invoice: {e}")
        return f"❌ שגיאה בשליחת חשבונית: {str(e)}"


@tool
def record_payment_tool(invoice_id: int, amount: float, payment_method: str) -> str:
    """
    Record a payment for an invoice.

    Args:
        invoice_id: The ID of the invoice.
        amount: The amount paid.
        payment_method: The method of payment (e.g., "credit_card", "cash", "bank_transfer").

    Returns:
        A success message.
    """
    try:
        green_invoice = GreenInvoiceClient()
        # In a real implementation, this would call the Green Invoice API
        payment_id = green_invoice.record_payment(invoice_id, amount, payment_method)
        return f"✅ תשלום בסך {amount} עבור חשבונית {invoice_id} נרשם בהצלחה. מזהה תשלום: {payment_id}"
    except Exception as e:
        logger.error(f"Error recording payment: {e}")
        return f"❌ שגיאה ברישום תשלום: {str(e)}"


@tool
def void_invoice_tool(invoice_id: int, reason: str) -> str:
    """
    Void an invoice.

    Args:
        invoice_id: The ID of the invoice to void.
        reason: The reason for voiding the invoice.

    Returns:
        A success message.
    """
    try:
        green_invoice = GreenInvoiceClient()
        # In a real implementation, this would call the Green Invoice API
        status = green_invoice.void_invoice(invoice_id, reason)
        return f"✅ חשבונית {invoice_id} בוטלה בהצלחה. סיבה: {reason}"
    except Exception as e:
        logger.error(f"Error voiding invoice: {e}")
        return f"❌ שגיאה בביטול חשבונית: {str(e)}"


# Update __all__
__all__.extend(["create_invoice_tool", "send_invoice_tool", "record_payment_tool", "void_invoice_tool"])




@tool
def create_expense_tool(amount: float, category: str, description: str) -> str:
    """
    Record a clinic expense.

    Args:
        amount: The amount of the expense.
        category: The category of the expense (e.g., "supplies", "rent", "salaries").
        description: A description of the expense.

    Returns:
        A success message with the expense details.
    """
    try:
        odoo = OdooClient()
        # In a real implementation, this would create an expense record in Odoo.
        expense_id = odoo.create_expense(amount, category, description)
        return f"✅ הוצאה בסך {amount} נרשמה בהצלחה. קטגוריה: {category}. מזהה: {expense_id}"
    except Exception as e:
        logger.error(f"Error creating expense: {e}")
        return f"❌ שגיאה ביצירת הוצאה: {str(e)}"


@tool
def get_budget_tool(department: str) -> str:
    """
    Get the budget for a specific department.

    Args:
        department: The department to get the budget for (e.g., "clinical", "marketing", "admin").

    Returns:
        A formatted string with the budget details.
    """
    try:
        odoo = OdooClient()
        # This is a mock implementation.
        budget_data = odoo.get_budget(department)
        return f"📊 **תקציב למחלקת {department}**\n\n**תקציב מאושר:** {budget_data['allocated']}\n**ניצול עד כה:** {budget_data['spent']}\n**יתרה:** {budget_data['remaining']}"
    except Exception as e:
        logger.error(f"Error getting budget: {e}")
        return f"❌ שגיאה בקבלת תקציב: {str(e)}"


@tool
def create_budget_tool(department: str, amount: float, year: int) -> str:
    """
    Create a budget for a department for a specific year.

    Args:
        department: The department to create the budget for.
        amount: The budget amount.
        year: The year the budget is for.

    Returns:
        A success message.
    """
    try:
        odoo = OdooClient()
        # In a real implementation, this would create a budget record in Odoo.
        budget_id = odoo.create_budget(department, amount, year)
        return f"✅ תקציב בסך {amount} למחלקת {department} לשנת {year} נוצר בהצלחה. מזהה: {budget_id}"
    except Exception as e:
        logger.error(f"Error creating budget: {e}")
        return f"❌ שגיאה ביצירת תקציב: {str(e)}"


# Update __all__
__all__.extend(["create_expense_tool", "get_budget_tool", "create_budget_tool"])




@tool
def submit_insurance_claim_tool(patient_id: int, invoice_id: int, insurance_company: str) -> str:
    """
    Submit an insurance claim for a patient.

    Args:
        patient_id: Patient ID in Odoo
        invoice_id: The ID of the invoice to claim.
        insurance_company: The name of the insurance company.

    Returns:
        A success message with the claim details.
    """
    try:
        odoo = OdooClient()
        # In a real implementation, this would integrate with Israeli insurance APIs.
        claim_id = odoo.submit_insurance_claim(patient_id, invoice_id, insurance_company)
        return f"✅ תביעת ביטוח נשלחה בהצלחה עבור מטופל {patient_id} לחברת {insurance_company}. מספר תביעה: {claim_id}"
    except Exception as e:
        logger.error(f"Error submitting insurance claim: {e}")
        return f"❌ שגיאה בשליחת תביעת ביטוח: {str(e)}"


@tool
def get_insurance_claims_tool(patient_id: int, status: Optional[str] = None) -> str:
    """
    Get a list of insurance claims for a patient.

    Args:
        patient_id: Patient ID in Odoo
        status: Filter claims by status - "submitted", "approved", "rejected", "paid".

    Returns:
        A formatted string with the claims list.
    """
    try:
        odoo = OdooClient()
        # This is a mock implementation.
        claims = odoo.get_insurance_claims(patient_id, status)
        if not claims:
            return "No insurance claims found for this patient."

        return "\n\n---\n\n".join([f"**תביעה:** {claim['id']}, **סטטוס:** {claim['status']}" for claim in claims])
    except Exception as e:
        logger.error(f"Error getting insurance claims: {e}")
        return f"❌ שגיאה בקבלת תביעות ביטוח: {str(e)}"


# Update __all__
__all__.extend(["submit_insurance_claim_tool", "get_insurance_claims_tool"])




@tool
def export_to_accounting_tool(format: str = "csv") -> str:
    """
    Export financial data to an accounting file.

    Args:
        format: The format of the export file - "csv" or "excel".

    Returns:
        A success message with the file path.
    """
    try:
        odoo = OdooClient()
        # In a real implementation, this would generate a file with financial data.
        file_path = odoo.export_to_accounting(format)
        return f"✅ נתונים פיננסיים יוצאו בהצלחה לקובץ: {file_path}"
    except Exception as e:
        logger.error(f"Error exporting to accounting: {e}")
        return f"❌ שגיאה ביצוא נתונים: {str(e)}"


@tool
def generate_tax_report_tool(year: int) -> str:
    """
    Generate a tax report for a specific year.

    Args:
        year: The year to generate the report for.

    Returns:
        A success message with the report file path.
    """
    try:
        odoo = OdooClient()
        # In a real implementation, this would generate a tax report compliant with Israeli tax law.
        report_path = odoo.generate_tax_report(year)
        return f"✅ דוח מס לשנת {year} נוצר בהצלחה: {report_path}"
    except Exception as e:
        logger.error(f"Error generating tax report: {e}")
        return f"❌ שגיאה ביצירת דוח מס: {str(e)}"


# Update __all__
__all__.extend(["export_to_accounting_tool", "generate_tax_report_tool"])

# Build marcus_financial_tools list for agent
marcus_financial_tools = [
    get_revenue_overview,
    get_outstanding_invoices,
    get_top_treatments_by_revenue,
    get_payment_collection_status,
    get_financial_summary,
    analyze_patient_financial_status,
    get_monthly_revenue_trend,
    create_invoice_tool,
    send_invoice_tool,
    record_payment_tool,
    void_invoice_tool,
    create_expense_tool,
    get_budget_tool,
    create_budget_tool,
    submit_insurance_claim_tool,
    get_insurance_claims_tool,
    export_to_accounting_tool,
    generate_tax_report_tool,
]

