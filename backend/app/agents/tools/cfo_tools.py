"""
CFO Agent Tools - Financial Data Access

Tools for accessing and analyzing financial data from Odoo.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_core.tools import tool

from app.integrations.odoo_client_v3 import OdooClientV3
from app.core.config import settings


logger = logging.getLogger(__name__)


def get_odoo_client() -> OdooClientV3:
    """Get Odoo client instance."""
    return OdooClientV3(
        url=settings.ODOO_URL,
        db=settings.ODOO_DB,
        username=settings.ODOO_USERNAME,
        password=settings.ODOO_PASSWORD,
    )


@tool
def get_revenue_overview_tool(days: int = 30) -> Dict[str, Any]:
    """
    Get revenue overview for a time period.
    
    Args:
        days: Number of days to analyze (default: 30)
        
    Returns:
        Revenue summary including total, average, and comparison
    """
    logger.info(f"Getting revenue overview for last {days} days")
    
    try:
        odoo = get_odoo_client()
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get invoices from Odoo (account.move with type out_invoice)
        period_invoices = odoo.search_read(
            'account.move',
            domain=[
                ('invoice_date', '>=', start_date.strftime("%Y-%m-%d")),
                ('invoice_date', '<=', end_date.strftime("%Y-%m-%d")),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
            ],
            fields=['invoice_date', 'amount_total', 'payment_state'],
            order='invoice_date DESC'
        )
        
        # Calculate metrics
        total_revenue = sum(inv['amount_total'] for inv in period_invoices)
        paid_revenue = sum(inv['amount_total'] for inv in period_invoices if inv.get('payment_state') == 'paid')
        pending_revenue = sum(inv['amount_total'] for inv in period_invoices if inv.get('payment_state') in ['not_paid', 'partial'])
        
        average_per_day = total_revenue / days if days > 0 else 0
        
        # Get previous period for comparison
        prev_start = start_date - timedelta(days=days)
        prev_end = start_date
        
        prev_invoices = odoo.search_read(
            'account.move',
            domain=[
                ('invoice_date', '>=', prev_start.strftime("%Y-%m-%d")),
                ('invoice_date', '<', prev_end.strftime("%Y-%m-%d")),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
            ],
            fields=['amount_total']
        )
        prev_revenue = sum(inv['amount_total'] for inv in prev_invoices)
        
        # Calculate growth
        growth = 0.0
        if prev_revenue > 0:
            growth = ((total_revenue - prev_revenue) / prev_revenue) * 100
        
        return {
            "period_days": days,
            "total_revenue": round(total_revenue, 2),
            "paid_revenue": round(paid_revenue, 2),
            "pending_revenue": round(pending_revenue, 2),
            "average_per_day": round(average_per_day, 2),
            "invoice_count": len(period_invoices),
            "previous_period_revenue": round(prev_revenue, 2),
            "growth_percentage": round(growth, 1),
        }
        
    except Exception as e:
        logger.error(f"Error getting revenue overview: {e}")
        return {"error": str(e)}


@tool
def get_payment_status_tool(days: int = 30) -> Dict[str, Any]:
    """
    Get payment status and collection rates.
    
    Args:
        days: Number of days to analyze (default: 30)
        
    Returns:
        Payment status summary
    """
    logger.info(f"Getting payment status for last {days} days")
    
    try:
        odoo = get_odoo_client()
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get invoices
        period_invoices = odoo.search_read(
            'account.move',
            domain=[
                ('invoice_date', '>=', start_date.strftime("%Y-%m-%d")),
                ('invoice_date', '<=', end_date.strftime("%Y-%m-%d")),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
            ],
            fields=['amount_total', 'payment_state', 'invoice_date_due'],
            order='invoice_date DESC'
        )
        
        # Calculate payment metrics
        total_invoices = len(period_invoices)
        
        paid_invoices = [inv for inv in period_invoices if inv.get('payment_state') == 'paid']
        pending_invoices = [inv for inv in period_invoices if inv.get('payment_state') == 'not_paid']
        
        # Check for overdue
        today = datetime.now().date()
        overdue_invoices = [
            inv for inv in pending_invoices
            if inv.get('invoice_date_due') and datetime.strptime(str(inv['invoice_date_due']), "%Y-%m-%d").date() < today
        ]
        
        paid_count = len(paid_invoices)
        pending_count = len(pending_invoices)
        overdue_count = len(overdue_invoices)
        
        paid_amount = sum(inv['amount_total'] for inv in paid_invoices)
        pending_amount = sum(inv['amount_total'] for inv in pending_invoices)
        overdue_amount = sum(inv['amount_total'] for inv in overdue_invoices)
        
        total_amount = paid_amount + pending_amount
        
        # Calculate rates
        payment_rate = (paid_count / total_invoices * 100) if total_invoices > 0 else 0
        collection_rate = (paid_amount / total_amount * 100) if total_amount > 0 else 0
        
        return {
            "period_days": days,
            "total_invoices": total_invoices,
            "paid_count": paid_count,
            "pending_count": pending_count,
            "overdue_count": overdue_count,
            "paid_amount": round(paid_amount, 2),
            "pending_amount": round(pending_amount, 2),
            "overdue_amount": round(overdue_amount, 2),
            "payment_rate_percentage": round(payment_rate, 1),
            "collection_rate_percentage": round(collection_rate, 1),
        }
        
    except Exception as e:
        logger.error(f"Error getting payment status: {e}")
        return {"error": str(e)}


@tool
def get_top_treatments_tool(limit: int = 10, days: int = 30) -> List[Dict[str, Any]]:
    """
    Get most profitable treatments.
    
    Args:
        limit: Number of top treatments to return (default: 10)
        days: Number of days to analyze (default: 30)
        
    Returns:
        List of top treatments by revenue
    """
    logger.info(f"Getting top {limit} treatments for last {days} days")
    
    try:
        odoo = get_odoo_client()
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get invoice lines (these contain treatment details)
        invoice_lines = odoo.search_read(
            'account.move.line',
            domain=[
                ('move_id.invoice_date', '>=', start_date.strftime("%Y-%m-%d")),
                ('move_id.invoice_date', '<=', end_date.strftime("%Y-%m-%d")),
                ('move_id.move_type', '=', 'out_invoice'),
                ('move_id.state', '=', 'posted'),
                ('display_type', '=', 'product'),
            ],
            fields=['product_id', 'name', 'price_subtotal'],
            limit=1000
        )
        
        # Aggregate by product/treatment
        treatment_stats = {}
        for line in invoice_lines:
            product = line.get('product_id')
            if not product:
                continue
                
            product_id = product[0] if isinstance(product, list) else product
            product_name = product[1] if isinstance(product, list) and len(product) > 1 else line.get('name', 'Unknown')
            
            if product_id not in treatment_stats:
                treatment_stats[product_id] = {
                    "treatment_type": product_name,
                    "count": 0,
                    "total_revenue": 0.0,
                }
            
            treatment_stats[product_id]["count"] += 1
            treatment_stats[product_id]["total_revenue"] += line.get('price_subtotal', 0)
        
        # Calculate average and sort by revenue
        for stats in treatment_stats.values():
            stats["average_revenue"] = round(stats["total_revenue"] / stats["count"], 2) if stats["count"] > 0 else 0
            stats["total_revenue"] = round(stats["total_revenue"], 2)
        
        # Sort by total revenue and limit
        top_treatments = sorted(
            treatment_stats.values(),
            key=lambda x: x["total_revenue"],
            reverse=True
        )[:limit]
        
        return top_treatments
        
    except Exception as e:
        logger.error(f"Error getting top treatments: {e}")
        return [{"error": str(e)}]


@tool
def get_outstanding_invoices_tool(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get list of outstanding (unpaid) invoices.
    
    Args:
        limit: Maximum number of invoices to return (default: 20)
        
    Returns:
        List of outstanding invoices
    """
    logger.info(f"Getting top {limit} outstanding invoices")
    
    try:
        odoo = get_odoo_client()
        
        # Get unpaid invoices
        outstanding = odoo.search_read(
            'account.move',
            domain=[
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial']),
            ],
            fields=['id', 'partner_id', 'amount_total', 'payment_state', 'invoice_date', 'invoice_date_due'],
            order='amount_total DESC, invoice_date ASC',
            limit=limit
        )
        
        # Format for display
        result = []
        for inv in outstanding:
            invoice_date = datetime.strptime(str(inv['invoice_date']), "%Y-%m-%d") if inv.get('invoice_date') else datetime.now()
            days_outstanding = (datetime.now() - invoice_date).days
            
            result.append({
                "invoice_id": inv['id'],
                "patient_id": inv.get('partner_id', [None])[0] if inv.get('partner_id') else None,
                "patient_name": inv.get('partner_id', [None, 'Unknown'])[1] if inv.get('partner_id') else 'Unknown',
                "amount": round(inv['amount_total'], 2),
                "status": inv.get('payment_state', 'unknown'),
                "date": str(inv.get('invoice_date', '')),
                "due_date": str(inv.get('invoice_date_due', '')),
                "days_outstanding": days_outstanding,
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting outstanding invoices: {e}")
        return [{"error": str(e)}]


@tool
def analyze_profitability_tool(days: int = 30) -> Dict[str, Any]:
    """
    Deep dive into profitability metrics.
    
    Args:
        days: Number of days to analyze (default: 30)
        
    Returns:
        Profitability analysis
    """
    logger.info(f"Analyzing profitability for last {days} days")
    
    try:
        odoo = get_odoo_client()
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get invoices
        period_invoices = odoo.search_read(
            'account.move',
            domain=[
                ('invoice_date', '>=', start_date.strftime("%Y-%m-%d")),
                ('invoice_date', '<=', end_date.strftime("%Y-%m-%d")),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
            ],
            fields=['amount_total', 'partner_id']
        )
        
        # Get appointments
        period_appointments = odoo.search_read(
            'medical.appointment',
            domain=[
                ('appointment_sdate', '>=', start_date.strftime("%Y-%m-%d 00:00:00")),
                ('appointment_sdate', '<=', end_date.strftime("%Y-%m-%d 23:59:59")),
            ],
            fields=['state']
        )
        
        # Calculate metrics
        total_revenue = sum(inv['amount_total'] for inv in period_invoices)
        total_appointments = len(period_appointments)
        completed_appointments = len([a for a in period_appointments if a.get('state') == 'done'])
        
        revenue_per_appointment = total_revenue / completed_appointments if completed_appointments > 0 else 0
        
        # Calculate completion rate
        completion_rate = (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0
        
        # Get patient count
        unique_patients = len(set(
            inv.get('partner_id', [None])[0] if inv.get('partner_id') else None
            for inv in period_invoices
        ))
        revenue_per_patient = total_revenue / unique_patients if unique_patients > 0 else 0
        
        return {
            "period_days": days,
            "total_revenue": round(total_revenue, 2),
            "total_appointments": total_appointments,
            "completed_appointments": completed_appointments,
            "completion_rate_percentage": round(completion_rate, 1),
            "revenue_per_appointment": round(revenue_per_appointment, 2),
            "unique_patients": unique_patients,
            "revenue_per_patient": round(revenue_per_patient, 2),
        }
        
    except Exception as e:
        logger.error(f"Error analyzing profitability: {e}")
        return {"error": str(e)}


@tool
def get_financial_trends_tool(days: int = 90) -> Dict[str, Any]:
    """
    Analyze financial trends over time.
    
    Args:
        days: Number of days to analyze (default: 90)
        
    Returns:
        Financial trends analysis
    """
    logger.info(f"Analyzing financial trends for last {days} days")
    
    try:
        odoo = get_odoo_client()
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get invoices
        period_invoices = odoo.search_read(
            'account.move',
            domain=[
                ('invoice_date', '>=', start_date.strftime("%Y-%m-%d")),
                ('invoice_date', '<=', end_date.strftime("%Y-%m-%d")),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
            ],
            fields=['invoice_date', 'amount_total'],
            order='invoice_date ASC'
        )
        
        # Group by week
        weekly_revenue = {}
        for inv in period_invoices:
            inv_date = datetime.strptime(str(inv['invoice_date']), "%Y-%m-%d")
            week_start = inv_date - timedelta(days=inv_date.weekday())
            week_key = week_start.strftime("%Y-%m-%d")
            
            if week_key not in weekly_revenue:
                weekly_revenue[week_key] = 0.0
            
            weekly_revenue[week_key] += inv['amount_total']
        
        # Calculate trend
        weeks = sorted(weekly_revenue.keys())
        revenues = [weekly_revenue[w] for w in weeks]
        
        if len(revenues) >= 2:
            # Simple linear trend
            first_half_avg = sum(revenues[:len(revenues)//2]) / (len(revenues)//2) if len(revenues) > 1 else 0
            second_half_avg = sum(revenues[len(revenues)//2:]) / (len(revenues) - len(revenues)//2) if len(revenues) > 1 else 0
            
            trend = "increasing" if second_half_avg > first_half_avg else "decreasing"
            trend_percentage = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
        else:
            trend = "stable"
            trend_percentage = 0.0
        
        return {
            "period_days": days,
            "weeks_analyzed": len(weeks),
            "trend": trend,
            "trend_percentage": round(trend_percentage, 1),
            "average_weekly_revenue": round(sum(revenues) / len(revenues), 2) if revenues else 0,
            "highest_week_revenue": round(max(revenues), 2) if revenues else 0,
            "lowest_week_revenue": round(min(revenues), 2) if revenues else 0,
        }
        
    except Exception as e:
        logger.error(f"Error analyzing financial trends: {e}")
        return {"error": str(e)}

