"""
Enhanced AI Message Processor with Engine Support
מעבד הודעות AI משופר עם תמיכה במנועים
"""

import asyncio
import logging
import json
from typing import Dict, Any
from datetime import datetime

from .engines.ai_engine_factory import AIEngineFactory, AIEngineType, AIEngineConfig
from .interfaces.ai_agent_interface import MessageProcessorInterface
from ..shared.redis_queue import RedisQueueManager

logger = logging.getLogger(__name__)

class EnhancedAIMessageProcessor(MessageProcessorInterface):
    """Enhanced AI Message Processor with pluggable AI engines"""
    
    def __init__(self, engine_type: AIEngineType = AIEngineType.OPENMANUS):
        self.engine_type = engine_type
        self.ai_engine = None
        self.agents = {}
        self.queue_manager = RedisQueueManager("redis://redis:6379/0")
        self.queue_name = "ai_messages"
        self.running = False
    
    async def initialize(self):
        """Initialize the enhanced message processor"""
        try:
            # Initialize queue manager
            await self.queue_manager.initialize()
            
            # Create AI engine
            config = AIEngineConfig.get_config_for_engine(self.engine_type)
            self.ai_engine = await AIEngineFactory.create_engine(self.engine_type, config)
            
            # Create agents
            await self._create_agents(config)
            
            logger.info(f"Enhanced AI Message Processor initialized with {self.engine_type.value} engine")
            
        except Exception as e:
            logger.error(f"Error initializing Enhanced AI Message Processor: {e}")
            raise
    
    async def _create_agents(self, config: Dict[str, Any]):
        """Create AI agents based on configuration"""
        try:
            agents_config = config.get("agents", {})
            
            for agent_name, agent_config in agents_config.items():
                agent_config["name"] = agent_name
                agent = await self.ai_engine.create_agent(agent_config)
                self.agents[agent_name] = agent
                logger.info(f"Created agent: {agent_name}")
                
        except Exception as e:
            logger.error(f"Error creating agents: {e}")
            raise
    
    async def process_message(self, message_data) -> Dict[str, Any]:
        """Process a single message using the appropriate agent"""
        try:
            logger.info(f"Processing message: {message_data}")
            
            # Handle both string and dict inputs
            if isinstance(message_data, str):
                text = message_data
                sender_id = ""
                channel = "api"
                metadata = {}
            else:
                # Extract message details from dict
                text = message_data.get("text")
                if text is None:
                    text = ""
                sender_id = message_data.get("sender_id", "")
                channel = message_data.get("channel", "api")
                metadata = message_data.get("metadata", {})
            
            # Determine which agent should handle this message
            agent_name = await self._route_to_agent(text, metadata)
            agent = self.agents.get(agent_name, self.agents.get("receptionist"))
            
            if not agent:
                raise RuntimeError("No suitable agent found")
            
            # Process with selected agent
            response = await agent.process_message(text, sender_id, metadata)
            
            # Prepare result
            result = {
                "success": True,
                "response": response.get("response", ""),
                "agent_used": agent_name,
                "intent": response.get("intent", "unknown"),
                "sender_id": sender_id,
                "channel": channel,
                "processed_at": datetime.now().isoformat(),
                "metadata": metadata,
                "engine_type": self.engine_type.value
            }
            
            logger.info(f"Message processed successfully by {agent_name} for {sender_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
            # Handle error response for both string and dict inputs
            if isinstance(message_data, str):
                sender_id = ""
                channel = "api"
            else:
                sender_id = message_data.get("sender_id", "")
                channel = message_data.get("channel", "api")
            
            return {
                "success": False,
                "error": str(e),
                "sender_id": sender_id,
                "channel": channel,
                "processed_at": datetime.now().isoformat(),
                "engine_type": self.engine_type.value
            }
    
    async def _route_to_agent(self, text: str, metadata: Dict[str, Any]) -> str:
        """Route message to appropriate agent based on content"""
        if not text:
            return "receptionist"
        text_lower = text.lower()

        # More specific confirmation keywords first
        if any(word in text_lower for word in ["cancel", "ביטול", "confirm", "אישור", "reminder", "תזכורת"]):
            return "confirmation"
        elif any(word in text_lower for word in ["appointment", "schedule", "book", "תור", "לקבוע"]):
            return "scheduler"
        else:
            return "receptionist"
    
    async def start_processing(self, max_workers: int = 2):
        """Start processing messages from the queue"""
        try:
            logger.info(f"Starting Enhanced AI Message Processor with {max_workers} workers")
            
            # Start workers
            await self.queue_manager.start_worker(
                self.queue_name,
                self.process_message,
                max_workers
            )
            
            self.running = True
            logger.info("Enhanced AI Message Processor started successfully")
            
        except Exception as e:
            logger.error(f"Error starting Enhanced AI Message Processor: {e}")
            raise
    
    async def stop_processing(self):
        """Stop processing messages"""
        try:
            self.running = False
            await self.queue_manager.stop_workers(self.queue_name)
            logger.info("Enhanced AI Message Processor stopped")
        except Exception as e:
            logger.error(f"Error stopping Enhanced AI Message Processor: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        try:
            queue_stats = await self.queue_manager.get_queue_stats(self.queue_name)
            engine_info = await self.ai_engine.get_engine_info() if self.ai_engine else {}
            
            # Get agent health status
            agent_health = {}
            for agent_name, agent in self.agents.items():
                agent_health[agent_name] = await agent.health_check()
            
            return {
                "processor_running": self.running,
                "engine_type": self.engine_type.value,
                "engine_info": engine_info,
                "queue_stats": queue_stats,
                "agents_count": len(self.agents),
                "agent_health": agent_health,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.stop_processing()
            
            # Cleanup agents
            for agent_name, agent in self.agents.items():
                await agent.cleanup()
                logger.info(f"Cleaned up agent: {agent_name}")
            
            # Cleanup engine
            if self.ai_engine:
                await self.ai_engine.shutdown()
            
            # Cleanup queue manager
            await self.queue_manager.cleanup()
            
            logger.info("Enhanced AI Message Processor cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Global instance
enhanced_message_processor = EnhancedAIMessageProcessor()

async def main():
    """Main function to run the enhanced message processor"""
    try:
        await enhanced_message_processor.initialize()
        await enhanced_message_processor.start_processing()
        
        # Keep running and show stats periodically
        while True:
            await asyncio.sleep(30)
            stats = await enhanced_message_processor.get_stats()
            logger.info(f"Enhanced Processor stats: {stats}")
            
    except KeyboardInterrupt:
        logger.info("Shutting down Enhanced AI Message Processor...")
        await enhanced_message_processor.cleanup()
    except Exception as e:
        logger.error(f"Error in main: {e}")
        await enhanced_message_processor.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
