"""
CFO Agent Tools - Financial Data Access

Tools for accessing and analyzing financial data from Mock Odoo.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_core.tools import tool

from app.integrations.mock_odoo import mock_odoo_client as mock_odoo


logger = logging.getLogger(__name__)


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
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get invoices from Mock Odoo
        all_invoices = mock_odoo.get_invoices()
        
        # Filter invoices by date range
        period_invoices = [
            inv for inv in all_invoices
            if start_date <= datetime.fromisoformat(inv["date"]) <= end_date
        ]
        
        # Calculate metrics
        total_revenue = sum(inv["amount"] for inv in period_invoices)
        paid_revenue = sum(inv["amount"] for inv in period_invoices if inv["status"] == "paid")
        pending_revenue = sum(inv["amount"] for inv in period_invoices if inv["status"] == "pending")
        
        average_per_day = total_revenue / days if days > 0 else 0
        
        # Get previous period for comparison
        prev_start = start_date - timedelta(days=days)
        prev_end = start_date
        
        prev_invoices = [
            inv for inv in all_invoices
            if prev_start <= datetime.fromisoformat(inv["date"]) < prev_end
        ]
        prev_revenue = sum(inv["amount"] for inv in prev_invoices)
        
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
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get invoices
        all_invoices = mock_odoo.get_invoices()
        
        period_invoices = [
            inv for inv in all_invoices
            if start_date <= datetime.fromisoformat(inv["date"]) <= end_date
        ]
        
        # Calculate payment metrics
        total_invoices = len(period_invoices)
        paid_invoices = [inv for inv in period_invoices if inv["status"] == "paid"]
        pending_invoices = [inv for inv in period_invoices if inv["status"] == "pending"]
        overdue_invoices = [inv for inv in period_invoices if inv["status"] == "overdue"]
        
        paid_count = len(paid_invoices)
        pending_count = len(pending_invoices)
        overdue_count = len(overdue_invoices)
        
        paid_amount = sum(inv["amount"] for inv in paid_invoices)
        pending_amount = sum(inv["amount"] for inv in pending_invoices)
        overdue_amount = sum(inv["amount"] for inv in overdue_invoices)
        
        total_amount = paid_amount + pending_amount + overdue_amount
        
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
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get treatment records
        all_treatments = mock_odoo.get_treatment_records()
        
        period_treatments = [
            t for t in all_treatments
            if start_date <= datetime.fromisoformat(t["date"]) <= end_date
        ]
        
        # Aggregate by treatment type
        treatment_stats = {}
        for treatment in period_treatments:
            treatment_type = treatment["treatment_type"]
            cost = treatment["cost"]
            
            if treatment_type not in treatment_stats:
                treatment_stats[treatment_type] = {
                    "treatment_type": treatment_type,
                    "count": 0,
                    "total_revenue": 0.0,
                }
            
            treatment_stats[treatment_type]["count"] += 1
            treatment_stats[treatment_type]["total_revenue"] += cost
        
        # Calculate average and sort by revenue
        for stats in treatment_stats.values():
            stats["average_revenue"] = round(stats["total_revenue"] / stats["count"], 2)
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
        # Get all invoices
        all_invoices = mock_odoo.get_invoices()
        
        # Filter unpaid invoices (pending or overdue)
        outstanding = [
            inv for inv in all_invoices
            if inv["status"] in ["pending", "overdue"]
        ]
        
        # Sort by amount (highest first) and date (oldest first)
        outstanding.sort(key=lambda x: (-x["amount"], x["date"]))
        
        # Limit results
        outstanding = outstanding[:limit]
        
        # Format for display
        result = []
        for inv in outstanding:
            result.append({
                "invoice_id": inv["id"],
                "patient_id": inv["patient_id"],
                "amount": round(inv["amount"], 2),
                "status": inv["status"],
                "date": inv["date"],
                "days_outstanding": (datetime.now() - datetime.fromisoformat(inv["date"])).days,
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
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get data
        all_invoices = mock_odoo.get_invoices()
        all_appointments = mock_odoo.get_appointments()
        
        period_invoices = [
            inv for inv in all_invoices
            if start_date <= datetime.fromisoformat(inv["date"]) <= end_date
        ]
        
        period_appointments = [
            apt for apt in all_appointments
            if start_date <= datetime.fromisoformat(apt["date"]) <= end_date
        ]
        
        # Calculate metrics
        total_revenue = sum(inv["amount"] for inv in period_invoices)
        total_appointments = len(period_appointments)
        completed_appointments = len([a for a in period_appointments if a["status"] == "completed"])
        
        revenue_per_appointment = total_revenue / completed_appointments if completed_appointments > 0 else 0
        
        # Calculate completion rate
        completion_rate = (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0
        
        # Get patient count
        unique_patients = len(set(inv["patient_id"] for inv in period_invoices))
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
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get invoices
        all_invoices = mock_odoo.get_invoices()
        
        period_invoices = [
            inv for inv in all_invoices
            if start_date <= datetime.fromisoformat(inv["date"]) <= end_date
        ]
        
        # Group by week
        weekly_revenue = {}
        for inv in period_invoices:
            inv_date = datetime.fromisoformat(inv["date"])
            week_start = inv_date - timedelta(days=inv_date.weekday())
            week_key = week_start.strftime("%Y-%m-%d")
            
            if week_key not in weekly_revenue:
                weekly_revenue[week_key] = 0.0
            
            weekly_revenue[week_key] += inv["amount"]
        
        # Calculate trend
        weeks = sorted(weekly_revenue.keys())
        revenues = [weekly_revenue[w] for w in weeks]
        
        if len(revenues) >= 2:
            # Simple linear trend
            first_half_avg = sum(revenues[:len(revenues)//2]) / (len(revenues)//2)
            second_half_avg = sum(revenues[len(revenues)//2:]) / (len(revenues) - len(revenues)//2)
            
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
