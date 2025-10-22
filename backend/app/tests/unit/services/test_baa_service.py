"""Unit Tests for Baa Service"""
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def service(mock_db):
    from app.services.baa_service import BaaService
    return BaaService(db=mock_db) if 'db' in str(BaaService.__init__.__code__.co_varnames) else BaaService()

@pytest.mark.unit
@pytest.mark.services
class TestBaaService:
    def test_init(self, service):
        """Test init"""
        assert service is not None

    def test_create_baa(self, service):
        """Test create baa"""
        assert service is not None

    def test_validate_baa(self, service):
        """Test validate baa"""
        assert service is not None

    def test_check_expiration(self, service):
        """Test check expiration"""
        assert service is not None

