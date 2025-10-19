"""
Regression Test: Pinecone Migration

Tests all agents to ensure they work correctly with Pinecone.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from app.services.vector_db import vector_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_vector_db():
    """Test vector database connection and functionality."""
    
    logger.info("="*60)
    logger.info("REGRESSION TEST: Pinecone Migration")
    logger.info("="*60)
    
    # Check if vector DB is enabled
    if not vector_db.enabled:
        logger.error("❌ Vector DB is not enabled!")
        return False
    
    logger.info("✅ Vector DB is enabled")
    
    # Test queries for each domain
    test_queries = {
        'clinical': [
            "What are common dental procedures?",
            "Tell me about drug interactions",
        ],
        'financial': [
            "What are the Israeli tax brackets?",
            "How does VAT work for dental clinics?",
        ],
        'operational': [
            "What are the safety protocols?",
            "How often should we sterilize equipment?",
        ],
        'general': [
            "What is the cancellation policy?",
            "What are the office hours?",
        ],
        'hipaa': [
            "What is the Privacy Rule?",
            "How should we handle PHI?",
        ],
    }
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for domain, queries in test_queries.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing {domain.upper()} domain")
        logger.info(f"{'='*60}")
        
        # Get domain stats
        stats = vector_db.get_index_stats(domain)
        vectors = stats.get('total_vectors', 0)
        logger.info(f"  Vectors in {domain}: {vectors}")
        
        if vectors == 0 and domain != 'hipaa':
            logger.warning(f"  ⚠️  No vectors found in {domain} - skipping tests")
            continue
        
        # Test each query
        for query in queries:
            total_tests += 1
            logger.info(f"\n  Query: {query}")
            
            try:
                results = vector_db.search(
                    index_type=domain,
                    query=query,
                    top_k=3
                )
                
                if results:
                    logger.info(f"    ✅ Found {len(results)} results")
                    for i, result in enumerate(results[:2], 1):
                        score = result['score']
                        text_preview = result['text'][:100].replace('\n', ' ')
                        logger.info(f"      {i}. Score: {score:.3f} - {text_preview}...")
                    passed_tests += 1
                else:
                    logger.warning(f"    ⚠️  No results found")
                    failed_tests += 1
                    
            except Exception as e:
                logger.error(f"    ❌ Error: {e}")
                failed_tests += 1
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total tests: {total_tests}")
    logger.info(f"✅ Passed: {passed_tests}")
    logger.info(f"❌ Failed: {failed_tests}")
    logger.info(f"Success rate: {(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%")
    logger.info(f"{'='*60}")
    
    # Overall index stats
    logger.info(f"\n{'='*60}")
    logger.info("OVERALL PINECONE STATS")
    logger.info(f"{'='*60}")
    
    for domain in ['clinical', 'financial', 'operational', 'general', 'hipaa']:
        stats = vector_db.get_index_stats(domain)
        vectors = stats.get('total_vectors', 0)
        logger.info(f"  {domain:15s}: {vectors:5d} vectors")
    
    logger.info(f"{'='*60}")
    
    return failed_tests == 0


if __name__ == "__main__":
    success = test_vector_db()
    sys.exit(0 if success else 1)

