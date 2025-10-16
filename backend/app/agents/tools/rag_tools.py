"""
RAG (Retrieval-Augmented Generation) Tools

Tools for agents to search knowledge bases and enhance responses.
"""

import logging
from typing import Dict, Any
from langchain_core.tools import tool

from app.services.knowledge_base import knowledge_base

logger = logging.getLogger(__name__)

# Demo knowledge - loaded from JSON file
import json
import os

# Load demo knowledge on module import
DEMO_KNOWLEDGE = []
try:
    demo_knowledge_path = os.path.join(
        os.path.dirname(__file__), 
        "..", "..", "knowledge", "demo_knowledge.json"
    )
    if os.path.exists(demo_knowledge_path):
        with open(demo_knowledge_path, 'r', encoding='utf-8') as f:
            demo_data = json.load(f)
            DEMO_KNOWLEDGE = demo_data.get('documents', [])
        logger.info(f"Loaded {len(DEMO_KNOWLEDGE)} demo knowledge documents")
except Exception as e:
    logger.warning(f"Could not load demo knowledge: {e}")


@tool
def search_clinical_knowledge_tool(query: str, top_results: int = 3) -> str:
    """
    Search clinical knowledge base for treatment guidelines, procedures, and drug interactions.
    
    Use this when you need:
    - Treatment recommendations
    - Procedure information
    - Drug interaction warnings
    - Clinical best practices
    
    Args:
        query: What you're looking for (e.g., "root canal procedure", "amoxicillin interactions")
        top_results: Number of results to return (default: 3)
        
    Returns:
        JSON string with relevant clinical knowledge
    """
    try:
        logger.info(f"Searching clinical knowledge: {query}")
        
        results = knowledge_base.search_knowledge(
            domain='clinical',
            query=query,
            top_k=top_results
        )
        
        if not results:
            return "No relevant clinical knowledge found. Recommend consulting with a specialist or referring to current clinical guidelines."
        
        # Format results
        formatted = {
            'query': query,
            'results_found': len(results),
            'knowledge': []
        }
        
        for i, result in enumerate(results, 1):
            formatted['knowledge'].append({
                'relevance_score': f"{result['score']:.2f}",
                'content': result['text'],
                'source': result['metadata'].get('title', 'Unknown'),
                'category': result['metadata'].get('category', 'general'),
            })
        
        import json
        return json.dumps(formatted, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error searching clinical knowledge: {e}")
        return f"Error accessing clinical knowledge: {str(e)}"


@tool
def search_financial_knowledge_tool(query: str, top_results: int = 3) -> str:
    """
    Search financial knowledge base for tax laws, accounting practices, and Israeli regulations.
    
    Use this when you need:
    - Israeli tax information
    - Deductible expenses
    - VAT regulations
    - Financial planning advice
    
    Args:
        query: What you're looking for (e.g., "VAT on dental services", "deductible expenses")
        top_results: Number of results to return (default: 3)
        
    Returns:
        JSON string with relevant financial knowledge
    """
    try:
        logger.info(f"Searching financial knowledge: {query}")
        
        results = knowledge_base.search_knowledge(
            domain='financial',
            query=query,
            top_k=top_results
        )
        
        if not results:
            return "No relevant financial knowledge found. **IMPORTANT:** Always recommend consulting with a certified Israeli accountant for specific tax and financial advice."
        
        # Format results
        formatted = {
            'query': query,
            'results_found': len(results),
            'knowledge': [],
            'disclaimer': '⚠️ This information is for general guidance only. Always consult with a certified Israeli accountant for personalized advice.'
        }
        
        for i, result in enumerate(results, 1):
            formatted['knowledge'].append({
                'relevance_score': f"{result['score']:.2f}",
                'content': result['text'],
                'source': result['metadata'].get('title', 'Unknown'),
                'year': result['metadata'].get('year', 'Unknown'),
            })
        
        import json
        return json.dumps(formatted, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error searching financial knowledge: {e}")
        return f"Error accessing financial knowledge: {str(e)}"


@tool
def search_operational_knowledge_tool(query: str, top_results: int = 3) -> str:
    """
    Search operational knowledge base for safety protocols, compliance, and best practices.
    
    Use this when you need:
    - Safety protocols
    - Compliance requirements
    - Best practices
    - Emergency procedures
    
    Args:
        query: What you're looking for (e.g., "sterilization protocol", "emergency kit")
        top_results: Number of results to return (default: 3)
        
    Returns:
        JSON string with relevant operational knowledge
    """
    try:
        logger.info(f"Searching operational knowledge: {query}")
        
        results = knowledge_base.search_knowledge(
            domain='operational',
            query=query,
            top_k=top_results
        )
        
        if not results:
            return "No relevant operational knowledge found. Refer to Israeli Ministry of Health guidelines and clinic policies."
        
        # Format results
        formatted = {
            'query': query,
            'results_found': len(results),
            'knowledge': []
        }
        
        for i, result in enumerate(results, 1):
            formatted['knowledge'].append({
                'relevance_score': f"{result['score']:.2f}",
                'content': result['text'],
                'source': result['metadata'].get('title', 'Unknown'),
                'category': result['metadata'].get('category', 'general'),
                'critical': result['metadata'].get('critical', False),
            })
        
        import json
        return json.dumps(formatted, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error searching operational knowledge: {e}")
        return f"Error accessing operational knowledge: {str(e)}"


@tool
def search_general_knowledge_tool(query: str, top_results: int = 3) -> str:
    """
    Search general knowledge base for clinic policies, FAQs, and common procedures.
    
    Use this when you need:
    - Clinic policies
    - Common questions
    - General procedures
    - Patient information
    
    Args:
        query: What you're looking for (e.g., "appointment cancellation policy")
        top_results: Number of results to return (default: 3)
        
    Returns:
        JSON string with relevant general knowledge
    """
    try:
        logger.info(f"Searching general knowledge: {query}")
        
        results = knowledge_base.search_knowledge(
            domain='general',
            query=query,
            top_k=top_results
        )
        
        if not results:
            return "No relevant information found in general knowledge base."
        
        # Format results
        formatted = {
            'query': query,
            'results_found': len(results),
            'knowledge': []
        }
        
        for i, result in enumerate(results, 1):
            formatted['knowledge'].append({
                'relevance_score': f"{result['score']:.2f}",
                'content': result['text'],
                'source': result['metadata'].get('title', 'Unknown'),
            })
        
        import json
        return json.dumps(formatted, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error searching general knowledge: {e}")
        return f"Error accessing general knowledge: {str(e)}"


@tool
def search_demo_knowledge_tool(query: str, top_results: int = 3) -> str:
    """
    Search demo/product knowledge base for DentaFlow features and capabilities.
    
    Use this ONLY in DEMO MODE when users ask about:
    - DentaFlow features and capabilities
    - Pricing and plans
    - Implementation process
    - AI agents (Alex, Sarah, Marcus, Sophia)
    - Integrations (Odoo, WhatsApp, Telegram)
    - Security and compliance
    - Free trial and pilot program
    
    Args:
        query: What the user is asking about (e.g., "pricing", "how does it work")
        top_results: Number of results to return (default: 3)
        
    Returns:
        JSON string with product information
    """
    try:
        logger.info(f"Searching demo knowledge: {query}")
        
        if not DEMO_KNOWLEDGE:
            return "Demo knowledge base not loaded. Please contact support."
        
        # Simple keyword matching (in production, use vector similarity)
        query_lower = query.lower()
        scored_docs = []
        
        for doc in DEMO_KNOWLEDGE:
            score = 0
            
            # Check title match
            if any(word in doc['title'].lower() for word in query_lower.split()):
                score += 3
            
            # Check keywords match
            for keyword in doc.get('keywords', []):
                if keyword.lower() in query_lower:
                    score += 2
            
            # Check content match
            if any(word in doc['content'].lower() for word in query_lower.split()):
                score += 1
            
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score and take top results
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        top_docs = scored_docs[:top_results]
        
        if not top_docs:
            return json.dumps({
                'query': query,
                'results_found': 0,
                'message': 'No specific information found. Would you like to schedule a demo with our team?'
            }, ensure_ascii=False, indent=2)
        
        # Format results
        formatted = {
            'query': query,
            'results_found': len(top_docs),
            'knowledge': []
        }
        
        for score, doc in top_docs:
            formatted['knowledge'].append({
                'relevance_score': f"{score}/10",
                'title': doc['title'],
                'content': doc['content'],
                'category': doc['category'],
            })
        
        return json.dumps(formatted, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error searching demo knowledge: {e}")
        return f"Error accessing demo knowledge: {str(e)}"

