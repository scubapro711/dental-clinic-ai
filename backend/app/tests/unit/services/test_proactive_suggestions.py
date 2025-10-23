"""Unit Tests for Proactive Suggestions Service"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta

from app.services.proactive_suggestions import ProactiveSuggestionsService, SuggestionType


@pytest.fixture
def mock_db():
    return Mock()


@pytest.fixture
def service(mock_db):
    return ProactiveSuggestionsService(mock_db)


@pytest.mark.unit
@pytest.mark.services
class TestProactiveSuggestionsService:
    """Test Proactive Suggestions Service."""
    
    def test_init(self, mock_db):
        """Test service initialization."""
        service = ProactiveSuggestionsService(mock_db)
        assert service.db == mock_db
        assert service.conversation_manager is not None
    
    @patch('app.services.proactive_suggestions.ConversationManager')
    def test_get_suggestions_no_conversation(self, mock_cm, service):
        """Test getting suggestions for non-existent conversation."""
        service.conversation_manager.get_conversation = Mock(return_value=None)
        
        suggestions = service.get_suggestions(uuid4())
        
        assert suggestions == []
    
    @patch('app.services.proactive_suggestions.ConversationManager')
    def test_get_suggestions_with_limit(self, mock_cm, service):
        """Test getting suggestions with limit."""
        mock_conv = Mock()
        service.conversation_manager.get_conversation = Mock(return_value=mock_conv)
        service._get_appointment_reminders = Mock(return_value=[
            {"type": "reminder1", "priority": 10},
            {"type": "reminder2", "priority": 9},
            {"type": "reminder3", "priority": 8},
            {"type": "reminder4", "priority": 7}
        ])
        service._get_checkup_reminders = Mock(return_value=[])
        service._get_treatment_plan_suggestions = Mock(return_value=[])
        service._get_payment_reminders = Mock(return_value=[])
        service._get_follow_up_suggestions = Mock(return_value=[])
        service._get_feedback_requests = Mock(return_value=[])
        service._get_contextual_suggestions = Mock(return_value=[])
        
        suggestions = service.get_suggestions(uuid4(), limit=2)
        
        assert len(suggestions) == 2
        assert suggestions[0]["priority"] == 10
        assert suggestions[1]["priority"] == 9
    
    def test_get_appointment_reminders(self, service):
        """Test getting appointment reminders."""
        mock_conv = Mock()
        mock_conv.patient_id = uuid4()
        result = service._get_appointment_reminders(mock_conv)
        assert isinstance(result, list)
    
    def test_get_checkup_reminders(self, service):
        """Test getting checkup reminders."""
        mock_conv = Mock()
        mock_conv.patient_id = uuid4()
        result = service._get_checkup_reminders(mock_conv)
        assert isinstance(result, list)
    
    def test_get_treatment_plan_suggestions(self, service):
        """Test getting treatment plan suggestions."""
        mock_conv = Mock()
        result = service._get_treatment_plan_suggestions(mock_conv)
        assert isinstance(result, list)
    
    def test_get_payment_reminders(self, service):
        """Test getting payment reminders."""
        mock_conv = Mock()
        result = service._get_payment_reminders(mock_conv)
        assert isinstance(result, list)
    
    def test_get_follow_up_suggestions(self, service):
        """Test getting follow-up suggestions."""
        mock_conv = Mock()
        result = service._get_follow_up_suggestions(mock_conv)
        assert isinstance(result, list)
    
    def test_get_feedback_requests(self, service):
        """Test getting feedback requests."""
        mock_conv = Mock()
        result = service._get_feedback_requests(mock_conv)
        assert isinstance(result, list)
    
    def test_get_contextual_suggestions(self, service):  
        """Test getting contextual suggestions."""
        from app.models.message import MessageRole
        mock_msg = Mock()
        mock_msg.content = "test message"
        mock_msg.role = MessageRole.USER
        mock_conv = Mock()
        mock_conv.id = uuid4()
        # Mock the conversation_manager.get_conversation_history to return messages
        service.conversation_manager = Mock()
        service.conversation_manager.get_conversation_history = Mock(return_value=[mock_msg])
        result = service._get_contextual_suggestions(mock_conv)
        assert isinstance(result, list)
    
    def test_suggestion_type_constants(self):
        """Test suggestion type constants."""
        assert SuggestionType.APPOINTMENT_REMINDER == "appointment_reminder"
        assert SuggestionType.SCHEDULE_CHECKUP == "schedule_checkup"
        assert SuggestionType.REVIEW_TREATMENT_PLAN == "review_treatment_plan"
        assert SuggestionType.PAYMENT_DUE == "payment_due"
        assert SuggestionType.PRESCRIPTION_REFILL == "prescription_refill"
        assert SuggestionType.FOLLOW_UP == "follow_up"
        assert SuggestionType.FEEDBACK_REQUEST == "feedback_request"
        assert SuggestionType.SPECIAL_OFFER == "special_offer"

