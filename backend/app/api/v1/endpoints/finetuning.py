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


@router.post("/create")
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


@router.get("/readiness")
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
