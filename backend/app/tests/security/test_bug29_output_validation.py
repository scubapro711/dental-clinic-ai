"""
Bug #29 Tests: Output Validation and PII/PHI Filtering

This test file verifies that the output validation layer correctly
detects and sanitizes PII/PHI in agent responses.

Author: Manus AI
Date: October 25, 2025
"""

import pytest
from app.core.security import validate_output, detect_pii_phi, sanitize_pii_phi


class TestOutputValidation:
    """
    Tests for Bug #29: Output Validation and PII/PHI Filtering.
    
    These tests verify that the validate_output() function correctly
    detects and sanitizes sensitive information in agent responses.
    """
    
    @pytest.mark.security
    def test_pii_detection_ssn(self):
        """Test that SSN is detected in output."""
        text = "Patient SSN: 123-45-6789"
        result = detect_pii_phi(text)
        
        assert result['contains_pii'] is True
        assert 'ssn' in result['pii_types']
        assert len(result['matches']) > 0
    
    @pytest.mark.security
    def test_pii_detection_phone(self):
        """Test that phone numbers are detected in output."""
        text = "Call us at (555) 123-4567"
        result = detect_pii_phi(text)
        
        assert result['contains_pii'] is True
        assert 'phone' in result['pii_types']
    
    @pytest.mark.security
    def test_pii_detection_email(self):
        """Test that email addresses are detected in output."""
        text = "Contact john.doe@example.com for more info"
        result = detect_pii_phi(text)
        
        assert result['contains_pii'] is True
        assert 'email' in result['pii_types']
    
    @pytest.mark.security
    def test_pii_detection_credit_card(self):
        """Test that credit card numbers are detected in output."""
        text = "Card ending in 4532"
        result = detect_pii_phi(text)
        
        assert result['contains_pii'] is True
        assert 'credit_card_partial' in result['pii_types']
    
    @pytest.mark.security
    def test_phi_detection_medical_terms(self):
        """Test that medical terms (PHI) are detected in output."""
        text = "Patient has been diagnosed with diabetes"
        result = detect_pii_phi(text)
        
        assert result['contains_phi'] is True
        assert 'medical_term' in result['phi_types']
    
    @pytest.mark.security
    def test_sanitize_pii_ssn(self):
        """Test that SSN is properly masked."""
        text = "Patient SSN: 123-45-6789"
        sanitized = sanitize_pii_phi(text)
        
        assert "123-45-6789" not in sanitized
        assert "***-**-****" in sanitized
    
    @pytest.mark.security
    def test_sanitize_pii_phone(self):
        """Test that phone numbers are properly masked."""
        text = "Call us at (555) 123-4567"
        sanitized = sanitize_pii_phi(text)
        
        assert "(555) 123-4567" not in sanitized
        assert "***-****" in sanitized
    
    @pytest.mark.security
    def test_sanitize_pii_email(self):
        """Test that email addresses are properly masked."""
        text = "Contact john.doe@example.com for more info"
        sanitized = sanitize_pii_phi(text)
        
        assert "john.doe@example.com" not in sanitized
        assert "***@***.***" in sanitized
    
    @pytest.mark.security
    def test_validate_output_safe_text(self):
        """Test that safe text passes validation."""
        text = "Your appointment is scheduled for tomorrow at 2 PM"
        result = validate_output(text, context="patient_chat")
        
        assert result['is_safe'] is True
        assert result['contains_pii'] is False
        assert result['contains_phi'] is False
        assert result['action'] == "allow"
    
    @pytest.mark.security
    def test_validate_output_pii_in_patient_chat(self):
        """Test that PII in patient chat is sanitized."""
        text = "Hello John Doe! Call us at (555) 123-4567"
        result = validate_output(text, context="patient_chat")
        
        assert result['is_safe'] is False
        assert result['contains_pii'] is True
        assert result['action'] == "sanitize"
        assert "(555) 123-4567" not in result['sanitized_output']
    
    @pytest.mark.security
    def test_validate_output_phi_unauthorized_user(self):
        """Test that PHI is blocked for unauthorized users."""
        text = "Patient has been diagnosed with diabetes"
        result = validate_output(text, user_role="patient", context="general")
        
        # PHI should be detected
        assert result['contains_phi'] is True
    
    @pytest.mark.security
    def test_validate_output_combined_pii_phi(self):
        """Test that combined PII and PHI are handled correctly."""
        text = (
            "Patient John Doe (SSN: 123-45-6789) has been diagnosed with diabetes. "
            "Call (555) 123-4567 for more info."
        )
        result = validate_output(text, context="patient_chat")
        
        assert result['contains_pii'] is True
        assert result['contains_phi'] is True
        assert result['is_safe'] is False
        
        # Verify sanitization
        sanitized = result['sanitized_output']
        assert "123-45-6789" not in sanitized
        assert "(555) 123-4567" not in sanitized
    
    @pytest.mark.security
    def test_validate_output_financial_data(self):
        """Test that financial data is sanitized."""
        text = "Your balance is $1,250. Card ending in 4532."
        result = validate_output(text, context="patient_chat")
        
        assert result['contains_pii'] is True
        assert "4532" not in result['sanitized_output']
    
    @pytest.mark.security
    def test_validate_output_address(self):
        """Test that addresses are sanitized."""
        text = "Patient lives at 456 Oak Avenue, Brooklyn"
        result = validate_output(text, context="patient_chat")
        
        assert result['contains_pii'] is True
        assert "456 Oak Avenue" not in result['sanitized_output']
    
    @pytest.mark.security
    def test_validate_output_no_false_positives(self):
        """Test that legitimate text is not flagged as PII/PHI."""
        text = "Your appointment is at our clinic at 2 PM tomorrow"
        result = validate_output(text, context="patient_chat")
        
        assert result['is_safe'] is True
        assert result['contains_pii'] is False
        assert result['contains_phi'] is False

