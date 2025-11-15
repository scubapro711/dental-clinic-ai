import xmlrpc.client
from datetime import datetime, timedelta
import random

url = "http://136.113.179.19:8069"
db = "dentalai_odoo"
username = "admin"
password = "DentaFlow2025Admin!"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
print(f"✓ Authenticated as UID: {uid}")

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Get patients (res.partner)
patient_ids = models.execute_kw(db, uid, password, 'res.partner', 'search', [[('is_patient', '=', True)]], {'limit': 50})
print(f"\n✓ Found {len(patient_ids)} patients")

# Get doctors (hr.employee)
doctor_ids = models.execute_kw(db, uid, password, 'hr.employee', 'search', [[('job_title', 'ilike', 'Dentist')]], {'limit': 10})
print(f"✓ Found {len(doctor_ids)} doctors")

# Get today's date
today = datetime.now().date()

# Create 5 appointments for today
for i in range(5):
    patient_id = random.choice(patient_ids)
    doctor_id = random.choice(doctor_ids)
    start_time = datetime(today.year, today.month, today.day, 9 + i, 0, 0)
    end_time = start_time + timedelta(minutes=45)
    
    appointment_vals = {
        'patient_id': patient_id,
        'doctor_id': doctor_id,
        'start': start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'stop': end_time.strftime('%Y-%m-%d %H:%M:%S'),
        'duration': 0.75,
        'allday': False,
        'state': 'confirmed',
        'appointment_type': 'checkup',
    }
    
    try:
        appointment_id = models.execute_kw(db, uid, password, 'patient.appointment', 'create', [appointment_vals])
        print(f"  - Created appointment {appointment_id} for patient {patient_id} at {start_time.strftime('%H:%M')}")
    except Exception as e:
        print(f"  - ✗ Error creating appointment: {e}")

print("\n✓ Finished creating today's appointments!")
