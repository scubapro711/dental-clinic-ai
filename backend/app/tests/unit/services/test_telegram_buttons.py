"""
Unit Tests for Telegram Buttons

Tests for app.services.telegram_buttons module including:
- TelegramButtons class (button generation methods)
- ButtonCallbackHandler class (callback parsing and action messages)
"""

import pytest
from typing import Dict, Any

from app.services.telegram_buttons import (
    TelegramButtons,
    ButtonCallbackHandler,
)


@pytest.mark.unit
@pytest.mark.service
class TestTelegramButtons:
    """Test TelegramButtons class."""
    
    def test_welcome_buttons(self):
        """Test welcome buttons generation."""
        result = TelegramButtons.welcome_buttons()
        
        assert "inline_keyboard" in result
        assert len(result["inline_keyboard"]) == 2
        
        # Check first row
        assert len(result["inline_keyboard"][0]) == 2
        assert result["inline_keyboard"][0][0]["text"] == "📅 קביעת תור"
        assert result["inline_keyboard"][0][0]["callback_data"] == "action:book_appointment"
        assert result["inline_keyboard"][0][1]["text"] == "🔍 התורים שלי"
        assert result["inline_keyboard"][0][1]["callback_data"] == "action:my_appointments"
        
        # Check second row
        assert len(result["inline_keyboard"][1]) == 2
        assert result["inline_keyboard"][1][0]["text"] == "❓ שאלה כללית"
        assert result["inline_keyboard"][1][1]["text"] == "📞 פרטי התקשרות"
    
    def test_appointment_booked_buttons(self):
        """Test appointment booked buttons generation."""
        appointment_id = 123
        result = TelegramButtons.appointment_booked_buttons(appointment_id)
        
        assert "inline_keyboard" in result
        assert len(result["inline_keyboard"]) == 2
        
        # Check acknowledgment button
        assert result["inline_keyboard"][0][0]["text"] == "✅ הבנתי, תודה"
        
        # Check calendar and directions buttons
        assert result["inline_keyboard"][1][0]["callback_data"] == f"action:add_calendar:{appointment_id}"
        assert result["inline_keyboard"][1][1]["callback_data"] == "action:directions"
    
    def test_appointment_reminder_buttons(self):
        """Test appointment reminder buttons generation."""
        appointment_id = 456
        result = TelegramButtons.appointment_reminder_buttons(appointment_id)
        
        assert "inline_keyboard" in result
        assert len(result["inline_keyboard"]) == 2
        
        # Check confirm/cancel buttons
        assert result["inline_keyboard"][0][0]["callback_data"] == f"action:confirm_arrival:{appointment_id}"
        assert result["inline_keyboard"][0][1]["callback_data"] == f"action:cancel_appointment:{appointment_id}"
        
        # Check reschedule button
        assert result["inline_keyboard"][1][0]["callback_data"] == f"action:reschedule:{appointment_id}"
    
    def test_appointment_list_buttons_empty(self):
        """Test appointment list buttons with empty list."""
        result = TelegramButtons.appointment_list_buttons([])
        
        assert "inline_keyboard" in result
        # Should have at least the "Book new appointment" button
        assert len(result["inline_keyboard"]) >= 1
        assert result["inline_keyboard"][-1][0]["text"] == "➕ קבע תור חדש"
    
    def test_appointment_list_buttons_with_appointments(self):
        """Test appointment list buttons with appointments."""
        appointments = [
            {"id": 1, "date": "2025-10-25", "time": "10:00"},
            {"id": 2, "date": "2025-10-26", "time": "14:00"},
            {"id": 3, "date": "2025-10-27", "time": "16:00"},
        ]
        result = TelegramButtons.appointment_list_buttons(appointments)
        
        assert "inline_keyboard" in result
        # 3 appointments + 1 "Book new" button
        assert len(result["inline_keyboard"]) == 4
        
        # Check first appointment button
        assert "📅 2025-10-25 10:00" in result["inline_keyboard"][0][0]["text"]
        assert result["inline_keyboard"][0][0]["callback_data"] == "action:view_appointment:1"
    
    def test_appointment_list_buttons_max_five(self):
        """Test appointment list buttons limits to 5 appointments."""
        appointments = [
            {"id": i, "date": f"2025-10-{20+i}", "time": "10:00"}
            for i in range(10)
        ]
        result = TelegramButtons.appointment_list_buttons(appointments)
        
        assert "inline_keyboard" in result
        # Max 5 appointments + 1 "Book new" button
        assert len(result["inline_keyboard"]) == 6
    
    def test_appointment_details_buttons_can_cancel(self):
        """Test appointment details buttons with cancellation allowed."""
        appointment_id = 789
        result = TelegramButtons.appointment_details_buttons(appointment_id, can_cancel=True)
        
        assert "inline_keyboard" in result
        assert len(result["inline_keyboard"]) == 3
        
        # Check reschedule and cancel buttons
        assert result["inline_keyboard"][0][0]["callback_data"] == f"action:reschedule:{appointment_id}"
        assert result["inline_keyboard"][0][1]["callback_data"] == f"action:cancel_appointment:{appointment_id}"
    
    def test_appointment_details_buttons_cannot_cancel(self):
        """Test appointment details buttons with cancellation not allowed."""
        appointment_id = 789
        result = TelegramButtons.appointment_details_buttons(appointment_id, can_cancel=False)
        
        assert "inline_keyboard" in result
        # Should have 2 rows (directions/calendar and back button)
        assert len(result["inline_keyboard"]) == 2
        
        # Check no cancel button in first row
        for button in result["inline_keyboard"][0]:
            assert "cancel" not in button["callback_data"]
    
    def test_payment_receipt_buttons_with_url(self):
        """Test payment receipt buttons with receipt URL."""
        payment_id = 999
        receipt_url = "https://example.com/receipt.pdf"
        result = TelegramButtons.payment_receipt_buttons(payment_id, receipt_url)
        
        assert "inline_keyboard" in result
        assert len(result["inline_keyboard"]) == 2
        
        # Check download button
        assert result["inline_keyboard"][0][0]["text"] == "📄 הורד קבלה"
        assert result["inline_keyboard"][0][0]["url"] == receipt_url
    
    def test_payment_receipt_buttons_without_url(self):
        """Test payment receipt buttons without receipt URL."""
        payment_id = 999
        result = TelegramButtons.payment_receipt_buttons(payment_id, receipt_url=None)
        
        assert "inline_keyboard" in result
        # Should have only 1 row (without download button)
        assert len(result["inline_keyboard"]) == 1
        
        # Check no download button
        for row in result["inline_keyboard"]:
            for button in row:
                assert "url" not in button or button.get("text") != "📄 הורד קבלה"
    
    def test_confirmation_buttons(self):
        """Test confirmation buttons generation."""
        confirm_action = "action:delete_account"
        cancel_action = "action:cancel"
        result = TelegramButtons.confirmation_buttons(confirm_action, cancel_action)
        
        assert "inline_keyboard" in result
        assert len(result["inline_keyboard"]) == 1
        assert len(result["inline_keyboard"][0]) == 2
        
        # Check yes/no buttons
        assert result["inline_keyboard"][0][0]["text"] == "✅ כן, בטוח"
        assert result["inline_keyboard"][0][0]["callback_data"] == confirm_action
        assert result["inline_keyboard"][0][1]["text"] == "❌ לא, ביטול"
        assert result["inline_keyboard"][0][1]["callback_data"] == cancel_action
    
    def test_contact_info_buttons(self):
        """Test contact info buttons generation."""
        phone = "+972-50-123-4567"
        address = "123 Main St, Tel Aviv"
        result = TelegramButtons.contact_info_buttons(phone, address)
        
        assert "inline_keyboard" in result
        assert len(result["inline_keyboard"]) == 3
        
        # Check phone button
        assert result["inline_keyboard"][0][0]["url"] == f"tel:{phone}"
        
        # Check navigation buttons
        assert "waze.com" in result["inline_keyboard"][1][0]["url"]
        assert "maps.google.com" in result["inline_keyboard"][1][1]["url"]
        
        # Check back button
        assert result["inline_keyboard"][2][0]["callback_data"] == "action:main_menu"
    
    def test_main_menu_button(self):
        """Test main menu button generation."""
        result = TelegramButtons.main_menu_button()
        
        assert "inline_keyboard" in result
        assert len(result["inline_keyboard"]) == 1
        assert result["inline_keyboard"][0][0]["text"] == "🏠 תפריט ראשי"
        assert result["inline_keyboard"][0][0]["callback_data"] == "action:main_menu"
    
    def test_get_buttons_for_context_welcome(self):
        """Test get_buttons_for_context with welcome context."""
        result = TelegramButtons.get_buttons_for_context("welcome")
        
        assert result is not None
        assert "inline_keyboard" in result
        # Should be same as welcome_buttons()
        expected = TelegramButtons.welcome_buttons()
        assert result == expected
    
    def test_get_buttons_for_context_appointment_booked(self):
        """Test get_buttons_for_context with appointment_booked context."""
        appointment_id = 123
        result = TelegramButtons.get_buttons_for_context("appointment_booked", appointment_id=appointment_id)
        
        assert result is not None
        assert "inline_keyboard" in result
    
    def test_get_buttons_for_context_invalid(self):
        """Test get_buttons_for_context with invalid context."""
        result = TelegramButtons.get_buttons_for_context("invalid_context")
        
        assert result is None
    
    def test_get_buttons_for_context_missing_kwargs(self):
        """Test get_buttons_for_context with missing required kwargs."""
        # appointment_booked requires appointment_id
        result = TelegramButtons.get_buttons_for_context("appointment_booked")
        
        assert result is None


@pytest.mark.unit
@pytest.mark.service
class TestButtonCallbackHandler:
    """Test ButtonCallbackHandler class."""
    
    def test_parse_callback_data_simple(self):
        """Test parsing simple callback data."""
        callback_data = "action:book_appointment"
        result = ButtonCallbackHandler.parse_callback_data(callback_data)
        
        assert result["action"] == "book_appointment"
        assert result["params"] == []
    
    def test_parse_callback_data_with_params(self):
        """Test parsing callback data with parameters."""
        callback_data = "action:view_appointment:123"
        result = ButtonCallbackHandler.parse_callback_data(callback_data)
        
        assert result["action"] == "view_appointment"
        assert result["params"] == ["123"]
    
    def test_parse_callback_data_with_multiple_params(self):
        """Test parsing callback data with multiple parameters."""
        callback_data = "action:reschedule:123:456"
        result = ButtonCallbackHandler.parse_callback_data(callback_data)
        
        assert result["action"] == "reschedule"
        assert result["params"] == ["123", "456"]
    
    def test_parse_callback_data_invalid(self):
        """Test parsing invalid callback data."""
        callback_data = "invalid"
        result = ButtonCallbackHandler.parse_callback_data(callback_data)
        
        assert result["action"] == "unknown"
        assert result["params"] == []
    
    def test_get_action_message_book_appointment(self):
        """Test get_action_message for book_appointment."""
        result = ButtonCallbackHandler.get_action_message("book_appointment", [])
        
        assert result == "אני רוצה לקבוע תור"
    
    def test_get_action_message_my_appointments(self):
        """Test get_action_message for my_appointments."""
        result = ButtonCallbackHandler.get_action_message("my_appointments", [])
        
        assert result == "תראה לי את התורים שלי"
    
    def test_get_action_message_view_appointment(self):
        """Test get_action_message for view_appointment with params."""
        result = ButtonCallbackHandler.get_action_message("view_appointment", ["123"])
        
        assert "123" in result
        assert "תראה לי" in result
    
    def test_get_action_message_cancel_appointment(self):
        """Test get_action_message for cancel_appointment with params."""
        result = ButtonCallbackHandler.get_action_message("cancel_appointment", ["456"])
        
        assert "456" in result
        assert "לבטל" in result
    
    def test_get_action_message_reschedule(self):
        """Test get_action_message for reschedule with params."""
        result = ButtonCallbackHandler.get_action_message("reschedule", ["789"])
        
        assert "789" in result
        assert "לשנות" in result
    
    def test_get_action_message_confirm_arrival(self):
        """Test get_action_message for confirm_arrival with params."""
        result = ButtonCallbackHandler.get_action_message("confirm_arrival", ["111"])
        
        assert "111" in result
        assert "מאשר" in result
    
    def test_get_action_message_add_calendar(self):
        """Test get_action_message for add_calendar with params."""
        result = ButtonCallbackHandler.get_action_message("add_calendar", ["222"])
        
        assert "222" in result
        assert "ליומן" in result
    
    def test_get_action_message_view_payments(self):
        """Test get_action_message for view_payments."""
        result = ButtonCallbackHandler.get_action_message("view_payments", [])
        
        assert "תשלומים" in result
    
    def test_get_action_message_unknown(self):
        """Test get_action_message for unknown action."""
        result = ButtonCallbackHandler.get_action_message("unknown_action", [])
        
        # Should return default message
        assert result == "המשך"
    
    def test_get_action_message_acknowledge(self):
        """Test get_action_message for acknowledge."""
        result = ButtonCallbackHandler.get_action_message("acknowledge", [])
        
        assert result == "תודה, הבנתי"
    
    def test_get_action_message_directions(self):
        """Test get_action_message for directions."""
        result = ButtonCallbackHandler.get_action_message("directions", [])
        
        assert "מגיעים" in result
    
    def test_get_action_message_main_menu(self):
        """Test get_action_message for main_menu."""
        result = ButtonCallbackHandler.get_action_message("main_menu", [])
        
        assert result == "תפריט ראשי"

