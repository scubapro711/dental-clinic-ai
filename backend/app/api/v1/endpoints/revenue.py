"""
Revenue API endpoints
Provides enriched revenue and financial health data
"""
from fastapi import APIRouter, Depends
from typing import Dict, List, Any
from pydantic import BaseModel

from app.api.dependencies import get_current_membership
from app.core.database import get_db
from app.models.organization_membership import OrganizationMembership
from app.shared.odoo_queries import (
    get_revenue_today,
    get_revenue_this_month,
    get_revenue_by_period,
    get_outstanding_invoices,
    get_payment_success_rate,
    get_treatments_by_revenue
)
from sqlalchemy.orm import Session

router = APIRouter()


class RevenueData(BaseModel):
    """Revenue data for different time periods"""
    today: float
    this_week: float
    this_month: float
    last_month: float
    this_year: float
    last_year: float


class FinancialHealthData(BaseModel):
    """Financial health metrics"""
    outstanding_amount: float
    outstanding_count: int
    payment_success_rate: float
    average_invoice: float
    collection_rate: float


class TreatmentRevenue(BaseModel):
    """Revenue data for a specific treatment"""
    name: str
    revenue: float
    count: int
    percentage: float


class RevenueDashboardResponse(BaseModel):
    """Complete revenue dashboard data"""
    revenue: RevenueData
    financial_health: FinancialHealthData
    top_treatments: List[TreatmentRevenue]


@router.get("/dashboard", response_model=RevenueDashboardResponse)
async def get_revenue_dashboard(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive revenue dashboard data
    
    Returns:
    - Revenue for multiple time periods (today, week, month, year)
    - Financial health metrics (outstanding, payment success, collection rate)
    - Top treatments by revenue
    
    This endpoint maximizes value by using ALL available revenue functions
    """
    try:
        org_id = membership.organization_id
        
        # Get revenue for different periods
        revenue_today = get_revenue_today(org_id)
        revenue_this_week = get_revenue_by_period(org_id, period='week')
        revenue_this_month = get_revenue_this_month(org_id)
        revenue_last_month = get_revenue_by_period(org_id, period='month', offset=-1)
        revenue_this_year = get_revenue_by_period(org_id, period='year')
        revenue_last_year = get_revenue_by_period(org_id, period='year', offset=-1)
        
        # Get outstanding invoices
        outstanding_invoices = get_outstanding_invoices(org_id)
        outstanding_amount = sum(inv.get('amount_residual', 0) for inv in outstanding_invoices)
        outstanding_count = len(outstanding_invoices)
        
        # Get payment success rate
        payment_success = get_payment_success_rate(org_id)
        
        # Calculate average invoice
        total_invoices = get_revenue_by_period(org_id, period='year')
        # Rough estimate: assume ~100 invoices per year
        average_invoice = total_invoices / 100 if total_invoices > 0 else 0
        
        # Calculate collection rate
        # Collection rate = (revenue / (revenue + outstanding)) * 100
        total_billed = revenue_this_year + outstanding_amount
        collection_rate = (revenue_this_year / total_billed * 100) if total_billed > 0 else 0
        
        # Get top treatments by revenue
        top_treatments_data = get_treatments_by_revenue(org_id, limit=3)
        
        # Calculate total revenue for percentage
        total_treatment_revenue = sum(t.get('revenue', 0) for t in top_treatments_data)
        
        # Transform treatments
        top_treatments = [
            TreatmentRevenue(
                name=t.get('name', 'Unknown'),
                revenue=t.get('revenue', 0),
                count=t.get('count', 0),
                percentage=(t.get('revenue', 0) / total_treatment_revenue * 100) if total_treatment_revenue > 0 else 0
            )
            for t in top_treatments_data
        ]
        
        # Build response
        return RevenueDashboardResponse(
            revenue=RevenueData(
                today=revenue_today,
                this_week=revenue_this_week,
                this_month=revenue_this_month,
                last_month=revenue_last_month,
                this_year=revenue_this_year,
                last_year=revenue_last_year
            ),
            financial_health=FinancialHealthData(
                outstanding_amount=outstanding_amount,
                outstanding_count=outstanding_count,
                payment_success_rate=payment_success,
                average_invoice=average_invoice,
                collection_rate=collection_rate
            ),
            top_treatments=top_treatments
        )
        
    except Exception as e:
        print(f"Error fetching revenue dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return empty data structure
        return RevenueDashboardResponse(
            revenue=RevenueData(
                today=0,
                this_week=0,
                this_month=0,
                last_month=0,
                this_year=0,
                last_year=0
            ),
            financial_health=FinancialHealthData(
                outstanding_amount=0,
                outstanding_count=0,
                payment_success_rate=0,
                average_invoice=0,
                collection_rate=0
            ),
            top_treatments=[]
        )
