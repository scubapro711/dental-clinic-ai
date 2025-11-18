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

# Step 1: Get patient.patient records
patients = models.execute_kw(db, uid, password, 'patient.patient', 'search_read',
    [[]], 
    {'fields': ['id', 'patient_name', 'patient_serial', 'contact_number'], 'limit': 15}
)

print(f"✅ Found {len(patients)} patients")

# Step 2: Get next appointment serial number
existing_appointments = models.execute_kw(db, uid, password, 'patient.appointment', 'search_read',
    [[]], 
    {'fields': ['appointment_serial'], 'order': 'id desc', 'limit': 1}
)

if existing_appointments:
    last_serial = existing_appointments[0]['appointment_serial']
    # Extract number from APT000001
    last_num = int(last_serial.replace('APT', ''))
    next_num = last_num + 1
else:
    next_num = 1

print(f"✅ Next appointment serial: APT{next_num:06d}")

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
    'reserve',
    'in_person',
]

appointment_statuses = [
    'draft',
    'confirm',
    'confirm',  # More confirmed
    'in_exam',
]

chief_complaints = [
    'Regular dental checkup',
    'Tooth pain in upper right molar',
    'Cleaning and scaling',
    'Follow-up visit for filling',
    'Sensitivity to cold',
    'Gum bleeding',
    'Crown adjustment needed',
    'New patient consultation',
]

created_count = 0

for i, (hour, minute) in enumerate(appointment_times):
    if i >= len(patients):
        break
    
    patient = patients[i]
    
    start_time = today.replace(hour=hour, minute=minute, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=30)
    duration = 0.5  # 0.5 hours
    
    appointment_data = {
        'appointment_serial': f'APT{next_num + i:06d}',
        'patient_id': patient['id'],
        'start': start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'stop': end_time.strftime('%Y-%m-%d %H:%M:%S'),
        'duration': duration,
        'appointment_status': random.choice(appointment_statuses),
        'appointment_type': random.choice(appointment_types),
        'chief_complaints': random.choice(chief_complaints),
        'contact_number': patient.get('contact_number') or '+972-50-000-0000',
    }
    
    try:
        appointment_id = models.execute_kw(db, uid, password, 'patient.appointment', 'create', [appointment_data])
        created_count += 1
        print(f"  ✅ Created appointment {appointment_data['appointment_serial']}: {patient['patient_name']} at {start_time.strftime('%H:%M')}")
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
