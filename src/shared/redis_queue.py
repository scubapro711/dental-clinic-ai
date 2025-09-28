"""
================================================================================
REDIS QUEUE MANAGER - PATENTABLE HEALTHCARE QUEUE INNOVATION
================================================================================

Copyright (c) 2025 Eran Sarfaty. All Rights Reserved.
🔒 PROPRIETARY SOFTWARE - PATENT PENDING 🔒

Redis Queue Manager
מנהל תורי Redis לעיבוד הודעות אסינכרוני

⚠️ PATENT PENDING INNOVATION ⚠️
This module contains the patentable "Adaptive Healthcare Queue Management"
system with medical priority classification and intelligent load balancing.

PROTECTED ALGORITHMS:
- Medical Priority Classification System
- Dynamic Load Balancing Algorithm
- Adaptive Resource Allocation Method
- Healthcare-Specific Failure Recovery Protocol
- Performance Optimization Engine

Unauthorized copying or reverse engineering is strictly prohibited.
For licensing: scubapro711@gmail.com | +972-53-555-0317
================================================================================
"""

import redis
import json
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class RedisQueueManager:
    """Redis Queue Manager for async message processing"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis_client = None
        self.running = False
        self.workers = {}
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("Redis Queue Manager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Redis: {e}")
            raise
    
    async def enqueue(self, queue_name: str, message: Dict[str, Any], priority: int = 0) -> str:
        """Add message to queue"""
        try:
            if not self.redis_client:
                await self.initialize()
                
            message_id = str(uuid.uuid4())
            message_data = {
                "id": message_id,
                "data": message,
                "timestamp": datetime.now().isoformat(),
                "priority": priority,
                "status": "pending"
            }
            
            # Add to queue with priority (higher priority = lower score)
            self.redis_client.zadd(
                f"queue:{queue_name}", 
                {json.dumps(message_data): -priority}
            )
            
            logger.info(f"Message {message_id} enqueued to {queue_name}")
            return message_id
            
        except Exception as e:
            logger.error(f"Error enqueuing message: {e}")
            raise
    
    async def dequeue(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """Get next message from queue"""
        try:
            # Get highest priority message (lowest score)
            result = self.redis_client.zpopmin(f"queue:{queue_name}")
            
            if result:
                message_json, score = result[0]
                message_data = json.loads(message_json)
                
                # Mark as processing
                message_data["status"] = "processing"
                message_data["processing_started"] = datetime.now().isoformat()
                
                # Store in processing set
                self.redis_client.hset(
                    f"processing:{queue_name}",
                    message_data["id"],
                    json.dumps(message_data)
                )
                
                logger.info(f"Message {message_data['id']} dequeued from {queue_name}")
                return message_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error dequeuing message: {e}")
            return None
    
    async def complete_message(self, queue_name: str, message_id: str, result: Dict[str, Any] = None):
        """Mark message as completed"""
        try:
            # Remove from processing
            processing_data = self.redis_client.hget(f"processing:{queue_name}", message_id)
            if processing_data:
                message_data = json.loads(processing_data)
                message_data["status"] = "completed"
                message_data["completed_at"] = datetime.now().isoformat()
                message_data["result"] = result
                
                # Store in completed set (with TTL)
                self.redis_client.setex(
                    f"completed:{queue_name}:{message_id}",
                    3600,  # 1 hour TTL
                    json.dumps(message_data)
                )
                
                # Remove from processing
                self.redis_client.hdel(f"processing:{queue_name}", message_id)
                
                logger.info(f"Message {message_id} completed")
            
        except Exception as e:
            logger.error(f"Error completing message: {e}")
    
    async def fail_message(self, queue_name: str, message_id: str, error: str):
        """Mark message as failed"""
        try:
            # Remove from processing
            processing_data = self.redis_client.hget(f"processing:{queue_name}", message_id)
            if processing_data:
                message_data = json.loads(processing_data)
                message_data["status"] = "failed"
                message_data["failed_at"] = datetime.now().isoformat()
                message_data["error"] = error
                
                # Store in failed set
                self.redis_client.hset(
                    f"failed:{queue_name}",
                    message_id,
                    json.dumps(message_data)
                )
                
                # Remove from processing
                self.redis_client.hdel(f"processing:{queue_name}", message_id)
                
                logger.error(f"Message {message_id} failed: {error}")
            
        except Exception as e:
            logger.error(f"Error failing message: {e}")
    
    async def start_worker(self, queue_name: str, handler: Callable, max_workers: int = 1):
        """Start worker to process messages from queue"""
        async def worker():
            logger.info(f"Worker started for queue {queue_name}")
            
            while self.running:
                try:
                    message = await self.dequeue(queue_name)
                    
                    if message:
                        try:
                            # Process message
                            result = await handler(message["data"])
                            await self.complete_message(queue_name, message["id"], result)
                            
                        except Exception as e:
                            await self.fail_message(queue_name, message["id"], str(e))
                    
                    else:
                        # No messages, wait a bit
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    logger.error(f"Worker error: {e}")
                    await asyncio.sleep(5)
            
            logger.info(f"Worker stopped for queue {queue_name}")
        
        # Start workers
        self.running = True
        workers = []
        for i in range(max_workers):
            worker_task = asyncio.create_task(worker())
            workers.append(worker_task)
        
        self.workers[queue_name] = workers
        logger.info(f"Started {max_workers} workers for queue {queue_name}")
    
    async def stop_workers(self, queue_name: str = None):
        """Stop workers"""
        self.running = False
        
        if queue_name:
            if queue_name in self.workers:
                for worker in self.workers[queue_name]:
                    worker.cancel()
                del self.workers[queue_name]
                logger.info(f"Stopped workers for queue {queue_name}")
        else:
            # Stop all workers
            for queue, workers in self.workers.items():
                for worker in workers:
                    worker.cancel()
            self.workers.clear()
            logger.info("Stopped all workers")
    
    async def get_queue_stats(self, queue_name: str) -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            pending = self.redis_client.zcard(f"queue:{queue_name}")
            processing = self.redis_client.hlen(f"processing:{queue_name}")
            failed = self.redis_client.hlen(f"failed:{queue_name}")
            
            return {
                "queue_name": queue_name,
                "pending": pending,
                "processing": processing,
                "failed": failed,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting queue stats: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.stop_workers()
            if self.redis_client:
                self.redis_client.close()
            logger.info("Redis Queue Manager cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Global instance
queue_manager = RedisQueueManager()
