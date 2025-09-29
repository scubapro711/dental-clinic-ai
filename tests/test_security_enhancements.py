# Test Security Enhancements
# Version: 1.0.0
# Date: 2025-12-29

import pytest
from src.shared.security_enhancements import hash_password, verify_password, generate_hmac, verify_hmac

@pytest.mark.parametrize("password", ["password123", "!@#$%^&*()", "a" * 100])
def test_password_hashing(password):
    hashed_password = hash_password(password)
    assert hashed_password != password
    assert verify_password(hashed_password, password)
    assert not verify_password(hashed_password, "wrong_password")

@pytest.mark.parametrize("data", [
    {"key1": "value1", "key2": "value2"},
    {"a": 1, "b": True, "c": [1, 2, 3]},
    {}
])
def test_hmac_generation_and_verification(data):
    generated_hmac = generate_hmac(data)
    assert verify_hmac(data, generated_hmac)
    
    # Tamper with the data
    if data:
        first_key = list(data.keys())[0]
        tampered_data = data.copy()
        tampered_data[first_key] = "tampered"
        assert not verify_hmac(tampered_data, generated_hmac)

