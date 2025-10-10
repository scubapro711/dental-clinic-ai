"""
Telegram Onboarding State Machine

Handles the onboarding flow for new Telegram users.
Guides users through:
1. Welcome
2. Invite code (if needed)
3. Patient identification (existing or new)
4. Data collection (for new patients)
5. Confirmation and linking

Reference: TELEGRAM_INTEGRATION_COMPLETE_SPEC.md
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class OnboardingState(str, Enum):
    """Onboarding states."""
    WELCOME = "welcome"
    NEED_INVITE_CODE = "need_invite_code"
    NEED_PHONE = "need_phone"
    CHECKING_PATIENT = "checking_patient"
    EXISTING_PATIENT_FOUND = "existing_patient_found"
    NEW_PATIENT_NAME = "new_patient_name"
    NEW_PATIENT_BIRTH_DATE = "new_patient_birth_date"
    NEW_PATIENT_EMAIL = "new_patient_email"
    CONFIRM_DETAILS = "confirm_details"
    COMPLETE = "complete"


class TelegramOnboarding:
    """
    State machine for Telegram user onboarding.
    
    Attributes:
        state: Current onboarding state
        data: Collected user data
        organization_id: Organization ID (from invite code)
    """
    
    def __init__(self):
        self.state = OnboardingState.WELCOME
        self.data: Dict[str, Any] = {}
        self.organization_id: Optional[str] = None
    
    def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user message based on current state.
        
        Args:
            message: User's message
            context: Additional context (telegram_user, etc.)
            
        Returns:
            Response dictionary with:
                - response: Text to send to user
                - next_state: Next onboarding state
                - action: Action to perform (if any)
                - complete: Whether onboarding is complete
        """
        handler = getattr(self, f"_handle_{self.state.value}", None)
        if not handler:
            logger.error(f"No handler for state: {self.state}")
            return self._error_response()
        
        return handler(message, context)
    
    def _handle_welcome(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle welcome state."""
        telegram_user = context.get("telegram_user")
        
        # Check if user already has organization
        if telegram_user and telegram_user.organization_id:
            # Skip invite code, go to phone
            self.organization_id = telegram_user.organization_id
            self.state = OnboardingState.NEED_PHONE
            return {
                "response": (
                    "שלום! 👋 אני Alex, קבלן הפנים הדיגיטלי של המרפאה.\n\n"
                    "כדי שאוכל לעזור לך, אני צריך לזהות אותך במערכת.\n"
                    "מה מספר הטלפון שלך? 📱"
                ),
                "next_state": OnboardingState.NEED_PHONE,
                "complete": False,
            }
        
        # Need invite code
        self.state = OnboardingState.NEED_INVITE_CODE
        return {
            "response": (
                "שלום! 👋 אני Alex, קבלן הפנים הדיגיטלי.\n\n"
                "כדי להתחיל, אני צריך את קוד ההזמנה שקיבלת מהמרפאה.\n"
                "אפשר לשלוח לי אותו? 🔑"
            ),
            "next_state": OnboardingState.NEED_INVITE_CODE,
            "complete": False,
        }
    
    def _handle_need_invite_code(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invite code input."""
        # Extract potential invite code
        code = message.strip().upper()
        
        # Validate format (simple check - actual validation in service)
        if len(code) < 6:
            return {
                "response": (
                    "הקוד נראה קצר מדי 🤔\n\n"
                    "קוד ההזמנה צריך להיות לפחות 6 תווים.\n"
                    "נסה שוב?"
                ),
                "next_state": OnboardingState.NEED_INVITE_CODE,
                "complete": False,
            }
        
        # Store code for validation
        self.data["invite_code"] = code
        
        # Request validation action
        self.state = OnboardingState.NEED_PHONE
        return {
            "response": (
                "תודה! 😊 אני בודק את הקוד...\n\n"
                "עכשיו, מה מספר הטלפון שלך? 📱\n"
                "(לדוגמה: 0501234567)"
            ),
            "next_state": OnboardingState.NEED_PHONE,
            "action": "validate_invite_code",
            "complete": False,
        }
    
    def _handle_need_phone(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle phone number input."""
        # Clean phone number
        phone = message.strip().replace("-", "").replace(" ", "")
        
        # Basic validation
        if not phone.isdigit() or len(phone) < 9:
            return {
                "response": (
                    "מספר הטלפון לא נראה תקין 🤔\n\n"
                    "אפשר לשלוח מספר טלפון ישראלי?\n"
                    "(לדוגמה: 0501234567)"
                ),
                "next_state": OnboardingState.NEED_PHONE,
                "complete": False,
            }
        
        # Normalize to Israeli format
        if phone.startswith("972"):
            phone = "0" + phone[3:]
        elif not phone.startswith("0"):
            phone = "0" + phone
        
        self.data["phone"] = phone
        
        # Request patient search
        self.state = OnboardingState.CHECKING_PATIENT
        return {
            "response": "רגע, אני בודק אם אתה כבר במערכת שלנו... 🔍",
            "next_state": OnboardingState.CHECKING_PATIENT,
            "action": "search_patient",
            "complete": False,
        }
    
    def _handle_checking_patient(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle patient search result."""
        patient_found = context.get("patient_found", False)
        patient_data = context.get("patient_data")
        
        if patient_found and patient_data:
            # Existing patient found
            self.data["patient_id"] = patient_data["id"]
            self.data["patient_name"] = patient_data["name"]
            self.state = OnboardingState.EXISTING_PATIENT_FOUND
            
            return {
                "response": (
                    f"מצאתי אותך! 🎉\n\n"
                    f"אתה {patient_data['name']}, נכון?\n"
                    f"(כתוב 'כן' לאישור או 'לא' אם זה לא אתה)"
                ),
                "next_state": OnboardingState.EXISTING_PATIENT_FOUND,
                "complete": False,
            }
        else:
            # New patient
            self.state = OnboardingState.NEW_PATIENT_NAME
            return {
                "response": (
                    "לא מצאתי אותך במערכת, אז זו הפעם הראשונה שלך אצלנו! 😊\n\n"
                    "בוא נרשום אותך. מה השם המלא שלך?"
                ),
                "next_state": OnboardingState.NEW_PATIENT_NAME,
                "complete": False,
            }
    
    def _handle_existing_patient_found(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle confirmation of existing patient."""
        message_lower = message.strip().lower()
        
        if message_lower in ["כן", "yes", "נכון", "זה אני"]:
            # Confirmed - link and complete
            self.state = OnboardingState.COMPLETE
            return {
                "response": (
                    f"מעולה! 🎉\n\n"
                    f"חיברתי אותך למערכת. מעכשיו אני יכול לעזור לך עם:\n"
                    f"📅 קביעת תורים\n"
                    f"💰 בדיקת חשבוניות\n"
                    f"📍 מידע על המרפאה\n\n"
                    f"איך אני יכול לעזור לך היום?"
                ),
                "next_state": OnboardingState.COMPLETE,
                "action": "link_patient",
                "complete": True,
            }
        elif message_lower in ["לא", "no", "זה לא אני"]:
            # Not them - start new patient flow
            self.state = OnboardingState.NEW_PATIENT_NAME
            return {
                "response": (
                    "אוקיי, אז בוא נרשום אותך כמטופל חדש 😊\n\n"
                    "מה השם המלא שלך?"
                ),
                "next_state": OnboardingState.NEW_PATIENT_NAME,
                "complete": False,
            }
        else:
            # Unclear response
            return {
                "response": (
                    "לא הבנתי... 🤔\n\n"
                    f"אתה {self.data.get('patient_name')}, נכון?\n"
                    f"כתוב 'כן' או 'לא'"
                ),
                "next_state": OnboardingState.EXISTING_PATIENT_FOUND,
                "complete": False,
            }
    
    def _handle_new_patient_name(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new patient name input."""
        name = message.strip()
        
        # Basic validation
        if len(name) < 2:
            return {
                "response": "השם נראה קצר מדי 🤔 אפשר את השם המלא שלך?",
                "next_state": OnboardingState.NEW_PATIENT_NAME,
                "complete": False,
            }
        
        self.data["name"] = name
        self.state = OnboardingState.NEW_PATIENT_BIRTH_DATE
        
        return {
            "response": (
                f"נעים מאוד, {name}! 😊\n\n"
                f"מה תאריך הלידה שלך?\n"
                f"(לדוגמה: 15/03/1985)"
            ),
            "next_state": OnboardingState.NEW_PATIENT_BIRTH_DATE,
            "complete": False,
        }
    
    def _handle_new_patient_birth_date(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle birth date input."""
        birth_date_str = message.strip()
        
        # Try to parse date
        try:
            # Support multiple formats
            for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"]:
                try:
                    birth_date = datetime.strptime(birth_date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                raise ValueError("No format matched")
            
            # Validate age (must be reasonable)
            age = (datetime.now() - birth_date).days // 365
            if age < 0 or age > 120:
                raise ValueError("Age out of range")
            
            self.data["birth_date"] = birth_date.strftime("%Y-%m-%d")
            self.state = OnboardingState.NEW_PATIENT_EMAIL
            
            return {
                "response": (
                    "תודה! 📧\n\n"
                    "יש לך כתובת אימייל? (אופציונלי)\n"
                    "(אם אין, כתוב 'אין' או 'דלג')"
                ),
                "next_state": OnboardingState.NEW_PATIENT_EMAIL,
                "complete": False,
            }
            
        except ValueError:
            return {
                "response": (
                    "התאריך לא נראה תקין 🤔\n\n"
                    "אפשר בפורמט: יום/חודש/שנה?\n"
                    "(לדוגמה: 15/03/1985)"
                ),
                "next_state": OnboardingState.NEW_PATIENT_BIRTH_DATE,
                "complete": False,
            }
    
    def _handle_new_patient_email(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email input."""
        message_lower = message.strip().lower()
        
        # Check if user wants to skip
        if message_lower in ["אין", "לא", "דלג", "skip", "no"]:
            self.data["email"] = None
        else:
            # Basic email validation
            email = message.strip()
            if "@" not in email or "." not in email:
                return {
                    "response": (
                        "האימייל לא נראה תקין 🤔\n\n"
                        "אפשר אימייל תקין? או כתוב 'דלג' אם אין לך"
                    ),
                    "next_state": OnboardingState.NEW_PATIENT_EMAIL,
                    "complete": False,
                }
            self.data["email"] = email
        
        # Show confirmation
        self.state = OnboardingState.CONFIRM_DETAILS
        
        confirmation_text = (
            "מעולה! בוא נוודא שהכל נכון:\n\n"
            f"📝 שם: {self.data['name']}\n"
            f"📱 טלפון: {self.data['phone']}\n"
            f"🎂 תאריך לידה: {self.data['birth_date']}\n"
        )
        
        if self.data.get("email"):
            confirmation_text += f"📧 אימייל: {self.data['email']}\n"
        
        confirmation_text += "\nהכל נכון? (כן/לא)"
        
        return {
            "response": confirmation_text,
            "next_state": OnboardingState.CONFIRM_DETAILS,
            "complete": False,
        }
    
    def _handle_confirm_details(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle details confirmation."""
        message_lower = message.strip().lower()
        
        if message_lower in ["כן", "yes", "נכון", "אישור"]:
            # Confirmed - create patient and link
            self.state = OnboardingState.COMPLETE
            return {
                "response": (
                    "נהדר! 🎉\n\n"
                    "יצרתי לך פרופיל במערכת וחיברתי אותך.\n"
                    "מעכשיו אני יכול לעזור לך עם:\n"
                    "📅 קביעת תורים\n"
                    "💰 בדיקת חשבוניות\n"
                    "📍 מידע על המרפאה\n\n"
                    "איך אני יכול לעזור לך היום?"
                ),
                "next_state": OnboardingState.COMPLETE,
                "action": "create_patient",
                "complete": True,
            }
        elif message_lower in ["לא", "no", "תקן"]:
            # Need to fix - restart
            self.state = OnboardingState.NEW_PATIENT_NAME
            self.data = {"phone": self.data["phone"]}  # Keep phone
            return {
                "response": (
                    "אוקיי, בוא נתחיל מחדש 😊\n\n"
                    "מה השם המלא שלך?"
                ),
                "next_state": OnboardingState.NEW_PATIENT_NAME,
                "complete": False,
            }
        else:
            return {
                "response": "לא הבנתי... כתוב 'כן' אם הכל נכון, או 'לא' אם צריך לתקן",
                "next_state": OnboardingState.CONFIRM_DETAILS,
                "complete": False,
            }
    
    def _error_response(self) -> Dict[str, Any]:
        """Return error response."""
        return {
            "response": (
                "אופס! משהו השתבש 😅\n\n"
                "בוא ננסה שוב מההתחלה. שלח /start"
            ),
            "next_state": OnboardingState.WELCOME,
            "complete": False,
        }

