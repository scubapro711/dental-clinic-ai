"""
Example: Patient model with encrypted PHI fields.

Demonstrates how to use encryption for HIPAA-compliant data storage.
"""
from sqlalchemy import Column, String, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base
from app.core.encryption import EncryptedString, EncryptedText


class PatientEncrypted(Base):
    """
    Patient model with encrypted PHI (Protected Health Information).
    
    HIPAA-compliant storage of sensitive patient data.
    
    Encrypted fields:
    - ssn: Social Security Number
    - id_number: Israeli ID number (תעודת זהות)
    - phone: Phone number
    - email: Email address
    - address: Home address
    - medical_history: Medical history notes
    - allergies: Allergy information
    - medications: Current medications
    - insurance_number: Insurance policy number
    """
    
    __tablename__ = 'patients_encrypted'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Organization (for multi-tenancy)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False, index=True)
    
    # Non-encrypted fields (can be indexed and searched)
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20))
    
    # Encrypted PHI fields (CANNOT be indexed or searched directly)
    ssn = Column(EncryptedString(20))  # US: 123-45-6789
    id_number = Column(EncryptedString(20))  # IL: 123456789
    phone = Column(EncryptedString(20))  # +972501234567
    email = Column(EncryptedString(255))  # patient@example.com
    address = Column(EncryptedString(500))  # Full address
    
    # Encrypted medical information
    medical_history = Column(EncryptedText)  # Large text field
    allergies = Column(EncryptedText)
    medications = Column(EncryptedText)
    
    # Encrypted insurance information
    insurance_provider = Column(EncryptedString(200))
    insurance_number = Column(EncryptedString(100))
    
    # Odoo integration
    odoo_partner_id = Column(String(50), index=True)
    
    # Timestamps
    created_at = Column(String(50))
    updated_at = Column(String(50))
    
    def __repr__(self):
        return f"<PatientEncrypted(id={self.id}, name={self.first_name} {self.last_name})>"


# ========== Usage Examples ==========

"""
Example 1: Create patient with encrypted data
----------------------------------------------

from app.models.patient_encrypted_example import PatientEncrypted
from app.core.database import get_db

patient = PatientEncrypted(
    organization_id=org_id,
    first_name="John",
    last_name="Doe",
    date_of_birth=date(1980, 1, 15),
    gender="male",
    ssn="123-45-6789",  # Automatically encrypted
    id_number="123456789",  # Automatically encrypted
    phone="+972501234567",  # Automatically encrypted
    email="john.doe@example.com",  # Automatically encrypted
    address="123 Main St, Tel Aviv",  # Automatically encrypted
    medical_history="Patient has history of...",  # Automatically encrypted
    allergies="Penicillin",  # Automatically encrypted
    medications="Aspirin 100mg daily"  # Automatically encrypted
)

db.add(patient)
db.commit()

# Data is stored encrypted in database
# When retrieved, it's automatically decrypted


Example 2: Query and retrieve patient
--------------------------------------

# Query by non-encrypted fields (indexed)
patient = db.query(PatientEncrypted).filter(
    PatientEncrypted.first_name == "John",
    PatientEncrypted.last_name == "Doe"
).first()

# Access encrypted fields (automatically decrypted)
print(patient.ssn)  # "123-45-6789" (decrypted)
print(patient.phone)  # "+972501234567" (decrypted)


Example 3: Search encrypted fields (limitation)
------------------------------------------------

# ❌ CANNOT search encrypted fields directly
patient = db.query(PatientEncrypted).filter(
    PatientEncrypted.phone == "+972501234567"  # This will NOT work!
).first()

# ✅ SOLUTION: Use searchable hash or separate search index
# Add a hashed_phone column for searching:

from hashlib import sha256

class PatientEncrypted(Base):
    phone = Column(EncryptedString(20))
    phone_hash = Column(String(64), index=True)  # SHA-256 hash for searching

# When creating/updating:
patient.phone = "+972501234567"
patient.phone_hash = sha256("+972501234567".encode()).hexdigest()

# When searching:
search_hash = sha256("+972501234567".encode()).hexdigest()
patient = db.query(PatientEncrypted).filter(
    PatientEncrypted.phone_hash == search_hash
).first()


Example 4: Bulk operations with encryption
-------------------------------------------

# Create multiple patients
patients = [
    PatientEncrypted(
        organization_id=org_id,
        first_name="Alice",
        last_name="Smith",
        ssn="111-11-1111",
        phone="+972501111111"
    ),
    PatientEncrypted(
        organization_id=org_id,
        first_name="Bob",
        last_name="Johnson",
        ssn="222-22-2222",
        phone="+972502222222"
    )
]

db.bulk_save_objects(patients)
db.commit()

# All encrypted fields are automatically encrypted


Example 5: Update encrypted fields
-----------------------------------

patient = db.query(PatientEncrypted).filter(
    PatientEncrypted.id == patient_id
).first()

# Update encrypted field
patient.phone = "+972509999999"  # Automatically encrypted
patient.address = "456 New St, Jerusalem"  # Automatically encrypted

db.commit()


Example 6: Export data (decrypted)
-----------------------------------

patients = db.query(PatientEncrypted).all()

# Export to CSV (data is automatically decrypted)
import csv

with open('patients_export.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Name', 'Phone', 'Email'])
    
    for patient in patients:
        writer.writerow([
            f"{patient.first_name} {patient.last_name}",
            patient.phone,  # Decrypted
            patient.email   # Decrypted
        ])


Example 7: Key rotation
------------------------

from app.core.encryption import rotate_encryption_key

# Rotate encryption key for phone field
rotate_encryption_key(
    old_key='old-encryption-key',
    new_key='new-encryption-key',
    model_class=PatientEncrypted,
    field_name='phone',
    db_session=db
)

# All phone numbers are re-encrypted with new key
"""
