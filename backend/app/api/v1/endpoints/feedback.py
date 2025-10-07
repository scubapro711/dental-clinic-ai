"""
Feedback API Endpoints

Endpoints for collecting human feedback on agent responses.
Part of the fine-tuning system.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Any
from enum import Enum
import tempfile
import os

from app.services.feedback_service import feedback_service, FeedbackType


router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackTypeEnum(str, Enum):
    """Feedback types for API"""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    RATING = "rating"
    COMMENT = "comment"


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback"""
    conversation_id: str
    message_id: str
    user_message: str
    agent_response: str
    agent_name: str
    feedback_type: FeedbackTypeEnum
    feedback_value: Any  # True/False for thumbs, 1-5 for rating
    comment: Optional[str] = None
    metadata: Optional[dict] = None


class ExportRequest(BaseModel):
    """Request model for exporting training data"""
    min_score: int = 4
    agent_name: Optional[str] = None
    include_system_prompt: bool = True


@router.post("/submit")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for an agent response.
    
    This is used to collect training data for fine-tuning.
    """
    try:
        feedback_entry = feedback_service.add_feedback(
            conversation_id=request.conversation_id,
            message_id=request.message_id,
            user_message=request.user_message,
            agent_response=request.agent_response,
            agent_name=request.agent_name,
            feedback_type=FeedbackType(request.feedback_type.value),
            feedback_value=request.feedback_value,
            comment=request.comment,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            "feedback_id": feedback_entry["message_id"],
            "message": "Feedback submitted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_feedback_stats():
    """
    Get statistics about collected feedback.
    
    Returns metrics like total feedback, thumbs up/down, training examples, etc.
    """
    try:
        stats = feedback_service.get_feedback_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/{conversation_id}")
async def get_conversation_feedback(conversation_id: str):
    """Get all feedback for a specific conversation"""
    try:
        feedback = feedback_service.get_conversation_feedback(conversation_id)
        return {
            "success": True,
            "conversation_id": conversation_id,
            "feedback": feedback
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_training_data(request: ExportRequest):
    """
    Export training data to JSONL format for OpenAI fine-tuning.
    
    Returns a downloadable file with training examples.
    """
    try:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.jsonl',
            delete=False,
            encoding='utf-8'
        )
        temp_file.close()
        
        # Export data
        count = feedback_service.export_training_data_jsonl(
            filepath=temp_file.name,
            min_score=request.min_score,
            agent_name=request.agent_name,
            include_system_prompt=request.include_system_prompt
        )
        
        if count == 0:
            os.unlink(temp_file.name)
            raise HTTPException(
                status_code=404,
                detail="No training examples found matching criteria"
            )
        
        # Return file
        return FileResponse(
            path=temp_file.name,
            media_type='application/jsonl',
            filename=f'training_data_{request.agent_name or "all"}_{count}_examples.jsonl',
            background=lambda: os.unlink(temp_file.name)  # Clean up after sending
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training-data")
async def get_training_data(
    min_score: int = 4,
    agent_name: Optional[str] = None
):
    """
    Get training examples (without downloading).
    
    Useful for previewing data before export.
    """
    try:
        examples = feedback_service.get_training_data(
            min_score=min_score,
            agent_name=agent_name
        )
        
        return {
            "success": True,
            "count": len(examples),
            "examples": examples[:10],  # Return first 10 for preview
            "total_available": len(examples)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def clear_feedback():
    """
    Clear all feedback (for testing only).
    
    WARNING: This will delete all collected feedback!
    """
    try:
        feedback_service.clear_feedback()
        return {
            "success": True,
            "message": "All feedback cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
