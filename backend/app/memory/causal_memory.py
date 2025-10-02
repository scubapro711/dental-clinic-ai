"""
Causal Memory System with Neo4j

This implements the causal memory graph that learns from agent interactions:
- Stores conversation patterns and outcomes
- Links similar situations using semantic similarity
- Enables agents to learn from past experiences
- Implements Bayesian updating for confidence scores
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4

from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer

from app.core.config import settings


class CausalMemoryGraph:
    """Causal Memory Graph using Neo4j and Sentence-BERT."""
    
    def __init__(self):
        """Initialize causal memory with Neo4j and embedding model."""
        # Neo4j connection
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        
        # Sentence-BERT for semantic similarity
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize schema
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Create indexes and constraints in Neo4j."""
        with self.driver.session() as session:
            # Create constraints
            session.run("""
                CREATE CONSTRAINT interaction_id IF NOT EXISTS
                FOR (i:Interaction) REQUIRE i.id IS UNIQUE
            """)
            
            session.run("""
                CREATE CONSTRAINT pattern_id IF NOT EXISTS
                FOR (p:Pattern) REQUIRE p.id IS UNIQUE
            """)
            
            # Create indexes
            session.run("""
                CREATE INDEX interaction_timestamp IF NOT EXISTS
                FOR (i:Interaction) ON (i.timestamp)
            """)
    
    def store_interaction(
        self,
        user_message: str,
        agent_response: str,
        agent_name: str,
        conversation_id: UUID,
        organization_id: UUID,
        outcome: str = "success",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store an interaction in the causal memory graph.
        
        Args:
            user_message: User's input message
            agent_response: Agent's response
            agent_name: Name of the agent that responded
            conversation_id: ID of the conversation
            organization_id: ID of the organization
            outcome: Outcome of the interaction (success, failure, escalated)
            metadata: Additional metadata
            
        Returns:
            Interaction ID
        """
        # Generate embedding for user message
        embedding = self.embedding_model.encode(user_message).tolist()
        
        interaction_id = str(uuid4())
        
        with self.driver.session() as session:
            session.run("""
                CREATE (i:Interaction {
                    id: $interaction_id,
                    user_message: $user_message,
                    agent_response: $agent_response,
                    agent_name: $agent_name,
                    conversation_id: $conversation_id,
                    organization_id: $organization_id,
                    outcome: $outcome,
                    embedding: $embedding,
                    timestamp: datetime($timestamp),
                    metadata: $metadata
                })
            """, {
                "interaction_id": interaction_id,
                "user_message": user_message,
                "agent_response": agent_response,
                "agent_name": agent_name,
                "conversation_id": str(conversation_id),
                "organization_id": str(organization_id),
                "outcome": outcome,
                "embedding": embedding,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            })
        
        # Find and link similar interactions
        self._link_similar_interactions(interaction_id, embedding)
        
        # Extract and store patterns
        self._extract_patterns(interaction_id, user_message, agent_response, outcome)
        
        return interaction_id
    
    def _link_similar_interactions(self, interaction_id: str, embedding: List[float]):
        """
        Find and link similar interactions using cosine similarity.
        
        Args:
            interaction_id: ID of the new interaction
            embedding: Embedding vector of the interaction
        """
        with self.driver.session() as session:
            # Find similar interactions (cosine similarity > 0.8)
            # Note: Neo4j doesn't have built-in vector similarity, so we fetch all and compute in Python
            # For production, use a vector database like Pinecone or Milvus
            
            similar = session.run("""
                MATCH (i:Interaction)
                WHERE i.id <> $interaction_id
                RETURN i.id AS id, i.embedding AS embedding
                LIMIT 100
            """, {"interaction_id": interaction_id})
            
            for record in similar:
                other_embedding = record["embedding"]
                similarity = self._cosine_similarity(embedding, other_embedding)
                
                if similarity > 0.8:
                    # Create SIMILAR_TO relationship
                    session.run("""
                        MATCH (i1:Interaction {id: $id1})
                        MATCH (i2:Interaction {id: $id2})
                        MERGE (i1)-[r:SIMILAR_TO {similarity: $similarity}]->(i2)
                    """, {
                        "id1": interaction_id,
                        "id2": record["id"],
                        "similarity": similarity
                    })
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import numpy as np
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _extract_patterns(
        self,
        interaction_id: str,
        user_message: str,
        agent_response: str,
        outcome: str
    ):
        """
        Extract and store patterns from the interaction.
        
        Args:
            interaction_id: ID of the interaction
            user_message: User's message
            agent_response: Agent's response
            outcome: Outcome of the interaction
        """
        # Simple pattern extraction (can be enhanced with NLP)
        # For MVP, we identify patterns based on keywords
        
        patterns = []
        
        # Appointment scheduling pattern
        if any(word in user_message.lower() for word in ["appointment", "schedule", "book", "תור"]):
            patterns.append("appointment_scheduling")
        
        # Medical question pattern
        if any(word in user_message.lower() for word in ["pain", "hurt", "tooth", "dental", "כאב"]):
            patterns.append("medical_question")
        
        # Billing pattern
        if any(word in user_message.lower() for word in ["payment", "invoice", "bill", "cost", "תשלום"]):
            patterns.append("billing_inquiry")
        
        # Store patterns
        with self.driver.session() as session:
            for pattern_name in patterns:
                pattern_id = f"pattern_{pattern_name}"
                
                # Create or update pattern node
                session.run("""
                    MERGE (p:Pattern {id: $pattern_id, name: $pattern_name})
                    ON CREATE SET p.count = 1, p.success_rate = $success_rate
                    ON MATCH SET p.count = p.count + 1,
                                 p.success_rate = (p.success_rate * (p.count - 1) + $success_rate) / p.count
                """, {
                    "pattern_id": pattern_id,
                    "pattern_name": pattern_name,
                    "success_rate": 1.0 if outcome == "success" else 0.0
                })
                
                # Link interaction to pattern
                session.run("""
                    MATCH (i:Interaction {id: $interaction_id})
                    MATCH (p:Pattern {id: $pattern_id})
                    MERGE (i)-[:MATCHES_PATTERN]->(p)
                """, {
                    "interaction_id": interaction_id,
                    "pattern_id": pattern_id
                })
    
    def get_similar_interactions(
        self,
        user_message: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get similar past interactions for a given user message.
        
        Args:
            user_message: User's message
            limit: Maximum number of similar interactions to return
            
        Returns:
            List of similar interactions with their responses and outcomes
        """
        # Generate embedding
        embedding = self.embedding_model.encode(user_message).tolist()
        
        with self.driver.session() as session:
            # Fetch recent interactions
            results = session.run("""
                MATCH (i:Interaction)
                WHERE i.timestamp > datetime() - duration('P7D')
                RETURN i.id AS id, i.user_message AS user_message,
                       i.agent_response AS agent_response, i.outcome AS outcome,
                       i.embedding AS embedding, i.agent_name AS agent_name
                ORDER BY i.timestamp DESC
                LIMIT 100
            """)
            
            similar_interactions = []
            
            for record in results:
                other_embedding = record["embedding"]
                similarity = self._cosine_similarity(embedding, other_embedding)
                
                if similarity > 0.7:
                    similar_interactions.append({
                        "id": record["id"],
                        "user_message": record["user_message"],
                        "agent_response": record["agent_response"],
                        "outcome": record["outcome"],
                        "agent_name": record["agent_name"],
                        "similarity": similarity
                    })
            
            # Sort by similarity and return top results
            similar_interactions.sort(key=lambda x: x["similarity"], reverse=True)
            return similar_interactions[:limit]
    
    def get_pattern_statistics(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific pattern.
        
        Args:
            pattern_name: Name of the pattern
            
        Returns:
            Pattern statistics including count and success rate
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Pattern {name: $pattern_name})
                RETURN p.count AS count, p.success_rate AS success_rate
            """, {"pattern_name": pattern_name})
            
            record = result.single()
            if record:
                return {
                    "pattern_name": pattern_name,
                    "count": record["count"],
                    "success_rate": record["success_rate"]
                }
            return None
    
    def close(self):
        """Close Neo4j connection."""
        self.driver.close()


# Global causal memory instance
causal_memory = CausalMemoryGraph()
