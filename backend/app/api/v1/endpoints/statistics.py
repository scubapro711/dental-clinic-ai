"""
Statistics API Endpoint

Provides clinic statistics and analytics for the dashboard.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta

from app.integrations.mock_odoo_realistic import realistic_mock_odoo

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/overview")
async def get_overview_statistics() -> Dict[str, Any]:
    """
    Get overview statistics for the clinic dashboard.
    
    Returns:
        Dictionary with clinic statistics
    """
    try:
        stats = realistic_mock_odoo.get_statistics()
        
        # Calculate additional metrics
        completion_rate = (
            stats["completed_appointments"] / stats["total_appointments"] * 100
            if stats["total_appointments"] > 0 else 0
        )
        
        payment_rate = (
            stats["paid_invoices"] / stats["total_invoices"] * 100
            if stats["total_invoices"] > 0 else 0
        )
        
        avg_revenue_per_patient = (
            stats["total_revenue"] / stats["total_patients"]
            if stats["total_patients"] > 0 else 0
        )
        
        return {
            **stats,
            "completion_rate": round(completion_rate, 1),
            "payment_rate": round(payment_rate, 1),
            "avg_revenue_per_patient": round(avg_revenue_per_patient, 2),
            "generated_at": datetime.now().isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patients")
async def get_patient_statistics() -> Dict[str, Any]:
    """
    Get patient-related statistics.
    
    Returns:
        Dictionary with patient statistics
    """
    try:
        # Get all patients
        patients = realistic_mock_odoo.patients
        
        # Calculate statistics
        total_patients = len(patients)
        
        # Patients with outstanding balance
        patients_with_balance = len([p for p in patients if p["outstanding_balance"] > 0])
        
        # New patients (registered in last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        new_patients = len([
            p for p in patients 
            if p["registration_date"] >= thirty_days_ago
        ])
        
        # Active patients (visited in last 90 days)
        ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        active_patients = len([
            p for p in patients 
            if p["last_visit"] and p["last_visit"] >= ninety_days_ago
        ])
        
        # Insurance distribution
        insurance_dist = {}
        for patient in patients:
            provider = patient.get("insurance_provider", "None")
            insurance_dist[provider] = insurance_dist.get(provider, 0) + 1
        
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
async def get_appointment_statistics() -> Dict[str, Any]:
    """
    Get appointment-related statistics.
    
    Returns:
        Dictionary with appointment statistics
    """
    try:
        appointments = realistic_mock_odoo.appointments
        
        # Status distribution
        status_dist = {}
        for appt in appointments:
            status = appt["status"]
            status_dist[status] = status_dist.get(status, 0) + 1
        
        # Upcoming appointments (next 7 days)
        today = datetime.now().strftime("%Y-%m-%d")
        seven_days = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        upcoming = len([
            a for a in appointments
            if a["status"] == "scheduled" and today <= a["date"] <= seven_days
        ])
        
        # Treatment type distribution
        treatment_dist = {}
        for appt in appointments:
            treatment = appt["treatment_type"]
            treatment_dist[treatment] = treatment_dist.get(treatment, 0) + 1
        
        # Sort by popularity
        treatment_dist = dict(sorted(treatment_dist.items(), key=lambda x: x[1], reverse=True))
        
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
async def get_revenue_statistics() -> Dict[str, Any]:
    """
    Get revenue and financial statistics.
    
    Returns:
        Dictionary with revenue statistics
    """
    try:
        invoices = realistic_mock_odoo.invoices
        
        # Total revenue
        total_revenue = sum(inv["total_amount"] for inv in invoices)
        
        # Outstanding balance
        outstanding = sum(inv["outstanding_amount"] for inv in invoices)
        
        # Paid vs unpaid
        paid_amount = sum(inv["paid_amount"] for inv in invoices)
        
        # Revenue by treatment type
        revenue_by_treatment = {}
        for inv in invoices:
            treatment = inv["treatment"]
            revenue_by_treatment[treatment] = revenue_by_treatment.get(treatment, 0) + inv["total_amount"]
        
        # Sort by revenue
        revenue_by_treatment = dict(sorted(revenue_by_treatment.items(), key=lambda x: x[1], reverse=True))
        
        # Monthly revenue (last 12 months)
        monthly_revenue = {}
        for inv in invoices:
            month = inv["issue_date"][:7]  # YYYY-MM
            monthly_revenue[month] = monthly_revenue.get(month, 0) + inv["total_amount"]
        
        # Sort by month
        monthly_revenue = dict(sorted(monthly_revenue.items()))
        
        return {
            "total_revenue": total_revenue,
            "paid_amount": paid_amount,
            "outstanding_balance": outstanding,
            "collection_rate": round(paid_amount / total_revenue * 100, 1) if total_revenue > 0 else 0,
            "revenue_by_treatment": revenue_by_treatment,
            "monthly_revenue": monthly_revenue,
            "generated_at": datetime.now().isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Error getting revenue statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-patients")
async def get_top_patients(limit: int = 10) -> Dict[str, Any]:
    """
    Get top patients by revenue.
    
    Args:
        limit: Number of top patients to return
        
    Returns:
        List of top patients
    """
    try:
        # Calculate revenue per patient
        patient_revenue = {}
        for inv in realistic_mock_odoo.invoices:
            patient_id = inv["patient_id"]
            patient_revenue[patient_id] = patient_revenue.get(patient_id, 0) + inv["total_amount"]
        
        # Sort by revenue
        top_patients = sorted(patient_revenue.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        # Get patient details
        result = []
        for patient_id, revenue in top_patients:
            patient = realistic_mock_odoo.get_patient(patient_id)
            if patient:
                result.append({
                    "patient_id": patient_id,
                    "name": patient["name"],
                    "phone": patient["phone"],
                    "total_revenue": revenue,
                    "total_visits": patient["total_visits"],
                    "outstanding_balance": patient["outstanding_balance"],
                })
        
        return {
            "top_patients": result,
            "generated_at": datetime.now().isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Error getting top patients: {e}")
        raise HTTPException(status_code=500, detail=str(e))
