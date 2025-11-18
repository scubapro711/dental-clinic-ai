#!/usr/bin/env python3
"""
Populate demo data by invoking the agent graph.

This script creates realistic checkpoints by actually running the agent graph,
which ensures all metadata and structure is correct.

SAFE: Uses the actual graph.invoke() method like production code.
"""

import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import random
import asyncio

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.agents.agent_graph_v5 import agent_graph_v5
from app.agents.graph_state import AgentState
from langchain_core.messages import HumanMessage, AIMessage
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Demo data constants
ORG_ID = "751d7aa8-07d4-4cff-b5b4-1ea199889cbd"  # DentaFlow Clinic

PATIENT_NAMES = [
    "David Cohen", "Sarah Levy", "Michael Mizrahi", "Rachel Goldstein",
    "Yossi Peretz", "Tamar Katz", "Avi Shapira", "Noa Ben-David",
    "Eitan Friedman", "Maya Rosenberg", "Daniel Aharoni", "Shira Weiss",
    "Amit Biton", "Lior Azoulay", "Chen Dahan", "Yael Golan",
    "Ron Malka", "Tal Oren", "Nir Barak", "Michal Segal"
]

# User prompts that will trigger different agents and create decisions
PROMPTS = {
    "Alex": [
        "Patient {patient} called to reschedule their appointment from tomorrow to next week. Can you help?",
        "We need to confirm appointments for tomorrow. Can you call {patient} to remind them?",
        "{patient} hasn't responded to our appointment reminder. What should we do?",
        "{patient} is requesting an emergency appointment today due to severe tooth pain.",
        "Can you send a follow-up message to {patient} about their upcoming appointment?"
    ],
    "Sarah": [
        "I need to review the treatment plan for {patient}. They need a complex multi-phase procedure.",
        "{patient}'s X-ray results show additional work is needed. Can you update the treatment plan?",
        "What preventive care would you recommend for {patient} based on their oral health history?",
        "{patient} is experiencing tooth sensitivity. What diagnostic steps should we take?",
        "Can you assess if {patient} needs a specialist consultation for their case?"
    ],
    "Marcus": [
        "{patient} is asking about payment plan options for an expensive procedure. Can you help?",
        "We need to verify insurance coverage for {patient}'s upcoming treatment.",
        "The insurance payment for {patient} was lower than expected. Can you review?",
        "{patient} is experiencing financial hardship. Can we offer extended payment terms?",
        "Can you create a bundled payment plan for {patient}'s multiple procedures?"
    ],
    "Sophia": [
        "We have a scheduling gap tomorrow. Can we fit in an emergency appointment for {patient}?",
        "There's a double-booking for {patient}'s time slot. How should we handle this?",
        "We need to optimize the schedule for next week. {patient} has requested a specific time.",
        "Equipment maintenance is scheduled tomorrow. Can you redistribute {patient}'s appointments?",
        "Can you check for appointment conflicts for {patient} next week?"
    ],
    "Harper": [
        "{patient}'s consent form is missing a signature. What's the compliance protocol?",
        "We need to update documentation for {patient}'s file. Can you review what's missing?",
        "A HIPAA audit detected missing information in {patient}'s records. Can you help?",
        "{patient} requested access to their medical records. What's the proper procedure?",
        "Can you verify if all compliance requirements are met for {patient}'s recent treatment?"
    ]
}


def create_demo_conversations():
    """Create demo conversations by invoking the graph."""
    
    logger.info("=" * 60)
    logger.info("CREATING DEMO CONVERSATIONS VIA GRAPH")
    logger.info("=" * 60)
    
    try:
        # Step 1: Clear existing demo checkpoints
        logger.info("\nStep 1: Clearing existing demo checkpoints...")
        from sqlalchemy import create_engine, text
        from app.core.config import settings
        
        engine = create_engine(settings.CHECKPOINT_DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(
                text("DELETE FROM checkpoints WHERE thread_id LIKE 'demo_%'"),
                {}
            )
            conn.commit()
            logger.info(f"Deleted {result.rowcount} existing demo checkpoints")
        
        # Step 2: Create conversations
        logger.info("\nStep 2: Creating 20 demo conversations...")
        
        conversations_created = 0
        patient_idx = 0
        
        # Create 4 conversations per agent (20 total)
        for agent_name in ["Alex", "Sarah", "Marcus", "Sophia", "Harper"]:
            agent_prompts = PROMPTS[agent_name]
            
            for i in range(4):
                patient_name = PATIENT_NAMES[patient_idx % len(PATIENT_NAMES)]
                patient_idx += 1
                
                # Select random prompt and fill in patient name
                prompt_template = random.choice(agent_prompts)
                prompt = prompt_template.format(patient=patient_name)
                
                # Create unique thread_id
                thread_id = f"demo_{agent_name.lower()}_{uuid.uuid4().hex[:12]}"
                
                # Create initial state
                initial_state: AgentState = {
                    "messages": [HumanMessage(content=prompt)],
                    "current_agent": "supervisor",
                    "next_agent": None,
                    "context": {
                        "org_id": ORG_ID,
                        "patient_name": patient_name,
                        "demo_mode": True
                    }
                }
                
                # Configuration with thread_id
                config = {
                    "configurable": {
                        "thread_id": thread_id
                    }
                }
                
                try:
                    logger.info(f"  Creating conversation {conversations_created + 1}/20: {agent_name} - {patient_name}")
                    
                    # Invoke the graph (this will create checkpoints automatically)
                    result = agent_graph_v5.graph.invoke(initial_state, config)
                    
                    conversations_created += 1
                    
                except Exception as e:
                    logger.warning(f"  Failed to create conversation: {e}")
                    continue
        
        logger.info(f"\n✅ Created {conversations_created} conversations")
        
        # Step 3: Verify checkpoints were created
        logger.info("\nStep 3: Verifying checkpoints...")
        
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT COUNT(*) FROM checkpoints WHERE thread_id LIKE 'demo_%'"),
                {}
            )
            count = result.scalar()
            logger.info(f"Total demo checkpoints: {count}")
            
            # Show sample
            result = conn.execute(
                text("""
                    SELECT 
                        thread_id,
                        checkpoint_id,
                        metadata
                    FROM checkpoints 
                    WHERE thread_id LIKE 'demo_%'
                    LIMIT 3
                """),
                {}
            )
            
            logger.info("\nSample checkpoints:")
            for row in result:
                logger.info(f"  Thread: {row.thread_id}")
                logger.info(f"  Metadata: {row.metadata}")
                logger.info("")
        
        logger.info("=" * 60)
        logger.info("✅ DEMO CONVERSATIONS CREATED SUCCESSFULLY")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    create_demo_conversations()
