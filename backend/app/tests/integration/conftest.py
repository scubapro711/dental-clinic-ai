"""
Pytest configuration for integration tests.

Provides fixtures and mocks for integration testing.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture(scope="session", autouse=True)
def mock_external_services():
    """Mock external services for integration tests."""
    with patch('smtplib.SMTP') as mock_smtp:
        
        mock_smtp.return_value = MagicMock()
        
        yield {
            'smtp': mock_smtp
        }

