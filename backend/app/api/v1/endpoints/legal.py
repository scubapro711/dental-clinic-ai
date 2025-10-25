"""
Legal Documents API Endpoint

Serves legal documents (Terms, Privacy Policy, etc.) to frontend
"""
from fastapi import APIRouter, HTTPException, Path
from pathlib import Path as FilePath
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Legal documents configuration
LEGAL_DOCS = {
    "terms": {
        "title": "Terms of Service",
        "title_he": "תנאי שימוש",
        "file": "TERMS_OF_SERVICE.md",
        "last_updated": "2025-10-16"
    },
    "privacy": {
        "title": "Privacy Policy",
        "title_he": "מדיניות פרטיות",
        "file": "PRIVACY_POLICY.md",
        "last_updated": "2025-10-16"
    },
    "cookies": {
        "title": "Cookie Policy",
        "title_he": "מדיניות עוגיות",
        "file": "COOKIE_POLICY.md",
        "last_updated": "2025-10-16"
    },
    "hipaa": {
        "title": "HIPAA Notice of Privacy Practices",
        "title_he": "הודעת פרטיות HIPAA",
        "file": "HIPAA_NOTICE.md",
        "last_updated": "2025-10-16"
    },
    "aup": {
        "title": "Acceptable Use Policy",
        "title_he": "מדיניות שימוש מקובל",
        "file": "ACCEPTABLE_USE_POLICY.md",
        "last_updated": "2025-10-16"
    },
    "dpa": {
        "title": "Data Processing Agreement",
        "title_he": "הסכם עיבוד נתונים",
        "file": "DATA_PROCESSING_AGREEMENT.md",
        "last_updated": "2025-10-16"
    },
    "sla": {
        "title": "Service Level Agreement",
        "title_he": "הסכם רמת שירות",
        "file": "SERVICE_LEVEL_AGREEMENT.md",
        "last_updated": "2025-10-16"
    }
}


@router.get("/legal")
async def list_legal_documents() -> Dict[str, Any]:
    """
    List all available legal documents
    
    Returns:
        Dict containing list of all legal documents with metadata
    """
    return {
        "documents": LEGAL_DOCS,
        "count": len(LEGAL_DOCS)
    }


@router.get("/legal/{document_id}")
async def get_legal_document(
    document_id: str = Path(..., description="Document ID (terms, privacy, cookies, hipaa, aup, dpa, sla)")
) -> Dict[str, Any]:
    """
    Get a specific legal document content
    
    Args:
        document_id: The document identifier
        
    Returns:
        Dict containing document metadata and content
        
    Raises:
        HTTPException: If document not found or cannot be read
    """
    # Validate document ID
    if document_id not in LEGAL_DOCS:
        raise HTTPException(
            status_code=404,
            detail=f"Legal document '{document_id}' not found. Available documents: {', '.join(LEGAL_DOCS.keys())}"
        )
    
    doc_info = LEGAL_DOCS[document_id]
    
    # Construct path to legal document
    # Documents are stored in docs/legal/ directory
    base_path = FilePath(__file__).parent.parent.parent.parent.parent / "docs" / "legal"
    doc_path = base_path / doc_info["file"]
    
    # Check if file exists
    if not doc_path.exists():
        logger.error(f"Legal document file not found: {doc_path}")
        raise HTTPException(
            status_code=500,
            detail=f"Legal document file '{doc_info['file']}' not found on server"
        )
    
    # Read document content
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Error reading legal document {doc_path}: {str(e)}")
        logger.error(f"Error reading legal document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again later."
        )
    
    return {
        "id": document_id,
        "title": doc_info["title"],
        "title_he": doc_info["title_he"],
        "file": doc_info["file"],
        "last_updated": doc_info["last_updated"],
        "content": content,
        "content_length": len(content)
    }


@router.get("/legal/{document_id}/metadata")
async def get_legal_document_metadata(
    document_id: str = Path(..., description="Document ID")
) -> Dict[str, Any]:
    """
    Get metadata for a legal document without content
    
    Args:
        document_id: The document identifier
        
    Returns:
        Dict containing document metadata only
        
    Raises:
        HTTPException: If document not found
    """
    if document_id not in LEGAL_DOCS:
        raise HTTPException(
            status_code=404,
            detail=f"Legal document '{document_id}' not found"
        )
    
    doc_info = LEGAL_DOCS[document_id]
    
    return {
        "id": document_id,
        "title": doc_info["title"],
        "title_he": doc_info["title_he"],
        "file": doc_info["file"],
        "last_updated": doc_info["last_updated"]
    }

