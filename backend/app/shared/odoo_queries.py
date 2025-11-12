"""
Shared Odoo query functions for dashboard and agent tools.

This module provides reusable functions for common Odoo queries used by both
dashboard endpoints and agent tools. This ensures consistency and reduces code duplication.

All functions use the OdooClient for database access.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.integrations.odoo_client import OdooClient

logger = logging.getLogger(__name__)


# ===== Appointment Queries =====

def get_appointments_by_date_range(
    odoo: OdooClient,
    start_date: str,
    end_date: str,
    state: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Get appointments within a date range.
    
    Args:
        odoo: OdooClient instance
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        state: Optional list of states to filter by (e.g., ['draft', 'confirmed', 'done'])
    
    Returns:
        List of appointment records
    
    Example:
        >>> appointments = get_appointments_by_date_range(
        ...     odoo, "2025-11-12", "2025-11-19", state=["confirmed"]
        ... )
    """
    domain = [
        ('start', '>=', f"{start_date} 00:00:00"),
        ('start', '<=', f"{end_date} 23:59:59"),
    ]
    
    if state:
        domain.append(('state', 'in', state))
    
    return odoo.search_read(
        'patient.appointment',
        domain=domain,
        fields=['id', 'patient_id', 'doctor_id', 'start', 'duration', 'state', 'appointment_type']
    )


def get_appointments_today(odoo: OdooClient) -> List[Dict[str, Any]]:
    """
    Get all appointments for today.
    
    Args:
        odoo: OdooClient instance
    
    Returns:
        List of today's appointment records
    
    Example:
        >>> appointments = get_appointments_today(odoo)
        >>> print(len(appointments))
        15
    """
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    return get_appointments_by_date_range(odoo, today_str, today_str)


def get_appointments_count_by_state(
    odoo: OdooClient,
    start_date: str,
    end_date: str
) -> Dict[str, int]:
    """
    Get count of appointments by state within a date range.
    
    Args:
        odoo: OdooClient instance
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        Dictionary with counts by state
    
    Example:
        >>> counts = get_appointments_count_by_state(odoo, "2025-11-12", "2025-11-19")
        >>> print(counts)
        {"draft": 5, "confirmed": 10, "done": 8, "cancelled": 2}
    """
    appointments = get_appointments_by_date_range(odoo, start_date, end_date)
    
    counts = {
        "draft": 0,
        "confirmed": 0,
        "done": 0,
        "cancelled": 0
    }
    
    for appointment in appointments:
        state = appointment.get("state", "draft")
        if state in counts:
            counts[state] += 1
    
    return counts


def get_upcoming_appointments(
    odoo: OdooClient,
    days_ahead: int = 7
) -> List[Dict[str, Any]]:
    """
    Get upcoming appointments for the next N days.
    
    Args:
        odoo: OdooClient instance
        days_ahead: Number of days to look ahead (default: 7)
    
    Returns:
        List of upcoming appointment records
    
    Example:
        >>> upcoming = get_upcoming_appointments(odoo, 7)
        >>> print(len(upcoming))
        42
    """
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    end_date = (datetime.utcnow() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    
    return get_appointments_by_date_range(
        odoo,
        today_str,
        end_date,
        state=['draft', 'confirmed']
    )


# ===== Revenue Queries =====

def get_revenue_by_period(
    odoo: OdooClient,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Get revenue data for a specific period.
    
    Args:
        odoo: OdooClient instance
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        Dictionary with revenue metrics:
        - total_revenue: Total revenue amount
        - invoice_count: Number of invoices
        - average_invoice: Average invoice amount
        - paid_amount: Amount paid
        - outstanding_amount: Amount outstanding
    
    Example:
        >>> revenue = get_revenue_by_period(odoo, "2025-11-01", "2025-11-30")
        >>> print(revenue["total_revenue"])
        125000.50
    """
    invoices = odoo.search_read(
        'account.move',
        domain=[
            ('move_type', '=', 'out_invoice'),
            ('invoice_date', '>=', start_date),
            ('invoice_date', '<=', end_date),
            ('state', '=', 'posted'),
        ],
        fields=['amount_total', 'amount_residual', 'payment_state']
    )
    
    total_revenue = sum(inv['amount_total'] for inv in invoices)
    invoice_count = len(invoices)
    average_invoice = total_revenue / invoice_count if invoice_count > 0 else 0.0
    
    paid_amount = sum(
        inv['amount_total'] - inv['amount_residual']
        for inv in invoices
    )
    outstanding_amount = sum(inv['amount_residual'] for inv in invoices)
    
    return {
        "total_revenue": total_revenue,
        "invoice_count": invoice_count,
        "average_invoice": average_invoice,
        "paid_amount": paid_amount,
        "outstanding_amount": outstanding_amount
    }


def get_revenue_today(odoo: OdooClient) -> float:
    """
    Get total revenue for today.
    
    Args:
        odoo: OdooClient instance
    
    Returns:
        Total revenue amount for today
    
    Example:
        >>> revenue = get_revenue_today(odoo)
        >>> print(revenue)
        5250.00
    """
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    revenue_data = get_revenue_by_period(odoo, today_str, today_str)
    return revenue_data["total_revenue"]


def get_revenue_this_month(odoo: OdooClient) -> float:
    """
    Get total revenue for the current month.
    
    Args:
        odoo: OdooClient instance
    
    Returns:
        Total revenue amount for current month
    
    Example:
        >>> revenue = get_revenue_this_month(odoo)
        >>> print(revenue)
        125000.50
    """
    month_start = datetime.utcnow().replace(day=1).strftime("%Y-%m-%d")
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    revenue_data = get_revenue_by_period(odoo, month_start, today_str)
    return revenue_data["total_revenue"]


# ===== Invoice Queries =====

def get_outstanding_invoices(
    odoo: OdooClient,
    patient_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get outstanding (unpaid) invoices.
    
    Args:
        odoo: OdooClient instance
        patient_id: Optional patient ID to filter by
    
    Returns:
        Dictionary with outstanding invoice data:
        - total_outstanding: Total outstanding amount
        - invoice_count: Number of outstanding invoices
        - invoices: List of invoice records
    
    Example:
        >>> outstanding = get_outstanding_invoices(odoo)
        >>> print(outstanding["total_outstanding"])
        15000.00
    """
    domain = [
        ('move_type', '=', 'out_invoice'),
        ('state', '=', 'posted'),
        ('payment_state', 'in', ['not_paid', 'partial']),
    ]
    
    if patient_id:
        domain.append(('partner_id', '=', patient_id))
    
    invoices = odoo.search_read(
        'account.move',
        domain=domain,
        fields=['id', 'name', 'partner_id', 'amount_total', 'amount_residual', 'invoice_date', 'payment_state']
    )
    
    total_outstanding = sum(inv['amount_residual'] for inv in invoices)
    
    return {
        "total_outstanding": total_outstanding,
        "invoice_count": len(invoices),
        "invoices": invoices
    }


def get_payment_success_rate(odoo: OdooClient) -> float:
    """
    Get payment success rate (percentage of paid invoices).
    
    Args:
        odoo: OdooClient instance
    
    Returns:
        Payment success rate as percentage (0-100)
    
    Example:
        >>> rate = get_payment_success_rate(odoo)
        >>> print(rate)
        85.5
    """
    total_invoices = odoo.search_count(
        'account.move',
        domain=[
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
        ]
    )
    
    paid_invoices = odoo.search_count(
        'account.move',
        domain=[
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'paid'),
        ]
    )
    
    return (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0.0


# ===== Patient Queries =====

def get_patient_count(odoo: OdooClient) -> int:
    """
    Get total number of patients.
    
    Args:
        odoo: OdooClient instance
    
    Returns:
        Total patient count
    
    Example:
        >>> count = get_patient_count(odoo)
        >>> print(count)
        1250
    """
    return odoo.search_count('res.partner', domain=[('is_patient', '=', True)])


def get_new_patients_by_period(
    odoo: OdooClient,
    start_date: str,
    end_date: str
) -> int:
    """
    Get count of new patients registered in a period.
    
    Args:
        odoo: OdooClient instance
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        Count of new patients
    
    Example:
        >>> new_patients = get_new_patients_by_period(odoo, "2025-11-01", "2025-11-30")
        >>> print(new_patients)
        25
    """
    return odoo.search_count(
        'res.partner',
        domain=[
            ('is_patient', '=', True),
            ('create_date', '>=', f"{start_date} 00:00:00"),
            ('create_date', '<=', f"{end_date} 23:59:59"),
        ]
    )


def get_patient_by_id(odoo: OdooClient, patient_id: int) -> Optional[Dict[str, Any]]:
    """
    Get patient details by ID.
    
    Args:
        odoo: OdooClient instance
        patient_id: Patient ID
    
    Returns:
        Patient record or None if not found
    
    Example:
        >>> patient = get_patient_by_id(odoo, 123)
        >>> print(patient["name"])
        "John Doe"
    """
    patients = odoo.search_read(
        'res.partner',
        domain=[('id', '=', patient_id), ('is_patient', '=', True)],
        fields=['id', 'name', 'email', 'phone', 'mobile', 'street', 'city']
    )
    
    return patients[0] if patients else None


# ===== Treatment Queries =====

def get_treatments_by_revenue(
    odoo: OdooClient,
    start_date: str,
    end_date: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get top treatments by revenue for a period.
    
    Args:
        odoo: OdooClient instance
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        limit: Maximum number of treatments to return (default: 10)
    
    Returns:
        List of treatment records with revenue data
    
    Example:
        >>> treatments = get_treatments_by_revenue(odoo, "2025-11-01", "2025-11-30", 5)
        >>> print(treatments[0]["name"])
        "Root Canal Treatment"
    """
    # Get invoice lines for the period
    invoice_lines = odoo.search_read(
        'account.move.line',
        domain=[
            ('move_id.move_type', '=', 'out_invoice'),
            ('move_id.invoice_date', '>=', start_date),
            ('move_id.invoice_date', '<=', end_date),
            ('move_id.state', '=', 'posted'),
            ('product_id', '!=', False),
        ],
        fields=['product_id', 'price_subtotal', 'quantity']
    )
    
    # Aggregate by treatment
    treatment_revenue = {}
    for line in invoice_lines:
        product_id = line['product_id'][0] if isinstance(line['product_id'], list) else line['product_id']
        product_name = line['product_id'][1] if isinstance(line['product_id'], list) else "Unknown"
        
        if product_id not in treatment_revenue:
            treatment_revenue[product_id] = {
                "product_id": product_id,
                "name": product_name,
                "total_revenue": 0.0,
                "quantity": 0
            }
        
        treatment_revenue[product_id]["total_revenue"] += line['price_subtotal']
        treatment_revenue[product_id]["quantity"] += line['quantity']
    
    # Sort by revenue and return top N
    sorted_treatments = sorted(
        treatment_revenue.values(),
        key=lambda x: x["total_revenue"],
        reverse=True
    )
    
    return sorted_treatments[:limit]


# ===== Utility Functions =====

def format_date_range(days_ago: int = 0, days_ahead: int = 0) -> tuple[str, str]:
    """
    Format date range for queries.
    
    Args:
        days_ago: Number of days in the past (default: 0 = today)
        days_ahead: Number of days in the future (default: 0 = today)
    
    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format
    
    Example:
        >>> start, end = format_date_range(days_ago=7, days_ahead=0)
        >>> print(start, end)
        "2025-11-05" "2025-11-12"
    """
    start_date = (datetime.utcnow() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    end_date = (datetime.utcnow() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    return start_date, end_date
