"""
Vector Database Service using ChromaDB

Provides semantic search and RAG capabilities for all agents.
Uses ChromaDB for local vector storage with OpenAI embeddings.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

import chromadb
from chromadb.config import Settings
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorDBService:
    """
    Vector database service for semantic search and RAG.
    
    Uses:
    - ChromaDB for vector storage (local, no API key needed)
    - OpenAI text-embedding-3-small for embeddings
    """
    
    def __init__(self):
        """Initialize vector database service."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not set - embeddings disabled")
            self.enabled = False
            return
        
        try:
            # Initialize ChromaDB client
            # Store data in backend/chroma_db directory
            chroma_db_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "chroma_db"
            )
            os.makedirs(chroma_db_path, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=chroma_db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Initialize OpenAI for embeddings
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            
            # Embedding model
            self.embedding_model = "text-embedding-3-small"
            self.embedding_dimension = 1536
            
            # Collection names for different knowledge bases
            self.collections = {
                'clinical': 'dentaflow_clinical',
                'financial': 'dentaflow_financial',
                'operational': 'dentaflow_operational',
                'general': 'dentaflow_general',
                'hipaa': 'dentaflow_hipaa',
            }
            
            # Initialize collections
            self._initialize_collections()
            
            self.enabled = True
            logger.info("Vector DB service initialized successfully with ChromaDB")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector DB: {e}")
            self.enabled = False
    
    def _initialize_collections(self):
        """Create ChromaDB collections if they don't exist."""
        try:
            for collection_name in self.collections.values():
                try:
                    # Try to get existing collection
                    self.client.get_collection(name=collection_name)
                    logger.info(f"Collection already exists: {collection_name}")
                except Exception:
                    # Create new collection if it doesn't exist
                    self.client.create_collection(
                        name=collection_name,
                        metadata={"hnsw:space": "cosine"}
                    )
                    logger.info(f"Created collection: {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize collections: {e}")
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
            index_type: Type of collection ('clinical', 'financial', 'operational', 'general', 'hipaa')
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
            # Get collection
            collection_name = self.collections.get(index_type)
            if not collection_name:
                logger.error(f"Unknown collection type: {index_type}")
                return False
            
            collection = self.client.get_collection(name=collection_name)
            
            # Generate embedding
            embedding = self.generate_embedding(text)
            if not embedding:
                return False
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            metadata.update({
                'text': text[:1000],  # Store first 1000 chars in metadata
                'full_text_length': len(text),
                'indexed_at': datetime.now().isoformat(),
            })
            
            # Upsert to ChromaDB
            collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata]
            )
            
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
            index_type: Type of collection to search
            query: Search query
            top_k: Number of results to return
            filter_dict: Metadata filters (where clause)
            
        Returns:
            List of matching documents with scores
        """
        if not self.enabled:
            logger.warning("Vector DB is disabled")
            return []
        
        try:
            # Get collection
            collection_name = self.collections.get(index_type)
            if not collection_name:
                logger.error(f"Unknown collection type: {index_type}")
                return []
            
            collection = self.client.get_collection(name=collection_name)
            
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            if not query_embedding:
                return []
            
            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_dict,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results and results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
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
            index_type: Type of collection
            doc_id: Document ID to delete
            
        Returns:
            Success status
        """
        if not self.enabled:
            logger.warning("Vector DB is disabled")
            return False
        
        try:
            collection_name = self.collections.get(index_type)
            if not collection_name:
                logger.error(f"Unknown collection type: {index_type}")
                return False
            
            collection = self.client.get_collection(name=collection_name)
            collection.delete(ids=[doc_id])
            
            logger.info(f"Deleted document {doc_id} from {index_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    def get_index_stats(self, index_type: str) -> Dict[str, Any]:
        """
        Get statistics for a collection.
        
        Args:
            index_type: Type of collection
            
        Returns:
            Collection statistics
        """
        if not self.enabled:
            return {'enabled': False}
        
        try:
            collection_name = self.collections.get(index_type)
            if not collection_name:
                return {'error': f"Unknown collection type: {index_type}"}
            
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()
            
            return {
                'enabled': True,
                'collection_name': collection_name,
                'total_vectors': count,
                'dimension': self.embedding_dimension,
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {'error': str(e)}
    
    def reset_collection(self, index_type: str) -> bool:
        """
        Reset (clear) a collection.
        
        Args:
            index_type: Type of collection to reset
            
        Returns:
            Success status
        """
        if not self.enabled:
            logger.warning("Vector DB is disabled")
            return False
        
        try:
            collection_name = self.collections.get(index_type)
            if not collection_name:
                logger.error(f"Unknown collection type: {index_type}")
                return False
            
            # Delete and recreate collection
            self.client.delete_collection(name=collection_name)
            self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"Reset collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            return False


# Global instance
vector_db = VectorDBService()

