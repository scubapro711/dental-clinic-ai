"""
Demo Tools for Interactive Demo Mode

These tools provide demo data instead of real Odoo data,
allowing potential customers to try DentaFlow without creating an account.
"""

import logging
from typing import Dict, Any, Optional
from langchain_core.tools import tool
import json
from datetime import datetime, timedelta

from app.services.demo_data import demo_data

logger = logging.getLogger(__name__)


@tool
def get_demo_patient_tool(patient_name: str) -> str:
    """
    Get demo patient information by name.
    
    Use this in DEMO MODE when user asks about a patient.
    
    Args:
        patient_name: Name of the patient to look up
        
    Returns:
        JSON string with patient information
    """
    try:
        logger.info(f"Demo: Looking up patient '{patient_name}'")
        
        patient = demo_data.get_demo_patient(name=patient_name)
        
        if not patient:
            # Suggest available demo patients
            available = [p["name"] for p in demo_data.DEMO_PATIENTS]
            return json.dumps({
                "found": False,
                "message": f"Patient '{patient_name}' not found in demo data.",
                "suggestion": f"Try one of these demo patients: {', '.join(available)}"
            }, ensure_ascii=False, indent=2)
        
        return json.dumps({
            "found": True,
            "patient": patient,
            "note": "⚠️ This is demo data. In your real clinic, this would be actual patient information from Odoo."
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting demo patient: {e}")
        return f"Error accessing demo patient data: {str(e)}"


@tool
def get_demo_appointments_tool(date: Optional[str] = None) -> str:
    """
    Get demo appointments for a specific date or all upcoming appointments.
    
    Use this in DEMO MODE when user asks about appointments or schedule.
    
    Args:
        date: Optional date string (YYYY-MM-DD). If None, returns next 7 days.
        
    Returns:
        JSON string with appointment list
    """
    try:
        if date:
            logger.info(f"Demo: Getting appointments for {date}")
        else:
            logger.info("Demo: Getting upcoming appointments")
            # Default to next 7 days
            today = datetime.now()
            appointments = []
            for i in range(7):
                day = (today + timedelta(days=i)).strftime("%Y-%m-%d")
                day_appts = demo_data.get_demo_appointments(day)
                appointments.extend(day_appts)
            
            return json.dumps({
                "date_range": f"{today.strftime('%Y-%m-%d')} to {(today + timedelta(days=6)).strftime('%Y-%m-%d')}",
                "total_appointments": len(appointments),
                "appointments": appointments[:10],  # Limit to 10 for readability
                "note": "⚠️ This is demo data. In your real clinic, this would be your actual appointment calendar from Odoo."
            }, ensure_ascii=False, indent=2)
        
        appointments = demo_data.get_demo_appointments(date)
        
        return json.dumps({
            "date": date,
            "total_appointments": len(appointments),
            "appointments": appointments,
            "note": "⚠️ This is demo data. In your real clinic, this would be your actual appointment calendar from Odoo."
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting demo appointments: {e}")
        return f"Error accessing demo appointments: {str(e)}"


@tool
def get_demo_available_slots_tool(date: str) -> str:
    """
    Get available appointment slots for a specific date in demo mode.
    
    Use this in DEMO MODE when user wants to book an appointment.
    
    Args:
        date: Date string (YYYY-MM-DD)
        
    Returns:
        JSON string with available time slots
    """
    try:
        logger.info(f"Demo: Getting available slots for {date}")
        
        slots = demo_data.get_demo_available_slots(date)
        
        return json.dumps({
            "date": date,
            "available_slots": len(slots),
            "slots": slots[:10],  # Limit to 10 for readability
            "note": "⚠️ This is demo data. In your real clinic, I'd check your actual Odoo calendar and book real appointments."
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting demo available slots: {e}")
        return f"Error accessing demo available slots: {str(e)}"


@tool
def get_demo_invoices_tool(patient_name: Optional[str] = None) -> str:
    """
    Get demo invoices, optionally filtered by patient.
    
    Use this in DEMO MODE when user asks about billing or invoices.
    
    Args:
        patient_name: Optional patient name to filter invoices
        
    Returns:
        JSON string with invoice list
    """
    try:
        if patient_name:
            logger.info(f"Demo: Getting invoices for patient '{patient_name}'")
            
            # Find patient first
            patient = demo_data.get_demo_patient(name=patient_name)
            if not patient:
                return json.dumps({
                    "found": False,
                    "message": f"Patient '{patient_name}' not found in demo data."
                }, ensure_ascii=False, indent=2)
            
            invoices = demo_data.get_demo_invoices(patient["id"])
        else:
            logger.info("Demo: Getting all invoices")
            invoices = demo_data.get_demo_invoices()
        
        return json.dumps({
            "total_invoices": len(invoices),
            "invoices": invoices,
            "note": "⚠️ This is demo data. In your real clinic, this would be actual billing information from Odoo."
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting demo invoices: {e}")
        return f"Error accessing demo invoices: {str(e)}"


@tool
def get_demo_financial_summary_tool() -> str:
    """
    Get demo financial summary and metrics.
    
    Use this in DEMO MODE when user asks about revenue, finances, or dashboard.
    
    Returns:
        JSON string with financial summary
    """
    try:
        logger.info("Demo: Getting financial summary")
        
        summary = demo_data.get_demo_financial_summary()
        
        return json.dumps({
            "summary": summary,
            "note": "⚠️ This is demo data. In your real clinic, Marcus (our CFO AI) would analyze your actual financial data from Odoo."
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting demo financial summary: {e}")
        return f"Error accessing demo financial summary: {str(e)}"


@tool
def get_demo_clinic_info_tool() -> str:
    """
    Get demo clinic information (hours, location, contact).
    
    Use this in DEMO MODE when user asks about clinic details.
    
    Returns:
        JSON string with clinic information
    """
    try:
        logger.info("Demo: Getting clinic info")
        
        clinic = demo_data.get_demo_clinic_info()
        
        return json.dumps({
            "clinic": clinic,
            "note": "⚠️ This is demo data. In your real clinic, this would be your actual clinic information from Odoo."
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting demo clinic info: {e}")
        return f"Error accessing demo clinic info: {str(e)}"


@tool
def book_demo_appointment_tool(patient_name: str, date: str, time: str, appointment_type: str) -> str:
    """
    Simulate booking an appointment in demo mode.
    
    Use this in DEMO MODE when user wants to book an appointment.
    
    Args:
        patient_name: Name of the patient
        date: Date string (YYYY-MM-DD)
        time: Time string (HH:MM)
        appointment_type: Type of appointment (e.g., "Cleaning", "Check-up")
        
    Returns:
        JSON string with booking confirmation
    """
    try:
        logger.info(f"Demo: Booking appointment for {patient_name} on {date} at {time}")
        
        # Check if patient exists
        patient = demo_data.get_demo_patient(name=patient_name)
        if not patient:
            return json.dumps({
                "success": False,
                "message": f"Patient '{patient_name}' not found. Try one of our demo patients: Sarah Johnson, David Cohen, Rachel Levi, Michael Green, Tamar Shapiro"
            }, ensure_ascii=False, indent=2)
        
        # Simulate successful booking
        import random
        doctor = random.choice(demo_data.DEMO_DOCTORS)
        
        confirmation = {
            "success": True,
            "message": "Appointment booked successfully!",
            "appointment": {
                "patient": patient_name,
                "date": date,
                "time": time,
                "type": appointment_type,
                "doctor": doctor["name"],
                "duration": "30 minutes",
                "confirmation_number": f"DEMO-{random.randint(1000, 9999)}"
            },
            "note": "⚠️ This is a simulated booking in demo mode. In your real clinic, this would create an actual appointment in Odoo and send confirmation via SMS/Email."
        }
        
        return json.dumps(confirmation, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error booking demo appointment: {e}")
        return f"Error booking demo appointment: {str(e)}"

