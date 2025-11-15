#!/usr/bin/env python3
"""
Populate today's patient appointments in Odoo.

This script creates realistic patient.appointment records for today
to populate the "Today's Patients" widget in the dashboard.
"""

import xmlrpc.client
from datetime import datetime, timedelta
import random

# Odoo connection
url = "http://136.113.179.19:8069"
db = "dentalai_odoo"
username = "admin"
password = "DentaFlow2025Admin!"

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print(f"✅ Connected to Odoo (UID: {uid})")

# Step 1: Check if patient.patient model exists
try:
    patient_count = models.execute_kw(db, uid, password, 'patient.patient', 'search_count', [[]])
    print(f"✅ patient.patient model exists with {patient_count} records")
except Exception as e:
    print(f"❌ patient.patient model not found: {e}")
    print("Creating patient.patient records from res.partner...")
    
    # Get all res.partner records
    partners = models.execute_kw(db, uid, password, 'res.partner', 'search_read', 
        [[('is_company', '=', False)]], 
        {'fields': ['id', 'name'], 'limit': 20}
    )
    
    print(f"Found {len(partners)} partners to convert to patients")
    
    # Create patient.patient for each partner
    for partner in partners:
        try:
            patient_id = models.execute_kw(db, uid, password, 'patient.patient', 'create', [{
                'name': partner['name'],
                'partner_id': partner['id'],
            }])
            print(f"  ✅ Created patient {patient_id} for partner {partner['id']} ({partner['name']})")
        except Exception as e:
            print(f"  ❌ Failed to create patient for {partner['name']}: {e}")
    
    patient_count = models.execute_kw(db, uid, password, 'patient.patient', 'search_count', [[]])
    print(f"✅ Now have {patient_count} patient.patient records")

# Step 2: Get patient.patient records
patients = models.execute_kw(db, uid, password, 'patient.patient', 'search_read',
    [[]], 
    {'fields': ['id', 'patient_name', 'patient_serial'], 'limit': 15}
)

print(f"\n✅ Found {len(patients)} patients")

# Step 3: Get doctors (res.users with groups_id containing 'Dental / Doctor')
doctors = models.execute_kw(db, uid, password, 'res.users', 'search_read',
    [[('active', '=', True)]], 
    {'fields': ['id', 'name'], 'limit': 5}
)

print(f"✅ Found {len(doctors)} doctors")

# Step 4: Create appointments for today
today = datetime.now()
appointment_times = [
    (9, 0),   # 09:00
    (10, 0),  # 10:00
    (11, 30),  # 11:30
    (13, 0),  # 13:00
    (14, 30),  # 14:30
    (15, 30),  # 15:30
    (16, 0),  # 16:00
    (17, 0),  # 17:00
]

appointment_types = [
    'checkup',
    'cleaning',
    'filling',
    'root_canal',
    'extraction',
    'consultation',
]

states = ['draft', 'confirmed', 'confirmed', 'confirmed']  # More confirmed than draft

created_count = 0

for i, (hour, minute) in enumerate(appointment_times):
    if i >= len(patients):
        break
    
    patient = patients[i]
    doctor = random.choice(doctors)
    
    start_time = today.replace(hour=hour, minute=minute, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=30)
    
    appointment_data = {
        'patient_id': patient['id'],
        'doctor_id': doctor['id'],
        'start': start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'stop': end_time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': random.choice(states),
        'appointment_type': random.choice(appointment_types),
        'comments': f"Scheduled via DentaFlow AI - {random.choice(['Regular checkup', 'Follow-up visit', 'New patient consultation'])}",
    }
    
    try:
        appointment_id = models.execute_kw(db, uid, password, 'patient.appointment', 'create', [appointment_data])
        created_count += 1
        print(f"  ✅ Created appointment {appointment_id}: {patient['patient_name']} at {start_time.strftime('%H:%M')}")
    except Exception as e:
        print(f"  ❌ Failed to create appointment for {patient['patient_name']}: {e}")

print(f"\n🎉 Successfully created {created_count} appointments for today!")

# Step 5: Verify
today_str = today.strftime('%Y-%m-%d')
today_appointments = models.execute_kw(db, uid, password, 'patient.appointment', 'search_count', [[
    ('start', '>=', f"{today_str} 00:00:00"),
    ('start', '<=', f"{today_str} 23:59:59"),
]])

print(f"✅ Total appointments for today: {today_appointments}")
