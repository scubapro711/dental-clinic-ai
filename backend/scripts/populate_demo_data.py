#!/usr/bin/env python3
"""
Populate Odoo with Demo Data for Demo User

This script creates realistic demo data in Odoo for the demo@dentaflow.ai user:
1. Creates a patient in Odoo (res.partner)
2. Creates appointments (medical.appointment)
3. Creates treatments (dental.treatment)
4. Creates invoices (account.invoice)
5. Creates user-patient mapping in PostgreSQL

This is NOT mock data - it's real data in the actual Odoo instance.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.core.config import settings
from app.core.database import SessionLocal
from app.integrations.odoo_client import OdooClient
from app.models.user import User
from app.models.organization import Organization
from sqlalchemy import select

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_demo_user_and_org(db):
    """Get the demo user and their organization from PostgreSQL."""
    logger.info("Fetching demo user from database...")
    
    # Get demo user
    user = db.execute(
        select(User).where(User.email == "demo@dentaflow.ai")
    ).scalar_one_or_none()
    
    if not user:
        logger.error("Demo user not found! Please create demo@dentaflow.ai first.")
        return None, None
    
    logger.info(f"Found demo user: {user.email} (ID: {user.id})")
    
    # Get user's organization
    if not user.organization_id:
        logger.error("Demo user has no organization!")
        return user, None
    
    org = user.organization  # Get organization via relationship
    logger.info(f"Found organization: {org.name} (ID: {org.id})")
    
    return user, org


def create_patient_in_odoo(odoo: OdooClient) -> Optional[int]:
    """Create a demo patient in Odoo."""
    logger.info("Creating patient in Odoo...")
    
    patient_data = {
        'name': 'Demo Patient',
        'email': 'demo@dentaflow.ai',
        'phone': '+972-50-555-0100',
        'mobile': '+972-50-555-0100',
        'street': '123 Rothschild Blvd',
        'city': 'Tel Aviv',
        'zip': '6688101',
        'country_id': 117,  # Israel (you may need to adjust this)
        'customer_rank': 1,  # Mark as customer
        'is_company': False,
        'type': 'contact',
        'comment': 'Demo patient for testing DentaFlow system',
    }
    
    try:
        # Check if patient already exists
        existing = odoo.search('res.partner', [('email', '=', 'demo@dentaflow.ai')])
        if existing:
            patient_id = existing[0]
            logger.info(f"Patient already exists with ID: {patient_id}")
            return patient_id
        
        # Create new patient
        patient_id = odoo.create('res.partner', patient_data)
        logger.info(f"Created patient with ID: {patient_id}")
        return patient_id
    
    except Exception as e:
        logger.error(f"Failed to create patient: {e}")
        return None


def create_appointments(odoo: OdooClient, patient_id: int) -> list:
    """Create demo appointments for the patient."""
    logger.info("Creating appointments...")
    
    appointments = []
    now = datetime.now()
    
    # Create 3 upcoming appointments
    appointment_times = [
        now + timedelta(days=2, hours=10),  # In 2 days at 10:00
        now + timedelta(days=7, hours=14),  # In 1 week at 14:00
        now + timedelta(days=14, hours=9),  # In 2 weeks at 09:00
    ]
    
    treatments = [
        'Dental Cleaning',
        'Cavity Filling',
        'Root Canal Consultation'
    ]
    
    for i, (appt_time, treatment) in enumerate(zip(appointment_times, treatments)):
        appt_data = {
            'patient_id': patient_id,
            'appointment_date': appt_time.strftime('%Y-%m-%d %H:%M:%S'),
            'state': 'scheduled',
            'notes': f'Demo appointment #{i+1} - {treatment}',
            'treatment_type': treatment,
        }
        
        try:
            appt_id = odoo.create('medical.appointment', appt_data)
            appointments.append(appt_id)
            logger.info(f"Created appointment {i+1}: {treatment} on {appt_time.strftime('%Y-%m-%d %H:%M')}")
        except Exception as e:
            logger.warning(f"Failed to create appointment {i+1}: {e}")
            # Try alternative model name
            try:
                appt_id = odoo.create('patient.appointment', appt_data)
                appointments.append(appt_id)
                logger.info(f"Created appointment {i+1} (alternative model): {treatment}")
            except Exception as e2:
                logger.error(f"Failed with alternative model too: {e2}")
    
    # Create 2 past appointments (completed)
    past_times = [
        now - timedelta(days=30),  # 1 month ago
        now - timedelta(days=90),  # 3 months ago
    ]
    
    past_treatments = [
        'Dental Cleaning',
        'Teeth Whitening'
    ]
    
    for i, (appt_time, treatment) in enumerate(zip(past_times, past_treatments)):
        appt_data = {
            'patient_id': patient_id,
            'appointment_date': appt_time.strftime('%Y-%m-%d %H:%M:%S'),
            'state': 'completed',
            'notes': f'Past appointment - {treatment}',
            'treatment_type': treatment,
        }
        
        try:
            appt_id = odoo.create('medical.appointment', appt_data)
            appointments.append(appt_id)
            logger.info(f"Created past appointment: {treatment} on {appt_time.strftime('%Y-%m-%d')}")
        except Exception as e:
            logger.warning(f"Failed to create past appointment: {e}")
    
    logger.info(f"Created {len(appointments)} appointments total")
    return appointments


def create_treatments(odoo: OdooClient, patient_id: int) -> list:
    """Create demo treatment records."""
    logger.info("Creating treatment records...")
    
    treatments = []
    
    treatment_data_list = [
        {
            'patient_id': patient_id,
            'treatment_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'treatment_type': 'Dental Cleaning',
            'description': 'Regular dental cleaning and examination',
            'tooth_number': None,
            'status': 'completed',
            'cost': 350.00,
        },
        {
            'patient_id': patient_id,
            'treatment_date': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
            'treatment_type': 'Teeth Whitening',
            'description': 'Professional teeth whitening treatment',
            'tooth_number': None,
            'status': 'completed',
            'cost': 1200.00,
        },
    ]
    
    for i, treatment_data in enumerate(treatment_data_list):
        try:
            treatment_id = odoo.create('dental.treatment', treatment_data)
            treatments.append(treatment_id)
            logger.info(f"Created treatment {i+1}: {treatment_data['treatment_type']}")
        except Exception as e:
            logger.warning(f"Failed to create treatment {i+1}: {e}")
    
    logger.info(f"Created {len(treatments)} treatments total")
    return treatments


def create_invoices(odoo: OdooClient, patient_id: int) -> list:
    """Create demo invoices."""
    logger.info("Creating invoices...")
    
    invoices = []
    
    invoice_data_list = [
        {
            'partner_id': patient_id,
            'invoice_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'state': 'paid',
            'amount_total': 350.00,
            'amount_residual': 0.00,
            'payment_state': 'paid',
            'invoice_line_ids': [(0, 0, {
                'name': 'Dental Cleaning',
                'quantity': 1,
                'price_unit': 350.00,
            })],
        },
        {
            'partner_id': patient_id,
            'invoice_date': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
            'state': 'paid',
            'amount_total': 1200.00,
            'amount_residual': 0.00,
            'payment_state': 'paid',
            'invoice_line_ids': [(0, 0, {
                'name': 'Teeth Whitening',
                'quantity': 1,
                'price_unit': 1200.00,
            })],
        },
        {
            'partner_id': patient_id,
            'invoice_date': datetime.now().strftime('%Y-%m-%d'),
            'state': 'posted',
            'amount_total': 800.00,
            'amount_residual': 800.00,
            'payment_state': 'not_paid',
            'invoice_line_ids': [(0, 0, {
                'name': 'Cavity Filling (Upcoming)',
                'quantity': 1,
                'price_unit': 800.00,
            })],
        },
    ]
    
    for i, invoice_data in enumerate(invoice_data_list):
        try:
            invoice_id = odoo.create('account.invoice', invoice_data)
            invoices.append(invoice_id)
            logger.info(f"Created invoice {i+1}: ₪{invoice_data['amount_total']:.2f} ({invoice_data['state']})")
        except Exception as e:
            logger.warning(f"Failed to create invoice {i+1}: {e}")
            # Try alternative model name
            try:
                invoice_id = odoo.create('account.move', invoice_data)
                invoices.append(invoice_id)
                logger.info(f"Created invoice {i+1} (alternative model)")
            except Exception as e2:
                logger.error(f"Failed with alternative model too: {e2}")
    
    logger.info(f"Created {len(invoices)} invoices total")
    return invoices


def create_user_patient_mapping(db, user_id, org_id, odoo_partner_id: int):
    """Create mapping between DentaFlow user and Odoo patient."""
    logger.info("Creating user-patient mapping...")
    
    try:
        # Check if mapping already exists
        from app.models.user_patient_mapping import UserPatientMapping
        
        existing = db.execute(
            select(UserPatientMapping).where(
                UserPatientMapping.user_id == user_id,
                UserPatientMapping.organization_id == org_id
            )
        ).scalar_one_or_none()
        
        if existing:
            logger.info(f"Mapping already exists: user_id={user_id} -> odoo_partner_id={existing.odoo_partner_id}")
            # Update if different
            if existing.odoo_partner_id != odoo_partner_id:
                existing.odoo_partner_id = odoo_partner_id
                db.commit()
                logger.info(f"Updated mapping to odoo_partner_id={odoo_partner_id}")
            return existing
        
        # Create new mapping
        mapping = UserPatientMapping(
            user_id=user_id,
            organization_id=org_id,
            odoo_partner_id=odoo_partner_id
        )
        db.add(mapping)
        db.commit()
        logger.info(f"Created mapping: user_id={user_id} -> odoo_partner_id={odoo_partner_id}")
        return mapping
    
    except Exception as e:
        logger.error(f"Failed to create mapping: {e}")
        db.rollback()
        return None


def main():
    """Main function to populate demo data."""
    logger.info("=" * 80)
    logger.info("DentaFlow Demo Data Population Script")
    logger.info("=" * 80)
    
    # Check Odoo configuration
    if not settings.ODOO_URL:
        logger.error("ODOO_URL not configured! Please set environment variables.")
        return 1
    
    logger.info(f"Odoo URL: {settings.ODOO_URL}")
    logger.info(f"Odoo DB: {settings.ODOO_DB}")
    
    # Initialize database session
    db = SessionLocal()
    
    try:
        # Step 1: Get demo user and organization
        user, org = get_demo_user_and_org(db)
        if not user or not org:
            return 1
        
        # Step 2: Initialize Odoo client
        logger.info("\nInitializing Odoo client...")
        odoo = OdooClient()
        
        # Test connection
        try:
            odoo.authenticate()
            logger.info("✅ Odoo connection successful!")
        except Exception as e:
            logger.error(f"❌ Odoo connection failed: {e}")
            return 1
        
        # Step 3: Create patient in Odoo
        logger.info("\n" + "=" * 80)
        patient_id = create_patient_in_odoo(odoo)
        if not patient_id:
            logger.error("Failed to create patient. Aborting.")
            return 1
        
        # Step 4: Create appointments
        logger.info("\n" + "=" * 80)
        appointments = create_appointments(odoo, patient_id)
        
        # Step 5: Create treatments
        logger.info("\n" + "=" * 80)
        treatments = create_treatments(odoo, patient_id)
        
        # Step 6: Create invoices
        logger.info("\n" + "=" * 80)
        invoices = create_invoices(odoo, patient_id)
        
        # Step 7: Create user-patient mapping
        logger.info("\n" + "=" * 80)
        mapping = create_user_patient_mapping(db, user.id, org.id, patient_id)
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("✅ Demo Data Population Complete!")
        logger.info("=" * 80)
        logger.info(f"Patient ID: {patient_id}")
        logger.info(f"Appointments: {len(appointments)}")
        logger.info(f"Treatments: {len(treatments)}")
        logger.info(f"Invoices: {len(invoices)}")
        logger.info(f"User-Patient Mapping: {'✅' if mapping else '❌'}")
        logger.info("=" * 80)
        
        return 0
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1
    
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
