"""
Tests for Bug #21: Weak password policy (HIPAA compliance).

Ensures that password validation enforces strong password requirements
to protect sensitive healthcare data in compliance with HIPAA security rules.
"""
import pytest
from pydantic import ValidationError

from app.schemas.auth import UserRegister


class TestBug21PasswordPolicy:
    """Test HIPAA-compliant password policy enforcement."""
    
    def test_valid_strong_password(self):
        """Test that a strong password meeting all requirements is accepted."""
        user_data = {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "full_name": "Test User"
        }
        user = UserRegister(**user_data)
        assert user.password == "StrongPass123!"
    
    def test_valid_password_with_various_special_chars(self):
        """Test that passwords with different special characters are accepted."""
        valid_passwords = [
            "Password1!",
            "Password1@",
            "Password1#",
            "Password1$",
            "Password1%",
            "Password1^",
            "Password1&",
            "Password1*",
            "Password1(",
            "Password1)",
            "Password1-",
            "Password1_",
            "Password1=",
            "Password1+",
            "Password1[",
            "Password1]",
            "Password1{",
            "Password1}",
            "Password1|",
            "Password1\\",
            "Password1;",
            "Password1:",
            "Password1'",
            "Password1\"",
            "Password1<",
            "Password1>",
            "Password1,",
            "Password1.",
            "Password1?",
            "Password1/",
            "Password1`",
            "Password1~",
        ]
        
        for password in valid_passwords:
            user_data = {
                "email": "test@example.com",
                "password": password,
                "full_name": "Test User"
            }
            user = UserRegister(**user_data)
            assert user.password == password
    
    def test_password_too_short(self):
        """Test that passwords shorter than 8 characters are rejected."""
        user_data = {
            "email": "test@example.com",
            "password": "Short1!",  # Only 7 characters
            "full_name": "Test User"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**user_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('password',)
        assert 'at least 8 characters' in errors[0]['msg'].lower()
    
    def test_password_no_uppercase(self):
        """Test that passwords without uppercase letters are rejected."""
        user_data = {
            "email": "test@example.com",
            "password": "lowercase123!",
            "full_name": "Test User"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**user_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('password',)
        assert 'uppercase' in errors[0]['msg'].lower()
    
    def test_password_no_lowercase(self):
        """Test that passwords without lowercase letters are rejected."""
        user_data = {
            "email": "test@example.com",
            "password": "UPPERCASE123!",
            "full_name": "Test User"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**user_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('password',)
        assert 'lowercase' in errors[0]['msg'].lower()
    
    def test_password_no_number(self):
        """Test that passwords without numbers are rejected."""
        user_data = {
            "email": "test@example.com",
            "password": "NoNumbers!",
            "full_name": "Test User"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**user_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('password',)
        assert 'number' in errors[0]['msg'].lower()
    
    def test_password_no_special_char(self):
        """Test that passwords without special characters are rejected."""
        user_data = {
            "email": "test@example.com",
            "password": "NoSpecial123",
            "full_name": "Test User"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**user_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('password',)
        assert 'special character' in errors[0]['msg'].lower()
    
    def test_password_only_lowercase(self):
        """Test that passwords with only lowercase letters are rejected."""
        user_data = {
            "email": "test@example.com",
            "password": "onlylowercase",
            "full_name": "Test User"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**user_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('password',)
    
    def test_password_only_uppercase(self):
        """Test that passwords with only uppercase letters are rejected."""
        user_data = {
            "email": "test@example.com",
            "password": "ONLYUPPERCASE",
            "full_name": "Test User"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**user_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('password',)
    
    def test_password_only_numbers(self):
        """Test that passwords with only numbers are rejected."""
        user_data = {
            "email": "test@example.com",
            "password": "12345678",
            "full_name": "Test User"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**user_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['loc'] == ('password',)
    
    def test_common_weak_passwords_rejected(self):
        """Test that common weak passwords are rejected."""
        weak_passwords = [
            "password",
            "12345678",
            "qwerty123",
            "admin123",
            "letmein1",
        ]
        
        for password in weak_passwords:
            user_data = {
                "email": "test@example.com",
                "password": password,
                "full_name": "Test User"
            }
            
            with pytest.raises(ValidationError):
                UserRegister(**user_data)
    
    def test_minimum_length_with_all_requirements(self):
        """Test that exactly 8 characters with all requirements is accepted."""
        user_data = {
            "email": "test@example.com",
            "password": "Pass123!",  # Exactly 8 characters
            "full_name": "Test User"
        }
        user = UserRegister(**user_data)
        assert user.password == "Pass123!"
    
    def test_very_long_password(self):
        """Test that very long passwords meeting requirements are accepted."""
        long_password = "VeryLongPassword123!WithManyCharacters" * 2
        user_data = {
            "email": "test@example.com",
            "password": long_password,
            "full_name": "Test User"
        }
        user = UserRegister(**user_data)
        assert user.password == long_password
    
    def test_password_with_spaces(self):
        """Test that passwords with spaces are accepted if they meet requirements."""
        user_data = {
            "email": "test@example.com",
            "password": "Pass Word 123!",
            "full_name": "Test User"
        }
        user = UserRegister(**user_data)
        assert user.password == "Pass Word 123!"
    
    def test_password_with_unicode(self):
        """Test that passwords with unicode characters are handled correctly."""
        user_data = {
            "email": "test@example.com",
            "password": "Pässwörd123!",
            "full_name": "Test User"
        }
        user = UserRegister(**user_data)
        assert user.password == "Pässwörd123!"
    
    def test_hipaa_compliant_password_examples(self):
        """Test realistic HIPAA-compliant password examples."""
        compliant_passwords = [
            "DentalClinic2024!",
            "Healthcare@2024",
            "SecurePass#123",
            "MyP@ssw0rd!",
            "Clinic$2024Admin",
            "HIPAA_Compliant1",
            "Strong&Secure99",
            "Medical*Pass2024",
        ]
        
        for password in compliant_passwords:
            user_data = {
                "email": "test@example.com",
                "password": password,
                "full_name": "Test User"
            }
            user = UserRegister(**user_data)
            assert user.password == password
    
    def test_edge_case_all_requirements_barely_met(self):
        """Test edge case where all requirements are barely met."""
        # Exactly 8 chars: 1 upper, 1 lower, 1 number, 1 special, rest lowercase
        user_data = {
            "email": "test@example.com",
            "password": "Aa1!bcde",
            "full_name": "Test User"
        }
        user = UserRegister(**user_data)
        assert user.password == "Aa1!bcde"
    
    def test_password_validation_error_messages(self):
        """Test that error messages are clear and helpful."""
        # Test missing uppercase
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="lowercase123!",
                full_name="Test User"
            )
        assert 'uppercase' in str(exc_info.value).lower()
        
        # Test missing number
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="NoNumbers!",
                full_name="Test User"
            )
        assert 'number' in str(exc_info.value).lower()
        
        # Test missing special char
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email="test@example.com",
                password="NoSpecial123",
                full_name="Test User"
            )
        assert 'special' in str(exc_info.value).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

