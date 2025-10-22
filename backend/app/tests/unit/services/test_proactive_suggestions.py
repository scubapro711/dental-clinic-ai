"""Unit Tests for Proactive Suggestions"""
import pytest
from unittest.mock import Mock, patch
from uuid import uuid4

from app.services.proactive_suggestions import ProactiveSuggestionsService

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def service(mock_db):
    return ProactiveSuggestionsService(db=mock_db)

@pytest.mark.unit
@pytest.mark.services
class TestInit:
    def test_init(self, mock_db):
        s = ProactiveSuggestionsService(db=mock_db)
        assert s.db == mock_db

@pytest.mark.unit
@pytest.mark.services
class TestSuggestions:
    def test_generate_suggestions(self, service):
        suggestions = service.generate_suggestions(conversation_id=uuid4())
        assert isinstance(suggestions, list)
    
    def test_get_appointment_suggestions(self, service):
        suggestions = service.get_appointment_suggestions(patient_id=uuid4())
        assert isinstance(suggestions, list)
    
    def test_get_treatment_suggestions(self, service):
        suggestions = service.get_treatment_suggestions(patient_id=uuid4())
        assert isinstance(suggestions, list)
    
    def test_get_followup_suggestions(self, service):
        suggestions = service.get_followup_suggestions(patient_id=uuid4())
        assert isinstance(suggestions, list)
    
    def test_rank_suggestions(self, service):
        suggestions = [{"score": 0.8}, {"score": 0.9}, {"score": 0.7}]
        ranked = service.rank_suggestions(suggestions)
        assert ranked[0]["score"] >= ranked[1]["score"]
