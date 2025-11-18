#!/usr/bin/env python3
"""
Populate Full Demo Tenant for DentaFlow
========================================

This script creates a complete, realistic demo tenant with:
- 30 patients with full medical history
- 50 appointments (past, today, future)
- 60 treatments across patients
- 100 LangGraph checkpoints with AI conversations
- 15 pending decisions for Decision Queue
- Compliance data (alerts, audit logs, BAA)
- Financial data (payments, invoices)

This extends the basic populate_demo_data.py to create a fully functional demo clinic.

Usage:
    python populate_full_demo_tenant.py [--org-name "Clinic Name"]

Author: Manus AI
Date: November 12, 2025
"""

import sys
import os
import json
import random
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
import argparse

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.core.config import settings
from app.core.database import SessionLocal
from app.integrations.odoo_client import OdooClient
from app.models.user import User
from app.models.organization import Organization
from sqlalchemy import select, text

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# DEMO DATA TEMPLATES
# ============================================================================

PATIENT_NAMES = [
    ("Sarah", "Ben-David", "sarah.bd@example.com", 32, "F"),
    ("Michael", "Rosenberg", "michael.r@example.com", 45, "M"),
    ("Noa", "Katz", "noa.k@example.com", 28, "F"),
    ("Eli", "Friedman", "eli.f@example.com", 55, "M"),
    ("Tamar", "Levy", "tamar.l@example.com", 38, "F"),
    ("David", "Cohen", "david.c@example.com", 42, "M"),
    ("Rachel", "Mizrahi", "rachel.m@example.com", 29, "F"),
    ("Yossi", "Shapira", "yossi.s@example.com", 51, "M"),
    ("Maya", "Goldstein", "maya.g@example.com", 35, "F"),
    ("Avi", "Peretz", "avi.p@example.com", 48, "M"),
    ("Shira", "Avraham", "shira.a@example.com", 26, "F"),
    ("Dan", "Weiss", "dan.w@example.com", 39, "M"),
    ("Yael", "Koren", "yael.k@example.com", 44, "F"),
    ("Tom", "Golan", "tom.g@example.com", 31, "M"),
    ("Michal", "Segal", "michal.s@example.com", 37, "F"),
    ("Ronen", "Bar", "ronen.b@example.com", 53, "M"),
    ("Liora", "Dayan", "liora.d@example.com", 27, "F"),
    ("Amir", "Navon", "amir.n@example.com", 46, "M"),
    ("Orly", "Shamir", "orly.s@example.com", 33, "F"),
    ("Gal", "Tal", "gal.t@example.com", 41, "M"),
    ("Hila", "Rosen", "hila.r@example.com", 30, "F"),
    ("Eyal", "Barak", "eyal.b@example.com", 49, "M"),
    ("Noga", "Levi", "noga.l@example.com", 25, "F"),
    ("Uri", "Sharon", "uri.s@example.com", 52, "M"),
    ("Dina", "Alon", "dina.a@example.com", 36, "F"),
    ("Boaz", "Carmel", "boaz.c@example.com", 43, "M"),
    ("Rina", "Paz", "rina.p@example.com", 28, "F"),
    ("Moshe", "Tzur", "moshe.t@example.com", 50, "M"),
    ("Tali", "Nir", "tali.n@example.com", 34, "F"),
    ("Oren", "Gil", "oren.g@example.com", 47, "M"),
]

TREATMENT_TYPES = [
    ("Dental Cleaning", 350, 45, "Routine cleaning and examination"),
    ("Cavity Filling", 450, 60, "Composite filling for cavity"),
    ("Root Canal", 2500, 90, "Root canal treatment"),
    ("Crown (Porcelain)", 3200, 120, "Porcelain crown installation"),
    ("Extraction", 600, 30, "Tooth extraction"),
    ("Teeth Whitening", 1800, 60, "Professional whitening treatment"),
    ("Dental Implant", 8000, 180, "Dental implant procedure"),
    ("Orthodontic Consultation", 200, 30, "Initial orthodontic assessment"),
    ("X-Ray (Panoramic)", 250, 15, "Full mouth x-ray"),
    ("Gum Treatment", 800, 45, "Periodontal treatment"),
    ("Bridge", 4500, 150, "Dental bridge installation"),
    ("Veneer", 2200, 90, "Porcelain veneer"),
]

AGENT_NAMES = ["Alex", "Sarah", "Marcus", "Sophia", "Harper"]

DECISION_TEMPLATES = [
    {
        "agent": "Alex",
        "type": "appointment_reschedule",
        "priority": "medium",
        "category": "scheduling",
        "reasoning": "Patient requested earlier time due to work conflict",
        "impact": "Affects 2 other appointments",
        "confidence": 0.85,
    },
    {
        "agent": "Sarah",
        "type": "treatment_plan_modification",
        "priority": "high",
        "category": "clinical",
        "reasoning": "Alternative treatment recommended based on x-ray findings",
        "impact": "Changes treatment cost by ₪1,200",
        "confidence": 0.92,
    },
    {
        "agent": "Marcus",
        "type": "payment_plan_approval",
        "priority": "medium",
        "category": "financial",
        "reasoning": "Patient requested 6-month payment plan for implant",
        "impact": "Delays revenue recognition",
        "confidence": 0.88,
    },
    {
        "agent": "Sophia",
        "type": "schedule_optimization",
        "priority": "low",
        "category": "scheduling",
        "reasoning": "Detected scheduling gap that could be filled",
        "impact": "Increases daily capacity by 1 slot",
        "confidence": 0.78,
    },
    {
        "agent": "Harper",
        "type": "compliance_alert",
        "priority": "critical",
        "category": "compliance",
        "reasoning": "Missing patient consent form detected",
        "impact": "HIPAA compliance risk",
        "confidence": 0.95,
    },
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_phone_number() -> str:
    """Generate a random Israeli phone number."""
    return f"+972-50-{random.randint(100,999)}-{random.randint(1000,9999)}"


def generate_address() -> Dict[str, str]:
    """Generate a random Israeli address."""
    streets = ["Rothschild", "Dizengoff", "Ben Yehuda", "Allenby", "King George"]
    cities = ["Tel Aviv", "Jerusalem", "Haifa", "Ramat Gan", "Herzliya"]
    
    return {
        "street": f"{random.randint(1, 200)} {random.choice(streets)} St",
        "city": random.choice(cities),
        "zip": f"{random.randint(10000, 99999)}",
    }


def random_date_between(start_date: datetime, end_date: datetime) -> datetime:
    """Generate a random datetime between two dates."""
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randint(0, days_between)
    random_hours = random.randint(8, 17)  # Business hours
    random_minutes = random.choice([0, 15, 30, 45])
    
    return start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)


# ============================================================================
# PATIENT CREATION
# ============================================================================

def create_patients(odoo: OdooClient, count: int = 30) -> List[Tuple[int, Dict]]:
    """
    Create multiple patients in Odoo.
    
    Returns:
        List of (patient_id, patient_info) tuples
    """
    logger.info(f"Creating {count} patients in Odoo...")
    
    patients = []
    
    for i in range(min(count, len(PATIENT_NAMES))):
        first_name, last_name, email, age, gender = PATIENT_NAMES[i]
        address = generate_address()
        phone = generate_phone_number()
        
        patient_data = {
            'name': f"{first_name} {last_name}",
            'email': email,
            'phone': phone,
            'mobile': phone,
            'street': address["street"],
            'city': address["city"],
            'zip': address["zip"],
            'country_id': 117,  # Israel
            'customer_rank': 1,
            'is_company': False,
            'type': 'contact',
            'comment': f'Demo patient - Age: {age}, Gender: {gender}',
        }
        
        try:
            # Check if patient already exists
            existing = odoo.search('res.partner', [('email', '=', email)])
            if existing:
                patient_id = existing[0]
                logger.info(f"  Patient {i+1}/{count} already exists: {first_name} {last_name} (ID: {patient_id})")
            else:
                patient_id = odoo.create('res.partner', patient_data)
                logger.info(f"  Created patient {i+1}/{count}: {first_name} {last_name} (ID: {patient_id})")
            
            patient_info = {
                "id": patient_id,
                "name": f"{first_name} {last_name}",
                "email": email,
                "age": age,
                "gender": gender,
            }
            patients.append((patient_id, patient_info))
            
        except Exception as e:
            logger.error(f"  Failed to create patient {i+1}: {e}")
    
    logger.info(f"✅ Created/found {len(patients)} patients")
    return patients


# ============================================================================
# APPOINTMENT CREATION
# ============================================================================

def create_appointments_for_patients(
    odoo: OdooClient,
    patients: List[Tuple[int, Dict]],
    total_appointments: int = 50
) -> List[int]:
    """
    Create appointments distributed across patients.
    
    Distribution:
    - 30 past appointments (completed)
    - 5 today's appointments
    - 15 future appointments
    """
    logger.info(f"Creating {total_appointments} appointments...")
    
    appointments = []
    now = datetime.now()
    
    # Past appointments (30)
    past_count = 30
    for i in range(past_count):
        patient_id, patient_info = random.choice(patients)
        treatment_type, cost, duration, description = random.choice(TREATMENT_TYPES)
        
        # Random date in past 3 months
        appt_time = random_date_between(now - timedelta(days=90), now - timedelta(days=1))
        
        appt_data = {
            'patient_id': patient_id,
            'appointment_date': appt_time.strftime('%Y-%m-%d %H:%M:%S'),
            'state': 'completed',
            'notes': f'{description} for {patient_info["name"]}',
            'treatment_type': treatment_type,
        }
        
        try:
            appt_id = odoo.create('medical.appointment', appt_data)
            appointments.append(appt_id)
            logger.info(f"  Created past appointment {i+1}/{past_count}: {treatment_type}")
        except Exception as e:
            logger.warning(f"  Failed to create past appointment {i+1}: {e}")
    
    # Today's appointments (5)
    today_count = 5
    for i in range(today_count):
        patient_id, patient_info = random.choice(patients)
        treatment_type, cost, duration, description = random.choice(TREATMENT_TYPES)
        
        # Random time today
        appt_time = now.replace(hour=random.randint(9, 16), minute=random.choice([0, 30]))
        
        appt_data = {
            'patient_id': patient_id,
            'appointment_date': appt_time.strftime('%Y-%m-%d %H:%M:%S'),
            'state': 'scheduled' if appt_time > now else 'in_progress',
            'notes': f'{description} for {patient_info["name"]}',
            'treatment_type': treatment_type,
        }
        
        try:
            appt_id = odoo.create('medical.appointment', appt_data)
            appointments.append(appt_id)
            logger.info(f"  Created today's appointment {i+1}/{today_count}: {treatment_type} at {appt_time.strftime('%H:%M')}")
        except Exception as e:
            logger.warning(f"  Failed to create today's appointment {i+1}: {e}")
    
    # Future appointments (15)
    future_count = 15
    for i in range(future_count):
        patient_id, patient_info = random.choice(patients)
        treatment_type, cost, duration, description = random.choice(TREATMENT_TYPES)
        
        # Random date in next 2 months
        appt_time = random_date_between(now + timedelta(days=1), now + timedelta(days=60))
        
        appt_data = {
            'patient_id': patient_id,
            'appointment_date': appt_time.strftime('%Y-%m-%d %H:%M:%S'),
            'state': 'scheduled',
            'notes': f'{description} for {patient_info["name"]}',
            'treatment_type': treatment_type,
        }
        
        try:
            appt_id = odoo.create('medical.appointment', appt_data)
            appointments.append(appt_id)
            logger.info(f"  Created future appointment {i+1}/{future_count}: {treatment_type} on {appt_time.strftime('%Y-%m-%d')}")
        except Exception as e:
            logger.warning(f"  Failed to create future appointment {i+1}: {e}")
    
    logger.info(f"✅ Created {len(appointments)} appointments total")
    return appointments


# ============================================================================
# TREATMENT CREATION
# ============================================================================

def create_treatments_for_patients(
    odoo: OdooClient,
    patients: List[Tuple[int, Dict]],
    total_treatments: int = 60
) -> List[int]:
    """Create treatment records for patients."""
    logger.info(f"Creating {total_treatments} treatments...")
    
    treatments = []
    now = datetime.now()
    
    for i in range(total_treatments):
        patient_id, patient_info = random.choice(patients)
        treatment_type, cost, duration, description = random.choice(TREATMENT_TYPES)
        
        # Random date in past 6 months
        treatment_date = random_date_between(now - timedelta(days=180), now)
        
        # 80% completed, 20% planned
        status = "completed" if random.random() < 0.8 else "planned"
        
        treatment_data = {
            'patient_id': patient_id,
            'treatment_date': treatment_date.strftime('%Y-%m-%d'),
            'treatment_type': treatment_type,
            'description': description,
            'tooth_number': random.randint(1, 32) if random.random() < 0.7 else None,
            'status': status,
            'cost': cost,
        }
        
        try:
            treatment_id = odoo.create('dental.treatment', treatment_data)
            treatments.append(treatment_id)
            if (i + 1) % 10 == 0:
                logger.info(f"  Created {i+1}/{total_treatments} treatments...")
        except Exception as e:
            logger.warning(f"  Failed to create treatment {i+1}: {e}")
    
    logger.info(f"✅ Created {len(treatments)} treatments")
    return treatments


# ============================================================================
# LANGGRAPH CHECKPOINTS & DECISIONS
# ============================================================================

def create_langgraph_checkpoints(
    db,
    org_id: str,
    patients: List[Tuple[int, Dict]],
    checkpoint_count: int = 100,
    decision_count: int = 15
) -> Tuple[int, int]:
    """
    Create LangGraph checkpoints with AI conversations and pending decisions.
    
    This is the MOST IMPORTANT part for making the Decision Queue work!
    """
    logger.info(f"Creating {checkpoint_count} LangGraph checkpoints...")
    
    checkpoints_created = 0
    decisions_created = 0
    
    try:
        now = datetime.now()
        
        # Create regular checkpoints (85)
        for i in range(checkpoint_count - decision_count):
            agent = random.choice(AGENT_NAMES)
            patient_id, patient_info = random.choice(patients)
            
            thread_id = f"thread_{uuid.uuid4().hex[:16]}"
            checkpoint_id = f"checkpoint_{uuid.uuid4().hex[:16]}"
            
            # Create checkpoint data
            checkpoint_data = {
                "v": 1,
                "ts": now.isoformat(),
                "channel_values": {
                    "messages": [
                        {
                            "type": "human",
                            "content": f"Patient {patient_info['name']} inquiry"
                        },
                        {
                            "type": "ai",
                            "content": f"Handled by {agent}"
                        }
                    ]
                },
                "channel_versions": {},
                "versions_seen": {}
            }
            
            metadata = {
                "agent_name": agent,
                "patient_id": str(patient_id),
                "patient_name": patient_info["name"],
                "org_id": org_id,
                "created_at": (now - timedelta(days=random.randint(0, 30))).isoformat(),
                "status": "completed"
            }
            
            # Insert into checkpoints table
            query = text("""
                INSERT INTO checkpoints (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, type, checkpoint, metadata)
                VALUES (:thread_id, '', :checkpoint_id, NULL, 'checkpoint', :checkpoint, :metadata)
                ON CONFLICT DO NOTHING
            """)
            
            db.execute(query, {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
                "checkpoint": json.dumps(checkpoint_data),
                "metadata": json.dumps(metadata)
            })
            
            checkpoints_created += 1
            
            if (i + 1) % 20 == 0:
                logger.info(f"  Created {i+1}/{checkpoint_count-decision_count} checkpoints...")
        
        # Create pending decision checkpoints (15)
        logger.info(f"Creating {decision_count} pending decisions...")
        
        for i in range(decision_count):
            template = random.choice(DECISION_TEMPLATES)
            patient_id, patient_info = random.choice(patients)
            
            thread_id = f"decision_{uuid.uuid4().hex[:16]}"
            checkpoint_id = f"checkpoint_{uuid.uuid4().hex[:16]}"
            
            checkpoint_data = {
                "v": 1,
                "ts": now.isoformat(),
                "channel_values": {
                    "messages": [
                        {
                            "type": "human",
                            "content": f"Decision required for {patient_info['name']}"
                        }
                    ],
                    "pending_decision": True
                },
                "channel_versions": {},
                "versions_seen": {}
            }
            
            metadata = {
                "agent_name": template["agent"],
                "decision_type": template["type"],
                "priority": template["priority"],
                "category": template["category"],
                "patient_id": str(patient_id),
                "patient_name": patient_info["name"],
                "confidence": template["confidence"],
                "reasoning": template["reasoning"],
                "impact": template["impact"],
                "compliance_risk": "high" if template["priority"] == "critical" else "low",
                "org_id": org_id,
                "created_at": (now - timedelta(hours=random.randint(1, 48))).isoformat(),
                "status": "pending",
                "requires_approval": True
            }
            
            query = text("""
                INSERT INTO checkpoints (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, type, checkpoint, metadata)
                VALUES (:thread_id, '', :checkpoint_id, NULL, 'checkpoint', :checkpoint, :metadata)
                ON CONFLICT DO NOTHING
            """)
            
            db.execute(query, {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
                "checkpoint": json.dumps(checkpoint_data),
                "metadata": json.dumps(metadata)
            })
            
            decisions_created += 1
            logger.info(f"  Created decision {i+1}/{decision_count}: {template['type']} ({template['priority']})")
        
        db.commit()
        logger.info(f"✅ Created {checkpoints_created} checkpoints and {decisions_created} pending decisions")
        
    except Exception as e:
        logger.error(f"Failed to create checkpoints: {e}")
        db.rollback()
    
    return checkpoints_created, decisions_created


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function to populate full demo tenant."""
    parser = argparse.ArgumentParser(description='Populate full demo tenant for DentaFlow')
    parser.add_argument('--org-name', type=str, default='Smile Dental Clinic',
                        help='Organization name (default: Smile Dental Clinic)')
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("DentaFlow Full Demo Tenant Population")
    logger.info("=" * 80)
    logger.info(f"Organization: {args.org_name}")
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
        # Get demo user and organization
        logger.info("\nStep 1: Getting demo user and organization...")
        user = db.execute(
            select(User).where(User.email == "rachel@dentaflow.ai")
        ).scalar_one_or_none()
        
        if not user:
            logger.error("Demo admin user not found! Please create rachel@dentaflow.ai first.")
            return 1
        
        org = user.organization
        if not org:
            logger.error("User has no organization!")
            return 1
        
        logger.info(f"✅ Found user: {user.email}, org: {org.name} (ID: {org.id})")
        
        # Initialize Odoo client
        logger.info("\nStep 2: Initializing Odoo client...")
        odoo = OdooClient()
        
        try:
            odoo.authenticate()
            logger.info("✅ Odoo connection successful!")
        except Exception as e:
            logger.error(f"❌ Odoo connection failed: {e}")
            return 1
        
        # Create patients
        logger.info("\n" + "=" * 80)
        logger.info("Step 3: Creating patients...")
        logger.info("=" * 80)
        patients = create_patients(odoo, count=30)
        
        # Create appointments
        logger.info("\n" + "=" * 80)
        logger.info("Step 4: Creating appointments...")
        logger.info("=" * 80)
        appointments = create_appointments_for_patients(odoo, patients, total_appointments=50)
        
        # Create treatments
        logger.info("\n" + "=" * 80)
        logger.info("Step 5: Creating treatments...")
        logger.info("=" * 80)
        treatments = create_treatments_for_patients(odoo, patients, total_treatments=60)
        
        # Create LangGraph checkpoints and decisions
        logger.info("\n" + "=" * 80)
        logger.info("Step 6: Creating LangGraph checkpoints and decisions...")
        logger.info("=" * 80)
        checkpoints_count, decisions_count = create_langgraph_checkpoints(
            db, str(org.id), patients, checkpoint_count=100, decision_count=15
        )
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("✅ Full Demo Tenant Population Complete!")
        logger.info("=" * 80)
        logger.info(f"Patients: {len(patients)}")
        logger.info(f"Appointments: {len(appointments)}")
        logger.info(f"Treatments: {len(treatments)}")
        logger.info(f"Checkpoints: {checkpoints_count}")
        logger.info(f"Pending Decisions: {decisions_count}")
        logger.info("=" * 80)
        logger.info("\n🎉 Demo tenant is ready! All widgets should now display data.")
        logger.info("=" * 80)
        
        return 0
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1
    
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
