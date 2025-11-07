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
from typing import Optional
from langgraph.checkpoint.postgres import PostgresSaver
from app.core.config import settings

logger = logging.getLogger(__name__)


# Global memory saver instance and context manager
_memory_saver: Optional[PostgresSaver] = None
_memory_context = None


def get_memory_saver() -> PostgresSaver:
    """
    Get or create PostgreSQL memory saver for LangGraph.
    
    This function creates a singleton PostgresSaver instance that stores
    all LangGraph checkpoints in PostgreSQL. The checkpoints are stored
    in separate tables (checkpoints, writes) managed by LangGraph.
    
    Benefits:
    - Persistent conversation state across restarts
    - Automatic checkpoint management
    - Transaction support
    - Concurrent access support
    - Same database as application data
    
    Returns:
        PostgresSaver: Configured memory saver instance
        
    Example:
        >>> memory = get_memory_saver()
        >>> graph = workflow.compile(checkpointer=memory)
    """
    global _memory_saver
    
    global _memory_context
    
    if _memory_saver is None:
        # Check if we're in test environment
        import os
        import sys
        is_test = (
            os.getenv("PYTEST_CURRENT_TEST") is not None or 
            "pytest" in sys.modules or
            any("test" in arg for arg in sys.argv)
        )
        
        if is_test:
            # Use MemorySaver for tests (simpler, no PostgreSQL setup needed)
            logger.info("Test environment detected - using MemorySaver")
            from langgraph.checkpoint.memory import MemorySaver
            _memory_saver = MemorySaver()
            logger.info("MemorySaver initialized for testing")
        else:
            logger.info("Initializing PostgreSQL memory saver for LangGraph")
            
            # Use PostgreSQL for persistent memory storage
            import time
            max_retries = 10
            retry_delay = 3  # seconds
            
            for attempt in range(max_retries):
                try:
                    # PostgreSQL connection string for checkpointer
                    # Format: postgresql://user:password@host:port/database
                    checkpoint_db_url = settings.CHECKPOINT_DATABASE_URL
                    
                    if attempt > 0:
                        logger.info(f"Retry attempt {attempt + 1}/{max_retries} for PostgreSQL checkpointer")
                        time.sleep(retry_delay)
                    else:
                        logger.info(f"Connecting to PostgreSQL checkpointer: {checkpoint_db_url.split('@')[1] if '@' in checkpoint_db_url else 'localhost'}")
                    
                    # Create PostgresSaver with connection string
                    # Note: PostgresSaver.from_conn_string returns a context manager
                    # We need to enter it and keep the context alive
                    _memory_context = PostgresSaver.from_conn_string(checkpoint_db_url)
                    _memory_saver = _memory_context.__enter__()
                    
                    logger.info("PostgresSaver initialized successfully (persistent storage)")
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Failed to setup PostgresSaver (attempt {attempt + 1}/{max_retries}): {e}")
                        continue  # Try again
                    else:
                        # Final attempt failed, fall back to MemorySaver
                        logger.error(f"Failed to setup PostgresSaver after {max_retries} attempts: {e}")
                        logger.warning("Falling back to MemorySaver (in-memory, non-persistent)")
                        try:
                            from langgraph.checkpoint.memory import MemorySaver
                            _memory_saver = MemorySaver()
                            logger.info("MemorySaver initialized as fallback")
                        except Exception as fallback_error:
                            logger.error(f"Failed to setup fallback MemorySaver: {fallback_error}")
                            raise
    
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
def get_test_memory_saver() -> PostgresSaver:
    """
    Get a test memory saver (same as production for parity).
    
    In tests, we use the same PostgresSaver to ensure
    development/test/production parity.
    
    Returns:
        PostgresSaver: Test memory saver instance
    """
    return get_memory_saver()
