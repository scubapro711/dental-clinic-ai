import re

class SecurityValidator:
    @staticmethod
    def validate_patient_name(name: str) -> bool:
        # Only Hebrew/English letters, spaces, hyphens, and apostrophes
        pattern = r'^[\u0590-\u05FFa-zA-Z\s\-\']{2,50}$'
        return bool(re.match(pattern, name))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        # Israeli format: 05X-XXXXXXX or 972-5X-XXXXXXX
        pattern = r'^(05[0-9]|972-5[0-9])-?[0-9]{7}$'
        return bool(re.match(pattern, phone))




import bleach

class DataSanitizer:
    ALLOWED_TAGS = []  # No HTML tags allowed
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize input to prevent XSS attacks."""
        return bleach.clean(text, tags=DataSanitizer.ALLOWED_TAGS, strip=True)

