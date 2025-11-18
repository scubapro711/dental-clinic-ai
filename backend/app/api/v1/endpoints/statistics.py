"""
Statistics API Endpoint

Provides clinic statistics and analytics for the dashboard.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta

from app.integrations.odoo_client import OdooClient
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def OdooClient() -> OdooClient:
    """Dependency to get Odoo client instance."""
    return OdooClient(
        url=settings.ODOO_URL,
        db=settings.ODOO_DB,
        username=settings.ODOO_USERNAME,
        password=settings.ODOO_PASSWORD,
    )


@router.get("/overview")
async def get_overview_statistics(
    odoo: OdooClient = Depends(OdooClient)
) -> Dict[str, Any]:
    """
    Get overview statistics for the clinic dashboard.
    
    Returns:
        Dictionary with clinic statistics
    """
    try:
        # Get total patients
        total_patients = odoo.search_count('res.partner', [('customer_rank', '>', 0)])
        
        # Get total appointments
        total_appointments = odoo.search_count('patient.appointment', [])
        
        # Get completed appointments
        completed_appointments = odoo.search_count(
            'patient.appointment',
            [('state', '=', 'done')]
        )
        
        # Get total invoices
        total_invoices = odoo.search_count(
            'account.move',
            [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]
        )
        
        # Get paid invoices
        paid_invoices = odoo.search_count(
            'account.move',
            [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'paid')
            ]
        )
        
        # Get total revenue
        invoices = odoo.search_read(
            'account.move',
            domain=[('move_type', '=', 'out_invoice'), ('state', '=', 'posted')],
            fields=['amount_total']
        )
        total_revenue = sum(inv['amount_total'] for inv in invoices)
        
        # Calculate additional metrics
        completion_rate = (
            completed_appointments / total_appointments * 100
            if total_appointments > 0 else 0
        )
        
        payment_rate = (
            paid_invoices / total_invoices * 100
            if total_invoices > 0 else 0
        )
        
        avg_revenue_per_patient = (
            total_revenue / total_patients
            if total_patients > 0 else 0
        )
        
        return {
            "total_patients": total_patients,
            "total_appointments": total_appointments,
            "completed_appointments": completed_appointments,
            "total_invoices": total_invoices,
            "paid_invoices": paid_invoices,
            "total_revenue": total_revenue,
            "completion_rate": round(completion_rate, 1),
            "payment_rate": round(payment_rate, 1),
            "avg_revenue_per_patient": round(avg_revenue_per_patient, 2),
            "generated_at": datetime.now().isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patients")
async def get_patient_statistics(
    odoo: OdooClient = Depends(OdooClient)
) -> Dict[str, Any]:
    """
    Get patient-related statistics.
    
    Returns:
        Dictionary with patient statistics
    """
    try:
        # Get total patients
        total_patients = odoo.search_count('res.partner', [('customer_rank', '>', 0)])
        
        # New patients (registered in last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        new_patients = odoo.search_count(
            'res.partner',
            [
                ('customer_rank', '>', 0),
                ('create_date', '>=', thirty_days_ago)
            ]
        )
        
        # Active patients (with appointments in last 90 days)
        ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        # Get patients with recent appointments
        recent_appointments = odoo.search_read(
            'patient.appointment',
            domain=[
                ('start', '>=', f"{ninety_days_ago} 00:00:00"),
                ('state', '=', 'done')
            ],
            fields=['patient_id']
        )
        
        # Count unique patients
        active_patient_ids = set()
        for appt in recent_appointments:
            patient_id = appt['patient_id'][0] if isinstance(appt['patient_id'], list) else appt['patient_id']
            active_patient_ids.add(patient_id)
        active_patients = len(active_patient_ids)
        
        # Patients with outstanding balance
        patients_with_balance = odoo.search_count(
            'res.partner',
            [
                ('customer_rank', '>', 0),
                ('credit', '>', 0)  # Odoo tracks receivables in 'credit' field
            ]
        )
        
        # Insurance distribution (if available)
        # TODO: Add insurance field to res.partner
        insurance_dist = {"None": total_patients}  # Placeholder
        
        return {
            "total_patients": total_patients,
            "new_patients_30d": new_patients,
            "active_patients_90d": active_patients,
            "patients_with_outstanding_balance": patients_with_balance,
            "insurance_distribution": insurance_dist,
            "generated_at": datetime.now().isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Error getting patient statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/appointments")
async def get_appointment_statistics(
    odoo: OdooClient = Depends(OdooClient)
) -> Dict[str, Any]:
    """
    Get appointment-related statistics.
    
    Returns:
        Dictionary with appointment statistics
    """
    try:
        # Get all appointments
        appointments = odoo.search_read(
            'patient.appointment',
            domain=[],
            fields=['id', 'state', 'start']
        )
        
        # Status distribution
        status_dist = {}
        for appt in appointments:
            status = appt['state']
            status_dist[status] = status_dist.get(status, 0) + 1
        
        # Upcoming appointments (next 7 days)
        today = datetime.now().strftime("%Y-%m-%d")
        seven_days = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        upcoming = odoo.search_count(
            'patient.appointment',
            [
                ('state', 'in', ['draft', 'confirmed']),
                ('start', '>=', f"{today} 00:00:00"),
                ('start', '<=', f"{seven_days} 23:59:59")
            ]
        )
        
        # Treatment type distribution
        # TODO: Add treatment_type field or use product.product
        treatment_dist = {"General Checkup": len(appointments)}  # Placeholder
        
        return {
            "total_appointments": len(appointments),
            "status_distribution": status_dist,
            "upcoming_appointments_7d": upcoming,
            "treatment_type_distribution": treatment_dist,
            "generated_at": datetime.now().isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Error getting appointment statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue")
async def get_revenue_statistics(
    odoo: OdooClient = Depends(OdooClient)
) -> Dict[str, Any]:
    """
    Get revenue and financial statistics.
    
    Returns:
        Dictionary with revenue statistics
    """
    try:
        # Get all posted invoices
        invoices = odoo.search_read(
            'account.move',
            domain=[('move_type', '=', 'out_invoice'), ('state', '=', 'posted')],
            fields=['amount_total', 'amount_residual', 'payment_state', 'invoice_date']
        )
        
        # Total revenue
        total_revenue = sum(inv['amount_total'] for inv in invoices)
        
        # Outstanding balance
        outstanding = sum(inv['amount_residual'] for inv in invoices)
        
        # Paid amount
        paid_amount = total_revenue - outstanding
        
        # Revenue by treatment type
        # TODO: Add treatment type from invoice lines
        revenue_by_treatment = {"General Treatment": total_revenue}  # Placeholder
        
        # Monthly revenue (last 12 months)
        monthly_revenue = {}
        for inv in invoices:
            if inv.get('invoice_date'):
                month = str(inv['invoice_date'])[:7]  # YYYY-MM
                monthly_revenue[month] = monthly_revenue.get(month, 0) + inv['amount_total']
        
        # Sort by month
        monthly_revenue = dict(sorted(monthly_revenue.items()))
        
        return {
            "total_revenue": round(total_revenue, 2),
            "paid_amount": round(paid_amount, 2),
            "outstanding_balance": round(outstanding, 2),
            "collection_rate": round(paid_amount / total_revenue * 100, 1) if total_revenue > 0 else 0,
            "revenue_by_treatment": revenue_by_treatment,
            "monthly_revenue": monthly_revenue,
            "generated_at": datetime.now().isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Error getting revenue statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-patients")
async def get_top_patients(
    limit: int = 10,
    odoo: OdooClient = Depends(OdooClient)
) -> Dict[str, Any]:
    """
    Get top patients by revenue.
    
    Args:
        limit: Number of top patients to return
        odoo: Odoo client instance
        
    Returns:
        List of top patients
    """
    try:
        # Get all patients with their total receivables
        patients = odoo.search_read(
            'res.partner',
            domain=[('customer_rank', '>', 0)],
            fields=['id', 'name', 'phone', 'credit', 'debit'],
            limit=limit * 3,  # Get more to filter
            order='debit DESC'  # Order by total invoiced (debit)
        )
        
        # Get patient details with appointment count
        result = []
        for patient in patients[:limit]:
            # Get appointment count
            appt_count = odoo.search_count(
                'patient.appointment',
                [('patient_id', '=', patient['id']), ('status', '=', 'done')]
            )
            
            # Get total revenue (from invoices)
            patient_invoices = odoo.search_read(
                'account.move',
                domain=[
                    ('partner_id', '=', patient['id']),
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted')
                ],
                fields=['amount_total', 'amount_residual']
            )
            
            total_revenue = sum(inv['amount_total'] for inv in patient_invoices)
            outstanding_balance = sum(inv['amount_residual'] for inv in patient_invoices)
            
            result.append({
                "patient_id": patient['id'],
                "name": patient['name'],
                "phone": patient.get('phone'),
                "total_revenue": round(total_revenue, 2),
                "total_visits": appt_count,
                "outstanding_balance": round(outstanding_balance, 2),
            })
        
        # Sort by revenue
        result.sort(key=lambda x: x['total_revenue'], reverse=True)
        
        return {
            "top_patients": result,
            "generated_at": datetime.now().isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Error getting top patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))

