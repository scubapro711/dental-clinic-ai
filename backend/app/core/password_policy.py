"""
Password Policy

Enforces strong password requirements for user accounts.
"""

import re
from typing import Tuple
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Cost factor for bcrypt
)


class PasswordPolicy:
    """
    Password policy enforcement.
    
    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - Not in common passwords list
    """
    
    # Policy settings
    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    
    # Special characters allowed
    SPECIAL_CHARS = r'!@#$%^&*(),.?":{}|<>[\]\\/_\-+=~`'
    
    @classmethod
    def validate(cls, password: str) -> Tuple[bool, str]:
        """
        Validate password against policy.
        
        Args:
            password: Password to validate
        
        Returns:
            (is_valid, error_message)
        """
        # Check length
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters long"
        
        # Check uppercase
        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check lowercase
        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check digit
        if cls.REQUIRE_DIGIT and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        # Check special character
        if cls.REQUIRE_SPECIAL:
            pattern = f'[{re.escape(cls.SPECIAL_CHARS)}]'
            if not re.search(pattern, password):
                return False, f"Password must contain at least one special character ({cls.SPECIAL_CHARS[:20]}...)"
        
        # Check against common passwords
        if password.lower() in COMMON_PASSWORDS:
            return False, "This password is too common. Please choose a different password."
        
        # Check for sequential characters
        if cls._has_sequential_chars(password):
            return False, "Password contains sequential characters (e.g., '123', 'abc')"
        
        # Check for repeated characters
        if cls._has_repeated_chars(password):
            return False, "Password contains too many repeated characters"
        
        return True, ""
    
    @classmethod
    def _has_sequential_chars(cls, password: str, length: int = 4) -> bool:
        """Check for sequential characters"""
        password_lower = password.lower()
        
        for i in range(len(password_lower) - length + 1):
            substr = password_lower[i:i+length]
            
            # Check numeric sequences
            if substr.isdigit():
                nums = [int(c) for c in substr]
                if all(nums[i] + 1 == nums[i+1] for i in range(len(nums)-1)):
                    return True
                if all(nums[i] - 1 == nums[i+1] for i in range(len(nums)-1)):
                    return True
            
            # Check alphabetic sequences
            if substr.isalpha():
                ords = [ord(c) for c in substr]
                if all(ords[i] + 1 == ords[i+1] for i in range(len(ords)-1)):
                    return True
                if all(ords[i] - 1 == ords[i+1] for i in range(len(ords)-1)):
                    return True
        
        return False
    
    @classmethod
    def _has_repeated_chars(cls, password: str, max_repeats: int = 3) -> bool:
        """Check for repeated characters"""
        for i in range(len(password) - max_repeats):
            if len(set(password[i:i+max_repeats+1])) == 1:
                return True
        return False
    
    @classmethod
    def hash(cls, password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)
    
    @classmethod
    def verify(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
        
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @classmethod
    def needs_rehash(cls, hashed_password: str) -> bool:
        """
        Check if password needs to be rehashed.
        
        This happens when the hashing algorithm or cost factor changes.
        
        Args:
            hashed_password: Hashed password
        
        Returns:
            True if needs rehash, False otherwise
        """
        return pwd_context.needs_update(hashed_password)
    
    @classmethod
    def generate_strong_password(cls, length: int = 16) -> str:
        """
        Generate a strong random password.
        
        Args:
            length: Password length (default: 16)
        
        Returns:
            Strong random password
        """
        import secrets
        import string
        
        # Ensure minimum length
        length = max(length, cls.MIN_LENGTH)
        
        # Character sets
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        special = cls.SPECIAL_CHARS
        
        # Ensure at least one of each required character type
        password = [
            secrets.choice(uppercase),
            secrets.choice(lowercase),
            secrets.choice(digits),
            secrets.choice(special),
        ]
        
        # Fill the rest with random characters
        all_chars = uppercase + lowercase + digits + special
        password.extend(secrets.choice(all_chars) for _ in range(length - 4))
        
        # Shuffle to avoid predictable patterns
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)


# Common passwords list (top 100)
# In production, load from a file with 10,000+ common passwords
COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123",
    "monkey", "1234567", "letmein", "trustno1", "dragon",
    "baseball", "111111", "iloveyou", "master", "sunshine",
    "ashley", "bailey", "passw0rd", "shadow", "123123",
    "654321", "superman", "qazwsx", "michael", "football",
    "password1", "password123", "welcome", "admin", "login",
    "starwars", "princess", "welcome1", "solo", "whatever",
    "donald", "batman", "zaq1zaq1", "password!", "qwerty123",
    "freedom", "passw0rd!", "password1!", "letmein1", "monkey123",
    "dragon123", "master123", "sunshine1", "welcome123", "admin123",
    "login123", "starwars1", "princess1", "batman123", "superman123",
    "football1", "baseball1", "iloveyou1", "trustno1!", "shadow123",
    "bailey123", "ashley123", "michael123", "qazwsx123", "654321!",
    "123123!", "abc123!", "111111!", "1234567!", "123456!",
    "password12", "password1234", "qwerty12", "qwerty1234", "welcome12",
    "admin12", "login12", "master12", "sunshine12", "dragon12",
    "monkey12", "football12", "baseball12", "batman12", "superman12",
    "princess12", "starwars12", "ashley12", "bailey12", "michael12",
    "shadow12", "trustno12", "letmein12", "iloveyou12", "qazwsx12",
    "freedom12", "whatever12", "solo12", "donald12", "zaq1zaq12",
}


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Convenience function to validate password.
    
    Args:
        password: Password to validate
    
    Returns:
        (is_valid, error_message)
    """
    return PasswordPolicy.validate(password)


def hash_password(password: str) -> str:
    """
    Convenience function to hash password.
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password
    """
    return PasswordPolicy.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Convenience function to verify password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
    
    Returns:
        True if password matches, False otherwise
    """
    return PasswordPolicy.verify(plain_password, hashed_password)
