"""
OpenManus Engine Implementation
יישום מנוע OpenManus
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from ..interfaces.ai_agent_interface import AIEngineInterface, AIAgentInterface
from ..openmanus_agents.openmanus_agent_wrapper import OpenManusAgentWrapper

logger = logging.getLogger(__name__)

class OpenManusEngine(AIEngineInterface):
    """OpenManus engine implementation with advanced AI capabilities"""
    
    def __init__(self):
        self.config = None
        self.agents = {}
        self.initialized = False
        logger.info("OpenManus engine created")
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the OpenManus engine"""
        try:
            self.config = config
            logger.info("🚀 OpenManus engine initialized successfully")
            self.initialized = True
        except Exception as e:
            logger.error(f"Error initializing OpenManus engine: {e}")
            raise
    
    async def create_agent(self, agent_config: Dict[str, Any]) -> AIAgentInterface:
        """Create a new OpenManus agent"""
        try:
            if not self.initialized:
                raise RuntimeError("Engine not initialized")
            
            agent_name = agent_config.get("name", "default_agent")
            agent = OpenManusAgentWrapper(agent_config, self.config)
            await agent.initialize()
            
            self.agents[agent_name] = agent
            logger.info(f"🤖 Created OpenManus agent: {agent_name}")
            return agent
            
        except Exception as e:
            logger.error(f"Error creating OpenManus agent: {e}")
            raise
    
    async def get_engine_info(self) -> Dict[str, Any]:
        """Get OpenManus engine information"""
        return {
            "engine_type": "openmanus",
            "version": "1.0.0",
            "initialized": self.initialized,
            "agents_count": len(self.agents),
            "agents": list(self.agents.keys()),
            "capabilities": [
                "advanced_nlp",
                "browser_automation", 
                "python_execution",
                "file_management",
                "mcp_integration",
                "multi_agent_coordination"
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self) -> None:
        """Shutdown the OpenManus engine"""
        try:
            for agent_name, agent in self.agents.items():
                await agent.cleanup()
                logger.info(f"Cleaned up OpenManus agent: {agent_name}")
            
            self.agents.clear()
            self.initialized = False
            logger.info("🔴 OpenManus engine shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during OpenManus engine shutdown: {e}")
            raise
