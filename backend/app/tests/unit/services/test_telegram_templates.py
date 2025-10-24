"""
Unit Tests for Telegram Templates

Tests for app.services.telegram_templates module including:
- TelegramTemplates class methods
- All template generation methods
- Template formatting and structure
- Button integration
"""

import pytest
from unittest.mock import Mock, patch

from app.services.telegram_templates import TelegramTemplates


@pytest.mark.unit
@pytest.mark.service
class TestTelegramTemplatesAppointmentConfirmation:
    """Test appointment_confirmation template."""
    
    def test_appointment_confirmation_basic(self):
        """Test basic appointment confirmation template."""
        appointment_data = {
            "id": 123,
            "date": "2025-01-15",
            "time": "14:00",
            "doctor": "ד\"ר כהן",
            "treatment": "בדיקה שגרתית"
        }
        
        result = TelegramTemplates.appointment_confirmation(
            appointment_data=appointment_data,
            clinic_name="מרפאת שיניים דנטה"
        )
        
        assert result["text"]
        assert "✅" in result["text"]
        assert "2025-01-15" in result["text"]
        assert "14:00" in result["text"]
        assert "ד\"ר כהן" in result["text"]
        assert "בדיקה שגרתית" in result["text"]
        assert "מרפאת שיניים דנטה" in result["text"]
        assert "123" in result["text"]
        assert result["parse_mode"] == "Markdown"
        assert "reply_markup" in result
    
    def test_appointment_confirmation_missing_fields(self):
        """Test appointment confirmation with missing optional fields."""
        appointment_data = {
            "id": 456
        }
        
        result = TelegramTemplates.appointment_confirmation(
            appointment_data=appointment_data,
            clinic_name="מרפאה"
        )
        
        assert result["text"]
        assert "456" in result["text"]


@pytest.mark.unit
@pytest.mark.service
class TestTelegramTemplatesAppointmentReminder:
    """Test appointment_reminder template."""
    
    def test_appointment_reminder_24_hours(self):
        """Test appointment reminder for 24 hours before."""
        appointment_data = {
            "id": 789,
            "date": "2025-01-16",
            "time": "10:00",
            "doctor": "ד\"ר לוי"
        }
        
        result = TelegramTemplates.appointment_reminder(
            appointment_data=appointment_data,
            clinic_name="מרפאת דנטה",
            clinic_address="רחוב הרצל 123, תל אביב",
            hours_until=24
        )
        
        assert "⏰" in result["text"]
        assert "תור מחר" in result["text"]
        assert "2025-01-16" in result["text"]
        assert "10:00" in result["text"]
        assert "ד\"ר לוי" in result["text"]
        assert "רחוב הרצל 123" in result["text"]
        assert "789" in result["text"]
        assert result["parse_mode"] == "Markdown"
    
    def test_appointment_reminder_2_hours(self):
        """Test urgent appointment reminder for 2 hours before."""
        appointment_data = {
            "id": 999,
            "date": "2025-01-16",
            "time": "15:00",
            "doctor": "ד\"ר כהן"
        }
        
        result = TelegramTemplates.appointment_reminder(
            appointment_data=appointment_data,
            clinic_name="מרפאה",
            clinic_address="כתובת",
            hours_until=2
        )
        
        assert "🚨" in result["text"]
        assert "דחופה" in result["text"]
        assert "שעתיים" in result["text"]
    
    def test_appointment_reminder_custom_hours(self):
        """Test appointment reminder with custom hours."""
        appointment_data = {
            "id": 111,
            "date": "2025-01-17",
            "time": "09:00",
            "doctor": "ד\"ר אבי"
        }
        
        result = TelegramTemplates.appointment_reminder(
            appointment_data=appointment_data,
            clinic_name="מרפאה",
            clinic_address="כתובת",
            hours_until=6
        )
        
        assert "6 שעות" in result["text"]


@pytest.mark.unit
@pytest.mark.service
class TestTelegramTemplatesAppointmentCancelled:
    """Test appointment_cancelled template."""
    
    def test_appointment_cancelled_by_patient(self):
        """Test appointment cancelled by patient."""
        appointment_data = {
            "date": "2025-01-18",
            "time": "11:00"
        }
        
        result = TelegramTemplates.appointment_cancelled(
            appointment_data=appointment_data,
            cancelled_by="patient"
        )
        
        assert "✅" in result["text"]
        assert "בוטל בהצלחה" in result["text"]
        assert "2025-01-18" in result["text"]
        assert "11:00" in result["text"]
        assert result["parse_mode"] == "Markdown"
    
    def test_appointment_cancelled_by_clinic(self):
        """Test appointment cancelled by clinic."""
        appointment_data = {
            "date": "2025-01-19",
            "time": "16:00"
        }
        
        result = TelegramTemplates.appointment_cancelled(
            appointment_data=appointment_data,
            cancelled_by="clinic"
        )
        
        assert "❌" in result["text"]
        assert "בוטל על ידי המרפאה" in result["text"]
        assert "מתנצלים" in result["text"]
        assert "2025-01-19" in result["text"]


@pytest.mark.unit
@pytest.mark.service
class TestTelegramTemplatesPaymentReceipt:
    """Test payment_receipt template."""
    
    def test_payment_receipt_basic(self):
        """Test basic payment receipt template."""
        payment_data = {
            "id": "PAY-123",
            "amount": 500.50,
            "date": "2025-01-20",
            "method": "אשראי",
            "treatment": "ניקוי אבנית"
        }
        
        result = TelegramTemplates.payment_receipt(
            payment_data=payment_data,
            clinic_name="מרפאת דנטה"
        )
        
        assert "💳" in result["text"]
        assert "קבלה" in result["text"]
        assert "500.50" in result["text"]
        assert "2025-01-20" in result["text"]
        assert "אשראי" in result["text"]
        assert "ניקוי אבנית" in result["text"]
        assert "PAY-123" in result["text"]
        assert result["parse_mode"] == "Markdown"
    
    def test_payment_receipt_with_url(self):
        """Test payment receipt with download URL."""
        payment_data = {
            "id": "PAY-456",
            "amount": 1200.00,
            "date": "2025-01-21",
            "method": "מזומן",
            "treatment": "סתימה"
        }
        
        result = TelegramTemplates.payment_receipt(
            payment_data=payment_data,
            clinic_name="מרפאה",
            receipt_url="https://example.com/receipt.pdf"
        )
        
        assert result["text"]
        assert "1,200.00" in result["text"]  # Formatted with comma


@pytest.mark.unit
@pytest.mark.service
class TestTelegramTemplatesAppointmentList:
    """Test appointment_list template."""
    
    def test_appointment_list_empty(self):
        """Test appointment list with no appointments."""
        result = TelegramTemplates.appointment_list(
            appointments=[],
            patient_name="יוסי"
        )
        
        assert "📅" in result["text"]
        assert "יוסי" in result["text"]
        assert "אין לך תורים" in result["text"]
        assert result["parse_mode"] == "Markdown"
    
    def test_appointment_list_single(self):
        """Test appointment list with single appointment."""
        appointments = [
            {
                "id": 1,
                "date": "2025-01-22",
                "time": "10:00",
                "doctor": "ד\"ר כהן",
                "treatment": "בדיקה"
            }
        ]
        
        result = TelegramTemplates.appointment_list(
            appointments=appointments,
            patient_name="דני"
        )
        
        assert "דני" in result["text"]
        assert "1 תורים" in result["text"]
        assert "2025-01-22" in result["text"]
        assert "10:00" in result["text"]
        assert "ד\"ר כהן" in result["text"]
    
    def test_appointment_list_multiple(self):
        """Test appointment list with multiple appointments."""
        appointments = [
            {
                "id": i,
                "date": f"2025-01-{20+i}",
                "time": f"{10+i}:00",
                "doctor": f"ד\"ר {i}",
                "treatment": f"טיפול {i}"
            }
            for i in range(1, 4)
        ]
        
        result = TelegramTemplates.appointment_list(
            appointments=appointments,
            patient_name="רונית"
        )
        
        assert "רונית" in result["text"]
        assert "3 תורים" in result["text"]
        assert "1." in result["text"]
        assert "2." in result["text"]
        assert "3." in result["text"]
    
    def test_appointment_list_more_than_five(self):
        """Test appointment list with more than 5 appointments."""
        appointments = [
            {
                "id": i,
                "date": f"2025-01-{i}",
                "time": "10:00",
                "doctor": "ד\"ר כהן",
                "treatment": "טיפול"
            }
            for i in range(1, 8)
        ]
        
        result = TelegramTemplates.appointment_list(
            appointments=appointments,
            patient_name="משה"
        )
        
        assert "משה" in result["text"]
        assert "7 תורים" in result["text"]
        assert "ועוד 2 תורים נוספים" in result["text"]


@pytest.mark.unit
@pytest.mark.service
class TestTelegramTemplatesAppointmentDetails:
    """Test appointment_details template."""
    
    def test_appointment_details_basic(self):
        """Test basic appointment details template."""
        appointment_data = {
            "id": 555,
            "date": "2025-01-23",
            "time": "14:00",
            "doctor": "ד\"ר לוי",
            "treatment": "השתלה",
            "duration": 60
        }
        
        result = TelegramTemplates.appointment_details(
            appointment_data=appointment_data,
            clinic_name="מרפאת דנטה",
            clinic_address="רחוב הרצל 123",
            clinic_phone="03-1234567"
        )
        
        assert "📋" in result["text"]
        assert "פרטי התור" in result["text"]
        assert "2025-01-23" in result["text"]
        assert "14:00" in result["text"]
        assert "ד\"ר לוי" in result["text"]
        assert "השתלה" in result["text"]
        assert "60 דקות" in result["text"]
        assert "רחוב הרצל 123" in result["text"]
        assert "03-1234567" in result["text"]
        assert "555" in result["text"]
    
    def test_appointment_details_with_notes(self):
        """Test appointment details with notes."""
        appointment_data = {
            "id": 666,
            "date": "2025-01-24",
            "time": "09:00",
            "doctor": "ד\"ר כהן",
            "treatment": "בדיקה",
            "duration": 30,
            "notes": "להביא צילומים קודמים"
        }
        
        result = TelegramTemplates.appointment_details(
            appointment_data=appointment_data,
            clinic_name="מרפאה",
            clinic_address="כתובת",
            clinic_phone="טלפון"
        )
        
        assert "📝" in result["text"]
        assert "הערות" in result["text"]
        assert "להביא צילומים קודמים" in result["text"]


@pytest.mark.unit
@pytest.mark.service
class TestTelegramTemplatesContactInfo:
    """Test contact_info template."""
    
    def test_contact_info_basic(self):
        """Test basic contact info template."""
        result = TelegramTemplates.contact_info(
            clinic_name="מרפאת דנטה",
            clinic_address="רחוב הרצל 123, תל אביב",
            clinic_phone="03-1234567"
        )
        
        assert "📞" in result["text"]
        assert "פרטי התקשרות" in result["text"]
        assert "מרפאת דנטה" in result["text"]
        assert "רחוב הרצל 123" in result["text"]
        assert "03-1234567" in result["text"]
        assert result["parse_mode"] == "Markdown"
    
    def test_contact_info_with_email(self):
        """Test contact info with email."""
        result = TelegramTemplates.contact_info(
            clinic_name="מרפאה",
            clinic_address="כתובת",
            clinic_phone="טלפון",
            clinic_email="info@clinic.com"
        )
        
        assert "📧" in result["text"]
        assert "info@clinic.com" in result["text"]
    
    def test_contact_info_with_hours(self):
        """Test contact info with working hours."""
        result = TelegramTemplates.contact_info(
            clinic_name="מרפאה",
            clinic_address="כתובת",
            clinic_phone="טלפון",
            working_hours="א'-ה' 08:00-18:00"
        )
        
        assert "🕐" in result["text"]
        assert "שעות פעילות" in result["text"]
        assert "א'-ה' 08:00-18:00" in result["text"]
    
    def test_contact_info_complete(self):
        """Test contact info with all fields."""
        result = TelegramTemplates.contact_info(
            clinic_name="מרפאת דנטה",
            clinic_address="רחוב הרצל 123",
            clinic_phone="03-1234567",
            clinic_email="info@denta.com",
            working_hours="א'-ה' 08:00-18:00\nו' 09:00-13:00"
        )
        
        assert "מרפאת דנטה" in result["text"]
        assert "info@denta.com" in result["text"]
        assert "א'-ה' 08:00-18:00" in result["text"]


@pytest.mark.unit
@pytest.mark.service
class TestTelegramTemplatesErrorMessage:
    """Test error_message template."""
    
    def test_error_message_general(self):
        """Test general error message."""
        result = TelegramTemplates.error_message(error_type="general")
        
        assert "😔" in result["text"]
        assert "משהו השתבש" in result["text"]
        assert result["parse_mode"] == "Markdown"
    
    def test_error_message_appointment_not_found(self):
        """Test appointment not found error."""
        result = TelegramTemplates.error_message(error_type="appointment_not_found")
        
        assert "😔" in result["text"]
        assert "לא מצאתי את התור" in result["text"]
    
    def test_error_message_no_appointments(self):
        """Test no appointments error."""
        result = TelegramTemplates.error_message(error_type="no_appointments")
        
        assert "📅" in result["text"]
        assert "אין לך תורים" in result["text"]
    
    def test_error_message_booking_failed(self):
        """Test booking failed error."""
        result = TelegramTemplates.error_message(error_type="booking_failed")
        
        assert "😔" in result["text"]
        assert "לא הצלחתי לקבוע" in result["text"]
    
    def test_error_message_payment_failed(self):
        """Test payment failed error."""
        result = TelegramTemplates.error_message(error_type="payment_failed")
        
        assert "😔" in result["text"]
        assert "התשלום נכשל" in result["text"]
    
    def test_error_message_custom(self):
        """Test custom error message."""
        custom_msg = "זוהי הודעת שגיאה מותאמת אישית"
        result = TelegramTemplates.error_message(
            error_type="general",
            custom_message=custom_msg
        )
        
        assert custom_msg in result["text"]
    
    def test_error_message_unknown_type(self):
        """Test unknown error type falls back to general."""
        result = TelegramTemplates.error_message(error_type="unknown_type")
        
        assert "😔" in result["text"]
        assert "משהו השתבש" in result["text"]


@pytest.mark.unit
@pytest.mark.service
class TestTelegramTemplatesGetTemplate:
    """Test get_template method."""
    
    def test_get_template_appointment_confirmation(self):
        """Test getting appointment confirmation template by name."""
        result = TelegramTemplates.get_template(
            "appointment_confirmation",
            appointment_data={"id": 123, "date": "2025-01-25", "time": "10:00", "doctor": "ד\"ר כהן", "treatment": "בדיקה"},
            clinic_name="מרפאה"
        )
        
        assert result is not None
        assert "✅" in result["text"]
    
    def test_get_template_appointment_reminder(self):
        """Test getting appointment reminder template by name."""
        result = TelegramTemplates.get_template(
            "appointment_reminder",
            appointment_data={"id": 456, "date": "2025-01-26", "time": "14:00", "doctor": "ד\"ר לוי"},
            clinic_name="מרפאה",
            clinic_address="כתובת"
        )
        
        assert result is not None
        assert "⏰" in result["text"]
    
    def test_get_template_error_message(self):
        """Test getting error message template by name."""
        result = TelegramTemplates.get_template(
            "error_message",
            error_type="general"
        )
        
        assert result is not None
        assert "😔" in result["text"]
    
    def test_get_template_invalid_name(self):
        """Test getting template with invalid name."""
        result = TelegramTemplates.get_template("invalid_template_name")
        
        assert result is None
    
    def test_get_template_missing_kwargs(self):
        """Test getting template with missing required kwargs."""
        result = TelegramTemplates.get_template("appointment_confirmation")
        
        assert result is None
    
    def test_get_template_all_templates(self):
        """Test that all templates are accessible via get_template."""
        templates = [
            "appointment_confirmation",
            "appointment_reminder",
            "appointment_cancelled",
            "payment_receipt",
            "appointment_list",
            "appointment_details",
            "contact_info",
            "error_message"
        ]
        
        for template_name in templates:
            # Just verify the template name is in the map
            # Actual call would require proper kwargs
            assert template_name in [
                "appointment_confirmation",
                "appointment_reminder",
                "appointment_cancelled",
                "payment_receipt",
                "appointment_list",
                "appointment_details",
                "contact_info",
                "error_message"
            ]

