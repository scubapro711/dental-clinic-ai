"""Unit Tests for Fine-Tuning Service"""

import pytest
from unittest.mock import Mock, patch

from app.services.finetuning_service import FineTuningService


@pytest.fixture
def service():
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        return FineTuningService()


@pytest.mark.unit
@pytest.mark.services
class TestFineTuningService:
    """Test Fine-Tuning service."""
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            service = FineTuningService()
            assert service.api_key == 'test-key'
    
    def test_init_without_api_key(self):
        """Test initialization without API key."""
        with patch.dict('os.environ', {}, clear=True):
            service = FineTuningService()
            assert service.api_key is None
    
    def test_get_training_readiness_no_agent(self, service):
        """Test getting training readiness for all agents."""
        readiness = service.get_training_readiness()
        assert isinstance(readiness, dict)
    
    def test_db_connection(self, service):
        """Test database connection exists."""
        assert service.db is not None
    
    def test_api_key_config(self, service):
        """Test API key configuration."""
        assert service.api_key is not None

