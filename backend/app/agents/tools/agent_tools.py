"""
Agent Tools - Simplified tool integration for agents

This module provides tools that agents can use to interact with Odoo
and other external systems.

Enhanced with RBAC (Role-Based Access Control) for data privacy and security.
"""

from typing import Optional
from datetime import datetime, timedelta
import logging

from app.core.config import settings
from app.agents.rbac import (
    has_permission,
    can_access_resource,
    get_permission_denied_message,
    log_access_attempt,
    Permission,
)
import os

logger = logging.getLogger(__name__)


def get_odoo_client():
    """Get Odoo client instance (mock in tests, real in production)."""
    # Use mock in test environment
    if os.getenv("TESTING") == "1" or os.getenv("APP_ENV") == "test":
        from app.integrations.mock_odoo_realistic import RealisticMockOdooClient
        return RealisticMockOdooClient()
    else:
        from app.integrations.odoo_client import OdooClient
        return OdooClient()


def search_patient_tool(
    name: Optional[str] = None,
    phone: Optional[str] = None,
    requesting_user_id: Optional[str] = None,
    requesting_user_role: Optional[str] = None,
) -> str:
    """
    Search for a patient by name or phone number.
    
    RBAC: Patients can only search for themselves, staff can search all.
    
    Args:
        name: Patient name (partial match allowed)
        phone: Patient phone number
        requesting_user_id: ID of user making the request
        requesting_user_role: Role of user making the request
        
    Returns:
        String with patient information or "not found" message
    """
    try:
        # RBAC Check: Patients can only search for themselves
        if requesting_user_role == "patient":
            # For patients, we assume they're searching for themselves
            # In real implementation, we'd verify the name/phone matches their record
            log_access_attempt(
                requesting_user_id,
                requesting_user_role,
                "search_patient",
                "patient",
                None,
                True
            )
        elif requesting_user_role in ["doctor", "owner"]:
            # Doctors and owners can search all patients
            log_access_attempt(
                requesting_user_id,
                requesting_user_role,
                "search_patient",
                "patient",
                None,
                True
            )
        else:
            log_access_attempt(
                requesting_user_id or "unknown",
                requesting_user_role or "unknown",
                "search_patient",
                "patient",
                None,
                False
            )
            return get_permission_denied_message(requesting_user_role or "unknown", "search_patients")
        
        odoo = get_odoo_client()
        
        # Build search domain
        domain = [('is_patient', '=', True)]
        if name and phone:
            domain = ['&'] + domain + ['|', ('name', 'ilike', name), ('phone', 'ilike', phone)]
        elif name:
            domain.append(('name', 'ilike', name))
        elif phone:
            domain.append(('phone', 'ilike', phone))
        
        # Search patients
        patients = odoo.search_read(
            'res.partner',
            domain=domain,
            fields=['id', 'name', 'phone', 'email'],
            limit=1
        )
        
        if not patients:
            return f"No patient found with name='{name}' or phone='{phone}'"
        
        patient = patients[0]
        
        # For patients, only return if it's their own record
        if requesting_user_role == "patient" and str(patient['id']) != requesting_user_id:
            return get_permission_denied_message(requesting_user_role, "view_other_patients")
        
        return f"Found patient: {patient['name']}, Phone: {patient.get('phone', 'N/A')}, Email: {patient.get('email', 'N/A')}, ID: {patient['id']}"
        
    except Exception as e:
        logger.error(f"Error in search_patient_tool: {str(e)}")
        return f"Error searching patient: {str(e)}"


def get_available_slots_tool(days_ahead: int = 7) -> str:
    """Get available appointment slots for the next N days.
    
    Args:
        days_ahead: Number of days to look ahead (default: 7)
    """
    try:
        odoo = get_odoo_client()
        
        date_from = datetime.now()
        date_to = date_from + timedelta(days=days_ahead)
        
        # Get all appointments in the date range
        appointments = odoo.search_read(
            'patient.appointment',
            domain=[
                ('start', '>=', date_from.strftime("%Y-%m-%d %H:%M:%S")),
                ('start', '<=', date_to.strftime("%Y-%m-%d %H:%M:%S")),
                ('state', '!=', 'cancel'),
            ],
            fields=['start']
        )
        
        # Extract booked times
        booked_times = set()
        for apt in appointments:
            if apt.get('start'):
                booked_times.add(str(apt['start']))
        
        # Generate available slots (9 AM to 5 PM, 30-minute intervals)
        available_slots = []
        current_date = date_from.replace(hour=9, minute=0, second=0, microsecond=0)
        
        while current_date <= date_to and len(available_slots) < 10:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday-Friday
                # Check working hours (9 AM - 5 PM)
                if 9 <= current_date.hour < 17:
                    slot_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
                    if slot_str not in booked_times:
                        available_slots.append(current_date)
            
            # Move to next 30-minute slot
            current_date += timedelta(minutes=30)
        
        if not available_slots:
            return "No available slots found in the next 7 days."
        
        # Format slots for display
        slot_strings = [slot.strftime("%A, %B %d at %I:%M %p") for slot in available_slots]
        
        return "Available appointment slots:\n" + "\n".join(f"- {s}" for s in slot_strings)
        
    except Exception as e:
        logger.error(f"Error in get_available_slots_tool: {str(e)}")
        return f"Error retrieving available slots: {str(e)}"


def create_appointment_tool(
    patient_name: str,
    patient_phone: str,
    appointment_date: str,
    notes: Optional[str] = None,
) -> str:
    """Create a new appointment for a patient.
    
    Args:
        patient_name: Full name of the patient
        patient_phone: Patient phone number
        appointment_date: Date and time in format "YYYY-MM-DD HH:MM"
        notes: Optional notes about the appointment
    """
    try:
        odoo = get_odoo_client()
        
        # Search for existing patient
        patients = odoo.search_read(
            'res.partner',
            domain=['|', ('name', 'ilike', patient_name), ('phone', 'ilike', patient_phone), ('is_patient', '=', True)],
            fields=['id', 'name'],
            limit=1
        )
        
        if not patients:
            # Create new patient
            patient_id = odoo.create('res.partner', {
                'name': patient_name,
                'phone': patient_phone,
                'is_patient': True,
            })
        else:
            patient_id = patients[0]['id']
        
        # Parse appointment date
        try:
            appt_datetime = datetime.strptime(appointment_date, "%Y-%m-%d %H:%M")
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD HH:MM format."
        
        # Create appointment
        appointment_id = odoo.create('patient.appointment', {
            'patient_id': patient_id,
            'start': appt_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            'stop': (appt_datetime + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            'state': 'draft',
            'comments': notes or '',
        })
        
        return (
            f"✅ Appointment created successfully!\n"
            f"Appointment ID: {appointment_id}\n"
            f"Patient: {patient_name}\n"
            f"Date & Time: {appt_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
            f"Phone: {patient_phone}\n"
            f"Please arrive 10 minutes early for check-in."
        )
        
    except Exception as e:
        logger.error(f"Error in create_appointment_tool: {str(e)}")
        return f"Error creating appointment: {str(e)}"


def get_patient_invoices_tool(patient_name: str, patient_phone: Optional[str] = None) -> str:
    """Get invoices for a patient.
    
    Args:
        patient_name: Patient name
        patient_phone: Patient phone (optional)
    """
    try:
        odoo = get_odoo_client()
        
        # Search for patient
        domain = [('name', 'ilike', patient_name), ('is_patient', '=', True)]
        if patient_phone:
            domain = ['&'] + domain + [('phone', 'ilike', patient_phone)]
        
        patients = odoo.search_read(
            'res.partner',
            domain=domain,
            fields=['id', 'name'],
            limit=1
        )
        
        if not patients:
            return f"No patient found with name '{patient_name}'"
        
        patient_id = patients[0]['id']
        
        # Get invoices
        invoices = odoo.search_read(
            'account.move',
            domain=[
                ('partner_id', '=', patient_id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
            ],
            fields=['id', 'name', 'invoice_date', 'amount_total', 'payment_state'],
            order='invoice_date DESC'
        )
        
        if not invoices:
            return f"No invoices found for {patient_name}"
        
        # Format invoices
        invoice_strings = []
        for inv in invoices:
            status = inv.get('payment_state', 'unknown')
            amount = inv.get('amount_total', 0)
            date = inv.get('invoice_date', 'N/A')
            invoice_strings.append(
                f"Invoice #{inv['id']}: ₪{amount:.2f} - {status} (Date: {date})"
            )
        
        return f"Invoices for {patient_name}:\n" + "\n".join(f"- {s}" for s in invoice_strings)
        
    except Exception as e:
        logger.error(f"Error in get_patient_invoices_tool: {str(e)}")
        return f"Error retrieving invoices: {str(e)}"


def get_invoice_details_tool(invoice_id: int) -> str:
    """Get detailed information about an invoice.
    
    Args:
        invoice_id: Invoice ID
    """
    try:
        odoo = get_odoo_client()
        
        # Get invoice
        invoices = odoo.read(
            'account.move',
            [invoice_id],
            ['id', 'name', 'partner_id', 'invoice_date', 'payment_state', 
             'amount_untaxed', 'amount_tax', 'amount_total']
        )
        
        if not invoices:
            return f"Invoice #{invoice_id} not found"
        
        invoice = invoices[0]
        
        # Format invoice details
        partner_name = invoice.get('partner_id', [None, 'N/A'])[1] if invoice.get('partner_id') else 'N/A'
        
        details = (
            f"Invoice #{invoice['id']} ({invoice.get('name', 'N/A')})\n"
            f"Patient: {partner_name}\n"
            f"Date: {invoice.get('invoice_date', 'N/A')}\n"
            f"Status: {invoice.get('payment_state', 'unknown')}\n"
            f"Subtotal: ₪{invoice.get('amount_untaxed', 0):.2f}\n"
            f"VAT (17%): ₪{invoice.get('amount_tax', 0):.2f}\n"
            f"Total: ₪{invoice.get('amount_total', 0):.2f}\n"
        )
        
        # Get line items
        lines = odoo.search_read(
            'account.move.line',
            domain=[('move_id', '=', invoice_id), ('display_type', '=', 'product')],
            fields=['name', 'price_subtotal'],
            limit=10
        )
        
        if lines:
            details += "\nLine Items:\n"
            for line in lines:
                details += f"- {line.get('name', 'N/A')}: ₪{line.get('price_subtotal', 0):.2f}\n"
        
        return details
        
    except Exception as e:
        logger.error(f"Error in get_invoice_details_tool: {str(e)}")
        return f"Error retrieving invoice details: {str(e)}"

