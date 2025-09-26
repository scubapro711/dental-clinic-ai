"""
AI Agent Interface - Abstract base for all AI agents
ממשק סוכן AI - בסיס מופשט לכל סוכני AI
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

class AIAgentInterface(ABC):
    """Abstract interface for all AI agents - enables future OpenManus integration"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the AI agent"""
        pass
    
    @abstractmethod
    async def process_message(self, text: str, sender_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message and return response"""
        pass
    
    @abstractmethod
    async def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health status"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup agent resources"""
        pass

class MessageProcessorInterface(ABC):
    """Abstract interface for message processors"""
    
    @abstractmethod
    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single message"""
        pass
    
    @abstractmethod
    async def start_processing(self, max_workers: int = 2) -> None:
        """Start processing messages from queue"""
        pass
    
    @abstractmethod
    async def stop_processing(self) -> None:
        """Stop processing messages"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        pass

class TaskExecutorInterface(ABC):
    """Abstract interface for task executors"""
    
    @abstractmethod
    async def execute_task(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task"""
        pass
    
    @abstractmethod
    async def get_supported_tasks(self) -> List[str]:
        """Get list of supported task types"""
        pass
    
    @abstractmethod
    async def validate_task(self, task_type: str, task_data: Dict[str, Any]) -> bool:
        """Validate if task can be executed"""
        pass

class AIEngineInterface(ABC):
    """Abstract interface for AI engines (CrewAI, OpenManus, etc.)"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the AI engine"""
        pass
    
    @abstractmethod
    async def create_agent(self, agent_config: Dict[str, Any]) -> AIAgentInterface:
        """Create a new AI agent"""
        pass
    
    @abstractmethod
    async def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the AI engine"""
        pass
