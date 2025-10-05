"""
Feedback Service for Fine-Tuning

Collects human feedback on agent responses to build training dataset.
Implements LangGraph Human-in-the-Loop pattern.
Now with SQLite persistence for production stability.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import json

from app.db.feedback_db import feedback_db

logger = logging.getLogger(__name__)


class FeedbackType(str, Enum):
    """Types of feedback"""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    RATING = "rating"  # 1-5 stars
    COMMENT = "comment"


class FeedbackService:
    """
    Service for collecting and managing feedback on agent responses.
    
    This is used to build a training dataset for fine-tuning the agents.
    Now uses SQLite for persistent storage.
    """
    
    def __init__(self):
        """Initialize feedback service with SQLite database"""
        self.db = feedback_db
        logger.info("Feedback service initialized with SQLite database")
        
    def add_feedback(
        self,
        conversation_id: str,
        message_id: str,
        user_message: str,
        agent_response: str,
        agent_name: str,
        feedback_type: FeedbackType,
        feedback_value: Any,
        comment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add feedback for an agent response.
        
        Args:
            conversation_id: ID of the conversation
            message_id: ID of the specific message
            user_message: The user's original message
            agent_response: The agent's response
            agent_name: Name of the agent (Alex, Marcus, Sophia)
            feedback_type: Type of feedback (thumbs, rating, comment)
            feedback_value: The feedback value (True/False for thumbs, 1-5 for rating)
            comment: Optional text comment
            metadata: Optional additional metadata
            
        Returns:
            The created feedback entry
        """
        try:
            # Add feedback to database
            feedback_id = self.db.add_feedback(
                conversation_id=conversation_id,
                message_id=message_id,
                user_message=user_message,
                agent_response=agent_response,
                agent_name=agent_name,
                feedback_type=feedback_type.value,
                feedback_value=feedback_value,
                comment=comment,
                metadata=metadata
            )
            
            # If positive feedback, add to training examples
            if self._is_positive_feedback(feedback_type, feedback_value):
                score = self._calculate_score(feedback_type, feedback_value)
                system_prompt = self._get_system_prompt(agent_name)
                
                self.db.add_training_example(
                    feedback_id=feedback_id,
                    agent_name=agent_name,
                    system_prompt=system_prompt,
                    user_message=user_message,
                    assistant_response=agent_response,
                    score=score
                )
            
            logger.info(f"Added feedback for conversation {conversation_id}, message {message_id}")
            
            return {
                "conversation_id": conversation_id,
                "message_id": message_id,
                "feedback_id": feedback_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error adding feedback: {e}")
            raise
    
    def _is_positive_feedback(self, feedback_type: FeedbackType, value: Any) -> bool:
        """Check if feedback is positive"""
        if feedback_type == FeedbackType.THUMBS_UP:
            return value is True
        elif feedback_type == FeedbackType.RATING:
            return value >= 4  # 4-5 stars is good
        return False
    
    def _calculate_score(self, feedback_type: FeedbackType, value: Any) -> int:
        """Calculate numerical score from feedback"""
        if feedback_type == FeedbackType.THUMBS_UP:
            return 5  # Thumbs up = 5 stars
        elif feedback_type == FeedbackType.RATING:
            return int(value)
        return 0
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get statistics about collected feedback"""
        try:
            stats = self.db.get_feedback_stats()
            
            # Calculate additional metrics
            thumbs_up = stats["by_type"].get("thumbs_up", 0)
            thumbs_down = stats["by_type"].get("thumbs_down", 0)
            ratings = stats["by_type"].get("rating", 0)
            
            return {
                "total_feedback": stats["total_feedback"],
                "thumbs_up": thumbs_up,
                "thumbs_down": thumbs_down,
                "ratings": ratings,
                "training_examples": stats["training_examples"],
                "high_quality_examples": stats["high_quality_examples"],
                "by_agent": stats["by_agent"],
                "ready_for_finetuning": stats["high_quality_examples"] >= 10  # Need at least 10 examples
            }
            
        except Exception as e:
            logger.error(f"Error getting feedback stats: {e}")
            return {
                "total_feedback": 0,
                "thumbs_up": 0,
                "thumbs_down": 0,
                "ratings": 0,
                "training_examples": 0,
                "high_quality_examples": 0,
                "by_agent": {},
                "ready_for_finetuning": False
            }
    
    def get_training_data(
        self,
        min_score: int = 4,
        agent_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get training examples for fine-tuning.
        
        Args:
            min_score: Minimum feedback score to include
            agent_name: Filter by agent name (optional)
            
        Returns:
            List of training examples in OpenAI format
        """
        try:
            examples = self.db.get_training_examples(
                agent_name=agent_name,
                min_score=min_score
            )
            
            # Convert to OpenAI format
            training_data = []
            for example in examples:
                training_data.append({
                    "messages": [
                        {
                            "role": "system",
                            "content": example["system_prompt"]
                        },
                        {
                            "role": "user",
                            "content": example["user_message"]
                        },
                        {
                            "role": "assistant",
                            "content": example["assistant_response"]
                        }
                    ],
                    "agent_name": example["agent_name"],
                    "score": example["score"],
                    "created_at": example["created_at"]
                })
            
            return training_data
            
        except Exception as e:
            logger.error(f"Error getting training data: {e}")
            return []
    
    def export_training_data_jsonl(
        self,
        filepath: str,
        min_score: int = 4,
        agent_name: Optional[str] = None,
        include_system_prompt: bool = True
    ) -> int:
        """
        Export training data to JSONL format for OpenAI fine-tuning.
        
        Args:
            filepath: Path to save JSONL file
            min_score: Minimum feedback score to include
            agent_name: Filter by agent name (optional)
            include_system_prompt: Include system prompt in examples
            
        Returns:
            Number of examples exported
        """
        try:
            examples = self.get_training_data(min_score, agent_name)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                for example in examples:
                    # OpenAI fine-tuning format
                    messages = example["messages"]
                    
                    # Remove system prompt if not requested
                    if not include_system_prompt:
                        messages = [m for m in messages if m["role"] != "system"]
                    
                    training_obj = {"messages": messages}
                    f.write(json.dumps(training_obj, ensure_ascii=False) + '\n')
            
            logger.info(f"Exported {len(examples)} training examples to {filepath}")
            return len(examples)
            
        except Exception as e:
            logger.error(f"Error exporting training data: {e}")
            raise
    
    def _get_system_prompt(self, agent_name: str) -> str:
        """Get system prompt for agent"""
        prompts = {
            "alex": "You are Alex, a friendly and empathetic patient care specialist at a dental clinic. You help patients with appointments, answer questions about treatments, and provide compassionate support.",
            "cfo": "You are Marcus, the CFO of a dental clinic, responsible for financial analysis, revenue tracking, and business insights. You provide data-driven financial guidance.",
            "admin": "You are Sophia, the practice administrator managing operations, scheduling, and clinic efficiency. You ensure smooth daily operations.",
            "Assistant": "You are a helpful AI assistant for a dental clinic, providing information and support to patients and staff."
        }
        return prompts.get(agent_name.lower(), prompts["Assistant"])
    
    def get_conversation_feedback(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all feedback for a specific conversation"""
        try:
            feedback = self.db.get_feedback(conversation_id=conversation_id)
            return feedback
        except Exception as e:
            logger.error(f"Error getting conversation feedback: {e}")
            return []
    
    def clear_feedback(self):
        """Clear all feedback (for testing)"""
        try:
            self.db.clear_all()
            logger.info("Cleared all feedback")
        except Exception as e:
            logger.error(f"Error clearing feedback: {e}")
            raise


# Global instance
feedback_service = FeedbackService()
