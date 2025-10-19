"""
Telegram Rich Message Templates

Pre-formatted, rich message templates for common scenarios.
Makes messages more professional and easier to read.

Reference: TELEGRAM_INTEGRATION_COMPLETE_SPEC.md
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from app.services.telegram_buttons import TelegramButtons


class TelegramTemplates:
    """Rich message templates for Telegram."""
    
    @staticmethod
    def appointment_confirmation(
        appointment_data: Dict[str, Any],
        clinic_name: str,
    ) -> Dict[str, Any]:
        """
        Rich template for appointment confirmation.
        
        Args:
            appointment_data: Appointment details
            clinic_name: Name of the clinic
            
        Returns:
            Message with text and buttons
        """
        date = appointment_data.get("date", "")
        time = appointment_data.get("time", "")
        doctor = appointment_data.get("doctor", "")
        treatment = appointment_data.get("treatment", "")
        appointment_id = appointment_data.get("id")
        
        text = f"""
✅ *תור אושר בהצלחה!*

📅 *תאריך:* {date}
🕐 *שעה:* {time}
👨‍⚕️ *רופא:* {doctor}
🦷 *טיפול:* {treatment}
🏥 *מרפאה:* {clinic_name}

תקבל תזכורת יום לפני התור 🔔

_מספר תור: {appointment_id}_
"""
        
        buttons = TelegramButtons.appointment_booked_buttons(appointment_id)
        
        return {
            "text": text.strip(),
            "parse_mode": "Markdown",
            "reply_markup": buttons,
        }
    
    @staticmethod
    def appointment_reminder(
        appointment_data: Dict[str, Any],
        clinic_name: str,
        clinic_address: str,
        hours_until: int = 24,
    ) -> Dict[str, Any]:
        """
        Rich template for appointment reminder.
        
        Args:
            appointment_data: Appointment details
            clinic_name: Name of the clinic
            clinic_address: Clinic address
            hours_until: Hours until appointment
            
        Returns:
            Message with text and buttons
        """
        date = appointment_data.get("date", "")
        time = appointment_data.get("time", "")
        doctor = appointment_data.get("doctor", "")
        appointment_id = appointment_data.get("id")
        
        if hours_until == 24:
            reminder_text = "⏰ *תזכורת - תור מחר!*"
        elif hours_until <= 2:
            reminder_text = "🚨 *תזכורת דחופה - תור בעוד שעתיים!*"
        else:
            reminder_text = f"⏰ *תזכורת - תור בעוד {hours_until} שעות!*"
        
        text = f"""
{reminder_text}

📅 *תאריך:* {date}
🕐 *שעה:* {time}
👨‍⚕️ *רופא:* {doctor}
🏥 *מרפאה:* {clinic_name}
📍 *כתובת:* {clinic_address}

אנא אשר הגעה או עדכן אם יש צורך בשינוי.

_מספר תור: {appointment_id}_
"""
        
        buttons = TelegramButtons.appointment_reminder_buttons(appointment_id)
        
        return {
            "text": text.strip(),
            "parse_mode": "Markdown",
            "reply_markup": buttons,
        }
    
    @staticmethod
    def appointment_cancelled(
        appointment_data: Dict[str, Any],
        cancelled_by: str = "patient",
    ) -> Dict[str, Any]:
        """
        Rich template for appointment cancellation.
        
        Args:
            appointment_data: Appointment details
            cancelled_by: Who cancelled (patient/clinic)
            
        Returns:
            Message with text and buttons
        """
        date = appointment_data.get("date", "")
        time = appointment_data.get("time", "")
        
        if cancelled_by == "clinic":
            text = f"""
❌ *התור בוטל על ידי המרפאה*

📅 *תאריך:* {date}
🕐 *שעה:* {time}

אנו מתנצלים על אי הנוחות.
נשמח לקבוע לך תור חלופי.
"""
        else:
            text = f"""
✅ *התור בוטל בהצלחה*

📅 *תאריך:* {date}
🕐 *שעה:* {time}

אם תרצה לקבוע תור חדש, אני כאן לעזור! 😊
"""
        
        buttons = TelegramButtons.main_menu_button()
        
        return {
            "text": text.strip(),
            "parse_mode": "Markdown",
            "reply_markup": buttons,
        }
    
    @staticmethod
    def payment_receipt(
        payment_data: Dict[str, Any],
        clinic_name: str,
        receipt_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Rich template for payment receipt.
        
        Args:
            payment_data: Payment details
            clinic_name: Name of the clinic
            receipt_url: URL to download receipt PDF
            
        Returns:
            Message with text and buttons
        """
        amount = payment_data.get("amount", 0)
        date = payment_data.get("date", "")
        method = payment_data.get("method", "")
        treatment = payment_data.get("treatment", "")
        payment_id = payment_data.get("id")
        
        text = f"""
💳 *קבלה על תשלום*

💰 *סכום:* ₪{amount:,.2f}
📅 *תאריך:* {date}
💳 *אמצעי תשלום:* {method}
🦷 *טיפול:* {treatment}
🏥 *מרפאה:* {clinic_name}

תודה על התשלום! 🙏

_מספר קבלה: {payment_id}_
"""
        
        buttons = TelegramButtons.payment_receipt_buttons(payment_id, receipt_url)
        
        return {
            "text": text.strip(),
            "parse_mode": "Markdown",
            "reply_markup": buttons,
        }
    
    @staticmethod
    def appointment_list(
        appointments: List[Dict[str, Any]],
        patient_name: str,
    ) -> Dict[str, Any]:
        """
        Rich template for appointment list.
        
        Args:
            appointments: List of appointments
            patient_name: Patient name
            
        Returns:
            Message with text and buttons
        """
        if not appointments:
            text = f"""
📅 *התורים שלך*

שלום {patient_name}! 👋

אין לך תורים קרובים כרגע.

רוצה לקבוע תור? 😊
"""
            buttons = TelegramButtons.welcome_buttons()
        else:
            text = f"📅 *התורים שלך*\n\nשלום {patient_name}! 👋\n\nיש לך {len(appointments)} תורים קרובים:\n\n"
            
            for i, apt in enumerate(appointments[:5], 1):
                date = apt.get("date", "")
                time = apt.get("time", "")
                doctor = apt.get("doctor", "")
                treatment = apt.get("treatment", "")
                
                text += f"{i}. *{date}* בשעה *{time}*\n"
                text += f"   👨‍⚕️ {doctor} | 🦷 {treatment}\n\n"
            
            if len(appointments) > 5:
                text += f"_ועוד {len(appointments) - 5} תורים נוספים..._\n\n"
            
            text += "לחץ על תור לפרטים נוספים."
            
            buttons = TelegramButtons.appointment_list_buttons(appointments)
        
        return {
            "text": text.strip(),
            "parse_mode": "Markdown",
            "reply_markup": buttons,
        }
    
    @staticmethod
    def appointment_details(
        appointment_data: Dict[str, Any],
        clinic_name: str,
        clinic_address: str,
        clinic_phone: str,
    ) -> Dict[str, Any]:
        """
        Rich template for detailed appointment view.
        
        Args:
            appointment_data: Appointment details
            clinic_name: Name of the clinic
            clinic_address: Clinic address
            clinic_phone: Clinic phone
            
        Returns:
            Message with text and buttons
        """
        date = appointment_data.get("date", "")
        time = appointment_data.get("time", "")
        doctor = appointment_data.get("doctor", "")
        treatment = appointment_data.get("treatment", "")
        duration = appointment_data.get("duration", 30)
        notes = appointment_data.get("notes", "")
        appointment_id = appointment_data.get("id")
        
        text = f"""
📋 *פרטי התור*

📅 *תאריך:* {date}
🕐 *שעה:* {time}
⏱️ *משך:* {duration} דקות
👨‍⚕️ *רופא:* {doctor}
🦷 *טיפול:* {treatment}

🏥 *מרפאה:* {clinic_name}
📍 *כתובת:* {clinic_address}
📞 *טלפון:* {clinic_phone}
"""
        
        if notes:
            text += f"\n📝 *הערות:* {notes}\n"
        
        text += f"\n_מספר תור: {appointment_id}_"
        
        # Check if cancellation is allowed (not within 24 hours)
        can_cancel = True  # TODO: Calculate based on appointment time
        
        buttons = TelegramButtons.appointment_details_buttons(appointment_id, can_cancel)
        
        return {
            "text": text.strip(),
            "parse_mode": "Markdown",
            "reply_markup": buttons,
        }
    
    @staticmethod
    def contact_info(
        clinic_name: str,
        clinic_address: str,
        clinic_phone: str,
        clinic_email: Optional[str] = None,
        working_hours: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Rich template for clinic contact information.
        
        Args:
            clinic_name: Name of the clinic
            clinic_address: Clinic address
            clinic_phone: Clinic phone
            clinic_email: Clinic email
            working_hours: Working hours text
            
        Returns:
            Message with text and buttons
        """
        text = f"""
📞 *פרטי התקשרות*

🏥 *{clinic_name}*

📍 *כתובת:*
{clinic_address}

📞 *טלפון:*
{clinic_phone}
"""
        
        if clinic_email:
            text += f"\n📧 *אימייל:*\n{clinic_email}\n"
        
        if working_hours:
            text += f"\n🕐 *שעות פעילות:*\n{working_hours}\n"
        
        text += "\nנשמח לעזור! 😊"
        
        buttons = TelegramButtons.contact_info_buttons(clinic_phone, clinic_address)
        
        return {
            "text": text.strip(),
            "parse_mode": "Markdown",
            "reply_markup": buttons,
        }
    
    @staticmethod
    def error_message(
        error_type: str = "general",
        custom_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Rich template for error messages.
        
        Args:
            error_type: Type of error (general, appointment_not_found, etc.)
            custom_message: Custom error message
            
        Returns:
            Message with text and buttons
        """
        error_messages = {
            "general": "😔 אופס! משהו השתבש.\n\nנסה שוב או פנה למרפאה.",
            "appointment_not_found": "😔 לא מצאתי את התור.\n\nייתכן שהוא כבר בוטל או שהמספר שגוי.",
            "no_appointments": "📅 אין לך תורים קרובים.\n\nרוצה לקבוע תור?",
            "booking_failed": "😔 לא הצלחתי לקבוע את התור.\n\nנסה שוב או פנה למרפאה.",
            "payment_failed": "😔 התשלום נכשל.\n\nנסה שוב או פנה למרפאה.",
        }
        
        text = custom_message or error_messages.get(error_type, error_messages["general"])
        
        buttons = TelegramButtons.main_menu_button()
        
        return {
            "text": text,
            "parse_mode": "Markdown",
            "reply_markup": buttons,
        }
    
    @staticmethod
    def get_template(
        template_name: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Get template by name with parameters.
        
        Args:
            template_name: Name of the template
            **kwargs: Template-specific parameters
            
        Returns:
            Formatted message or None
        """
        template_map = {
            "appointment_confirmation": TelegramTemplates.appointment_confirmation,
            "appointment_reminder": TelegramTemplates.appointment_reminder,
            "appointment_cancelled": TelegramTemplates.appointment_cancelled,
            "payment_receipt": TelegramTemplates.payment_receipt,
            "appointment_list": TelegramTemplates.appointment_list,
            "appointment_details": TelegramTemplates.appointment_details,
            "contact_info": TelegramTemplates.contact_info,
            "error_message": TelegramTemplates.error_message,
        }
        
        template_func = template_map.get(template_name)
        if not template_func:
            return None
        
        try:
            return template_func(**kwargs)
        except TypeError:
            # Missing required kwargs
            return None


# Export main class
__all__ = ["TelegramTemplates"]

