#!/usr/bin/env python3
"""
Populate demo checkpoints and pending decisions in PostgreSQL.

This script creates realistic LangGraph checkpoints with pending decisions
to demonstrate the Enhanced Decision Queue widget functionality.

SAFE: Only inserts data into PostgreSQL checkpoints table, no Odoo dependency.
"""

import asyncio
import sys
import uuid
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import random

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import SessionLocal
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

DECISION_TYPES = {
    "Alex": ["appointment_reschedule", "patient_communication", "appointment_reminder"],
    "Sarah": ["treatment_plan_review", "clinical_assessment", "procedure_recommendation"],
    "Marcus": ["payment_plan_creation", "insurance_verification", "billing_adjustment"],
    "Sophia": ["schedule_optimization", "resource_allocation", "appointment_conflict"],
    "Harper": ["compliance_check", "documentation_review", "hipaa_verification"]
}

CATEGORIES = {
    "Alex": "scheduling",
    "Sarah": "clinical",
    "Marcus": "financial",
    "Sophia": "optimization",
    "Harper": "compliance"
}

PRIORITIES = ["critical", "high", "medium", "low"]

# Israeli patient names for realism
PATIENT_NAMES = [
    "David Cohen", "Sarah Levy", "Michael Mizrahi", "Rachel Goldstein",
    "Yossi Peretz", "Tamar Katz", "Avi Shapira", "Noa Ben-David",
    "Eitan Friedman", "Maya Rosenberg", "Daniel Aharoni", "Shira Weiss",
    "Amit Biton", "Lior Azoulay", "Chen Dahan", "Yael Golan",
    "Ron Malka", "Tal Oren", "Nir Barak", "Michal Segal"
]

REASONING_TEMPLATES = {
    "appointment_reschedule": [
        "Patient requested to move appointment due to work conflict. Suggested alternative time slot available.",
        "Dentist running late, offering to reschedule to avoid long wait time for patient.",
        "Patient called in sick, proposing next available slot within the same week."
    ],
    "treatment_plan_review": [
        "Complex case requiring multi-phase treatment. Recommending consultation with specialist.",
        "Patient's insurance coverage changed, adjusting treatment plan to maximize benefits.",
        "New clinical findings suggest alternative treatment approach may be more effective."
    ],
    "payment_plan_creation": [
        "Patient requested installment plan for expensive procedure. Proposed 6-month payment schedule.",
        "Insurance denied partial coverage, offering flexible payment options to patient.",
        "Large treatment plan requires upfront payment discussion and financing options."
    ],
    "schedule_optimization": [
        "Detected scheduling gap that can accommodate emergency appointment.",
        "Multiple cancellations created opportunity to consolidate appointments and reduce wait times.",
        "Identified pattern of no-shows for specific time slots, suggesting schedule adjustment."
    ],
    "compliance_check": [
        "Patient consent form missing signature, requires follow-up before next appointment.",
        "HIPAA audit detected missing documentation in patient file.",
        "Sterilization log incomplete for today's procedures, needs immediate attention."
    ]
}


def generate_checkpoint_data(
    agent_name: str,
    decision_type: str,
    priority: str,
    patient_name: str,
    is_pending: bool = False
) -> Dict[str, Any]:
    """Generate realistic checkpoint data."""
    
    thread_id = f"thread_{uuid.uuid4().hex[:16]}"
    checkpoint_id = f"checkpoint_{uuid.uuid4().hex[:16]}"
    
    # Generate realistic timestamps
    if is_pending:
        # Pending decisions are recent (last 24 hours)
        created_at = datetime.utcnow() - timedelta(hours=random.randint(1, 24))
    else:
        # Completed conversations are older (last 7 days)
        created_at = datetime.utcnow() - timedelta(days=random.randint(1, 7))
    
    # Generate confidence score (higher for non-pending)
    confidence = random.uniform(0.85, 0.98) if not is_pending else random.uniform(0.75, 0.92)
    
    # Select reasoning
    reasoning = random.choice(REASONING_TEMPLATES.get(decision_type, ["Standard procedure"]))
    
    # Generate metadata
    metadata = {
        "org_id": ORG_ID,
        "agent_name": agent_name,
        "decision_type": decision_type,
        "category": CATEGORIES[agent_name],
        "priority": priority,
        "patient_name": patient_name,
        "patient_id": str(random.randint(1000, 9999)),
        "confidence": round(confidence, 2),
        "reasoning": reasoning,
        "impact": f"Affects {patient_name}'s care timeline and satisfaction",
        "compliance_risk": random.choice(["low", "medium"]) if agent_name == "Harper" else "low",
        "created_at": created_at.isoformat(),
        "status": "pending" if is_pending else "completed",
        "requires_approval": is_pending
    }
    
    # Generate checkpoint data
    checkpoint = {
        "ts": created_at.isoformat(),
        "channel_values": {
            "messages": [
                {
                    "role": "user",
                    "content": f"Request regarding {patient_name}"
                },
                {
                    "role": "assistant",
                    "content": reasoning
                }
            ]
        },
        "next": ["__end__"] if not is_pending else ["human_approval"]
    }
    
    return {
        "thread_id": thread_id,
        "checkpoint_id": checkpoint_id,
        "metadata": json.dumps(metadata),
        "checkpoint": json.dumps(checkpoint),
        "parent_checkpoint_id": None
    }


async def populate_checkpoints():
    """Populate checkpoints table with demo data."""
    
    logger.info("=" * 60)
    logger.info("STARTING DEMO CHECKPOINTS POPULATION")
    logger.info("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Step 1: Check current checkpoint count
        logger.info("\nStep 1: Checking existing checkpoints...")
        result = await db.execute(
            text("SELECT COUNT(*) as count FROM checkpoints WHERE metadata->>'org_id' = :org_id"),
            {"org_id": ORG_ID}
        )
        existing_count = result.scalar()
        logger.info(f"Found {existing_count} existing checkpoints for org {ORG_ID}")
        
        # Step 2: Generate pending decisions (15 total)
        logger.info("\nStep 2: Generating 15 pending decisions...")
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
                decision_type = random.choice(DECISION_TYPES[agent])
                patient_name = PATIENT_NAMES[patient_idx % len(PATIENT_NAMES)]
                patient_idx += 1
                
                checkpoint_data = generate_checkpoint_data(
                    agent_name=agent,
                    decision_type=decision_type,
                    priority=priority,
                    patient_name=patient_name,
                    is_pending=True
                )
                pending_decisions.append(checkpoint_data)
        
        logger.info(f"Generated {len(pending_decisions)} pending decisions")
        
        # Step 3: Generate completed conversations (85 total)
        logger.info("\nStep 3: Generating 85 completed conversations...")
        completed_conversations = []
        
        for i in range(85):
            agent = random.choice(AGENTS)
            decision_type = random.choice(DECISION_TYPES[agent])
            priority = random.choice(PRIORITIES)
            patient_name = PATIENT_NAMES[patient_idx % len(PATIENT_NAMES)]
            patient_idx += 1
            
            checkpoint_data = generate_checkpoint_data(
                agent_name=agent,
                decision_type=decision_type,
                priority=priority,
                patient_name=patient_name,
                is_pending=False
            )
            completed_conversations.append(checkpoint_data)
        
        logger.info(f"Generated {len(completed_conversations)} completed conversations")
        
        # Step 4: Insert all checkpoints
        logger.info("\nStep 4: Inserting checkpoints into database...")
        all_checkpoints = pending_decisions + completed_conversations
        
        insert_query = text("""
            INSERT INTO checkpoints (thread_id, checkpoint_id, metadata, checkpoint, parent_checkpoint_id)
            VALUES (:thread_id, :checkpoint_id, :metadata::jsonb, :checkpoint::jsonb, :parent_checkpoint_id)
            ON CONFLICT (thread_id, checkpoint_id) DO NOTHING
        """)
        
        inserted_count = 0
        for checkpoint in all_checkpoints:
            result = await db.execute(insert_query, checkpoint)
            if result.rowcount > 0:
                inserted_count += 1
        
        await db.commit()
        
        logger.info(f"✅ Successfully inserted {inserted_count} checkpoints")
        
        # Step 5: Verify insertion
        logger.info("\nStep 5: Verifying insertion...")
        result = await db.execute(
            text("SELECT COUNT(*) as count FROM checkpoints WHERE metadata->>'org_id' = :org_id"),
            {"org_id": ORG_ID}
        )
        total_count = result.scalar()
        logger.info(f"Total checkpoints now: {total_count}")
        
        # Verify pending decisions
        result = await db.execute(
            text("""
                SELECT COUNT(*) as count FROM checkpoints 
                WHERE metadata->>'org_id' = :org_id 
                AND metadata->>'status' = 'pending'
            """),
            {"org_id": ORG_ID}
        )
        pending_count = result.scalar()
        logger.info(f"Pending decisions: {pending_count}")
        
        # Show breakdown by agent
        logger.info("\nBreakdown by agent:")
        result = await db.execute(
            text("""
                SELECT 
                    metadata->>'agent_name' as agent,
                    COUNT(*) as total,
                    SUM(CASE WHEN metadata->>'status' = 'pending' THEN 1 ELSE 0 END) as pending
                FROM checkpoints 
                WHERE metadata->>'org_id' = :org_id
                GROUP BY metadata->>'agent_name'
                ORDER BY total DESC
            """),
            {"org_id": ORG_ID}
        )
        for row in result:
            logger.info(f"  {row.agent}: {row.total} total ({row.pending} pending)")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ DEMO CHECKPOINTS POPULATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error during population: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(populate_checkpoints())
