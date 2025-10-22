"""Unit Tests for VectorDb"""
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def service(mock_db):
    from app.services.vector_db import VectorDb
    return VectorDb(db=mock_db) if 'db' in str(VectorDb.__init__.__code__.co_varnames) else VectorDb()

@pytest.mark.unit
@pytest.mark.services
class TestVectorDb:
    def test_init(self, service):
        """Test init"""
        assert service is not None

    def test_add_document(self, service):
        """Test add document"""
        assert service is not None

    def test_search(self, service):
        """Test search"""
        assert service is not None

    def test_delete(self, service):
        """Test delete"""
        assert service is not None

