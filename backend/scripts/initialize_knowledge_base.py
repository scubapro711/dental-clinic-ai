#!/usr/bin/env python3
"""
Initialize Knowledge Base

This script initializes the vector database with clinical, financial,
and operational knowledge for RAG.

Usage:
    python scripts/initialize_knowledge_base.py
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.knowledge_base import knowledge_base
from app.services.vector_db import vector_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Initialize all knowledge bases."""
    logger.info("=" * 80)
    logger.info("Knowledge Base Initialization")
    logger.info("=" * 80)
    
    # Check if Vector DB is enabled
    if not vector_db.enabled:
        logger.error("❌ Vector DB is disabled!")
        logger.error("Please set PINECONE_API_KEY and PINECONE_ENVIRONMENT in .env")
        return False
    
    logger.info(f"✅ Vector DB enabled: {vector_db.enabled}")
    logger.info(f"📊 Embedding model: {vector_db.embedding_model}")
    
    # Initialize knowledge bases
    logger.info("\n" + "=" * 80)
    logger.info("Ingesting Knowledge...")
    logger.info("=" * 80 + "\n")
    
    success = knowledge_base.initialize_all_knowledge()
    
    if success:
        logger.info("\n" + "=" * 80)
        logger.info("✅ Knowledge Base Initialization Complete!")
        logger.info("=" * 80)
        logger.info("\nKnowledge domains initialized:")
        logger.info("  - Clinical: Procedures, drug interactions")
        logger.info("  - Financial: Israeli tax system, accounting")
        logger.info("  - Operational: Safety protocols, compliance")
        logger.info("\nAgents can now use RAG for enhanced responses!")
        return True
    else:
        logger.error("\n" + "=" * 80)
        logger.error("❌ Knowledge Base Initialization Failed!")
        logger.error("=" * 80)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

