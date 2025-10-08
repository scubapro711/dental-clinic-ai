"""
Proactive Suggestions Service.

Analyzes conversation context and patient data to provide intelligent,
proactive suggestions before the user asks.

Examples:
- "You have an appointment tomorrow at 10:00. Would you like a reminder?"
- "It's been 6 months since your last checkup. Time to schedule?"
- "Your treatment plan is ready. Would you like to review it?"
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
import logging

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.services.conversation_manager import ConversationManager

logger = logging.getLogger(__name__)


class SuggestionType:
    """Types of proactive suggestions."""
    
    APPOINTMENT_REMINDER = "appointment_reminder"
    SCHEDULE_CHECKUP = "schedule_checkup"
    REVIEW_TREATMENT_PLAN = "review_treatment_plan"
    PAYMENT_DUE = "payment_due"
    PRESCRIPTION_REFILL = "prescription_refill"
    FOLLOW_UP = "follow_up"
    FEEDBACK_REQUEST = "feedback_request"
    SPECIAL_OFFER = "special_offer"


class ProactiveSuggestionsService:
    """
    Service for generating proactive suggestions.
    
    Analyzes:
    - Conversation history
    - Patient appointments
    - Treatment history
    - Payment status
    - Time since last visit
    """
    
    def __init__(self, db: Session):
        """
        Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.conversation_manager = ConversationManager(db)
    
    def get_suggestions(
        self,
        conversation_id: UUID,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get proactive suggestions for conversation.
        
        Args:
            conversation_id: Conversation UUID
            limit: Maximum number of suggestions
        
        Returns:
            List of suggestion dictionaries
        """
        conversation = self.conversation_manager.get_conversation(conversation_id)
        
        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found")
            return []
        
        suggestions = []
        
        # Get all suggestion types
        suggestions.extend(self._get_appointment_reminders(conversation))
        suggestions.extend(self._get_checkup_reminders(conversation))
        suggestions.extend(self._get_treatment_plan_suggestions(conversation))
        suggestions.extend(self._get_payment_reminders(conversation))
        suggestions.extend(self._get_follow_up_suggestions(conversation))
        suggestions.extend(self._get_feedback_requests(conversation))
        suggestions.extend(self._get_contextual_suggestions(conversation))
        
        # Sort by priority (higher = more important)
        suggestions.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        # Return top N
        return suggestions[:limit]
    
    def _get_appointment_reminders(
        self,
        conversation: Conversation
    ) -> List[Dict[str, Any]]:
        """Get appointment reminder suggestions."""
        
        suggestions = []
        
        # TODO: Query Odoo for upcoming appointments
        # For now, return mock suggestion
        
        # Check if patient has upcoming appointment in next 24 hours
        # upcoming_appointments = odoo_client.get_patient_appointments(
        #     patient_phone=conversation.patient_phone,
        #     date_from=datetime.now(),
        #     date_to=datetime.now() + timedelta(days=1)
        # )
        
        # Mock: Assume appointment tomorrow at 10:00
        mock_has_appointment = False  # Set to True to test
        
        if mock_has_appointment:
            suggestions.append({
                "type": SuggestionType.APPOINTMENT_REMINDER,
                "priority": 10,  # High priority
                "title": "תזכורת לתור מחר",
                "message": "יש לך תור מחר בשעה 10:00. האם תרצה תזכורת נוספת?",
                "actions": [
                    {
                        "label": "כן, שלח תזכורת",
                        "action": "send_reminder",
                        "data": {"appointment_id": 123}
                    },
                    {
                        "label": "לא צריך",
                        "action": "dismiss"
                    }
                ],
                "metadata": {
                    "appointment_date": "2025-10-09",
                    "appointment_time": "10:00"
                }
            })
        
        return suggestions
    
    def _get_checkup_reminders(
        self,
        conversation: Conversation
    ) -> List[Dict[str, Any]]:
        """Get checkup reminder suggestions."""
        
        suggestions = []
        
        # TODO: Query Odoo for last appointment
        # last_appointment = odoo_client.get_last_appointment(
        #     patient_phone=conversation.patient_phone
        # )
        
        # Mock: Assume last checkup was 6 months ago
        mock_needs_checkup = False  # Set to True to test
        
        if mock_needs_checkup:
            suggestions.append({
                "type": SuggestionType.SCHEDULE_CHECKUP,
                "priority": 8,
                "title": "הגיע הזמן לבדיקה",
                "message": "עברו 6 חודשים מהבדיקה האחרונה. מומלץ לקבוע תור לבדיקה שגרתית.",
                "actions": [
                    {
                        "label": "קבע תור עכשיו",
                        "action": "schedule_appointment",
                        "data": {"treatment_type": "checkup"}
                    },
                    {
                        "label": "הזכר לי בעוד שבוע",
                        "action": "remind_later",
                        "data": {"days": 7}
                    }
                ],
                "metadata": {
                    "last_checkup_date": "2025-04-08",
                    "months_since_checkup": 6
                }
            })
        
        return suggestions
    
    def _get_treatment_plan_suggestions(
        self,
        conversation: Conversation
    ) -> List[Dict[str, Any]]:
        """Get treatment plan suggestions."""
        
        suggestions = []
        
        # TODO: Query Odoo for pending treatment plans
        # treatment_plans = odoo_client.get_pending_treatment_plans(
        #     patient_phone=conversation.patient_phone
        # )
        
        mock_has_treatment_plan = False
        
        if mock_has_treatment_plan:
            suggestions.append({
                "type": SuggestionType.REVIEW_TREATMENT_PLAN,
                "priority": 7,
                "title": "תוכנית הטיפול שלך מוכנה",
                "message": "הרופא הכין עבורך תוכנית טיפול. האם תרצה לעבור עליה?",
                "actions": [
                    {
                        "label": "כן, הצג תוכנית",
                        "action": "show_treatment_plan",
                        "data": {"plan_id": 456}
                    },
                    {
                        "label": "אחר כך",
                        "action": "dismiss"
                    }
                ],
                "metadata": {
                    "plan_id": 456,
                    "created_date": "2025-10-07"
                }
            })
        
        return suggestions
    
    def _get_payment_reminders(
        self,
        conversation: Conversation
    ) -> List[Dict[str, Any]]:
        """Get payment reminder suggestions."""
        
        suggestions = []
        
        # TODO: Query Odoo for unpaid invoices
        # unpaid_invoices = odoo_client.get_unpaid_invoices(
        #     patient_phone=conversation.patient_phone
        # )
        
        mock_has_unpaid = False
        
        if mock_has_unpaid:
            suggestions.append({
                "type": SuggestionType.PAYMENT_DUE,
                "priority": 9,
                "title": "תשלום ממתין",
                "message": "יש לך חשבונית פתוחה בסך 500 ₪. האם תרצה לשלם עכשיו?",
                "actions": [
                    {
                        "label": "שלם עכשיו",
                        "action": "pay_invoice",
                        "data": {"invoice_id": 789, "amount": 500}
                    },
                    {
                        "label": "הצג פרטים",
                        "action": "show_invoice",
                        "data": {"invoice_id": 789}
                    }
                ],
                "metadata": {
                    "invoice_id": 789,
                    "amount": 500,
                    "due_date": "2025-10-15"
                }
            })
        
        return suggestions
    
    def _get_follow_up_suggestions(
        self,
        conversation: Conversation
    ) -> List[Dict[str, Any]]:
        """Get follow-up suggestions after treatment."""
        
        suggestions = []
        
        # TODO: Query Odoo for recent treatments requiring follow-up
        # recent_treatments = odoo_client.get_recent_treatments(
        #     patient_phone=conversation.patient_phone,
        #     days=7
        # )
        
        mock_needs_followup = False
        
        if mock_needs_followup:
            suggestions.append({
                "type": SuggestionType.FOLLOW_UP,
                "priority": 6,
                "title": "מעקב אחרי הטיפול",
                "message": "איך אתה מרגיש אחרי הטיפול מלפני שבוע? יש כאבים או אי נוחות?",
                "actions": [
                    {
                        "label": "הכל בסדר",
                        "action": "followup_ok"
                    },
                    {
                        "label": "יש בעיה",
                        "action": "followup_issue"
                    }
                ],
                "metadata": {
                    "treatment_date": "2025-10-01",
                    "treatment_type": "filling"
                }
            })
        
        return suggestions
    
    def _get_feedback_requests(
        self,
        conversation: Conversation
    ) -> List[Dict[str, Any]]:
        """Get feedback request suggestions."""
        
        suggestions = []
        
        # Check if conversation is completed and no feedback given
        # TODO: Check if feedback already provided
        
        mock_needs_feedback = False
        
        if mock_needs_feedback:
            suggestions.append({
                "type": SuggestionType.FEEDBACK_REQUEST,
                "priority": 3,  # Low priority
                "title": "נשמח לשמוע ממך",
                "message": "איך היתה החוויה שלך? נשמח לקבל משוב קצר.",
                "actions": [
                    {
                        "label": "דרג את השירות",
                        "action": "provide_feedback"
                    },
                    {
                        "label": "אחר כך",
                        "action": "dismiss"
                    }
                ],
                "metadata": {
                    "conversation_id": str(conversation.id)
                }
            })
        
        return suggestions
    
    def _get_contextual_suggestions(
        self,
        conversation: Conversation
    ) -> List[Dict[str, Any]]:
        """Get suggestions based on conversation context."""
        
        suggestions = []
        
        # Get recent messages
        messages = self.conversation_manager.get_conversation_history(
            conversation.id,
            limit=5
        )
        
        if not messages:
            # First message - welcome suggestions
            suggestions.append({
                "type": "welcome",
                "priority": 5,
                "title": "איך אפשר לעזור?",
                "message": "שלום! איך אני יכול לעזור לך היום?",
                "actions": [
                    {
                        "label": "קבע תור",
                        "action": "schedule_appointment"
                    },
                    {
                        "label": "שאל שאלה",
                        "action": "ask_question"
                    },
                    {
                        "label": "בדוק סטטוס תור",
                        "action": "check_appointment"
                    }
                ]
            })
            return suggestions
        
        # Analyze recent messages for keywords
        recent_content = " ".join([
            m.content.lower()
            for m in messages
            if m.role == MessageRole.USER
        ])
        
        # Appointment-related
        if any(word in recent_content for word in ["תור", "appointment", "schedule", "קבע"]):
            suggestions.append({
                "type": "contextual",
                "priority": 6,
                "title": "תורים פנויים",
                "message": "מצאתי כמה תורים פנויים השבוע. רוצה לראות?",
                "actions": [
                    {
                        "label": "כן, הצג תורים",
                        "action": "show_available_slots"
                    }
                ]
            })
        
        # Price-related
        elif any(word in recent_content for word in ["מחיר", "כמה עולה", "price", "cost"]):
            suggestions.append({
                "type": "contextual",
                "priority": 6,
                "title": "מחירון טיפולים",
                "message": "רוצה לראות את המחירון המלא של הטיפולים?",
                "actions": [
                    {
                        "label": "כן, הצג מחירון",
                        "action": "show_price_list"
                    }
                ]
            })
        
        # Pain/emergency
        elif any(word in recent_content for word in ["כאב", "pain", "דחוף", "emergency"]):
            suggestions.append({
                "type": "contextual",
                "priority": 10,  # High priority!
                "title": "תור דחוף",
                "message": "נשמע דחוף. האם תרצה תור בהקדם האפשרי?",
                "actions": [
                    {
                        "label": "כן, תור דחוף",
                        "action": "schedule_urgent"
                    },
                    {
                        "label": "התקשר למרפאה",
                        "action": "call_clinic"
                    }
                ]
            })
        
        return suggestions
    
    def dismiss_suggestion(
        self,
        conversation_id: UUID,
        suggestion_type: str
    ) -> bool:
        """
        Mark suggestion as dismissed.
        
        Args:
            conversation_id: Conversation UUID
            suggestion_type: Type of suggestion
        
        Returns:
            True if successful
        """
        conversation = self.conversation_manager.get_conversation(conversation_id)
        
        if not conversation:
            return False
        
        # Add to dismissed suggestions in state
        state = conversation.langgraph_state or {}
        dismissed = state.get("dismissed_suggestions", [])
        
        if suggestion_type not in dismissed:
            dismissed.append(suggestion_type)
            state["dismissed_suggestions"] = dismissed
            
            self.conversation_manager.update_conversation_state(
                conversation_id=conversation_id,
                state_update=state
            )
        
        logger.info(f"Dismissed suggestion {suggestion_type} for conversation {conversation_id}")
        
        return True
    
    def execute_suggestion_action(
        self,
        conversation_id: UUID,
        action: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute action from suggestion.
        
        Args:
            conversation_id: Conversation UUID
            action: Action name
            data: Action data
        
        Returns:
            Result dictionary
        """
        logger.info(f"Executing action {action} for conversation {conversation_id}")
        
        # Route to appropriate handler
        if action == "schedule_appointment":
            return self._handle_schedule_appointment(conversation_id, data)
        elif action == "send_reminder":
            return self._handle_send_reminder(conversation_id, data)
        elif action == "show_treatment_plan":
            return self._handle_show_treatment_plan(conversation_id, data)
        elif action == "pay_invoice":
            return self._handle_pay_invoice(conversation_id, data)
        elif action == "provide_feedback":
            return self._handle_provide_feedback(conversation_id, data)
        elif action == "dismiss":
            return {"success": True, "message": "הצעה נדחתה"}
        else:
            logger.warning(f"Unknown action: {action}")
            return {"success": False, "error": "Unknown action"}
    
    def _handle_schedule_appointment(
        self,
        conversation_id: UUID,
        data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle schedule appointment action."""
        
        # TODO: Integrate with appointment scheduling
        
        return {
            "success": True,
            "message": "בואו נקבע תור. מתי נוח לך להגיע?",
            "next_step": "ask_preferred_date"
        }
    
    def _handle_send_reminder(
        self,
        conversation_id: UUID,
        data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle send reminder action."""
        
        # TODO: Schedule reminder
        
        return {
            "success": True,
            "message": "תזכורת נשלחה! תקבל הודעה 2 שעות לפני התור."
        }
    
    def _handle_show_treatment_plan(
        self,
        conversation_id: UUID,
        data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle show treatment plan action."""
        
        # TODO: Fetch treatment plan from Odoo
        
        return {
            "success": True,
            "message": "הנה תוכנית הטיפול שלך...",
            "treatment_plan": {
                "plan_id": data.get("plan_id") if data else None,
                "treatments": []
            }
        }
    
    def _handle_pay_invoice(
        self,
        conversation_id: UUID,
        data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle pay invoice action."""
        
        # TODO: Integrate with payment gateway
        
        return {
            "success": True,
            "message": "מעביר אותך לעמוד התשלום...",
            "payment_url": "https://dentaflow.ai/pay/123"
        }
    
    def _handle_provide_feedback(
        self,
        conversation_id: UUID,
        data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle provide feedback action."""
        
        return {
            "success": True,
            "message": "תודה! איך היית מדרג את השירות שלנו מ-1 עד 5?",
            "next_step": "collect_rating"
        }


# Convenience function
def get_proactive_suggestions_service(db: Session) -> ProactiveSuggestionsService:
    """Get ProactiveSuggestionsService instance."""
    return ProactiveSuggestionsService(db)
