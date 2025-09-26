#!/usr/bin/env python3
"""
AI Agents Service - Main Entry Point
שירות סוכני הבינה המלאכותית - נקודת כניסה ראשית

This service runs the AI agents worker that processes messages from Redis Queue.
"""

import asyncio
import logging
import signal
import sys
import os
from typing import Optional

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.ai_agents.enhanced_message_processor import EnhancedAIMessageProcessor
from src.ai_agents.engines.ai_engine_factory import AIEngineType
from src.ai_agents.health_server import health_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/ai_agents.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

class AIAgentsService:
    """Main AI Agents Service"""
    
    def __init__(self):
        self.processor: Optional[EnhancedAIMessageProcessor] = None
        self.running = False
        
    async def start(self):
        """Start the AI Agents Service"""
        try:
            logger.info("🚀 Starting AI Agents Service...")
            
            # Start health check server
            await health_server.start()
            
            # Create and initialize the enhanced message processor
            self.processor = EnhancedAIMessageProcessor(AIEngineType.CREWAI)
            await self.processor.initialize()
            
            # Start processing messages
            await self.processor.start_processing(max_workers=3)
            
            self.running = True
            logger.info("✅ AI Agents Service started successfully")
            
            # Keep the service running and show periodic stats
            await self._run_service_loop()
            
        except Exception as e:
            logger.error(f"❌ Error starting AI Agents Service: {e}")
            raise
    
    async def _run_service_loop(self):
        """Main service loop with periodic status updates"""
        stats_interval = 60  # Show stats every minute
        last_stats_time = 0
        
        while self.running:
            try:
                # Show stats periodically
                current_time = asyncio.get_event_loop().time()
                if current_time - last_stats_time >= stats_interval:
                    if self.processor:
                        stats = await self.processor.get_stats()
                        logger.info(f"📊 Service Stats: {stats}")
                    last_stats_time = current_time
                
                # Sleep for a short interval
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in service loop: {e}")
                await asyncio.sleep(10)
    
    async def stop(self):
        """Stop the AI Agents Service"""
        try:
            logger.info("🛑 Stopping AI Agents Service...")
            self.running = False
            
            if self.processor:
                await self.processor.cleanup()
            
            # Stop health server
            await health_server.stop()
            
            logger.info("✅ AI Agents Service stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping AI Agents Service: {e}")

# Global service instance
service = AIAgentsService()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    asyncio.create_task(service.stop())

async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy" if service.running else "stopped",
        "service": "ai-agents",
        "timestamp": asyncio.get_event_loop().time()
    }

async def main():
    """Main function"""
    try:
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("🦷 AI Dental Clinic - AI Agents Service")
        logger.info("=" * 50)
        
        # Start the service
        await service.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        await service.stop()
    except Exception as e:
        logger.error(f"Fatal error in AI Agents Service: {e}")
        await service.stop()
        sys.exit(1)

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs('/app/logs', exist_ok=True)
    
    # Run the service
    asyncio.run(main())
