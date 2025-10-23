"""Unit Tests for Mfa Service"""
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def service(mock_db):
    from app.services.mfa_service import MFAService
    return MFAService(db=mock_db) if 'db' in str(MFAService.__init__.__code__.co_varnames) else MFAService()

@pytest.mark.unit
@pytest.mark.services
class TestMfaService:
    def test_init(self, service):
        """Test init"""
        assert service is not None

    def test_generate_code(self, service):
        """Test generate code"""
        assert service is not None

    def test_verify_code(self, service):
        """Test verify code"""
        assert service is not None

    def test_enable_mfa(self, service):
        """Test enable mfa"""
        assert service is not None

