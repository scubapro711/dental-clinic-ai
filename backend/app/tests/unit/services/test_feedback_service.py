"""
Unit Tests for Feedback Service

Tests for app.services.feedback_service module including:
- Adding feedback (thumbs up/down, ratings, comments)
- Positive feedback detection
- Score calculation
- Training data generation
- Feedback statistics
- Training data export to JSONL
- Conversation feedback retrieval
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from datetime import datetime
import json

from app.services.feedback_service import FeedbackService, FeedbackType


@pytest.fixture
def mock_feedback_db():
    """Create a mock feedback database."""
    db = Mock()
    db.add_feedback.return_value = "feedback_123"
    db.add_training_example.return_value = None
    db.get_feedback_stats.return_value = {
        "total_feedback": 10,
        "by_type": {
            "thumbs_up": 5,
            "thumbs_down": 3,
            "rating": 2
        },
        "training_examples": 7,
        "high_quality_examples": 5,
        "by_agent": {
            "alex": 4,
            "marcus": 3,
            "sophia": 3
        }
    }
    db.get_training_examples.return_value = [
        {
            "system_prompt": "You are Alex...",
            "user_message": "I need an appointment",
            "assistant_response": "I'd be happy to help you schedule an appointment.",
            "agent_name": "alex",
            "score": 5,
            "created_at": "2025-10-24T10:00:00"
        }
    ]
    db.get_feedback.return_value = [
        {
            "id": "feedback_123",
            "conversation_id": "conv_123",
            "message_id": "msg_123",
            "feedback_type": "thumbs_up",
            "feedback_value": True,
            "created_at": "2025-10-24T10:00:00"
        }
    ]
    return db


@pytest.fixture
def feedback_service(mock_feedback_db):
    """Create feedback service with mocked database."""
    with patch("app.services.feedback_service.feedback_db", mock_feedback_db):
        service = FeedbackService()
        return service


@pytest.mark.unit
@pytest.mark.service
class TestAddFeedback:
    """Test add_feedback method."""
    
    def test_add_thumbs_up_feedback(self, feedback_service, mock_feedback_db):
        """Test adding thumbs up feedback."""
        result = feedback_service.add_feedback(
            conversation_id="conv_123",
            message_id="msg_123",
            user_message="I need help",
            agent_response="I'm here to help!",
            agent_name="alex",
            feedback_type=FeedbackType.THUMBS_UP,
            feedback_value=True
        )
        
        assert result["conversation_id"] == "conv_123"
        assert result["message_id"] == "msg_123"
        assert result["feedback_id"] == "feedback_123"
        assert "timestamp" in result
        
        # Should add to database
        mock_feedback_db.add_feedback.assert_called_once()
        
        # Should add to training examples (positive feedback)
        mock_feedback_db.add_training_example.assert_called_once()
    
    def test_add_thumbs_down_feedback(self, feedback_service, mock_feedback_db):
        """Test adding thumbs down feedback."""
        result = feedback_service.add_feedback(
            conversation_id="conv_123",
            message_id="msg_123",
            user_message="I need help",
            agent_response="Sorry, I can't help.",
            agent_name="alex",
            feedback_type=FeedbackType.THUMBS_DOWN,
            feedback_value=True
        )
        
        assert result["feedback_id"] == "feedback_123"
        
        # Should add to database
        mock_feedback_db.add_feedback.assert_called_once()
        
        # Should NOT add to training examples (negative feedback)
        mock_feedback_db.add_training_example.assert_not_called()
    
    def test_add_high_rating_feedback(self, feedback_service, mock_feedback_db):
        """Test adding high rating (4-5 stars)."""
        result = feedback_service.add_feedback(
            conversation_id="conv_123",
            message_id="msg_123",
            user_message="Great service!",
            agent_response="Thank you!",
            agent_name="alex",
            feedback_type=FeedbackType.RATING,
            feedback_value=5
        )
        
        assert result["feedback_id"] == "feedback_123"
        
        # Should add to training examples (high rating)
        mock_feedback_db.add_training_example.assert_called_once()
    
    def test_add_low_rating_feedback(self, feedback_service, mock_feedback_db):
        """Test adding low rating (1-3 stars)."""
        result = feedback_service.add_feedback(
            conversation_id="conv_123",
            message_id="msg_123",
            user_message="Not helpful",
            agent_response="Sorry about that.",
            agent_name="alex",
            feedback_type=FeedbackType.RATING,
            feedback_value=2
        )
        
        assert result["feedback_id"] == "feedback_123"
        
        # Should NOT add to training examples (low rating)
        mock_feedback_db.add_training_example.assert_not_called()


@pytest.mark.unit
@pytest.mark.service
class TestPositiveFeedbackDetection:
    """Test _is_positive_feedback method."""
    
    def test_thumbs_up_is_positive(self, feedback_service):
        """Test that thumbs up is positive."""
        assert feedback_service._is_positive_feedback(FeedbackType.THUMBS_UP, True) is True
    
    def test_thumbs_down_is_not_positive(self, feedback_service):
        """Test that thumbs down is not positive."""
        assert feedback_service._is_positive_feedback(FeedbackType.THUMBS_DOWN, True) is False
    
    def test_high_rating_is_positive(self, feedback_service):
        """Test that 4-5 stars is positive."""
        assert feedback_service._is_positive_feedback(FeedbackType.RATING, 4) is True
        assert feedback_service._is_positive_feedback(FeedbackType.RATING, 5) is True
    
    def test_low_rating_is_not_positive(self, feedback_service):
        """Test that 1-3 stars is not positive."""
        assert feedback_service._is_positive_feedback(FeedbackType.RATING, 1) is False
        assert feedback_service._is_positive_feedback(FeedbackType.RATING, 2) is False
        assert feedback_service._is_positive_feedback(FeedbackType.RATING, 3) is False


@pytest.mark.unit
@pytest.mark.service
class TestScoreCalculation:
    """Test _calculate_score method."""
    
    def test_thumbs_up_score(self, feedback_service):
        """Test that thumbs up = 5 stars."""
        assert feedback_service._calculate_score(FeedbackType.THUMBS_UP, True) == 5
    
    def test_rating_score(self, feedback_service):
        """Test that rating returns the value."""
        assert feedback_service._calculate_score(FeedbackType.RATING, 5) == 5
        assert feedback_service._calculate_score(FeedbackType.RATING, 4) == 4
        assert feedback_service._calculate_score(FeedbackType.RATING, 3) == 3


@pytest.mark.unit
@pytest.mark.service
class TestFeedbackStats:
    """Test get_feedback_stats method."""
    
    def test_get_feedback_stats(self, feedback_service):
        """Test getting feedback statistics."""
        stats = feedback_service.get_feedback_stats()
        
        assert stats["total_feedback"] == 10
        assert stats["thumbs_up"] == 5
        assert stats["thumbs_down"] == 3
        assert stats["ratings"] == 2
        assert stats["training_examples"] == 7
        assert stats["high_quality_examples"] == 5
        assert "by_agent" in stats
        assert stats["ready_for_finetuning"] is False  # Need 10 examples, have 5


@pytest.mark.unit
@pytest.mark.service
class TestTrainingData:
    """Test get_training_data method."""
    
    def test_get_training_data(self, feedback_service, mock_feedback_db):
        """Test getting training data."""
        training_data = feedback_service.get_training_data()
        
        assert len(training_data) == 1
        
        example = training_data[0]
        assert "messages" in example
        assert len(example["messages"]) == 3
        
        # Check message structure
        assert example["messages"][0]["role"] == "system"
        assert example["messages"][1]["role"] == "user"
        assert example["messages"][2]["role"] == "assistant"
        
        assert example["agent_name"] == "alex"
        assert example["score"] == 5


@pytest.mark.unit
@pytest.mark.service
class TestSystemPrompts:
    """Test _get_system_prompt method."""
    
    def test_get_alex_system_prompt(self, feedback_service):
        """Test getting Alex's system prompt."""
        prompt = feedback_service._get_system_prompt("alex")
        assert "Alex" in prompt
        assert "patient care" in prompt.lower()
    
    def test_get_cfo_system_prompt(self, feedback_service):
        """Test getting CFO (Marcus) system prompt."""
        prompt = feedback_service._get_system_prompt("cfo")
        assert "Marcus" in prompt
        assert "CFO" in prompt
    
    def test_get_default_system_prompt(self, feedback_service):
        """Test getting default system prompt for unknown agent."""
        prompt = feedback_service._get_system_prompt("unknown_agent")
        assert "helpful ai assistant" in prompt.lower()

