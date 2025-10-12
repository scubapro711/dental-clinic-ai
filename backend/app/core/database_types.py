"""
Custom database types for cross-database compatibility.

This module provides type decorators that work across different databases,
particularly for UUID support in SQLite.
"""

from sqlalchemy import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class UUID(TypeDecorator):
    """
    Platform-independent UUID type.
    
    Uses PostgreSQL's UUID type when available, otherwise uses
    CHAR(36) storing as stringified UUIDs.
    
    This allows the same models to work with both PostgreSQL (production)
    and SQLite (testing).
    """
    
    impl = CHAR
    cache_ok = True
    
    def __init__(self, as_uuid=True, *args, **kwargs):
        """
        Initialize UUID type.
        
        Args:
            as_uuid: Whether to return UUID objects (True) or strings (False)
        """
        super().__init__(*args, **kwargs)
        self.as_uuid = as_uuid
    
    def load_dialect_impl(self, dialect):
        """Load the appropriate type for the dialect."""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=self.as_uuid))
        else:
            return dialect.type_descriptor(CHAR(36))
    
    def process_bind_param(self, value, dialect):
        """Convert UUID to string for non-PostgreSQL databases."""
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)
    
    def process_result_value(self, value, dialect):
        """Convert string back to UUID for non-PostgreSQL databases."""
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            else:
                return value
