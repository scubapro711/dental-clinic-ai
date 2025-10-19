"""
Telegram Quick Reply Buttons

Contextual button generation for natural Telegram conversations.
Makes it easy for patients to interact with Alex without typing.

Reference: TELEGRAM_INTEGRATION_COMPLETE_SPEC.md
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class TelegramButtons:
    """Generate contextual quick reply buttons for Telegram."""
    
    @staticmethod
    def welcome_buttons() -> Dict[str, Any]:
        """
        Welcome buttons shown when user starts conversation.
        
        Returns:
            Telegram inline keyboard markup
        """
        return {
            "inline_keyboard": [
                [
                    {"text": "📅 קביעת תור", "callback_data": "action:book_appointment"},
                    {"text": "🔍 התורים שלי", "callback_data": "action:my_appointments"}
                ],
                [
                    {"text": "❓ שאלה כללית", "callback_data": "action:ask_question"},
                    {"text": "📞 פרטי התקשרות", "callback_data": "action:contact_info"}
                ]
            ]
        }
    
    @staticmethod
    def appointment_booked_buttons(appointment_id: int) -> Dict[str, Any]:
        """
        Buttons shown after successfully booking an appointment.
        
        Args:
            appointment_id: ID of the booked appointment
            
        Returns:
            Telegram inline keyboard markup
        """
        return {
            "inline_keyboard": [
                [
                    {"text": "✅ הבנתי, תודה", "callback_data": "action:acknowledge"}
                ],
                [
                    {"text": "🗓️ הוסף ליומן", "callback_data": f"action:add_calendar:{appointment_id}"},
                    {"text": "📍 הוראות הגעה", "callback_data": "action:directions"}
                ]
            ]
        }
    
    @staticmethod
    def appointment_reminder_buttons(appointment_id: int) -> Dict[str, Any]:
        """
        Buttons shown in appointment reminder message.
        
        Args:
            appointment_id: ID of the appointment
            
        Returns:
            Telegram inline keyboard markup
        """
        return {
            "inline_keyboard": [
                [
                    {"text": "✅ מאשר הגעה", "callback_data": f"action:confirm_arrival:{appointment_id}"},
                    {"text": "❌ צריך לבטל", "callback_data": f"action:cancel_appointment:{appointment_id}"}
                ],
                [
                    {"text": "⏰ שנה שעה", "callback_data": f"action:reschedule:{appointment_id}"}
                ]
            ]
        }
    
    @staticmethod
    def appointment_list_buttons(appointments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Buttons for navigating through appointment list.
        
        Args:
            appointments: List of appointments
            
        Returns:
            Telegram inline keyboard markup
        """
        buttons = []
        
        # Add button for each appointment (max 5)
        for i, apt in enumerate(appointments[:5]):
            date_str = apt.get('date', '')
            time_str = apt.get('time', '')
            apt_id = apt.get('id')
            
            buttons.append([
                {"text": f"📅 {date_str} {time_str}", "callback_data": f"action:view_appointment:{apt_id}"}
            ])
        
        # Add "Book new appointment" button
        buttons.append([
            {"text": "➕ קבע תור חדש", "callback_data": "action:book_appointment"}
        ])
        
        return {"inline_keyboard": buttons}
    
    @staticmethod
    def appointment_details_buttons(appointment_id: int, can_cancel: bool = True) -> Dict[str, Any]:
        """
        Buttons for appointment details view.
        
        Args:
            appointment_id: ID of the appointment
            can_cancel: Whether cancellation is allowed
            
        Returns:
            Telegram inline keyboard markup
        """
        buttons = []
        
        if can_cancel:
            buttons.append([
                {"text": "⏰ שנה שעה", "callback_data": f"action:reschedule:{appointment_id}"},
                {"text": "❌ בטל תור", "callback_data": f"action:cancel_appointment:{appointment_id}"}
            ])
        
        buttons.append([
            {"text": "📍 הוראות הגעה", "callback_data": "action:directions"},
            {"text": "🗓️ הוסף ליומן", "callback_data": f"action:add_calendar:{appointment_id}"}
        ])
        
        buttons.append([
            {"text": "🔙 חזרה לרשימה", "callback_data": "action:my_appointments"}
        ])
        
        return {"inline_keyboard": buttons}
    
    @staticmethod
    def payment_receipt_buttons(payment_id: int, receipt_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Buttons shown with payment receipt.
        
        Args:
            payment_id: ID of the payment
            receipt_url: URL to download receipt PDF
            
        Returns:
            Telegram inline keyboard markup
        """
        buttons = []
        
        if receipt_url:
            buttons.append([
                {"text": "📄 הורד קבלה", "url": receipt_url}
            ])
        
        buttons.append([
            {"text": "💳 תשלומים נוספים", "callback_data": "action:view_payments"},
            {"text": "✅ הבנתי", "callback_data": "action:acknowledge"}
        ])
        
        return {"inline_keyboard": buttons}
    
    @staticmethod
    def confirmation_buttons(confirm_action: str, cancel_action: str = "action:cancel") -> Dict[str, Any]:
        """
        Generic confirmation buttons (Yes/No).
        
        Args:
            confirm_action: Callback data for confirmation
            cancel_action: Callback data for cancellation
            
        Returns:
            Telegram inline keyboard markup
        """
        return {
            "inline_keyboard": [
                [
                    {"text": "✅ כן, בטוח", "callback_data": confirm_action},
                    {"text": "❌ לא, ביטול", "callback_data": cancel_action}
                ]
            ]
        }
    
    @staticmethod
    def contact_info_buttons(phone: str, address: str) -> Dict[str, Any]:
        """
        Buttons for clinic contact information.
        
        Args:
            phone: Clinic phone number
            address: Clinic address
            
        Returns:
            Telegram inline keyboard markup
        """
        return {
            "inline_keyboard": [
                [
                    {"text": "📞 התקשר למרפאה", "url": f"tel:{phone}"}
                ],
                [
                    {"text": "📍 פתח ב-Waze", "url": f"https://waze.com/ul?q={address}"},
                    {"text": "🗺️ פתח ב-Google Maps", "url": f"https://maps.google.com/?q={address}"}
                ],
                [
                    {"text": "🔙 חזרה לתפריט", "callback_data": "action:main_menu"}
                ]
            ]
        }
    
    @staticmethod
    def main_menu_button() -> Dict[str, Any]:
        """
        Single button to return to main menu.
        
        Returns:
            Telegram inline keyboard markup
        """
        return {
            "inline_keyboard": [
                [
                    {"text": "🏠 תפריט ראשי", "callback_data": "action:main_menu"}
                ]
            ]
        }
    
    @staticmethod
    def get_buttons_for_context(
        context: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Get appropriate buttons based on conversation context.
        
        Args:
            context: Context identifier (e.g., 'welcome', 'appointment_booked')
            **kwargs: Additional context-specific parameters
            
        Returns:
            Telegram inline keyboard markup or None
        """
        button_map = {
            "welcome": TelegramButtons.welcome_buttons,
            "main_menu": TelegramButtons.welcome_buttons,
            "appointment_booked": TelegramButtons.appointment_booked_buttons,
            "appointment_reminder": TelegramButtons.appointment_reminder_buttons,
            "appointment_list": TelegramButtons.appointment_list_buttons,
            "appointment_details": TelegramButtons.appointment_details_buttons,
            "payment_receipt": TelegramButtons.payment_receipt_buttons,
            "contact_info": TelegramButtons.contact_info_buttons,
        }
        
        button_func = button_map.get(context)
        if not button_func:
            return None
        
        try:
            return button_func(**kwargs)
        except TypeError:
            # Missing required kwargs
            return None


class ButtonCallbackHandler:
    """Handle button callback queries from Telegram."""
    
    @staticmethod
    def parse_callback_data(callback_data: str) -> Dict[str, Any]:
        """
        Parse callback data from button click.
        
        Format: "action:action_name" or "action:action_name:param1:param2"
        
        Args:
            callback_data: Callback data string
            
        Returns:
            Dictionary with action and parameters
        """
        parts = callback_data.split(":")
        
        if len(parts) < 2:
            return {"action": "unknown", "params": []}
        
        return {
            "action": parts[1],
            "params": parts[2:] if len(parts) > 2 else []
        }
    
    @staticmethod
    def get_action_message(action: str, params: List[str]) -> str:
        """
        Convert button action to natural language message for Alex.
        
        This allows us to treat button clicks as if the user typed a message,
        making it seamless for Alex to handle.
        
        Args:
            action: Action name
            params: Action parameters
            
        Returns:
            Natural language message
        """
        action_messages = {
            "book_appointment": "אני רוצה לקבוע תור",
            "my_appointments": "תראה לי את התורים שלי",
            "ask_question": "יש לי שאלה",
            "contact_info": "מה פרטי ההתקשרות של המרפאה?",
            "acknowledge": "תודה, הבנתי",
            "directions": "איך מגיעים למרפאה?",
            "main_menu": "תפריט ראשי",
        }
        
        # Handle actions with parameters
        if action == "view_appointment" and params:
            return f"תראה לי את פרטי התור מספר {params[0]}"
        
        elif action == "cancel_appointment" and params:
            return f"אני רוצה לבטל את התור מספר {params[0]}"
        
        elif action == "reschedule" and params:
            return f"אני רוצה לשנות את התור מספר {params[0]}"
        
        elif action == "confirm_arrival" and params:
            return f"אני מאשר הגעה לתור מספר {params[0]}"
        
        elif action == "add_calendar" and params:
            return f"הוסף את התור מספר {params[0]} ליומן שלי"
        
        elif action == "view_payments":
            return "תראה לי את התשלומים שלי"
        
        # Default message
        return action_messages.get(action, "המשך")


# Export main classes
__all__ = [
    "TelegramButtons",
    "ButtonCallbackHandler",
]

