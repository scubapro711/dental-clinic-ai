"""
Vector Database Service using Pinecone

Provides semantic search and RAG capabilities for all agents.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorDBService:
    """
    Vector database service for semantic search and RAG.
    
    Uses:
    - Pinecone for vector storage
    - OpenAI text-embedding-3-small for embeddings
    """
    
    def __init__(self):
        """Initialize vector database service."""
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.pinecone_api_key:
            logger.warning("PINECONE_API_KEY not set - vector DB disabled")
            self.enabled = False
            return
        
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not set - embeddings disabled")
            self.enabled = False
            return
        
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=self.pinecone_api_key)
            
            # Initialize OpenAI for embeddings
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            
            # Embedding model
            self.embedding_model = "text-embedding-3-small"
            self.embedding_dimension = 1536
            
            # Index names for different knowledge bases
            self.indexes = {
                'clinical': 'dentaflow-clinical',
                'financial': 'dentaflow-financial',
                'operational': 'dentaflow-operational',
                'general': 'dentaflow-general',
            }
            
            # Initialize indexes
            self._initialize_indexes()
            
            self.enabled = True
            logger.info("Vector DB service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector DB: {e}")
            self.enabled = False
    
    def _initialize_indexes(self):
        """Create Pinecone indexes if they don't exist."""
        try:
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            for index_name in self.indexes.values():
                if index_name not in existing_indexes:
                    logger.info(f"Creating index: {index_name}")
                    self.pc.create_index(
                        name=index_name,
                        dimension=self.embedding_dimension,
                        metric='cosine',
                        spec=ServerlessSpec(
                            cloud='aws',
                            region='us-east-1'
                        )
                    )
                else:
                    logger.info(f"Index already exists: {index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize indexes: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return []
    
    def upsert_document(
        self,
        index_type: str,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Insert or update a document in the vector database.
        
        Args:
            index_type: Type of index ('clinical', 'financial', 'operational', 'general')
            doc_id: Unique document ID
            text: Document text
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        if not self.enabled:
            logger.warning("Vector DB is disabled")
            return False
        
        try:
            # Get index
            index_name = self.indexes.get(index_type)
            if not index_name:
                logger.error(f"Unknown index type: {index_type}")
                return False
            
            index = self.pc.Index(index_name)
            
            # Generate embedding
            embedding = self.generate_embedding(text)
            if not embedding:
                return False
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            metadata.update({
                'text': text[:1000],  # Store first 1000 chars
                'full_text_length': len(text),
                'indexed_at': datetime.now().isoformat(),
            })
            
            # Upsert to Pinecone
            index.upsert(vectors=[(doc_id, embedding, metadata)])
            
            logger.info(f"Upserted document {doc_id} to {index_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert document: {e}")
            return False
    
    def search(
        self,
        index_type: str,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            index_type: Type of index to search
            query: Search query
            top_k: Number of results to return
            filter_dict: Metadata filters
            
        Returns:
            List of matching documents with scores
        """
        if not self.enabled:
            logger.warning("Vector DB is disabled")
            return []
        
        try:
            # Get index
            index_name = self.indexes.get(index_type)
            if not index_name:
                logger.error(f"Unknown index type: {index_type}")
                return []
            
            index = self.pc.Index(index_name)
            
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            if not query_embedding:
                return []
            
            # Search
            results = index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    'id': match.id,
                    'score': match.score,
                    'text': match.metadata.get('text', ''),
                    'metadata': match.metadata,
                })
            
            logger.info(f"Found {len(formatted_results)} results for query in {index_type}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return []
    
    def delete_document(self, index_type: str, doc_id: str) -> bool:
        """
        Delete a document from the vector database.
        
        Args:
            index_type: Type of index
            doc_id: Document ID to delete
            
        Returns:
            Success status
        """
        if not self.enabled:
            logger.warning("Vector DB is disabled")
            return False
        
        try:
            index_name = self.indexes.get(index_type)
            if not index_name:
                logger.error(f"Unknown index type: {index_type}")
                return False
            
            index = self.pc.Index(index_name)
            index.delete(ids=[doc_id])
            
            logger.info(f"Deleted document {doc_id} from {index_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    def get_index_stats(self, index_type: str) -> Dict[str, Any]:
        """
        Get statistics for an index.
        
        Args:
            index_type: Type of index
            
        Returns:
            Index statistics
        """
        if not self.enabled:
            return {'enabled': False}
        
        try:
            index_name = self.indexes.get(index_type)
            if not index_name:
                return {'error': f"Unknown index type: {index_type}"}
            
            index = self.pc.Index(index_name)
            stats = index.describe_index_stats()
            
            return {
                'enabled': True,
                'index_name': index_name,
                'total_vectors': stats.total_vector_count,
                'dimension': stats.dimension,
                'namespaces': stats.namespaces,
            }
            
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {'error': str(e)}


# Global instance
vector_db = VectorDBService()

