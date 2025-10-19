#!/usr/bin/env python3
"""
Simplified script to upload HIPAA knowledge base documents to Pinecone.

This script directly uses Pinecone and OpenAI without requiring the full app configuration.
"""

import os
import sys
from pathlib import Path
import logging

# Check for required environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not PINECONE_API_KEY:
    print("ERROR: PINECONE_API_KEY environment variable is not set")
    sys.exit(1)

# Use a direct OpenAI API key (not through Manus proxy)
# You can set this as an environment variable or hardcode it temporarily
DIRECT_OPENAI_KEY = os.getenv("DIRECT_OPENAI_KEY") or "sk-proj-YOUR_KEY_HERE"

if DIRECT_OPENAI_KEY == "sk-proj-YOUR_KEY_HERE":
    print("ERROR: Please set DIRECT_OPENAI_KEY environment variable with your OpenAI API key")
    print("Or edit the script to hardcode your OpenAI API key temporarily")
    sys.exit(1)

from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_embedding(openai_client, text: str):
    """Generate embedding for text using OpenAI."""
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return None


def upload_hipaa_documents():
    """Upload all HIPAA knowledge base documents to Pinecone."""
    
    # Initialize Pinecone
    logger.info("Initializing Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Initialize OpenAI with direct API key
    logger.info("Initializing OpenAI...")
    openai_client = OpenAI(
        api_key=DIRECT_OPENAI_KEY,
        base_url="https://api.openai.com/v1"  # Use OpenAI directly, not Manus proxy
    )
    
    # Index configuration
    index_name = "dentaflow-hipaa"
    embedding_dimension = 1536
    
    # Check if index exists, create if not
    logger.info(f"Checking for index: {index_name}")
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    
    if index_name not in existing_indexes:
        logger.info(f"Creating index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=embedding_dimension,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
        logger.info("Index created successfully")
    else:
        logger.info(f"Index already exists: {index_name}")
    
    # Get index
    index = pc.Index(index_name)
    
    # Path to HIPAA knowledge base
    backend_dir = Path(__file__).parent.parent
    hipaa_kb_path = backend_dir / "app" / "knowledge" / "hipaa"
    
    if not hipaa_kb_path.exists():
        logger.error(f"HIPAA knowledge base path does not exist: {hipaa_kb_path}")
        return False
    
    # Find all markdown files
    md_files = list(hipaa_kb_path.rglob("*.md"))
    logger.info(f"Found {len(md_files)} markdown files in HIPAA knowledge base")
    
    success_count = 0
    fail_count = 0
    
    for md_file in md_files:
        try:
            # Read file content
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip empty files
            if not content.strip():
                logger.warning(f"Skipping empty file: {md_file}")
                continue
            
            # Generate document ID from file path
            relative_path = md_file.relative_to(hipaa_kb_path)
            doc_id = str(relative_path).replace('/', '_').replace('\\', '_').replace('.md', '')
            
            # Prepare metadata
            metadata = {
                'file_path': str(relative_path),
                'file_name': md_file.name,
                'category': relative_path.parts[0] if len(relative_path.parts) > 1 else 'general',
                'source': 'hipaa_knowledge_base',
                'text': content[:1000],  # Store first 1000 chars
                'full_text_length': len(content),
            }
            
            # Generate embedding
            logger.info(f"Generating embedding for: {relative_path}")
            embedding = generate_embedding(openai_client, content)
            
            if not embedding:
                logger.error(f"✗ Failed to generate embedding for: {relative_path}")
                fail_count += 1
                continue
            
            # Upload to Pinecone
            logger.info(f"Uploading to Pinecone: {relative_path}")
            index.upsert(vectors=[(doc_id, embedding, metadata)])
            
            logger.info(f"✓ Successfully uploaded: {relative_path}")
            success_count += 1
                
        except Exception as e:
            logger.error(f"Error processing {md_file}: {e}")
            fail_count += 1
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("UPLOAD SUMMARY")
    logger.info("="*50)
    logger.info(f"Total files processed: {len(md_files)}")
    logger.info(f"Successfully uploaded: {success_count}")
    logger.info(f"Failed: {fail_count}")
    logger.info("="*50)
    
    # Get index stats
    try:
        stats = index.describe_index_stats()
        logger.info(f"\nHIPAA Index Stats:")
        logger.info(f"  - Total vectors: {stats.total_vector_count}")
        logger.info(f"  - Dimension: {stats.dimension}")
    except Exception as e:
        logger.error(f"Failed to get index stats: {e}")
    
    return fail_count == 0


if __name__ == "__main__":
    success = upload_hipaa_documents()
    sys.exit(0 if success else 1)

