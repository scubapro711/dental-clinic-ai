
import pytest
from src.shared.security_validators import SecurityValidator, DataSanitizer

class TestSecurityValidator:
    @pytest.mark.parametrize("name, expected", [
        ("John Doe", True),
        ("ישראל ישראלי", True),
        ("John-Doe", True),
        ("O'Malley", True),
        ("J", False),  # Too short
        ("John Doe123", False),  # Contains numbers
        ("John@Doe", False),  # Contains special characters
    ])
    def test_validate_patient_name(self, name, expected):
        assert SecurityValidator.validate_patient_name(name) == expected

    @pytest.mark.parametrize("phone, expected", [
        ("050-1234567", True),
        ("0521234567", True),
        ("972-54-1234567", True),
        ("972-581234567", True),
        ("050-123456", False),  # Too short
        ("050-12345678", False), # Too long
        ("060-1234567", False), # Invalid prefix
        ("abc-defghij", False), # Contains letters
    ])
    def test_validate_phone(self, phone, expected):
        assert SecurityValidator.validate_phone(phone) == expected

class TestDataSanitizer:
    def test_sanitize_input(self):
        dirty_input = "<script>alert('XSS')</script>Hello"
        clean_input = DataSanitizer.sanitize_input(dirty_input)
        assert clean_input == "alert('XSS')Hello"

    def test_sanitize_clean_input(self):
        clean_input = "Hello, world!"
        sanitized_input = DataSanitizer.sanitize_input(clean_input)
        assert sanitized_input == clean_input

