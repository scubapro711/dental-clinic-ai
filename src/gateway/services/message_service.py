"""
Message Service
שירות לעיבוד הודעות דרך Redis Queue
"""

import logging
from typing import Dict, Any
from ..config import get_settings
from ...shared.redis_queue import RedisQueueManager

logger = logging.getLogger(__name__)

class MessageService:
    """Service for processing messages through Redis Queue"""
    
    def __init__(self):
        self.settings = get_settings()
        self.queue_name = "ai_messages"
        self.queue_manager = RedisQueueManager("redis://redis:6379/0")
    
    async def initialize(self):
        """Initialize the message service"""
        try:
            await self.queue_manager.initialize()
            logger.info("Message Service initialized")
        except Exception as e:
            logger.error(f"Error initializing Message Service: {e}")
            raise
    
    async def process_message_async(self, message_data: Dict[str, Any]) -> str:
        """Process message asynchronously through Redis Queue"""
        try:
            # Add message to queue
            message_id = await self.queue_manager.enqueue(
                self.queue_name,
                message_data,
                priority=1  # Normal priority
            )
            
            logger.info(f"Message {message_id} queued for processing")
            return message_id
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise
    
    async def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Get status of a message"""
        try:
            # Check if message is completed
            completed_key = f"completed:{self.queue_name}:{message_id}"
            completed_data = self.queue_manager.redis_client.get(completed_key)
            
            if completed_data:
                import json
                return json.loads(completed_data)
            
            # Check if message is processing
            processing_data = self.queue_manager.redis_client.hget(
                f"processing:{self.queue_name}", 
                message_id
            )
            
            if processing_data:
                import json
                return json.loads(processing_data)
            
            # Check if message failed
            failed_data = self.queue_manager.redis_client.hget(
                f"failed:{self.queue_name}", 
                message_id
            )
            
            if failed_data:
                import json
                return json.loads(failed_data)
            
            # Message not found
            return {
                "id": message_id,
                "status": "not_found",
                "error": "Message not found"
            }
            
        except Exception as e:
            logger.error(f"Error getting message status: {e}")
            return {
                "id": message_id,
                "status": "error",
                "error": str(e)
            }
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            return await self.queue_manager.get_queue_stats(self.queue_name)
        except Exception as e:
            logger.error(f"Error getting queue stats: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.queue_manager.cleanup()
            logger.info("Message Service cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Global instance
# Global instance
# message_service = MessageService()
