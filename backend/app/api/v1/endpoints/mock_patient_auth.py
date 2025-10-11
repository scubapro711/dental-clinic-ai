"""
Mock Patient Authentication for Testing Patient Portal
Simple authentication that returns a token with a valid Odoo patient ID
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional

router = APIRouter(prefix="/mock-auth", tags=["Mock Patient Auth"])

# Mock Odoo patients (from Mock Odoo Dental data)
MOCK_PATIENTS = {
    "patient1@test.com": {
        "patient_id": 1,
        "name": "Shane גבע",
        "email": "shane.גבע@gmail.com",
        "phone": "+972521481915",
        "password": "test123"
    },
    "patient2@test.com": {
        "patient_id": 2,
        "name": "Yvonne Osborne",
        "email": "yvonne.osborne@gmail.com",
        "phone": "+972527594181",
        "password": "test123"
    },
    "patient3@test.com": {
        "patient_id": 3,
        "name": "Melanie Simmons",
        "email": "melanie.simmons@gmail.com",
        "phone": "+972528765432",
        "password": "test123"
    }
}

SECRET_KEY = "test_secret_key_for_mock_auth_only"
ALGORITHM = "HS256"

class MockLoginRequest(BaseModel):
    email: str
    password: str

class MockTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    patient_id: int
    patient_name: str

@router.post("/login", response_model=MockTokenResponse)
async def mock_patient_login(credentials: MockLoginRequest):
    """
    Mock patient login - returns token with Odoo patient ID
    
    Test credentials:
    - patient1@test.com / test123 (Shane גבע)
    - patient2@test.com / test123 (Yvonne Osborne)
    - patient3@test.com / test123 (Melanie Simmons)
    """
    patient = MOCK_PATIENTS.get(credentials.email)
    
    if not patient or patient["password"] != credentials.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Create token with patient info
    token_data = {
        "sub": credentials.email,
        "patient_id": patient["patient_id"],
        "name": patient["name"],
        "email": patient["email"],
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return MockTokenResponse(
        access_token=access_token,
        patient_id=patient["patient_id"],
        patient_name=patient["name"]
    )

@router.get("/patients")
async def list_mock_patients():
    """List available mock patients for testing"""
    return {
        "patients": [
            {
                "email": email,
                "name": data["name"],
                "patient_id": data["patient_id"],
                "password": "test123"
            }
            for email, data in MOCK_PATIENTS.items()
        ]
    }

