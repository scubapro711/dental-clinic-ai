"""
Status mapping utilities for Odoo field conversions.

This module provides mapping functions between Odoo's actual field names/values
and our application's expected field names/values.

Odoo uses 'attendee_status' with values: needsAction, accepted, declined, tentative
Our app uses 'appointment_status' with values: draft, confirm, cancelled, pending
"""

from typing import Dict, List


def map_odoo_status_to_app_status(odoo_status: str) -> str:
    """
    Map Odoo attendee_status to application appointment_status.
    
    Args:
        odoo_status: Odoo attendee_status value
    
    Returns:
        Application status value
    
    Example:
        >>> map_odoo_status_to_app_status('accepted')
        'confirm'
        >>> map_odoo_status_to_app_status('needsAction')
        'draft'
    """
    mapping = {
        'needsAction': 'draft',
        'accepted': 'confirm',
        'declined': 'cancelled',
        'tentative': 'pending'
    }
    return mapping.get(odoo_status, 'draft')


def map_app_status_to_odoo_status(app_status: str) -> str:
    """
    Map application appointment_status to Odoo attendee_status.
    
    Args:
        app_status: Application status value
    
    Returns:
        Odoo attendee_status value
    
    Example:
        >>> map_app_status_to_odoo_status('confirm')
        'accepted'
        >>> map_app_status_to_odoo_status('draft')
        'needsAction'
    """
    mapping = {
        'draft': 'needsAction',
        'confirm': 'accepted',
        'cancelled': 'declined',
        'pending': 'tentative',
        'completed_appointment': 'accepted'  # Map completed to accepted
    }
    return mapping.get(app_status, 'needsAction')


def map_app_statuses_to_odoo_statuses(app_statuses: List[str]) -> List[str]:
    """
    Map list of application statuses to Odoo statuses.
    
    Args:
        app_statuses: List of application status values
    
    Returns:
        List of Odoo attendee_status values
    
    Example:
        >>> map_app_statuses_to_odoo_statuses(['draft', 'confirm'])
        ['needsAction', 'accepted']
    """
    return [map_app_status_to_odoo_status(status) for status in app_statuses]


def enrich_appointment_with_app_status(appointment: Dict) -> Dict:
    """
    Enrich Odoo appointment record with application status field.
    
    Converts Odoo's attendee_status to our app's appointment_status
    and adds it to the appointment dict.
    
    Args:
        appointment: Odoo appointment record dict
    
    Returns:
        Enriched appointment dict with appointment_status field
    
    Example:
        >>> appt = {'id': 1, 'attendee_status': 'accepted'}
        >>> enrich_appointment_with_app_status(appt)
        {'id': 1, 'attendee_status': 'accepted', 'appointment_status': 'confirm'}
    """
    odoo_status = appointment.get('attendee_status', 'needsAction')
    app_status = map_odoo_status_to_app_status(odoo_status)
    appointment['appointment_status'] = app_status
    return appointment
