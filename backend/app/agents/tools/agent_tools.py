"""
Agent Tools - Simplified tool integration for agents

This module provides tools that agents can use to interact with Odoo
and other external systems.
"""

from typing import Optional
from datetime import datetime, timedelta

from app.integrations.mock_odoo_realistic import realistic_mock_odoo

# Use realistic mock Odoo client with 1500+ patients
mock_odoo = realistic_mock_odoo


def search_patient_tool(name: Optional[str] = None, phone: Optional[str] = None) -> str:
    """
    Search for a patient by name or phone number.
    
    Args:
        name: Patient name (partial match allowed)
        phone: Patient phone number
        
    Returns:
        String with patient information or "not found" message
    """
    try:
        patient_ids = mock_odoo.search_patients(name=name, phone=phone)
        
        if not patient_ids:
            return f"No patient found with name='{name}' or phone='{phone}'"
        
        # Get details of first matching patient
        patient = mock_odoo.get_patient(patient_ids[0])
        if patient:
            return f"Found patient: {patient['name']}, Phone: {patient.get('phone', 'N/A')}, Email: {patient.get('email', 'N/A')}, ID: {patient['id']}"
        else:
            return "Patient found but could not retrieve details"
    except Exception as e:
        return f"Error searching patient: {str(e)}"


def get_available_slots_tool(days_ahead: int = 7) -> str:
    """
    Get available appointment slots for the next N days.
    
    Args:
        days_ahead: Number of days to look ahead (default: 7)
        
    Returns:
        String with available time slots
    """
    try:
        date_from = datetime.now()
        date_to = date_from + timedelta(days=days_ahead)
        
        slots = mock_odoo.get_available_slots(date_from, date_to)
        
        if not slots:
            return "No available slots found in the next 7 days."
        
        # Format slots for display
        slot_strings = []
        for slot in slots[:10]:  # Show first 10 slots
            slot_strings.append(slot.strftime("%A, %B %d at %I:%M %p"))
        
        return "Available appointment slots:\n" + "\n".join(f"- {s}" for s in slot_strings)
    except Exception as e:
        return f"Error retrieving available slots: {str(e)}"


def create_appointment_tool(
    patient_name: str,
    patient_phone: str,
    appointment_date: str,
    notes: Optional[str] = None,
) -> str:
    """
    Create a new appointment for a patient.
    
    Args:
        patient_name: Full name of the patient
        patient_phone: Patient phone number
        appointment_date: Date and time in format "YYYY-MM-DD HH:MM"
        notes: Optional notes about the appointment
        
    Returns:
        Confirmation message with appointment details
    """
    try:
        # Search for existing patient
        patient_ids = mock_odoo.search_patients(name=patient_name, phone=patient_phone)
        
        if not patient_ids:
            # Create new patient
            patient_id = mock_odoo.create_patient(
                name=patient_name,
                phone=patient_phone,
            )
        else:
            patient_id = patient_ids[0]
        
        # Parse appointment date
        try:
            appt_datetime = datetime.strptime(appointment_date, "%Y-%m-%d %H:%M")
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD HH:MM format."
        
        # Create appointment
        appointment_id = mock_odoo.create_appointment(
            patient_id=patient_id,
            date=appt_datetime,
            notes=notes,
        )
        
        return (
            f"✅ Appointment created successfully!\n"
            f"Appointment ID: {appointment_id}\n"
            f"Patient: {patient_name}\n"
            f"Date & Time: {appt_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
            f"Phone: {patient_phone}\n"
            f"Please arrive 10 minutes early for check-in."
        )
    except Exception as e:
        return f"Error creating appointment: {str(e)}"


def get_patient_invoices_tool(patient_name: str, patient_phone: Optional[str] = None) -> str:
    """
    Get invoices for a patient.
    
    Args:
        patient_name: Patient name
        patient_phone: Patient phone (optional)
        
    Returns:
        String with invoice information
    """
    try:
        # Search for patient
        patient_ids = mock_odoo.search_patients(name=patient_name, phone=patient_phone)
        
        if not patient_ids:
            return f"No patient found with name '{patient_name}'"
        
        patient_id = patient_ids[0]
        
        # Get invoices
        invoices = mock_odoo.get_patient_invoices(patient_id)
        
        if not invoices:
            return f"No invoices found for {patient_name}"
        
        # Format invoices
        invoice_strings = []
        for inv in invoices:
            status = inv.get('state', 'unknown')
            amount = inv.get('amount_total', 0)
            date = inv.get('date', 'N/A')
            invoice_strings.append(
                f"Invoice #{inv['id']}: ₪{amount:.2f} - {status} (Date: {date})"
            )
        
        return f"Invoices for {patient_name}:\n" + "\n".join(f"- {s}" for s in invoice_strings)
    except Exception as e:
        return f"Error retrieving invoices: {str(e)}"


def get_invoice_details_tool(invoice_id: int) -> str:
    """
    Get detailed information about an invoice.
    
    Args:
        invoice_id: Invoice ID
        
    Returns:
        String with detailed invoice information
    """
    try:
        invoice = mock_odoo.get_invoice(invoice_id)
        
        if not invoice:
            return f"Invoice #{invoice_id} not found"
        
        # Format invoice details
        details = (
            f"Invoice #{invoice['id']}\n"
            f"Patient ID: {invoice.get('patient_id', 'N/A')}\n"
            f"Date: {invoice.get('date', 'N/A')}\n"
            f"Status: {invoice.get('state', 'unknown')}\n"
            f"Subtotal: ₪{invoice.get('amount_untaxed', 0):.2f}\n"
            f"VAT (17%): ₪{invoice.get('amount_tax', 0):.2f}\n"
            f"Total: ₪{invoice.get('amount_total', 0):.2f}\n"
        )
        
        # Add line items if available
        if invoice.get('invoice_lines'):
            details += "\nLine Items:\n"
            for line in invoice['invoice_lines']:
                details += f"- {line.get('description', 'N/A')}: ₪{line.get('price', 0):.2f}\n"
        
        return details
    except Exception as e:
        return f"Error retrieving invoice details: {str(e)}"
