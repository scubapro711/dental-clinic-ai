#!/usr/bin/env python3
"""
Populate demo data with direct SQL insertion in LangGraph format.

This script inserts checkpoints directly into the database in the exact format
that LangGraph PostgresSaver uses, bypassing all API layers.

SAFE: Direct SQL with correct schema, no external dependencies.
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

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Demo data constants
ORG_ID = "751d7aa8-07d4-4cff-b5b4-1ea199889cbd"

PATIENT_NAMES = [
    "David Cohen", "Sarah Levy", "Michael Mizrahi", "Rachel Goldstein",
    "Yossi Peretz", "Tamar Katz", "Avi Shapira", "Noa Ben-David",
    "Eitan Friedman", "Maya Rosenberg", "Daniel Aharoni", "Shira Weiss",
    "Amit Biton", "Lior Azoulay", "Chen Dahan", "Yael Golan"
]

DECISION_TEMPLATES = {
    "Alex": [
        ("Appointment reschedule request", "Patient {patient} requested to move appointment", "Reschedule to suggested time"),
        ("Patient communication needed", "Patient {patient} hasn't responded to reminder", "Call patient to confirm"),
        ("Emergency appointment request", "Patient {patient} reports severe tooth pain", "Schedule emergency appointment")
    ],
    "Sarah": [
        ("Treatment plan review", "Complex case for {patient} needs multi-phase treatment", "Approve specialist consultation"),
        ("Clinical assessment needed", "X-ray results for {patient} show additional work", "Update treatment plan"),
        ("Procedure recommendation", "Preventive care recommended for {patient}", "Schedule follow-up procedure")
    ],
    "Marcus": [
        ("Payment plan creation", "Patient {patient} requested installment plan", "Approve 6-month payment schedule"),
        ("Insurance verification", "Patient {patient} insurance needs pre-authorization", "Submit authorization request"),
        ("Billing adjustment", "Insurance payment for {patient} lower than expected", "Adjust patient balance")
    ],
    "Sophia": [
        ("Schedule optimization", "Scheduling gap can accommodate {patient}", "Consolidate appointments"),
        ("Appointment conflict", "Double-booking detected for {patient}", "Reschedule one patient"),
        ("Resource allocation", "High demand requires staff for {patient} appointments", "Approve overtime hours")
    ],
    "Harper": [
        ("Compliance check", "Patient {patient} consent form missing signature", "Follow up before appointment"),
        ("HIPAA verification", "Patient {patient} file needs documentation", "Complete missing documentation"),
        ("Documentation review", "Treatment notes for {patient} incomplete", "Request dentist finalization")
    ]
}

CATEGORIES = {
    "Alex": "scheduling",
    "Sarah": "clinical",
    "Marcus": "financial",
    "Sophia": "optimization",
    "Harper": "compliance"
}


def create_checkpoint_sql(
    thread_id: str,
    checkpoint_id: str,
    agent_name: str,
    patient_name: str,
    title: str,
    description: str,
    action: str,
    priority: str,
    is_pending: bool,
    created_at: datetime
) -> Dict[str, Any]:
    """Create checkpoint data in LangGraph PostgresSaver format."""
    
    # Create checkpoint structure (this is what LangGraph creates)
    checkpoint = {
        "v": 1,
        "ts": created_at.isoformat(),
        "id": checkpoint_id,
        "channel_values": {
            "messages": [
                {
                    "type": "human",
                    "content": description.format(patient=patient_name)
                },
                {
                    "type": "ai",
                    "content": f"I recommend: {action}",
                    # These fields are what get_pending_decisions looks for
                    "title": title,
                    "description": description.format(patient=patient_name),
                    "action": action,
                    "priority": priority,
                    "category": CATEGORIES[agent_name],
                    "confidence": str(random.randint(75, 95)),
                    "reasoning": description.format(patient=patient_name),
                    "patient_id": str(random.randint(1000, 9999)),
                    "patient_name": patient_name,
                    "impact_level": "high" if priority in ["critical", "high"] else "medium",
                    "compliance_risk": "true" if agent_name == "Harper" else "false",
                    "requires_approval": "true" if is_pending else "false",
                    "approval_status": "pending" if is_pending else "approved"
                }
            ]
        },
        "channel_versions": {
            "__start__": 2,
            "messages": 2
        },
        "versions_seen": {
            "__input__": {},
            "__start__": {"__start__": 1}
        },
        "pending_sends": []
    }
    
    # Create metadata (this is what queries filter by)
    metadata = {
        "source": "update",
        "step": 1,
        "writes": {
            "messages": [
                {
                    "type": "ai",
                    "content": f"I recommend: {action}"
                }
            ]
        },
        # Custom fields for our app
        "org_id": ORG_ID,
        "agent_name": agent_name,
        "patient_name": patient_name,
        "category": CATEGORIES[agent_name],
        "priority": priority,
        "status": "pending" if is_pending else "completed"
    }
    
    return {
        "thread_id": thread_id,
        "checkpoint_ns": "",
        "checkpoint_id": checkpoint_id,
        "parent_checkpoint_id": None,
        "type": None,
        "checkpoint": json.dumps(checkpoint),
        "metadata": json.dumps(metadata)
    }


def populate_demo_data():
    """Populate demo data with direct SQL."""
    
    logger.info("=" * 60)
    logger.info("POPULATING DEMO DATA VIA DIRECT SQL")
    logger.info("=" * 60)
    
    engine = create_engine(settings.CHECKPOINT_DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Step 1: Clear existing demo data
            logger.info("\nStep 1: Clearing existing demo checkpoints...")
            result = conn.execute(
                text("DELETE FROM checkpoints WHERE thread_id LIKE 'demo_%'")
            )
            conn.commit()
            logger.info(f"Deleted {result.rowcount} existing checkpoints")
            
            # Step 2: Generate pending decisions (15 total)
            logger.info("\nStep 2: Generating 15 pending decisions...")
            
            checkpoints = []
            patient_idx = 0
            
            # Distribution: 2 critical, 5 high, 6 medium, 2 low
            priority_dist = [
                ("critical", 2),
                ("high", 5),
                ("medium", 6),
                ("low", 2)
            ]
            
            for priority, count in priority_dist:
                for _ in range(count):
                    agent = random.choice(list(DECISION_TEMPLATES.keys()))
                    template = random.choice(DECISION_TEMPLATES[agent])
                    patient = PATIENT_NAMES[patient_idx % len(PATIENT_NAMES)]
                    patient_idx += 1
                    
                    thread_id = f"demo_{agent.lower()}_{uuid.uuid4().hex[:12]}"
                    checkpoint_id = str(uuid.uuid4())
                    created_at = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
                    
                    cp = create_checkpoint_sql(
                        thread_id=thread_id,
                        checkpoint_id=checkpoint_id,
                        agent_name=agent,
                        patient_name=patient,
                        title=template[0],
                        description=template[1],
                        action=template[2],
                        priority=priority,
                        is_pending=True,
                        created_at=created_at
                    )
                    checkpoints.append(cp)
            
            logger.info(f"Generated {len(checkpoints)} pending decisions")
            
            # Step 3: Generate completed decisions (35 total)
            logger.info("\nStep 3: Generating 35 completed decisions...")
            
            for _ in range(35):
                agent = random.choice(list(DECISION_TEMPLATES.keys()))
                template = random.choice(DECISION_TEMPLATES[agent])
                patient = PATIENT_NAMES[patient_idx % len(PATIENT_NAMES)]
                patient_idx += 1
                priority = random.choice(["critical", "high", "medium", "low"])
                
                thread_id = f"demo_{agent.lower()}_{uuid.uuid4().hex[:12]}"
                checkpoint_id = str(uuid.uuid4())
                created_at = datetime.utcnow() - timedelta(days=random.randint(1, 14))
                
                cp = create_checkpoint_sql(
                    thread_id=thread_id,
                    checkpoint_id=checkpoint_id,
                    agent_name=agent,
                    patient_name=patient,
                    title=template[0],
                    description=template[1],
                    action=template[2],
                    priority=priority,
                    is_pending=False,
                    created_at=created_at
                )
                checkpoints.append(cp)
            
            logger.info(f"Total checkpoints to insert: {len(checkpoints)}")
            
            # Step 4: Insert all checkpoints
            logger.info("\nStep 4: Inserting checkpoints...")
            
            insert_sql = text("""
                INSERT INTO checkpoints (
                    thread_id,
                    checkpoint_ns,
                    checkpoint_id,
                    parent_checkpoint_id,
                    type,
                    checkpoint,
                    metadata
                ) VALUES (
                    :thread_id,
                    :checkpoint_ns,
                    :checkpoint_id,
                    :parent_checkpoint_id,
                    :type,
                    :checkpoint,
                    :metadata
                )
            """)
            
            for i, cp in enumerate(checkpoints, 1):
                conn.execute(insert_sql, cp)
                if i % 10 == 0:
                    logger.info(f"  Inserted {i}/{len(checkpoints)} checkpoints...")
            
            conn.commit()
            logger.info(f"✅ Inserted {len(checkpoints)} checkpoints")
            
            # Step 5: Verify with the actual API query
            logger.info("\nStep 5: Verifying with get_pending_decisions query...")
            
            verify_sql = text("""
                SELECT 
                    c.thread_id,
                    c.metadata->>'agent_name' as agent_name,
                    msg->>'title' as title,
                    msg->>'priority' as priority
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
            
            result = conn.execute(verify_sql, {"org_id": ORG_ID})
            rows = result.fetchall()
            
            logger.info(f"\n✅ Found {len(rows)} pending decisions via API query")
            
            if rows:
                logger.info("\nSample pending decisions:")
                for i, row in enumerate(rows[:5], 1):
                    logger.info(f"  {i}. [{row.priority.upper()}] {row.agent_name}: {row.title}")
            
            # Count by agent
            agent_sql = text("""
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
            
            result = conn.execute(agent_sql, {"org_id": ORG_ID})
            rows = result.fetchall()
            
            logger.info("\nPending decisions by agent:")
            for row in rows:
                logger.info(f"  {row.agent_name}: {row.count}")
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ DEMO DATA POPULATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    populate_demo_data()
