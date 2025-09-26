"""
CrewAI Engine Implementation
יישום מנוע CrewAI
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from ..interfaces.ai_agent_interface import AIEngineInterface, AIAgentInterface
from ..crewai_agents.crewai_agent_wrapper import CrewAIAgentWrapper

logger = logging.getLogger(__name__)

class CrewAIEngine(AIEngineInterface):
    """CrewAI engine implementation"""
    
    def __init__(self):
        self.config = None
        self.agents = {}
        self.initialized = False
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the CrewAI engine"""
        try:
            self.config = config
            logger.info("CrewAI engine initialized successfully")
            self.initialized = True
        except Exception as e:
            logger.error(f"Error initializing CrewAI engine: {e}")
            raise
    
    async def create_agent(self, agent_config: Dict[str, Any]) -> AIAgentInterface:
        """Create a new CrewAI agent"""
        try:
            if not self.initialized:
                raise RuntimeError("Engine not initialized")
            
            agent_name = agent_config.get("name", "default_agent")
            agent = CrewAIAgentWrapper(agent_config, self.config)
            await agent.initialize()
            
            self.agents[agent_name] = agent
            logger.info(f"Created CrewAI agent: {agent_name}")
            return agent
            
        except Exception as e:
            logger.error(f"Error creating CrewAI agent: {e}")
            raise
    
    async def get_engine_info(self) -> Dict[str, Any]:
        """Get CrewAI engine information"""
        return {
            "engine_type": "crewai",
            "version": "0.1.0",
            "initialized": self.initialized,
            "agents_count": len(self.agents),
            "agents": list(self.agents.keys()),
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self) -> None:
        """Shutdown the CrewAI engine"""
        try:
            for agent_name, agent in self.agents.items():
                await agent.cleanup()
                logger.info(f"Cleaned up agent: {agent_name}")
            
            self.agents.clear()
            self.initialized = False
            logger.info("CrewAI engine shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during CrewAI engine shutdown: {e}")
            raise
