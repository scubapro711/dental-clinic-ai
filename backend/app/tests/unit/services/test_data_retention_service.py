"""Unit Tests for Data Retention Service"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.services.data_retention_service import DataRetentionService

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def service(mock_db):
    return DataRetentionService(db=mock_db)

@pytest.mark.unit
@pytest.mark.services
class TestInit:
    def test_init(self, mock_db):
        s = DataRetentionService(db=mock_db)
        assert s.db == mock_db

@pytest.mark.unit
@pytest.mark.services
class TestRetention:
    def test_cleanup_old_data(self, service):
        result = service.cleanup_old_data(days=90)
        assert isinstance(result, dict)
    
    def test_archive_conversations(self, service):
        result = service.archive_conversations(days=180)
        assert isinstance(result, dict)
    
    def test_delete_expired_data(self, service):
        result = service.delete_expired_data()
        assert isinstance(result, dict)
    
    def test_get_retention_policy(self, service):
        policy = service.get_retention_policy()
        assert isinstance(policy, dict)
    
    def test_apply_retention_policy(self, service):
        result = service.apply_retention_policy()
        assert isinstance(result, dict)
