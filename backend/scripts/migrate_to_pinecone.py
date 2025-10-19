"""
Migrate all knowledge bases to Pinecone

This script migrates clinical, financial, operational, and general knowledge
from the knowledge_base service to Pinecone.

HIPAA knowledge is already in Pinecone (uploaded separately).
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from app.services.vector_db_v2 import VectorDBService
from app.services.knowledge_base import KnowledgeBaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_knowledge_to_pinecone():
    """Migrate all knowledge bases to Pinecone."""
    
    logger.info("="*60)
    logger.info("MIGRATION: ChromaDB → Pinecone")
    logger.info("="*60)
    
    # Initialize services
    logger.info("Initializing services...")
    vector_db = VectorDBService()
    kb_manager = KnowledgeBaseManager()
    
    if not vector_db.enabled:
        logger.error("Vector DB is not enabled. Check API keys.")
        return False
    
    # Domains to migrate
    domains = ['clinical', 'financial', 'operational', 'general']
    
    total_success = 0
    total_failed = 0
    
    for domain in domains:
        logger.info(f"\n{'='*60}")
        logger.info(f"Migrating {domain.upper()} knowledge...")
        logger.info(f"{'='*60}")
        
        try:
            # Ingest knowledge for this domain
            if domain == 'clinical':
                kb_manager.ingest_clinical_knowledge()
            elif domain == 'financial':
                kb_manager.ingest_financial_knowledge()
            elif domain == 'operational':
                kb_manager.ingest_operational_knowledge()
            elif domain == 'general':
                kb_manager.ingest_general_knowledge()
            
            # Get stats
            stats = vector_db.get_index_stats(domain)
            logger.info(f"✅ {domain}: {stats.get('total_vectors', 0)} vectors")
            total_success += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to migrate {domain}: {e}")
            total_failed += 1
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("MIGRATION SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Successful: {total_success}/{len(domains)}")
    logger.info(f"❌ Failed: {total_failed}/{len(domains)}")
    
    # Get overall stats
    logger.info(f"\n{'='*60}")
    logger.info("PINECONE INDEX STATS")
    logger.info(f"{'='*60}")
    
    for domain in domains + ['hipaa']:
        stats = vector_db.get_index_stats(domain)
        vectors = stats.get('total_vectors', 0)
        logger.info(f"  {domain:15s}: {vectors:5d} vectors")
    
    logger.info(f"{'='*60}")
    logger.info("✅ Migration complete!")
    logger.info(f"{'='*60}")
    
    return total_failed == 0


if __name__ == "__main__":
    success = migrate_knowledge_to_pinecone()
    sys.exit(0 if success else 1)

