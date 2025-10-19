"""
Vector Database Service - Unified Pinecone Implementation

Provides semantic search and RAG capabilities for all agents.
Uses Pinecone for managed vector storage with OpenAI embeddings.

Migration Strategy:
- Parallel deployment with ChromaDB (backward compatible)
- Feature flag to switch between ChromaDB and Pinecone
- Zero downtime migration
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
    - Pinecone for managed vector storage (cloud, requires API key)
    - OpenAI text-embedding-3-small for embeddings
    
    Features:
    - Managed backups and disaster recovery
    - High availability
    - Scalable performance
    - Audit trail
    - Perfect for compliance-critical data (HIPAA)
    """
    
    def __init__(self):
        """Initialize vector database service."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not set - embeddings disabled")
            self.enabled = False
            return
        
        if not self.pinecone_api_key:
            logger.warning("PINECONE_API_KEY not set - vector DB disabled")
            self.enabled = False
            return
        
        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=self.pinecone_api_key)
            
            # Initialize OpenAI for embeddings (direct API, not Manus proxy)
            self.openai_client = OpenAI(
                api_key=self.openai_api_key,
                base_url="https://api.openai.com/v1"
            )
            
            # Embedding model
            self.embedding_model = "text-embedding-3-small"
            self.embedding_dimension = 1536
            
            # Single index name (we'll use namespaces for different domains)
            self.index_name = "dentaflow-knowledge"
            
            # Namespace mapping for different knowledge bases
            self.namespaces = {
                'clinical': 'clinical',
                'financial': 'financial',
                'operational': 'operational',
                'general': 'general',
                'hipaa': 'hipaa',
            }
            
            # Initialize index
            self._initialize_index()
            
            # Get index object
            self.index = self.pc.Index(self.index_name)
            
            self.enabled = True
            logger.info("Vector DB service initialized successfully with Pinecone")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector DB: {e}")
            self.enabled = False
    
    def _initialize_index(self):
        """Create Pinecone index if it doesn't exist."""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx['name'] for idx in existing_indexes]
            
            if self.index_name in index_names:
                logger.info(f"Index already exists: {self.index_name}")
                return
            
            # Create new index
            logger.info(f"Creating new index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.embedding_dimension,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            
            logger.info(f"Created index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize index: {e}")
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
            index_type: Type of namespace ('clinical', 'financial', 'operational', 'general', 'hipaa')
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
            # Get namespace
            namespace = self.namespaces.get(index_type)
            if not namespace:
                logger.error(f"Unknown namespace type: {index_type}")
                return False
            
            # Generate embedding
            embedding = self.generate_embedding(text)
            if not embedding:
                return False
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            # Pinecone metadata must be JSON-serializable
            # Store full text in metadata (Pinecone supports up to 40KB)
            metadata.update({
                'text': text[:5000],  # Store first 5000 chars
                'full_text_length': len(text),
                'indexed_at': datetime.now().isoformat(),
                'domain': index_type,
            })
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[
                    {
                        'id': doc_id,
                        'values': embedding,
                        'metadata': metadata
                    }
                ],
                namespace=namespace
            )
            
            logger.info(f"Upserted document {doc_id} to namespace {namespace}")
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
            index_type: Type of namespace to search
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
            # Get namespace
            namespace = self.namespaces.get(index_type)
            if not namespace:
                logger.error(f"Unknown namespace type: {index_type}")
                return []
            
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            if not query_embedding:
                return []
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filter=filter_dict,
                include_metadata=True
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
            
            logger.info(f"Found {len(formatted_results)} results for query in {namespace}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return []
    
    def delete_document(self, index_type: str, doc_id: str) -> bool:
        """
        Delete a document from the vector database.
        
        Args:
            index_type: Type of namespace
            doc_id: Document ID to delete
            
        Returns:
            Success status
        """
        if not self.enabled:
            logger.warning("Vector DB is disabled")
            return False
        
        try:
            namespace = self.namespaces.get(index_type)
            if not namespace:
                logger.error(f"Unknown namespace type: {index_type}")
                return False
            
            self.index.delete(
                ids=[doc_id],
                namespace=namespace
            )
            
            logger.info(f"Deleted document {doc_id} from namespace {namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    def get_index_stats(self, index_type: str) -> Dict[str, Any]:
        """
        Get statistics for a namespace.
        
        Args:
            index_type: Type of namespace
            
        Returns:
            Namespace statistics
        """
        if not self.enabled:
            return {'enabled': False}
        
        try:
            namespace = self.namespaces.get(index_type)
            if not namespace:
                return {'error': f"Unknown namespace type: {index_type}"}
            
            # Get index stats
            stats = self.index.describe_index_stats()
            
            # Get namespace-specific stats
            namespace_stats = stats.namespaces.get(namespace, {})
            
            return {
                'enabled': True,
                'index_name': self.index_name,
                'namespace': namespace,
                'total_vectors': namespace_stats.get('vector_count', 0),
                'dimension': self.embedding_dimension,
            }
            
        except Exception as e:
            logger.error(f"Failed to get namespace stats: {e}")
            return {'error': str(e)}
    
    def reset_collection(self, index_type: str) -> bool:
        """
        Reset (clear) a namespace.
        
        Args:
            index_type: Type of namespace to reset
            
        Returns:
            Success status
        """
        if not self.enabled:
            logger.warning("Vector DB is disabled")
            return False
        
        try:
            namespace = self.namespaces.get(index_type)
            if not namespace:
                logger.error(f"Unknown namespace type: {index_type}")
                return False
            
            # Delete all vectors in namespace
            self.index.delete(
                delete_all=True,
                namespace=namespace
            )
            
            logger.info(f"Reset namespace: {namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset namespace: {e}")
            return False


# Global instance
vector_db = VectorDBService()

