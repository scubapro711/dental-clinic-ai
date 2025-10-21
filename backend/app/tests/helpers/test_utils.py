"""
DentaFlow SaaS - Test Utilities
================================
Helper functions and utilities for testing.
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from uuid import uuid4


def assert_valid_uuid(value: str) -> None:
    """Assert that a string is a valid UUID."""
    from uuid import UUID
    try:
        UUID(value)
    except (ValueError, AttributeError):
        raise AssertionError(f"'{value}' is not a valid UUID")


def assert_response_success(response, status_code: int = 200) -> None:
    """Assert that an API response is successful."""
    assert response.status_code == status_code, (
        f"Expected status code {status_code}, got {response.status_code}. "
        f"Response: {response.text}"
    )


def generate_user_data(**overrides) -> Dict[str, Any]:
    """Generate test user data."""
    data = {
        "id": str(uuid4()),
        "email": f"test_{uuid4().hex[:8]}@dentaflow.com",
        "full_name": "Test User",
        "role": "clinic_admin",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.utcnow().isoformat()
    }
    data.update(overrides)
    return data
