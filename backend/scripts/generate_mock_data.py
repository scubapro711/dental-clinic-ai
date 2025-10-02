#!/usr/bin/env python3
"""
Generate Realistic Mock Data for Dental Clinic

Creates 1500+ patients with realistic:
- Patient profiles
- Appointment history
- Treatment records
- Invoices
- Medical notes
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from faker import Faker

# Initialize Faker for realistic data
fake = Faker(['en_US', 'he_IL'])


# Israeli first names and last names
ISRAELI_FIRST_NAMES = [
    "David", "Sarah", "Michael", "Rachel", "Daniel", "Leah", "Jonathan", "Rebecca",
    "Yosef", "Miriam", "Avi", "Tamar", "Eli", "Noa", "Moshe", "Shira", "Aaron", "Maya",
    "Benjamin", "Yael", "Isaac", "Rivka", "Jacob", "Esther", "Samuel", "Hannah",
    "Shlomo", "Dinah", "Chaim", "Ruth", "Uri", "Naomi", "Gideon", "Deborah",
]

ISRAELI_LAST_NAMES = [
    "Cohen", "Levi", "Mizrahi", "Peretz", "Biton", "Dahan", "Avraham", "Friedman",
    "Azoulay", "Katz", "Malka", "Ohayon", "Ben-David", "Gabay", "Eliyahu", "Amar",
    "Benaim", "Yosef", "Vaknin", "Aflalo", "Ohana", "Levy", "Shalom", "Amsalem",
]

TREATMENT_TYPES = [
    {"name": "Cleaning", "price_range": (300, 450), "duration": 60},
    {"name": "Filling", "price_range": (400, 800), "duration": 45},
    {"name": "Root Canal", "price_range": (1500, 2500), "duration": 90},
    {"name": "Crown", "price_range": (2000, 3500), "duration": 120},
    {"name": "Extraction", "price_range": (500, 1200), "duration": 30},
    {"name": "Whitening", "price_range": (800, 1500), "duration": 60},
    {"name": "Implant", "price_range": (5000, 8000), "duration": 180},
    {"name": "Braces Consultation", "price_range": (200, 400), "duration": 30},
    {"name": "X-Ray", "price_range": (150, 300), "duration": 15},
    {"name": "Emergency Visit", "price_range": (300, 600), "duration": 30},
]

DENTAL_NOTES = [
    "Patient reports sensitivity to cold",
    "No cavities detected",
    "Gum health is good",
    "Recommended fluoride treatment",
    "Patient has good oral hygiene",
    "Slight plaque buildup",
    "Wisdom teeth extraction recommended",
    "Patient wears night guard",
    "No allergies reported",
    "Previous root canal on tooth #14",
]


def generate_patient(patient_id: int) -> Dict[str, Any]:
    """Generate a realistic patient profile."""
    is_israeli = random.random() < 0.7  # 70% Israeli names
    
    if is_israeli:
        first_name = random.choice(ISRAELI_FIRST_NAMES)
        last_name = random.choice(ISRAELI_LAST_NAMES)
    else:
        first_name = fake.first_name()
        last_name = fake.last_name()
    
    # Generate realistic phone number
    phone_prefix = random.choice(["+97250", "+97252", "+97254", "+97258"])
    phone = f"{phone_prefix}{random.randint(1000000, 9999999)}"
    
    # Email
    email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(['gmail.com', 'yahoo.com', 'walla.co.il', 'hotmail.com'])}"
    
    # Birth date (18-80 years old)
    age = random.randint(18, 80)
    birth_date = datetime.now() - timedelta(days=age*365)
    
    # Registration date (within last 5 years)
    registration_date = datetime.now() - timedelta(days=random.randint(0, 1825))
    
    return {
        "id": patient_id,
        "name": f"{first_name} {last_name}",
        "email": email,
        "phone": phone,
        "birth_date": birth_date.strftime("%Y-%m-%d"),
        "registration_date": registration_date.strftime("%Y-%m-%d"),
        "address": fake.address().replace("\n", ", "),
        "insurance_provider": random.choice(["Clalit", "Maccabi", "Meuhedet", "Leumit", "None"]),
        "insurance_number": f"IL{random.randint(100000000, 999999999)}" if random.random() < 0.8 else None,
        "emergency_contact": phone_prefix.replace("50", "52") + str(random.randint(1000000, 9999999)),
        "allergies": random.choice(["None", "Penicillin", "Latex", "Lidocaine", "None", "None"]),
        "medical_conditions": random.choice(["None", "Diabetes", "Hypertension", "None", "None", "None"]),
        "last_visit": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
        "total_visits": random.randint(1, 50),
        "outstanding_balance": random.choice([0, 0, 0, 0, random.randint(100, 2000)]),  # 80% have no balance
    }


def generate_appointment(appointment_id: int, patient_id: int, patient_name: str) -> Dict[str, Any]:
    """Generate a realistic appointment."""
    treatment = random.choice(TREATMENT_TYPES)
    
    # Mix of past and future appointments
    is_past = random.random() < 0.7  # 70% past, 30% future
    
    if is_past:
        # Past appointment (within last year)
        days_ago = random.randint(1, 365)
        appointment_date = datetime.now() - timedelta(days=days_ago)
        status = random.choice(["completed", "completed", "completed", "cancelled", "no-show"])
    else:
        # Future appointment (within next 60 days)
        days_ahead = random.randint(1, 60)
        appointment_date = datetime.now() + timedelta(days=days_ahead)
        status = "scheduled"
    
    # Appointment time (8 AM - 6 PM)
    hour = random.randint(8, 17)
    minute = random.choice([0, 15, 30, 45])
    appointment_datetime = appointment_date.replace(hour=hour, minute=minute)
    
    return {
        "id": appointment_id,
        "patient_id": patient_id,
        "patient_name": patient_name,
        "date": appointment_datetime.strftime("%Y-%m-%d"),
        "time": appointment_datetime.strftime("%H:%M"),
        "datetime": appointment_datetime.isoformat(),
        "treatment_type": treatment["name"],
        "duration_minutes": treatment["duration"],
        "dentist": random.choice(["Dr. Smith", "Dr. Cohen", "Dr. Levi"]),
        "status": status,
        "notes": random.choice(DENTAL_NOTES) if status == "completed" else "",
        "created_at": (appointment_datetime - timedelta(days=random.randint(1, 30))).isoformat(),
    }


def generate_invoice(invoice_id: int, patient_id: int, patient_name: str, appointment_id: int) -> Dict[str, Any]:
    """Generate a realistic invoice."""
    treatment = random.choice(TREATMENT_TYPES)
    base_price = random.randint(*treatment["price_range"])
    
    # Insurance coverage (0-80%)
    insurance_coverage = random.choice([0, 0, 0.5, 0.6, 0.7, 0.8])
    insurance_amount = int(base_price * insurance_coverage)
    patient_amount = base_price - insurance_amount
    
    # Payment status
    is_paid = random.random() < 0.85  # 85% paid
    paid_amount = patient_amount if is_paid else random.randint(0, patient_amount)
    
    issue_date = datetime.now() - timedelta(days=random.randint(1, 365))
    due_date = issue_date + timedelta(days=30)
    
    return {
        "id": invoice_id,
        "patient_id": patient_id,
        "patient_name": patient_name,
        "appointment_id": appointment_id,
        "issue_date": issue_date.strftime("%Y-%m-%d"),
        "due_date": due_date.strftime("%Y-%m-%d"),
        "treatment": treatment["name"],
        "total_amount": base_price,
        "insurance_amount": insurance_amount,
        "patient_amount": patient_amount,
        "paid_amount": paid_amount,
        "outstanding_amount": patient_amount - paid_amount,
        "status": "paid" if paid_amount >= patient_amount else "partial" if paid_amount > 0 else "unpaid",
        "payment_method": random.choice(["Credit Card", "Cash", "Bank Transfer", "Check"]) if paid_amount > 0 else None,
        "invoice_number": f"INV-{issue_date.year}-{invoice_id:05d}",
    }


def generate_treatment_record(record_id: int, patient_id: int, appointment_id: int) -> Dict[str, Any]:
    """Generate a treatment record."""
    treatment = random.choice(TREATMENT_TYPES)
    treatment_date = datetime.now() - timedelta(days=random.randint(1, 730))
    
    return {
        "id": record_id,
        "patient_id": patient_id,
        "appointment_id": appointment_id,
        "date": treatment_date.strftime("%Y-%m-%d"),
        "treatment_type": treatment["name"],
        "tooth_number": random.choice([None, f"#{random.randint(1, 32)}"]),
        "diagnosis": random.choice([
            "Dental caries", "Gingivitis", "Periodontitis", "Tooth sensitivity",
            "Tooth fracture", "Tooth abscess", "Routine checkup", "Preventive care"
        ]),
        "procedure_notes": random.choice(DENTAL_NOTES),
        "dentist": random.choice(["Dr. Smith", "Dr. Cohen", "Dr. Levi"]),
        "follow_up_required": random.choice([True, False, False, False]),
        "follow_up_date": (treatment_date + timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d") if random.random() < 0.3 else None,
    }


def main():
    """Generate all mock data."""
    print("🏥 Generating Mock Data for Dental Clinic AI")
    print("=" * 60)
    
    NUM_PATIENTS = 1500
    APPOINTMENTS_PER_PATIENT = (1, 15)  # Range of appointments per patient
    
    patients = []
    appointments = []
    invoices = []
    treatment_records = []
    
    appointment_id = 1
    invoice_id = 1
    record_id = 1
    
    print(f"\n📊 Generating {NUM_PATIENTS} patients...")
    for patient_id in range(1, NUM_PATIENTS + 1):
        if patient_id % 100 == 0:
            print(f"   Generated {patient_id}/{NUM_PATIENTS} patients...")
        
        # Generate patient
        patient = generate_patient(patient_id)
        patients.append(patient)
        
        # Generate appointments for this patient
        num_appointments = random.randint(*APPOINTMENTS_PER_PATIENT)
        for _ in range(num_appointments):
            appointment = generate_appointment(appointment_id, patient_id, patient["name"])
            appointments.append(appointment)
            
            # Generate invoice for completed appointments
            if appointment["status"] == "completed":
                invoice = generate_invoice(invoice_id, patient_id, patient["name"], appointment_id)
                invoices.append(invoice)
                invoice_id += 1
                
                # Generate treatment record
                record = generate_treatment_record(record_id, patient_id, appointment_id)
                treatment_records.append(record)
                record_id += 1
            
            appointment_id += 1
    
    print(f"\n✅ Generated:")
    print(f"   - {len(patients)} patients")
    print(f"   - {len(appointments)} appointments")
    print(f"   - {len(invoices)} invoices")
    print(f"   - {len(treatment_records)} treatment records")
    
    # Save to JSON files
    print(f"\n💾 Saving data to files...")
    
    with open('/home/ubuntu/dental-clinic-ai-repo/backend/data/mock_patients.json', 'w', encoding='utf-8') as f:
        json.dump(patients, f, indent=2, ensure_ascii=False)
    
    with open('/home/ubuntu/dental-clinic-ai-repo/backend/data/mock_appointments.json', 'w', encoding='utf-8') as f:
        json.dump(appointments, f, indent=2, ensure_ascii=False)
    
    with open('/home/ubuntu/dental-clinic-ai-repo/backend/data/mock_invoices.json', 'w', encoding='utf-8') as f:
        json.dump(invoices, f, indent=2, ensure_ascii=False)
    
    with open('/home/ubuntu/dental-clinic-ai-repo/backend/data/mock_treatment_records.json', 'w', encoding='utf-8') as f:
        json.dump(treatment_records, f, indent=2, ensure_ascii=False)
    
    # Generate statistics
    print(f"\n📈 Statistics:")
    print(f"   - Total revenue: ₪{sum(inv['total_amount'] for inv in invoices):,}")
    print(f"   - Outstanding balance: ₪{sum(inv['outstanding_amount'] for inv in invoices):,}")
    print(f"   - Average visits per patient: {len(appointments) / len(patients):.1f}")
    print(f"   - Completion rate: {len([a for a in appointments if a['status'] == 'completed']) / len(appointments) * 100:.1f}%")
    
    print(f"\n🎉 Mock data generation complete!")
    print(f"   Files saved to: backend/data/")


if __name__ == "__main__":
    main()
