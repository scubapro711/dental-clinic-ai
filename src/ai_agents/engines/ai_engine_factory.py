"""
================================================================================
AI ENGINE FACTORY - PATENTABLE INNOVATION
================================================================================

Copyright (c) 2025 Eran Sarfaty. All Rights Reserved.
🔒 PROPRIETARY SOFTWARE - PATENT PENDING 🔒

AI Engine Factory - Factory for creating AI engines
מפעל מנועי AI - מפעל ליצירת מנועי AI

⚠️ PATENT PENDING INNOVATION ⚠️
This module contains the core patentable "Multi-Agent AI Orchestration System"
including dynamic engine selection and failover mechanisms.

PROTECTED ALGORITHMS:
- Dynamic AI Engine Selection Method
- Multi-Agent Coordination Protocol  
- Automatic Failover and Load Balancing
- Context Preservation Across Engine Transitions

Unauthorized copying or reverse engineering is strictly prohibited.
For licensing: scubapro711@gmail.com | +972-53-555-0317
================================================================================
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

from ..interfaces.ai_agent_interface import AIEngineInterface
from .crewai_engine import CrewAIEngine
# from .openmanus_engine import OpenManusEngine  # Future implementation

logger = logging.getLogger(__name__)

class AIEngineType(Enum):
    """Supported AI engine types"""
    CREWAI = "crewai"
    OPENMANUS = "openmanus"

class AIEngineFactory:
    """Factory for creating AI engines with future OpenManus support"""
    
    _engines = {
        AIEngineType.CREWAI: CrewAIEngine,
        # AIEngineType.OPENMANUS: OpenManusEngine,  # Future implementation
    }
    
    @classmethod
    async def create_engine(
        cls, 
        engine_type: AIEngineType, 
        config: Dict[str, Any]
    ) -> AIEngineInterface:
        """Create an AI engine instance"""
        try:
            if engine_type not in cls._engines:
                raise ValueError(f"Unsupported engine type: {engine_type}")
            
            engine_class = cls._engines[engine_type]
            engine = engine_class()
            await engine.initialize(config)
            
            logger.info(f"Created AI engine: {engine_type.value}")
            return engine
            
        except Exception as e:
            logger.error(f"Error creating AI engine {engine_type.value}: {e}")
            raise
    
    @classmethod
    def get_supported_engines(cls) -> list[AIEngineType]:
        """Get list of supported engine types"""
        return list(cls._engines.keys())
    
    @classmethod
    async def create_default_engine(cls, config: Dict[str, Any]) -> AIEngineInterface:
        """Create default AI engine (CrewAI for now)"""
        return await cls.create_engine(AIEngineType.CREWAI, config)

# Configuration helper
class AIEngineConfig:
    """Configuration helper for AI engines"""
    
    @staticmethod
    def get_crewai_config() -> Dict[str, Any]:
        """Get default CrewAI configuration"""
        return {
            "engine_type": "crewai",
            "model": "gpt-4o-mini",
            "temperature": 0.1,
            "max_tokens": 2000,
            "agents": {
                "receptionist": {
                    "role": "Receptionist Agent",
                    "goal": "Handle patient inquiries and appointment requests",
                    "backstory": "You are a helpful dental clinic receptionist"
                },
                "scheduler": {
                    "role": "Scheduler Agent", 
                    "goal": "Schedule and manage appointments",
                    "backstory": "You are an expert at managing dental appointments"
                },
                "confirmation": {
                    "role": "Confirmation Agent",
                    "goal": "Confirm appointments and send reminders",
                    "backstory": "You ensure patients are reminded of their appointments"
                }
            }
        }
    
    @staticmethod
    def get_openmanus_config() -> Dict[str, Any]:
        """Get default OpenManus configuration (future implementation)"""
        return {
            "engine_type": "openmanus",
            "model": "gpt-4o",
            "temperature": 0.0,
            "max_tokens": 4096,
            "tools": [
                "browser_automation",
                "file_processing", 
                "web_search",
                "dental_pms_integration"
            ],
            "capabilities": [
                "appointment_scheduling",
                "patient_communication",
                "document_processing",
                "automated_workflows"
            ]
        }
    
    @staticmethod
    def get_config_for_engine(engine_type: AIEngineType) -> Dict[str, Any]:
        """Get configuration for specific engine type"""
        if engine_type == AIEngineType.CREWAI:
            return AIEngineConfig.get_crewai_config()
        elif engine_type == AIEngineType.OPENMANUS:
            return AIEngineConfig.get_openmanus_config()
        else:
            raise ValueError(f"Unknown engine type: {engine_type}")
