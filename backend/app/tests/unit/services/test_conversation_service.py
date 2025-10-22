"""Unit Tests for Conversation Service"""
import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.services.conversation_service import ConversationService

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def service(mock_db):
    return ConversationService(db=mock_db)

@pytest.mark.unit
@pytest.mark.services
class TestInit:
    def test_init(self, mock_db):
        s = ConversationService(db=mock_db)
        assert s.db == mock_db

@pytest.mark.unit
@pytest.mark.services
class TestOperations:
    def test_create(self, service):
        result = service.create(organization_id=uuid4())
        assert result is not None
    
    def test_get_by_id(self, service):
        service.db.query.return_value.filter.return_value.first.return_value = Mock()
        result = service.get(uuid4())
        assert result is not None
    
    def test_list_conversations(self, service):
        service.db.query.return_value.filter.return_value.all.return_value = []
        result = service.list(organization_id=uuid4())
        assert isinstance(result, list)
    
    def test_update(self, service):
        mock_conv = Mock()
        service.db.query.return_value.filter.return_value.first.return_value = mock_conv
        service.update(uuid4(), status="closed")
        service.db.commit.assert_called()
    
    def test_delete(self, service):
        mock_conv = Mock()
        service.db.query.return_value.filter.return_value.first.return_value = mock_conv
        service.delete(uuid4())
        service.db.delete.assert_called()
