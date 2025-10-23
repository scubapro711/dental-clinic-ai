"""
Pytest configuration for integration tests.

Provides fixtures and mocks for integration testing.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys


@pytest.fixture(scope="session", autouse=True)
def mock_database_for_integration():
    """Mock database to avoid UUID/SQLite issues in integration tests."""
    with patch('app.core.database.Base') as mock_base, \
         patch('app.core.database.get_db') as mock_get_db, \
         patch('app.core.database_types.UUID') as mock_uuid:
        
        mock_get_db.return_value = Mock()
        mock_uuid.return_value = Mock()
        
        yield {
            'base': mock_base,
            'get_db': mock_get_db,
            'uuid': mock_uuid
        }


@pytest.fixture(scope="session", autouse=True)
def mock_external_services():
    """Mock external services for integration tests."""
    with patch('smtplib.SMTP') as mock_smtp:
        
        mock_smtp.return_value = MagicMock()
        
        yield {
            'smtp': mock_smtp
        }

