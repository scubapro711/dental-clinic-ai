"""
Fine-Tuning Service

Manages OpenAI fine-tuning jobs for agent improvement.
"""

import logging
import os
import tempfile
from typing import Optional, Dict, Any, List
from datetime import datetime
import openai

from app.db.feedback_db import feedback_db
from app.services.feedback_service import feedback_service

logger = logging.getLogger(__name__)


class FineTuningService:
    """
    Service for managing OpenAI fine-tuning jobs.
    
    Workflow:
    1. Collect high-quality training examples from feedback
    2. Export to JSONL format
    3. Upload to OpenAI
    4. Create fine-tuning job
    5. Monitor job status
    6. Deploy fine-tuned model
    """
    
    def __init__(self):
        """Initialize fine-tuning service"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
            logger.info("Fine-tuning service initialized with OpenAI API key")
        else:
            logger.warning("OpenAI API key not found - fine-tuning will not be available")
        
        self.db = feedback_db
    
    async def create_finetuning_job(
        self,
        agent_name: str,
        min_score: int = 4,
        model: str = "gpt-4o-mini-2024-07-18",
        hyperparameters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create a new fine-tuning job.
        
        Args:
            agent_name: Name of the agent to fine-tune
            min_score: Minimum feedback score to include
            model: Base model to fine-tune
            hyperparameters: Optional hyperparameters for training
            
        Returns:
            Job information including job_id and status
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        try:
            # Get training examples
            examples = feedback_service.get_training_data(
                min_score=min_score,
                agent_name=agent_name
            )
            
            if len(examples) < 10:
                raise ValueError(f"Not enough training examples. Need at least 10, got {len(examples)}")
            
            logger.info(f"Creating fine-tuning job for {agent_name} with {len(examples)} examples")
            
            # Export to temporary JSONL file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8') as f:
                temp_file = f.name
                feedback_service.export_training_data_jsonl(
                    filepath=temp_file,
                    min_score=min_score,
                    agent_name=agent_name,
                    include_system_prompt=True
                )
            
            # Upload file to OpenAI
            logger.info(f"Uploading training file to OpenAI...")
            with open(temp_file, 'rb') as f:
                file_response = openai.files.create(
                    file=f,
                    purpose='fine-tune'
                )
            
            training_file_id = file_response.id
            logger.info(f"Training file uploaded: {training_file_id}")
            
            # Clean up temp file
            os.unlink(temp_file)
            
            # Create fine-tuning job
            hyperparams = hyperparameters or {
                "n_epochs": 3,
                "batch_size": 1,
                "learning_rate_multiplier": 1.0
            }
            
            logger.info(f"Creating fine-tuning job with hyperparameters: {hyperparams}")
            job_response = openai.fine_tuning.jobs.create(
                training_file=training_file_id,
                model=model,
                hyperparameters=hyperparams
            )
            
            job_id = job_response.id
            logger.info(f"Fine-tuning job created: {job_id}")
            
            # Save job to database
            self.db.add_finetuning_job(
                job_id=job_id,
                agent_name=agent_name,
                model=model,
                status="created",
                training_examples_count=len(examples),
                hyperparameters=hyperparams,
                metadata={
                    "training_file_id": training_file_id,
                    "min_score": min_score
                }
            )
            
            return {
                "job_id": job_id,
                "status": "created",
                "agent_name": agent_name,
                "model": model,
                "training_examples": len(examples),
                "training_file_id": training_file_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating fine-tuning job: {e}")
            raise
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a fine-tuning job.
        
        Args:
            job_id: OpenAI fine-tuning job ID
            
        Returns:
            Job status information
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        try:
            job = openai.fine_tuning.jobs.retrieve(job_id)
            
            # Update database
            status = job.status
            fine_tuned_model = getattr(job, 'fine_tuned_model', None)
            error = getattr(job, 'error', None)
            
            self.db.update_finetuning_job(
                job_id=job_id,
                status=status,
                fine_tuned_model=fine_tuned_model,
                error=str(error) if error else None
            )
            
            return {
                "job_id": job_id,
                "status": status,
                "fine_tuned_model": fine_tuned_model,
                "error": error,
                "created_at": job.created_at,
                "finished_at": getattr(job, 'finished_at', None)
            }
            
        except Exception as e:
            logger.error(f"Error getting job status: {e}")
            raise
    
    async def list_jobs(
        self,
        agent_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List fine-tuning jobs.
        
        Args:
            agent_name: Filter by agent name (optional)
            limit: Maximum number of jobs to return
            
        Returns:
            List of job information
        """
        try:
            jobs = self.db.get_finetuning_jobs(
                agent_name=agent_name,
                limit=limit
            )
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error listing jobs: {e}")
            raise
    
    async def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a fine-tuning job.
        
        Args:
            job_id: OpenAI fine-tuning job ID
            
        Returns:
            Cancellation confirmation
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        try:
            job = openai.fine_tuning.jobs.cancel(job_id)
            
            # Update database
            self.db.update_finetuning_job(
                job_id=job_id,
                status="cancelled"
            )
            
            logger.info(f"Fine-tuning job cancelled: {job_id}")
            
            return {
                "job_id": job_id,
                "status": "cancelled"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling job: {e}")
            raise
    
    def get_training_readiness(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if there's enough data to start training.
        
        Args:
            agent_name: Filter by agent name (optional)
            
        Returns:
            Readiness information
        """
        try:
            stats = feedback_service.get_feedback_stats()
            
            high_quality_examples = stats.get("high_quality_examples", 0)
            total_feedback = stats.get("total_feedback", 0)
            
            ready = high_quality_examples >= 10
            
            return {
                "ready": ready,
                "high_quality_examples": high_quality_examples,
                "total_feedback": total_feedback,
                "minimum_required": 10,
                "recommended": 50,
                "message": (
                    "Ready to start training!" if ready
                    else f"Need {10 - high_quality_examples} more high-quality examples"
                )
            }
            
        except Exception as e:
            logger.error(f"Error checking training readiness: {e}")
            return {
                "ready": False,
                "error": str(e)
            }


# Global instance
finetuning_service = FineTuningService()
