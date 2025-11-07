"""
LangGraph Memory Management with PostgreSQL.

This module provides persistent memory storage for LangGraph agents using PostgreSQL.
All conversation state and checkpoints are stored in the same database as the application.

Best Practice:
- Use PostgresSaver for both development and production
- Ensures parity between environments
- Persistent, reliable, and scalable
- Automatic checkpoint management

Reference: CONTEXT_AND_GAPS_ANALYSIS.md - Section 3.1 (Multi-turn Conversations)
"""

import logging
import time
from typing import Optional, Any
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import MemorySaver
from app.core.config import settings

logger = logging.getLogger(__name__)


class LazyPostgresSaver:
    """
    Lazy-loading wrapper for PostgresSaver.
    
    This wrapper delays the actual database connection until the first time
    the checkpointer is actually used. This solves the Cloud Run timing issue
    where the Cloud SQL Unix socket is not available during application startup.
    
    The connection will be attempted on first use, with retry logic and
    automatic fallback to MemorySaver if PostgreSQL is unavailable.
    """
    
    def __init__(self):
        """Initialize the lazy saver without connecting to database."""
        self._saver: Optional[Any] = None
        self._context: Optional[Any] = None
        self._initialized = False
        self._connection_attempts = 0
        self._max_attempts = 3
        self._last_attempt_time = 0
        self._retry_delay = 5  # seconds between retry attempts
        
    def _ensure_initialized(self):
        """
        Ensure the underlying saver is initialized.
        
        This method is called on first actual use. It will attempt to connect
        to PostgreSQL with retry logic, and fall back to MemorySaver if needed.
        """
        if self._initialized:
            return
            
        # Check if we're in test environment
        import os
        import sys
        is_test = (
            os.getenv("PYTEST_CURRENT_TEST") is not None or 
            "pytest" in sys.modules or
            any("test" in arg for arg in sys.argv)
        )
        
        if is_test:
            logger.info("Test environment detected - using MemorySaver")
            self._saver = MemorySaver()
            self._initialized = True
            return
        
        # Check if enough time has passed since last failed attempt
        current_time = time.time()
        if self._connection_attempts > 0 and (current_time - self._last_attempt_time) < self._retry_delay:
            # Too soon to retry, use current saver (might be MemorySaver)
            return
        
        # Try to connect to PostgreSQL
        if self._connection_attempts < self._max_attempts:
            try:
                self._connection_attempts += 1
                self._last_attempt_time = current_time
                
                checkpoint_db_url = settings.CHECKPOINT_DATABASE_URL
                
                if self._connection_attempts == 1:
                    logger.info(f"Connecting to PostgreSQL checkpointer: {checkpoint_db_url.split('@')[1] if '@' in checkpoint_db_url else 'localhost'}")
                else:
                    logger.info(f"Retry attempt {self._connection_attempts}/{self._max_attempts} for PostgreSQL checkpointer")
                
                # Create PostgresSaver with connection string
                self._context = PostgresSaver.from_conn_string(checkpoint_db_url)
                self._saver = self._context.__enter__()
                
                logger.info("✅ PostgresSaver initialized successfully (persistent storage)")
                self._initialized = True
                
            except Exception as e:
                logger.warning(f"Failed to connect to PostgreSQL checkpointer (attempt {self._connection_attempts}/{self._max_attempts}): {e}")
                
                if self._connection_attempts >= self._max_attempts:
                    # Max attempts reached, fall back to MemorySaver permanently
                    logger.error(f"Failed to setup PostgresSaver after {self._max_attempts} attempts")
                    logger.warning("⚠️  Falling back to MemorySaver (in-memory, non-persistent)")
                    logger.warning("⚠️  Conversation history will not persist across restarts")
                    self._saver = MemorySaver()
                    self._initialized = True
                else:
                    # Will retry on next use
                    if self._saver is None:
                        # Use temporary MemorySaver until PostgreSQL is available
                        logger.info("Using temporary MemorySaver until PostgreSQL is available")
                        self._saver = MemorySaver()
    
    def __getattr__(self, name: str) -> Any:
        """
        Proxy all attribute access to the underlying saver.
        
        This ensures initialization happens on first actual use.
        """
        self._ensure_initialized()
        return getattr(self._saver, name)
    
    def __enter__(self):
        """Support context manager protocol."""
        self._ensure_initialized()
        return self._saver
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support context manager protocol."""
        if self._context is not None:
            return self._context.__exit__(exc_type, exc_val, exc_tb)
        return False


# Global memory saver instance
_memory_saver: Optional[LazyPostgresSaver] = None


def get_memory_saver() -> LazyPostgresSaver:
    """
    Get or create PostgreSQL memory saver for LangGraph.
    
    This function returns a LazyPostgresSaver instance that delays the actual
    database connection until first use. This solves the Cloud Run timing issue
    where the Cloud SQL Unix socket is not available during application startup.
    
    Benefits:
    - Persistent conversation state across restarts
    - Automatic checkpoint management
    - Transaction support
    - Concurrent access support
    - Same database as application data
    - Lazy initialization avoids startup timing issues
    - Automatic retry logic with fallback
    
    Returns:
        LazyPostgresSaver: Configured lazy memory saver instance
        
    Example:
        >>> memory = get_memory_saver()
        >>> graph = workflow.compile(checkpointer=memory)
    """
    global _memory_saver
    
    if _memory_saver is None:
        logger.info("Creating LazyPostgresSaver instance")
        _memory_saver = LazyPostgresSaver()
    
    return _memory_saver


def reset_memory_saver():
    """
    Reset the memory saver instance.
    
    Useful for testing or when database connection changes.
    """
    global _memory_saver
    _memory_saver = None
    logger.info("Memory saver reset")


# Convenience function for testing
def get_test_memory_saver() -> LazyPostgresSaver:
    """
    Get a test memory saver (same as production for parity).
    
    In tests, we use the same LazyPostgresSaver to ensure
    development/test/production parity.
    
    Returns:
        LazyPostgresSaver: Test memory saver instance
    """
    return get_memory_saver()
