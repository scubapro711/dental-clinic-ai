"""
Fine-Tuning API Endpoints

Endpoints for managing OpenAI fine-tuning jobs.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.services.finetuning_service import finetuning_service


router = APIRouter(prefix="/finetuning", tags=["finetuning"])


class CreateJobRequest(BaseModel):
    """Request model for creating fine-tuning job"""
    agent_name: str
    min_score: int = 4
    model: str = "gpt-4o-mini-2024-07-18"
    hyperparameters: Optional[Dict[str, Any]] = None


@router.post(
    "/create",
    tags=["Fine-Tuning"],
    summary="Create fine-tuning job",
    description="""
    Create a new OpenAI fine-tuning job for an AI agent.
    
    **Requirements:**
    - At least 10 high-quality training examples (score >= min_score)
    - Valid agent name (alex, marcus, sarah, sophia)
    - Sufficient OpenAI credits
    
    **Authentication:** Requires valid JWT token with admin/owner role
    
    **Example Request:**
    ```json
    {
      "agent_name": "alex",
      "min_score": 4,
      "model": "gpt-4o-mini-2024-07-18",
      "hyperparameters": {
        "n_epochs": 3
      }
    }
    ```
    
    **Example Response:**
    ```json
    {
      "success": true,
      "job": {
        "id": "ftjob-abc123",
        "status": "validating_files",
        "model": "gpt-4o-mini-2024-07-18",
        "created_at": 1234567890
      }
    }
    ```
    """,
    responses={
        200: {"description": "Fine-tuning job created successfully"},
        400: {"description": "Bad request - insufficient training data or invalid parameters"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - requires admin/owner role"},
        500: {"description": "Internal server error"}
    }
)
async def create_finetuning_job(request: CreateJobRequest):
    """
    Create a new fine-tuning job.
    
    Requires at least 10 high-quality training examples.
    """
    try:
        job = await finetuning_service.create_finetuning_job(
            agent_name=request.agent_name,
            min_score=request.min_score,
            model=request.model,
            hyperparameters=request.hyperparameters
        )
        
        return {
            "success": True,
            "job": job
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status of a fine-tuning job.
    """
    try:
        status = await finetuning_service.get_job_status(job_id)
        
        return {
            "success": True,
            "job": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
async def list_jobs(agent_name: Optional[str] = None, limit: int = 10):
    """
    List fine-tuning jobs.
    """
    try:
        jobs = await finetuning_service.list_jobs(
            agent_name=agent_name,
            limit=limit
        )
        
        return {
            "success": True,
            "jobs": jobs,
            "count": len(jobs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/job/{job_id}/cancel")
async def cancel_job(job_id: str):
    """
    Cancel a fine-tuning job.
    """
    try:
        result = await finetuning_service.cancel_job(job_id)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/readiness",
    tags=["Fine-Tuning"],
    summary="Check training readiness",
    description="""
    Check if there's enough training data to start fine-tuning.
    
    Returns statistics about available training examples and readiness status.
    
    **Authentication:** Requires valid JWT token
    
    **Example Response:**
    ```json
    {
      "success": true,
      "readiness": {
        "alex": {
          "ready": true,
          "total_examples": 45,
          "good_examples": 38,
          "bad_examples": 7,
          "min_required": 10
        },
        "marcus": {
          "ready": false,
          "total_examples": 8,
          "good_examples": 6,
          "bad_examples": 2,
          "min_required": 10
        }
      }
    }
    ```
    """,
    responses={
        200: {"description": "Training readiness information"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def check_training_readiness(agent_name: Optional[str] = None):
    """
    Check if there's enough data to start training.
    """
    try:
        readiness = finetuning_service.get_training_readiness(agent_name)
        
        return {
            "success": True,
            "readiness": readiness
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
