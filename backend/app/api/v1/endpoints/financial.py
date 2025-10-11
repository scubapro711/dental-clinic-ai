"""
Financial API Endpoints

Provides financial data and analytics for clinic dashboard.
Integrates with Marcus (CFO Agent) and Odoo Client V3.

Reference: Phase 3 - Marcus Expansion
"""

import logging
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.api.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.integrations.odoo_client_v3 import odoo_client_v3

router = APIRouter(prefix="/financial", tags=["Financial"])
logger = logging.getLogger(__name__)


# Schemas
class FinancialSummaryResponse(BaseModel):
    """Financial summary response schema."""
    period: dict
    revenue: dict
    outstanding: dict
    payments: dict
    top_treatments: list


# Endpoints
@router.get("/summary", response_model=FinancialSummaryResponse)
def get_financial_summary(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
):
    """
    Get comprehensive financial summary.
    
    Only owners and admins can access financial data.
    """
    try:
        # Default to last 30 days
        if not date_to:
            date_to = datetime.now().strftime("%Y-%m-%d")
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Get summary from Odoo
        summary = odoo_client_v3.get_financial_summary(date_from, date_to)
        
        logger.info(
            f"User {current_user.id} fetched financial summary "
            f"from {date_from} to {date_to}"
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting financial summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue")
def get_revenue(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
):
    """
    Get revenue overview for a time period.
    """
    try:
        # Default to last 30 days
        if not date_to:
            date_to = datetime.now().strftime("%Y-%m-%d")
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        revenue = odoo_client_v3.get_revenue_by_period(date_from, date_to)
        
        return revenue
        
    except Exception as e:
        logger.error(f"Error getting revenue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outstanding")
def get_outstanding(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
):
    """
    Get outstanding balance (unpaid invoices).
    """
    try:
        outstanding = odoo_client_v3.get_outstanding_balance(patient_id=patient_id)
        
        return outstanding
        
    except Exception as e:
        logger.error(f"Error getting outstanding balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/treatments")
def get_treatment_revenue(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(20, description="Number of top treatments"),
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
):
    """
    Get revenue by treatment type.
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
        
        return treatments
        
    except Exception as e:
        logger.error(f"Error getting treatment revenue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices")
def get_invoices(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    state: Optional[str] = Query(None, description="Filter by state"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, description="Maximum number of results"),
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
):
    """
    Get invoices with optional filters.
    """
    try:
        invoices = odoo_client_v3.get_invoices(
            patient_id=patient_id,
            state=state,
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )
        
        return invoices
        
    except Exception as e:
        logger.error(f"Error getting invoices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payments")
def get_payments(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, description="Maximum number of results"),
    current_user: User = Depends(require_role(UserRole.ORG_ADMIN)),
):
    """
    Get payments with optional filters.
    """
    try:
        payments = odoo_client_v3.get_payments(
            patient_id=patient_id,
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )
        
        return payments
        
    except Exception as e:
        logger.error(f"Error getting payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

