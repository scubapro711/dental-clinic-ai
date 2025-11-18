#!/usr/bin/env python3
"""
Populate demo decisions in correct format for the Decisions API.

This script creates LangGraph checkpoints with messages in the format
expected by get_pending_decisions() function.

SAFE: Uses PostgresSaver API with correct message structure.
"""

import sys
import uuid
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import random

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from langgraph.checkpoint.postgres import PostgresSaver
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Demo data constants
ORG_ID = "751d7aa8-07d4-4cff-b5b4-1ea199889cbd"  # DentaFlow Clinic

AGENTS = ["Alex", "Sarah", "Marcus", "Sophia", "Harper"]

DECISION_TEMPLATES = {
    "Alex": [
        {
            "title": "Appointment reschedule request",
            "description": "Patient {patient} requested to move appointment due to work conflict",
            "action": "Reschedule to suggested time slot",
            "decision_type": "appointment_reschedule"
        },
        {
            "title": "Patient communication needed",
            "description": "Patient {patient} hasn't responded to appointment reminder",
            "action": "Call patient to confirm attendance",
            "decision_type": "patient_communication"
        },
        {
            "title": "Emergency appointment request",
            "description": "Patient {patient} reports severe tooth pain, requesting urgent care",
            "action": "Schedule emergency appointment today",
            "decision_type": "appointment_reschedule"
        }
    ],
    "Sarah": [
        {
            "title": "Treatment plan review required",
            "description": "Complex case for {patient} requiring multi-phase treatment",
            "action": "Approve specialist consultation",
            "decision_type": "treatment_plan_review"
        },
        {
            "title": "Clinical assessment needed",
            "description": "X-ray results for {patient} indicate additional work needed",
            "action": "Update treatment plan and notify patient",
            "decision_type": "clinical_assessment"
        },
        {
            "title": "Procedure recommendation",
            "description": "Preventive care recommended for {patient} based on oral health history",
            "action": "Schedule follow-up procedure",
            "decision_type": "procedure_recommendation"
        }
    ],
    "Marcus": [
        {
            "title": "Payment plan creation",
            "description": "Patient {patient} requested installment plan for expensive procedure",
            "action": "Approve 6-month payment schedule",
            "decision_type": "payment_plan_creation"
        },
        {
            "title": "Insurance verification needed",
            "description": "Patient {patient}'s insurance requires pre-authorization",
            "action": "Submit pre-authorization request",
            "decision_type": "insurance_verification"
        },
        {
            "title": "Billing adjustment required",
            "description": "Insurance payment for {patient} lower than expected",
            "action": "Adjust patient balance and notify",
            "decision_type": "billing_adjustment"
        }
    ],
    "Sophia": [
        {
            "title": "Schedule optimization opportunity",
            "description": "Detected scheduling gap that can accommodate emergency for {patient}",
            "action": "Consolidate appointments to free up slot",
            "decision_type": "schedule_optimization"
        },
        {
            "title": "Appointment conflict detected",
            "description": "Double-booking detected for {patient}'s time slot",
            "action": "Reschedule one patient to alternative time",
            "decision_type": "appointment_conflict"
        },
        {
            "title": "Resource allocation needed",
            "description": "High demand period requires additional staff for {patient} appointments",
            "action": "Approve overtime hours for hygienist",
            "decision_type": "resource_allocation"
        }
    ],
    "Harper": [
        {
            "title": "Compliance check required",
            "description": "Patient {patient} consent form missing signature",
            "action": "Follow up before next appointment",
            "decision_type": "compliance_check"
        },
        {
            "title": "HIPAA verification needed",
            "description": "Patient {patient} file requires documentation update",
            "action": "Complete missing documentation",
            "decision_type": "hipaa_verification"
        },
        {
            "title": "Documentation review urgent",
            "description": "Treatment notes for {patient} incomplete",
            "action": "Request dentist to finalize documentation",
            "decision_type": "documentation_review"
        }
    ]
}

PATIENT_NAMES = [
    "David Cohen", "Sarah Levy", "Michael Mizrahi", "Rachel Goldstein",
    "Yossi Peretz", "Tamar Katz", "Avi Shapira", "Noa Ben-David",
    "Eitan Friedman", "Maya Rosenberg", "Daniel Aharoni", "Shira Weiss",
    "Amit Biton", "Lior Azoulay", "Chen Dahan", "Yael Golan",
    "Ron Malka", "Tal Oren", "Nir Barak", "Michal Segal"
]

PRIORITIES = ["critical", "high", "medium", "low"]
CATEGORIES = {
    "Alex": "scheduling",
    "Sarah": "clinical",
    "Marcus": "financial",
    "Sophia": "optimization",
    "Harper": "compliance"
}


def generate_decision_checkpoint(
    agent_name: str,
    patient_name: str,
    priority: str,
    is_pending: bool = True
) -> Dict[str, Any]:
    """Generate checkpoint with decision message in correct format."""
    
    thread_id = f"demo_thread_{uuid.uuid4().hex[:16]}"
    checkpoint_id = str(uuid.uuid4())
    
    # Select random decision template for this agent
    template = random.choice(DECISION_TEMPLATES[agent_name])
    
    # Generate timestamps
    if is_pending:
        hours_ago = random.randint(1, 48)
        created_at = datetime.utcnow() - timedelta(hours=hours_ago)
    else:
        days_ago = random.randint(1, 14)
        created_at = datetime.utcnow() - timedelta(days=days_ago)
    
    # Generate confidence score
    confidence = random.uniform(75, 95) if is_pending else random.uniform(85, 98)
    
    # Create decision message in the format expected by get_pending_decisions
    decision_message = {
        "type": "ai",
        "content": f"I recommend: {template['action']}",
        "title": template["title"],
        "description": template["description"].format(patient=patient_name),
        "action": template["action"],
        "priority": priority,
        "category": CATEGORIES[agent_name],
        "confidence": str(int(confidence)),
        "reasoning": template["description"].format(patient=patient_name),
        "patient_id": str(random.randint(1000, 9999)),
        "patient_name": patient_name,
        "impact_level": "high" if priority in ["critical", "high"] else "medium",
        "compliance_risk": "true" if agent_name == "Harper" else "false",
        "requires_approval": "true" if is_pending else "false",
        "approval_status": "pending" if is_pending else "approved",
        "due_by": (created_at + timedelta(hours=24)).isoformat() if is_pending else None
    }
    
    # Create checkpoint with messages in channel_values
    checkpoint = {
        "v": 1,
        "ts": created_at.isoformat(),
        "id": checkpoint_id,
        "channel_values": {
            "messages": [decision_message]
        },
        "channel_versions": {
            "__start__": 1,
            "messages": 1
        },
        "versions_seen": {
            "__input__": {},
            "__start__": {"__start__": 1}
        },
        "pending_sends": []
    }
    
    # Create metadata
    metadata = {
        "org_id": ORG_ID,
        "agent_name": agent_name,
        "decision_type": template["decision_type"],
        "category": CATEGORIES[agent_name],
        "priority": priority,
        "patient_name": patient_name,
        "status": "pending" if is_pending else "completed",
        "created_at": created_at.isoformat()
    }
    
    return {
        "thread_id": thread_id,
        "checkpoint_id": checkpoint_id,
        "checkpoint": checkpoint,
        "metadata": metadata,
        "created_at": created_at
    }


def populate_decisions():
    """Populate decisions using PostgresSaver API."""
    
    logger.info("=" * 60)
    logger.info("STARTING DEMO DECISIONS POPULATION")
    logger.info("=" * 60)
    
    try:
        # Initialize PostgresSaver
        logger.info("\nStep 1: Connecting to PostgreSQL checkpointer...")
        with PostgresSaver.from_conn_string(settings.CHECKPOINT_DATABASE_URL) as checkpointer:
            logger.info("✅ Connected successfully")
            
            # Step 2: Clear existing demo data
            logger.info("\nStep 2: Clearing existing demo checkpoints...")
            from sqlalchemy import create_engine, text
            engine = create_engine(settings.CHECKPOINT_DATABASE_URL)
            with engine.connect() as conn:
                result = conn.execute(
                    text("DELETE FROM checkpoints WHERE metadata->>'org_id' = :org_id"),
                    {"org_id": ORG_ID}
                )
                conn.commit()
                logger.info(f"Deleted {result.rowcount} existing checkpoints")
            
            # Step 3: Generate pending decisions (15 total)
            logger.info("\nStep 3: Generating 15 pending decisions...")
            pending_decisions = []
            
            # Distribution: 2 critical, 5 high, 6 medium, 2 low
            priority_distribution = [
                ("critical", 2),
                ("high", 5),
                ("medium", 6),
                ("low", 2)
            ]
            
            patient_idx = 0
            for priority, count in priority_distribution:
                for _ in range(count):
                    agent = random.choice(AGENTS)
                    patient_name = PATIENT_NAMES[patient_idx % len(PATIENT_NAMES)]
                    patient_idx += 1
                    
                    checkpoint_data = generate_decision_checkpoint(
                        agent_name=agent,
                        patient_name=patient_name,
                        priority=priority,
                        is_pending=True
                    )
                    pending_decisions.append(checkpoint_data)
            
            logger.info(f"Generated {len(pending_decisions)} pending decisions")
            
            # Step 4: Generate completed decisions (35 total)
            logger.info("\nStep 4: Generating 35 completed decisions...")
            completed_decisions = []
            
            for i in range(35):
                agent = random.choice(AGENTS)
                priority = random.choice(PRIORITIES)
                patient_name = PATIENT_NAMES[patient_idx % len(PATIENT_NAMES)]
                patient_idx += 1
                
                checkpoint_data = generate_decision_checkpoint(
                    agent_name=agent,
                    patient_name=patient_name,
                    priority=priority,
                    is_pending=False
                )
                completed_decisions.append(checkpoint_data)
            
            logger.info(f"Generated {len(completed_decisions)} completed decisions")
            
            # Step 5: Insert all checkpoints
            logger.info("\nStep 5: Inserting checkpoints using PostgresSaver API...")
            all_checkpoints = pending_decisions + completed_decisions
            
            # Sort by created_at to insert in chronological order
            all_checkpoints.sort(key=lambda x: x["created_at"])
            
            inserted_count = 0
            for cp_data in all_checkpoints:
                try:
                    config = {
                        "configurable": {
                            "thread_id": cp_data["thread_id"],
                            "checkpoint_ns": "",
                            "checkpoint_id": cp_data["checkpoint_id"]
                        }
                    }
                    
                    checkpointer.put(
                        config=config,
                        checkpoint=cp_data["checkpoint"],
                        metadata=cp_data["metadata"],
                        new_versions={}
                    )
                    
                    inserted_count += 1
                    
                    if inserted_count % 10 == 0:
                        logger.info(f"  Inserted {inserted_count}/{len(all_checkpoints)} checkpoints...")
                        
                except Exception as e:
                    logger.warning(f"  Failed to insert checkpoint: {e}")
                    continue
            
            logger.info(f"✅ Successfully inserted {inserted_count} checkpoints")
            
            # Step 6: Verify using the actual API query
            logger.info("\nStep 6: Verifying using get_pending_decisions query...")
            
            # Test the actual query that the API uses
            from sqlalchemy import create_engine, text
            engine = create_engine(settings.CHECKPOINT_DATABASE_URL)
            with engine.connect() as conn:
                # This is the exact query from get_pending_decisions
                query = text("""
                    SELECT 
                        c.thread_id,
                        c.checkpoint_id,
                        c.metadata->>'agent_name' as agent_name,
                        msg->>'title' as title,
                        msg->>'priority' as priority,
                        msg->>'requires_approval' as requires_approval,
                        msg->>'approval_status' as approval_status
                    FROM checkpoints c,
                    jsonb_array_elements(c.checkpoint->'channel_values'->'messages') as msg
                    WHERE c.metadata->>'org_id' = :org_id
                    AND msg->>'requires_approval' = 'true'
                    AND msg->>'approval_status' = 'pending'
                    ORDER BY 
                        CASE msg->>'priority'
                            WHEN 'critical' THEN 0
                            WHEN 'high' THEN 1
                            WHEN 'medium' THEN 2
                            WHEN 'low' THEN 3
                            ELSE 2
                        END
                    LIMIT 20
                """)
                
                result = conn.execute(query, {"org_id": ORG_ID})
                rows = result.fetchall()
                
                logger.info(f"\n✅ Found {len(rows)} pending decisions via API query")
                
                if rows:
                    logger.info("\nSample pending decisions:")
                    for i, row in enumerate(rows[:5], 1):
                        logger.info(f"  {i}. [{row.priority.upper()}] {row.agent_name}: {row.title}")
                
                # Count by agent
                agent_query = text("""
                    SELECT 
                        c.metadata->>'agent_name' as agent_name,
                        COUNT(*) as count
                    FROM checkpoints c,
                    jsonb_array_elements(c.checkpoint->'channel_values'->'messages') as msg
                    WHERE c.metadata->>'org_id' = :org_id
                    AND msg->>'requires_approval' = 'true'
                    AND msg->>'approval_status' = 'pending'
                    GROUP BY c.metadata->>'agent_name'
                    ORDER BY count DESC
                """)
                
                result = conn.execute(agent_query, {"org_id": ORG_ID})
                rows = result.fetchall()
                
                logger.info("\nPending decisions by agent:")
                for row in rows:
                    logger.info(f"  {row.agent_name}: {row.count}")
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ DEMO DECISIONS POPULATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            
    except Exception as e:
        logger.error(f"❌ Error during population: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    populate_decisions()
