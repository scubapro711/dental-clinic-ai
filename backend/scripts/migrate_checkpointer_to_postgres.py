#!/usr/bin/env python3
"""
Migration script to setup PostgreSQL checkpointer for LangGraph.

This script:
1. Creates the necessary tables for LangGraph checkpoints
2. Verifies the connection
3. Provides status information

Usage:
    python scripts/migrate_checkpointer_to_postgres.py
"""

import sys
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from langgraph.checkpoint.postgres import PostgresSaver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Setup PostgreSQL checkpointer tables."""
    
    logger.info("=" * 60)
    logger.info("PostgreSQL Checkpointer Migration")
    logger.info("=" * 60)
    
    # Get checkpoint database URL
    checkpoint_url = settings.CHECKPOINT_DATABASE_URL
    logger.info(f"Checkpoint Database: {checkpoint_url.split('@')[1] if '@' in checkpoint_url else checkpoint_url}")
    
    try:
        # Create PostgresSaver
        logger.info("Creating PostgresSaver...")
        
        # PostgresSaver.from_conn_string returns a context manager
        with PostgresSaver.from_conn_string(checkpoint_url) as saver:
            # Setup tables
            logger.info("Setting up tables...")
            saver.setup()
            
            logger.info("✅ PostgreSQL checkpointer setup complete!")
            logger.info("")
            logger.info("Tables created:")
            logger.info("  - checkpoints: Stores conversation state")
            logger.info("  - writes: Stores pending writes")
            logger.info("")
            logger.info("Next steps:")
            logger.info("  1. Restart the backend server")
            logger.info("  2. Test conversation persistence")
            logger.info("  3. Verify checkpoints are saved")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Failed to setup PostgreSQL checkpointer: {e}")
        logger.error("")
        logger.error("Troubleshooting:")
        logger.error("  1. Check PostgreSQL is running: sudo systemctl status postgresql")
        logger.error("  2. Verify database exists: psql -U dentaflow -d dentaflow_checkpoints")
        logger.error("  3. Check credentials in .env file")
        logger.error("  4. Ensure user has permissions: GRANT ALL ON DATABASE dentaflow_checkpoints TO dentaflow")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

