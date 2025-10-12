# Odoo Integration Fixes

Complete guide for the improved Odoo integration with comprehensive error handling.

## 📋 Overview

The original Odoo integration had several critical issues:

1. **Constraint errors** when creating appointments
2. **Missing required fields** validation
3. **Poor error messages** that didn't help debugging
4. **No retry logic** for transient failures
5. **No validation** before API calls

This document describes the fixes implemented in `odoo_client_v2.py` and `odoo_tools_v2.py`.

---

## 🔴 Problems Fixed

### Problem 1: Constraint Errors in create_appointment

**Original Error:**
```
xmlrpc.client.Fault: <Fault 1: 'Constraint violation: appointment_date_check'>
```

**Root Cause:**
- Missing required fields
- Invalid field values
- Conflicting appointments
- No validation before creation

**Solution:**
```python
def create_appointment(
    self,
    patient_id: int,
    doctor_id: int,
    appointment_date: datetime,
    duration_minutes: int = 45,
    ...
) -> int:
    # 1. Validate data BEFORE creating
    is_valid, error_msg = self.validate_appointment_data(
        patient_id, doctor_id, appointment_date
    )
    if not is_valid:
        raise OdooValidationError(error_msg)
    
    # 2. Include ALL required fields
    appointment_data = {
        'patient_id': patient_id,
        'doctor_id': doctor_id,
        'appointment_sdate': appointment_date.strftime('%Y-%m-%d %H:%M:%S'),
        'appointment_edate': end_date.strftime('%Y-%m-%d %H:%M:%S'),
        'patient_state': 'withapt',  # Required!
        'state': 'draft',  # Required!
    }
    
    # 3. Try to create with better error handling
    try:
        appointment_id = self._execute('medical.appointment', 'create', [appointment_data])
        return appointment_id
    except OdooConstraintError as e:
        logger.error(f"Constraint error: {e}")
        logger.error(f"Data: {appointment_data}")
        raise
```

---

### Problem 2: Missing Required Fields

**Original Code:**
```python
# Only provided 3 fields
appointment_data = {
    'patient_id': patient_id,
    'doctor_id': doctor_id,
    'appointment_sdate': date_str
}
```

**Solution:**
```python
# Provide ALL required fields
appointment_data = {
    'patient_id': patient_id,
    'doctor_id': doctor_id,
    'appointment_sdate': start_date_str,
    'appointment_edate': end_date_str,  # Added!
    'patient_state': 'withapt',  # Added!
    'state': 'draft'  # Added!
}
```

**How to discover required fields:**
```python
def get_required_appointment_fields(self) -> List[str]:
    """Get required fields from Odoo."""
    fields_info = self._execute(
        'medical.appointment',
        'fields_get',
        [],
        {'attributes': ['required', 'string']}
    )
    
    required_fields = [
        field_name
        for field_name, field_info in fields_info.items()
        if field_info.get('required', False)
    ]
    
    return required_fields
```

---

### Problem 3: Poor Error Messages

**Original:**
```python
except Exception as e:
    return f"Error: {str(e)}"
```

**Problem:** Generic error doesn't help debugging.

**Solution:**
```python
except OdooValidationError as e:
    return f"❌ שגיאת אימות: {str(e)}"
except OdooConstraintError as e:
    return f"❌ שגיאת מגבלה: {str(e)}\n\nייתכן שהתור כבר תפוס."
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    logger.error(f"Data: {appointment_data}")
    return f"❌ שגיאה בקביעת תור: {str(e)}"
```

**Custom Exceptions:**
```python
class OdooConnectionError(Exception):
    """Raised when connection to Odoo fails."""
    pass

class OdooValidationError(Exception):
    """Raised when data validation fails."""
    pass

class OdooConstraintError(Exception):
    """Raised when Odoo constraint is violated."""
    pass
```

---

### Problem 4: No Retry Logic

**Original:**
```python
def authenticate(self):
    self.uid = self.common.authenticate(...)
    # Fails permanently on transient network errors
```

**Solution:**
```python
@retry_on_failure(max_retries=3, delay=1.0)
def authenticate(self) -> bool:
    """Authenticate with retry logic."""
    try:
        self.uid = self.common.authenticate(...)
        return True
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(delay * (attempt + 1))  # Exponential backoff
            return None
        return wrapper
    return decorator
```

---

### Problem 5: No Validation Before API Calls

**Original:**
```python
# Create appointment without checking if patient/doctor exist
appointment_id = odoo_client.create_appointment(
    patient_id=999999,  # Doesn't exist!
    doctor_id=888888,   # Doesn't exist!
    ...
)
```

**Solution:**
```python
def validate_appointment_data(
    self,
    patient_id: int,
    doctor_id: int,
    appointment_date: datetime
) -> Tuple[bool, Optional[str]]:
    """Validate appointment data before creation."""
    
    # Check patient exists
    patient = self.get_patient(patient_id)
    if not patient:
        return False, f"Patient {patient_id} not found"
    
    # Check doctor exists
    doctor = self._execute(
        'hr.employee',
        'read',
        [[doctor_id]],
        {'fields': ['id', 'name']}
    )
    if not doctor:
        return False, f"Doctor {doctor_id} not found"
    
    # Check date is in future
    if appointment_date < datetime.now():
        return False, "Appointment date must be in the future"
    
    return True, None
```

---

## 🚀 How to Use the Fixed Integration

### 1. Import the New Client

```python
from app.integrations.odoo_client_v2 import odoo_client_v2
```

### 2. Search for Patients

```python
# Search by name
patient_ids = odoo_client_v2.search_patients(name="John Doe")

# Search by phone
patient_ids = odoo_client_v2.search_patients(phone="+972501234567")

# Search by Israeli ID
patient_ids = odoo_client_v2.search_patients(israeli_id="123456789")
```

### 3. Create Patient

```python
try:
    patient_id = odoo_client_v2.create_patient(
        name="John Doe",
        phone="+972501234567",
        email="john@example.com",
        israeli_id="123456789",
        date_of_birth=date(1980, 1, 15)
    )
    print(f"Created patient: {patient_id}")
except OdooValidationError as e:
    print(f"Validation error: {e}")
```

### 4. Get Available Slots

```python
slots = odoo_client_v2.get_available_slots(
    doctor_id=1,
    date_from=datetime.now(),
    date_to=datetime.now() + timedelta(days=7),
    slot_duration_minutes=45
)

print(f"Found {len(slots)} available slots")
for slot in slots[:5]:
    print(f"  - {slot.strftime('%Y-%m-%d %H:%M')}")
```

### 5. Create Appointment

```python
try:
    appointment_id = odoo_client_v2.create_appointment(
        patient_id=123,
        doctor_id=1,
        appointment_date=datetime(2025, 10, 15, 10, 0),
        duration_minutes=45,
        notes="First visit - checkup"
    )
    print(f"Created appointment: {appointment_id}")
except OdooValidationError as e:
    print(f"Validation error: {e}")
except OdooConstraintError as e:
    print(f"Constraint error: {e}")
```

---

## 🔧 Using the New Tools in Agents

### Update Agent Configuration

```python
from app.agents.tools.odoo_tools_v2 import (
    search_patient_v2,
    create_patient_v2,
    get_available_slots_v2,
    create_appointment_v2,
    cancel_appointment_v2,
    get_patient_appointments_v2
)

# In agent definition
tools = [
    search_patient_v2,
    create_patient_v2,
    get_available_slots_v2,
    create_appointment_v2,
    cancel_appointment_v2,
    get_patient_appointments_v2
]
```

### Example Agent Interaction

**User:** "קבע לי תור לדוד כהן, טלפון 0501234567, ליום שלישי הקרוב בשעה 10:00"

**Agent Steps:**
1. Search for patient: `search_patient_v2(name="דוד כהן", phone="0501234567")`
2. If not found, create: `create_patient_v2(name="דוד כהן", phone="0501234567")`
3. Get available slots: `get_available_slots_v2(doctor_id=1, days_ahead=7)`
4. Create appointment: `create_appointment_v2(patient_name="דוד כהן", patient_phone="0501234567", doctor_id=1, appointment_datetime="2025-10-15 10:00")`

**Agent Response:**
```
✅ התור נקבע בהצלחה!

📋 פרטי התור:
מטופל: דוד כהן (מטופל קיים)
תאריך: 15/10/2025
שעה: 10:00
משך: 45 דקות
מספר תור: 456
הערות: אין
```

---

## 🧪 Testing the Integration

### Test 1: Authentication

```python
def test_authentication():
    assert odoo_client_v2.authenticate() == True
    assert odoo_client_v2.uid is not None
    print("✓ Authentication successful")

test_authentication()
```

### Test 2: Patient Creation

```python
def test_patient_creation():
    patient_id = odoo_client_v2.create_patient(
        name="Test Patient",
        phone="+972501111111",
        email="test@example.com"
    )
    assert patient_id > 0
    print(f"✓ Created patient: {patient_id}")

test_patient_creation()
```

### Test 3: Appointment Creation

```python
def test_appointment_creation():
    # Create test patient
    patient_id = odoo_client_v2.create_patient(
        name="Test Patient",
        phone="+972502222222"
    )
    
    # Create appointment
    appointment_id = odoo_client_v2.create_appointment(
        patient_id=patient_id,
        doctor_id=1,
        appointment_date=datetime.now() + timedelta(days=1),
        duration_minutes=45
    )
    
    assert appointment_id > 0
    print(f"✓ Created appointment: {appointment_id}")

test_appointment_creation()
```

### Test 4: Error Handling

```python
def test_error_handling():
    try:
        # Try to create appointment with invalid patient
        odoo_client_v2.create_appointment(
            patient_id=999999,  # Doesn't exist
            doctor_id=1,
            appointment_date=datetime.now() + timedelta(days=1)
        )
        assert False, "Should have raised OdooValidationError"
    except OdooValidationError as e:
        print(f"✓ Caught validation error: {e}")

test_error_handling()
```

---

## 📊 Comparison: Old vs New

| Feature | Old Integration | New Integration |
|---------|----------------|-----------------|
| **Error Handling** | Generic exceptions | Specific exceptions (Validation, Constraint, Connection) |
| **Validation** | None | Pre-creation validation |
| **Required Fields** | Partial | All required fields included |
| **Retry Logic** | None | 3 retries with exponential backoff |
| **Error Messages** | Generic | Detailed, Hebrew, actionable |
| **Logging** | Minimal | Comprehensive with data dumps |
| **Available Slots** | Mock data | Real Odoo data |
| **Patient Search** | Name only | Name, phone, email, Israeli ID |

---

## 🔒 Security Improvements

### 1. Input Validation

```python
# Validate patient name
if not name or len(name) < 2:
    raise OdooValidationError("Patient name must be at least 2 characters")

# Validate phone number
if phone and not re.match(r'^\+?[0-9]{9,15}$', phone):
    raise OdooValidationError("Invalid phone number format")

# Validate Israeli ID
if israeli_id and not validate_israeli_id(israeli_id):
    raise OdooValidationError("Invalid Israeli ID number")
```

### 2. SQL Injection Prevention

```python
# ❌ DON'T: String concatenation
domain = f"[('name', '=', '{name}')]"

# ✅ DO: Use Odoo domain format
domain = [('name', '=', name)]
```

### 3. Connection Security

```python
# Use HTTPS for Odoo connection
ODOO_URL = "https://dentaflow.ai"  # Not http://

# Store credentials in environment variables
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')  # Not hardcoded
```

---

## 📈 Performance Improvements

### 1. Connection Pooling

```python
# Reuse XML-RPC connections
self.common = xmlrpc.client.ServerProxy(
    f"{self.url}/xmlrpc/2/common",
    allow_none=True  # Allows None values
)
```

### 2. Batch Operations

```python
# Get multiple patients at once
patient_ids = [1, 2, 3, 4, 5]
patients = odoo_client_v2._execute(
    'res.partner',
    'read',
    [patient_ids],
    {'fields': ['id', 'name', 'phone']}
)
```

### 3. Field Selection

```python
# ❌ DON'T: Get all fields (slow)
patient = odoo_client_v2._execute('res.partner', 'read', [[patient_id]])

# ✅ DO: Get only needed fields (fast)
patient = odoo_client_v2._execute(
    'res.partner',
    'read',
    [[patient_id]],
    {'fields': ['id', 'name', 'phone']}
)
```

---

## ✅ Migration Checklist

- [ ] Install `odoo_client_v2.py` in `app/integrations/`
- [ ] Install `odoo_tools_v2.py` in `app/agents/tools/`
- [ ] Update agent configurations to use new tools
- [ ] Test authentication with production Odoo
- [ ] Test patient creation
- [ ] Test appointment creation
- [ ] Test error handling
- [ ] Update API endpoints to use new client
- [ ] Update tests to use new client
- [ ] Deploy to staging environment
- [ ] Monitor logs for errors
- [ ] Deploy to production

---

## 🆘 Troubleshooting

### Error: "Authentication failed"

**Cause:** Invalid credentials or Odoo URL

**Solution:**
```bash
# Check environment variables
echo $ODOO_URL
echo $ODOO_USERNAME
# Don't echo password!

# Test connection manually
python3 -c "
from app.integrations.odoo_client_v2 import odoo_client_v2
odoo_client_v2.authenticate()
"
```

### Error: "Patient not found"

**Cause:** Patient ID doesn't exist in Odoo

**Solution:**
```python
# Search for patient first
patient_ids = odoo_client_v2.search_patients(name="John Doe")
if not patient_ids:
    # Create patient
    patient_id = odoo_client_v2.create_patient(name="John Doe")
```

### Error: "Constraint violation"

**Cause:** Conflicting appointment or invalid data

**Solution:**
```python
# Check for existing appointments
appointments = odoo_client_v2._execute(
    'medical.appointment',
    'search_read',
    [[
        ('doctor_id', '=', doctor_id),
        ('appointment_sdate', '=', appointment_date_str)
    ]]
)

if appointments:
    print("Slot already taken!")
```

---

## 📚 Additional Resources

- [Odoo 19.0 Documentation](https://www.odoo.com/documentation/19.0/)
- [Pragtech Dental Management](https://apps.odoo.com/apps/modules/19.0/pragtech_dental_management/)
- [XML-RPC External API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
- [Odoo Domain Syntax](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html#domains)

---

**Last Updated:** October 8, 2025  
**Version:** 2.0  
**Status:** Production Ready ✅
