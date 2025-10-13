# Odoo System Architecture - DentaFlow

**תאריך:** 13 אוקטובר 2025  
**גרסה:** 1.0  
**סטטוס:** ✅ Verified with Live System

---

## 🎯 Executive Summary

מסמך זה מתעד את הארכיטקטורה המלאה של מערכת Odoo Dental שלנו, מבוסס על ניתוח מעמיק של המערכת החיה.

**Key Findings:**
- ✅ Odoo 16.0 (server_version: 16.0-20241007)
- ✅ Pragtech Dental Management v19.0.0.2
- 🔴 **אין קשר ישיר בין `patient.patient` ל-`res.partner`!**
- ✅ 4 מודלים ראשיים: patient.patient, patient.appointment, patient.prescription, res.partner

---

## 📦 System Information

### Odoo Version
```json
{
  "server_version": "16.0-20241007",
  "server_serie": "16.0",
  "protocol_version": 1
}
```

### Installed Dental Module
```
Module: dental_clinic
Description: Pragtech Dental Management
Author: Pragmatic TechSoft Pvt. Ltd.
Version: 19.0.0.2
License: OPL-1 (Odoo Proprietary License)
Price: $499 USD (one-time purchase)
```

---

## 🗂️ Data Models

### 1. patient.patient (8 records)

**Purpose:** Core patient record with medical information

#### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `patient_serial` | char | Patient ID (e.g., PAT000001) - **REQUIRED!** |

#### Key Optional Fields
| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `patient_name` | char | - | Full name |
| `contact_number` | char | - | Phone number |
| `date_of_birth` | date | YYYY-MM-DD | Date of birth |
| `gender` | selection | male, female, other | Gender |
| `blood_type` | selection | a+, a-, b+, b-, o+, o-, ab+, ab- | Blood type |
| `marital_status` | selection | single, married, divorced, widowed | Marital status |
| `occupation` | char | - | Occupation |
| `age` | char | - | Auto-calculated from DOB |
| `qstn_1` | selection | yes, no | Medical question 1 |
| `qstn_1_note` | char | - | Notes for question 1 |
| `qstn_2` | selection | yes, no | Medical question 2 |
| `qstn_2_note` | char | - | Notes for question 2 |

#### Relations
| Field | Type | Target Model | Description |
|-------|------|--------------|-------------|
| `appointment_id` | one2many | patient.appointment | Patient's appointments |
| `patient_prescriptions` | one2many | patient.prescription | Patient's prescriptions |

#### Sample Record
```python
{
    'id': 1,
    'patient_serial': 'PAT000001',
    'patient_name': 'John Smith',
    'contact_number': '+972-50-123-4567',
    'date_of_birth': '1985-03-15',
    'age': '40.0Years Old',
    'gender': 'male',
    'blood_type': 'a+',
    'marital_status': 'married',
    'occupation': 'Software Engineer',
    'appointment_id': [1, 2],
    'patient_prescriptions': [1]
}
```

---

### 2. res.partner (9 records)

**Purpose:** Odoo standard contact/partner record

#### Key Fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | char | Contact name |
| `phone` | char | Phone number |
| `mobile` | char | Mobile number |
| `email` | char | Email address |
| `street` | char | Street address |
| `city` | char | City |
| `zip` | char | Postal code |
| `country_id` | many2one | Country |
| `is_patient` | boolean | Mark as patient |
| `is_company` | boolean | Is a company |
| `company_id` | many2one | Related company |

#### 🔴 Critical Finding
**There is NO direct relationship between `patient.patient` and `res.partner`!**

- No `partner_id` field in `patient.patient`
- No `patient_id` field in `res.partner`
- They are **separate, independent models**
- Must be linked manually (e.g., by phone number or email)

---

### 3. patient.appointment (18 records)

**Purpose:** Patient appointments and scheduling

#### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `appointment_serial` | char | Appointment ID (e.g., APT000001) |
| `start` | datetime | Start time |
| `stop` | datetime | End time |

#### Key Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | char | Meeting subject |
| `contact_number` | char | Contact number |
| `appointment_type` | selection | Type of appointment |
| `appointment_status` | selection | Status |
| `chief_complaints` | text | Patient complaints |
| `duration` | float | Duration in hours |

#### Relations
| Field | Type | Target Model | Description |
|-------|------|--------------|-------------|
| `patient_id` | many2one | patient.patient | Related patient |
| `doctor_id` | many2one | clinic.doctor | Assigned doctor |
| `user_id` | many2one | res.users | Assistant |
| `procedure_line_id` | one2many | dental.procedure.line | Procedures performed |
| `patient_appointment_prescription_id` | one2many | patient.prescription | Prescriptions |

---

### 4. patient.prescription (6 records)

**Purpose:** Medical prescriptions

#### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `prescription_serial` | char | Prescription ID (e.g., PRE000001) |

#### Key Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| `prescription_date` | date | Date of formulation |
| `appointment_id_name` | char | Appointment name |

#### Relations
| Field | Type | Target Model | Description |
|-------|------|--------------|-------------|
| `patient_id` | many2one | patient.patient | Related patient |
| `appointment_id` | many2one | patient.appointment | Related appointment |
| `prescription_line_id` | one2many | patient.prescription.line | Prescription lines (medications) |

---

## 🔄 Model Relationships

```
patient.patient (1)
    ├── appointment_id (one2many) → patient.appointment (N)
    │       ├── patient_appointment_prescription_id (one2many) → patient.prescription (N)
    │       └── procedure_line_id (one2many) → dental.procedure.line (N)
    └── patient_prescriptions (one2many) → patient.prescription (N)
            └── prescription_line_id (one2many) → patient.prescription.line (N)

res.partner (independent)
    └── NO DIRECT LINK to patient.patient!
```

### 🔴 Critical Architecture Decision

**Problem:** No built-in relationship between `patient.patient` and `res.partner`

**Current Approach:**
- Create both records separately
- Link them manually by phone number or email
- Use `is_patient=True` flag on `res.partner`

**Implications:**
1. ❌ Cannot use `partner_id` in `patient.patient`
2. ✅ Must search by phone/email to find related records
3. ✅ Can have patients without partners (and vice versa)
4. ⚠️ Risk of data inconsistency

**Recommendation:**
- Always create both records
- Use phone number as primary key for linking
- Implement sync logic to keep them consistent

---

## 🛠️ Implementation Guidelines

### Creating a New Patient

```python
# Step 1: Create res.partner (for contact info)
partner_data = {
    'name': 'John Doe',
    'phone': '+972-50-123-4567',
    'email': 'john@example.com',
    'street': '123 Main St',
    'city': 'Tel Aviv',
    'is_patient': True,
}
partner_id = odoo.create('res.partner', partner_data)

# Step 2: Generate patient serial
last_patient = odoo.search_read(
    'patient.patient',
    domain=[],
    fields=['patient_serial'],
    order='patient_serial desc',
    limit=1
)
new_serial = generate_next_serial(last_patient)  # PAT000009

# Step 3: Create patient.patient (for medical info)
patient_data = {
    'patient_serial': new_serial,  # REQUIRED!
    'patient_name': 'John Doe',
    'contact_number': '+972-50-123-4567',  # Link by phone!
    'date_of_birth': '1990-01-15',
    'gender': 'male',
    'blood_type': 'a+',
    'marital_status': 'single',
    'occupation': 'Engineer',
}
patient_id = odoo.create('patient.patient', patient_data)

# Step 4: Link them (in our system)
# Store both IDs together in our database
```

### Finding Related Records

```python
# Find patient by phone
patient = odoo.search_read(
    'patient.patient',
    domain=[('contact_number', '=', '+972-50-123-4567')],
    fields=['id', 'patient_serial', 'patient_name'],
    limit=1
)

# Find partner by phone
partner = odoo.search_read(
    'res.partner',
    domain=[('phone', '=', '+972-50-123-4567')],
    fields=['id', 'name', 'email'],
    limit=1
)
```

---

## ✅ Verification Checklist

- [x] Odoo version confirmed (16.0)
- [x] Dental module identified (Pragtech v19.0.0.2)
- [x] All models documented
- [x] All fields verified
- [x] Relationships mapped
- [x] Sample data analyzed
- [x] Critical findings documented
- [x] Implementation guidelines provided

---

## 📚 References

- Live system analysis: `/home/ubuntu/odoo_system_analysis_report.txt`
- Analysis script: `/home/ubuntu/comprehensive_odoo_analysis.py`
- Odoo 16 Documentation: https://www.odoo.com/documentation/16.0/
- Pragtech Dental Module: https://apps.odoo.com/apps/modules/browse?search=dental

---

**Last Updated:** 2025-10-13  
**Verified By:** Manus AI Agent  
**Status:** ✅ Production Ready

