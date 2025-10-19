#!/usr/bin/env python3
"""
Script to upload HIPAA knowledge base documents to ChromaDB vector database.

This script:
1. Scans all HIPAA knowledge base markdown files
2. Chunks them appropriately for RAG
3. Generates embeddings using OpenAI
4. Uploads to ChromaDB 'hipaa' collection
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import hashlib

# Add the backend app to the path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.vector_db import vector_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks for better RAG performance.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum chunk size in characters
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size // 2:  # Only break if it's not too early
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks


def generate_doc_id(file_path: str, chunk_index: int) -> str:
    """
    Generate a unique document ID for a chunk.
    
    Args:
        file_path: Path to the source file
        chunk_index: Index of the chunk
        
    Returns:
        Unique document ID
    """
    # Create a hash of the file path for uniqueness
    path_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
    return f"hipaa_{path_hash}_chunk_{chunk_index}"


def extract_metadata(file_path: Path, content: str) -> Dict[str, Any]:
    """
    Extract metadata from file path and content.
    
    Args:
        file_path: Path to the file
        content: File content
        
    Returns:
        Metadata dictionary
    """
    # Determine category from path
    parts = file_path.parts
    category = 'general'
    
    if 'regulations' in parts:
        category = 'regulations'
    elif 'policies' in parts:
        category = 'policies'
    elif 'faq' in parts or 'faqs' in parts:
        category = 'faq'
    elif 'best-practices' in parts or 'best_practices' in parts:
        category = 'best_practices'
    
    # Extract title from first line (usually # Title)
    lines = content.split('\n')
    title = file_path.stem.replace('_', ' ').title()
    
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break
    
    return {
        'category': category,
        'title': title,
        'filename': file_path.name,
        'source_path': str(file_path),
    }


def upload_hipaa_knowledge():
    """Main function to upload all HIPAA knowledge to ChromaDB."""
    
    # Check if vector DB is enabled
    if not vector_db.enabled:
        logger.error("Vector DB is not enabled. Please check your OPENAI_API_KEY.")
        return False
    
    # Base path for HIPAA knowledge
    base_path = backend_dir / "app" / "knowledge" / "hipaa"
    
    if not base_path.exists():
        logger.error(f"HIPAA knowledge base path not found: {base_path}")
        return False
    
    # Find all markdown files
    md_files = list(base_path.rglob('*.md'))
    logger.info(f"Found {len(md_files)} markdown files to process")
    
    total_chunks = 0
    successful_uploads = 0
    failed_uploads = 0
    
    # Process each file
    for file_path in md_files:
        try:
            logger.info(f"Processing: {file_path.relative_to(base_path)}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip empty files
            if not content.strip():
                logger.warning(f"Skipping empty file: {file_path.name}")
                continue
            
            # Extract metadata
            metadata = extract_metadata(file_path, content)
            
            # Chunk the content
            chunks = chunk_text(content, chunk_size=1000, overlap=200)
            logger.info(f"  Created {len(chunks)} chunks")
            
            # Upload each chunk
            for i, chunk in enumerate(chunks):
                doc_id = generate_doc_id(str(file_path), i)
                
                # Add chunk-specific metadata
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                })
                
                # Upload to ChromaDB
                success = vector_db.upsert_document(
                    index_type='hipaa',
                    doc_id=doc_id,
                    text=chunk,
                    metadata=chunk_metadata
                )
                
                if success:
                    successful_uploads += 1
                else:
                    failed_uploads += 1
                    logger.error(f"  Failed to upload chunk {i} of {file_path.name}")
                
                total_chunks += 1
        
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            failed_uploads += 1
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("UPLOAD SUMMARY")
    logger.info("="*60)
    logger.info(f"Total files processed: {len(md_files)}")
    logger.info(f"Total chunks created: {total_chunks}")
    logger.info(f"Successful uploads: {successful_uploads}")
    logger.info(f"Failed uploads: {failed_uploads}")
    if total_chunks > 0:
        logger.info(f"Success rate: {successful_uploads/total_chunks*100:.1f}%")
    logger.info("="*60)
    
    # Get collection stats
    stats = vector_db.get_index_stats('hipaa')
    logger.info(f"\nHIPAA Collection Stats: {stats}")
    
    return failed_uploads == 0


if __name__ == '__main__':
    success = upload_hipaa_knowledge()
    sys.exit(0 if success else 1)

