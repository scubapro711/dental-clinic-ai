#!/usr/bin/env python3
"""
Populate demo checkpoints and pending decisions using PostgresSaver API.

This script creates realistic LangGraph checkpoints with pending decisions
to demonstrate the Enhanced Decision Queue widget functionality.

SAFE: Uses PostgresSaver API properly, no direct SQL manipulation.
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
    "Ron Malka", "Tal Oren", "Nir Barak", "Michal Segal",
    "Dov Koren", "Rina Shamir", "Gadi Stein", "Liora Navon",
    "Oren Hazan", "Shani Roth", "Boaz Levi", "Talia Mor"
]

REASONING_TEMPLATES = {
    "appointment_reschedule": [
        "Patient requested to move appointment due to work conflict. Suggested alternative time slot available.",
        "Dentist running late, offering to reschedule to avoid long wait time for patient.",
        "Patient called in sick, proposing next available slot within the same week.",
        "Emergency case requires immediate attention, need to reschedule routine checkup.",
        "Patient's child is sick, requesting to move appointment to next week."
    ],
    "treatment_plan_review": [
        "Complex case requiring multi-phase treatment. Recommending consultation with specialist.",
        "Patient's insurance coverage changed, adjusting treatment plan to maximize benefits.",
        "New clinical findings suggest alternative treatment approach may be more effective.",
        "Patient expressed concerns about treatment duration, proposing modified timeline.",
        "X-ray results indicate additional work needed, updating treatment plan accordingly."
    ],
    "payment_plan_creation": [
        "Patient requested installment plan for expensive procedure. Proposed 6-month payment schedule.",
        "Insurance denied partial coverage, offering flexible payment options to patient.",
        "Large treatment plan requires upfront payment discussion and financing options.",
        "Patient experiencing financial hardship, suggesting extended payment terms.",
        "Multiple procedures scheduled, creating bundled payment plan with discount."
    ],
    "schedule_optimization": [
        "Detected scheduling gap that can accommodate emergency appointment.",
        "Multiple cancellations created opportunity to consolidate appointments and reduce wait times.",
        "Identified pattern of no-shows for specific time slots, suggesting schedule adjustment.",
        "Equipment maintenance scheduled, need to redistribute appointments across other days.",
        "Staff vacation upcoming, optimizing schedule to maintain service levels."
    ],
    "compliance_check": [
        "Patient consent form missing signature, requires follow-up before next appointment.",
        "HIPAA audit detected missing documentation in patient file.",
        "Sterilization log incomplete for today's procedures, needs immediate attention.",
        "Controlled substance inventory discrepancy requires investigation and documentation.",
        "Patient privacy breach reported, initiating compliance review and remediation."
    ],
    "patient_communication": [
        "Patient hasn't responded to appointment reminder, need to confirm attendance.",
        "Lab results ready for review, scheduling follow-up consultation.",
        "Patient requested information about new treatment options.",
        "Post-procedure follow-up call to check on patient recovery.",
        "Patient feedback survey response indicates service improvement opportunity."
    ],
    "clinical_assessment": [
        "Routine checkup revealed potential cavity, recommending further examination.",
        "Patient reports tooth sensitivity, scheduling diagnostic appointment.",
        "Gum inflammation observed, suggesting periodontal evaluation.",
        "Wisdom tooth extraction assessment needed based on X-ray findings.",
        "Orthodontic consultation recommended for bite alignment issues."
    ],
    "insurance_verification": [
        "Patient's insurance coverage requires pre-authorization for planned procedure.",
        "Insurance claim rejected, need to resubmit with additional documentation.",
        "Patient's insurance plan changed, verifying new coverage details.",
        "Out-of-network provider status affecting coverage, discussing options with patient.",
        "Insurance deductible not met, informing patient of out-of-pocket costs."
    ],
    "appointment_reminder": [
        "Sending 48-hour reminder for upcoming appointment.",
        "Patient has history of no-shows, sending extra confirmation request.",
        "Appointment tomorrow morning, confirming patient will attend.",
        "Follow-up appointment scheduled for next week, sending reminder.",
        "Annual checkup due, inviting patient to schedule appointment."
    ],
    "procedure_recommendation": [
        "Preventive care recommended based on patient's oral health history.",
        "Cosmetic procedure suggested to address patient's aesthetic concerns.",
        "Restorative work needed to prevent further tooth decay.",
        "Root canal recommended to save infected tooth.",
        "Crown placement advised for cracked tooth protection."
    ],
    "billing_adjustment": [
        "Insurance payment lower than expected, adjusting patient balance.",
        "Billing error detected, issuing credit to patient account.",
        "Patient overpayment requires refund processing.",
        "Service code correction needed for proper insurance billing.",
        "Payment plan modification requested due to changed financial circumstances."
    ],
    "resource_allocation": [
        "High demand for hygienist appointments, considering additional staff hours.",
        "Dental chair maintenance scheduled, redistributing patients to other operatories.",
        "Specialist visit scheduled, blocking time for complex procedures.",
        "Training session planned, adjusting schedule to accommodate staff development.",
        "Equipment upgrade delivery expected, planning installation downtime."
    ],
    "appointment_conflict": [
        "Double-booked appointment detected, need to reschedule one patient.",
        "Provider requested time off overlaps with scheduled appointments.",
        "Emergency case conflicts with routine appointment, prioritizing urgent care.",
        "Patient arrived for wrong appointment time, accommodating if possible.",
        "Overbooking in specific time slot, extending hours to serve all patients."
    ],
    "documentation_review": [
        "Treatment notes incomplete, requesting dentist to finalize documentation.",
        "Medical history update needed before next procedure.",
        "Informed consent documentation missing for recent treatment.",
        "Chart audit revealed missing diagnostic codes, updating records.",
        "Patient file requires digital scanning for electronic health record system."
    ],
    "hipaa_verification": [
        "Staff training on HIPAA compliance due for annual renewal.",
        "Patient requested access to medical records, processing request per HIPAA guidelines.",
        "Third-party vendor requires Business Associate Agreement review.",
        "Privacy policy update needed to reflect new data handling procedures.",
        "Security incident reported, conducting HIPAA breach assessment."
    ]
}


def generate_checkpoint_data(
    agent_name: str,
    decision_type: str,
    priority: str,
    patient_name: str,
    is_pending: bool = False
) -> Dict[str, Any]:
    """Generate realistic checkpoint data for PostgresSaver."""
    
    thread_id = f"demo_thread_{uuid.uuid4().hex[:16]}"
    checkpoint_id = str(uuid.uuid4())
    
    # Generate realistic timestamps
    if is_pending:
        # Pending decisions are recent (last 48 hours)
        hours_ago = random.randint(1, 48)
        created_at = datetime.utcnow() - timedelta(hours=hours_ago)
    else:
        # Completed conversations are older (last 14 days)
        days_ago = random.randint(1, 14)
        created_at = datetime.utcnow() - timedelta(days=days_ago)
    
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
        "requires_approval": is_pending,
        "estimated_resolution_time": f"{random.randint(5, 60)} minutes" if is_pending else None
    }
    
    # Generate checkpoint data (LangGraph state format)
    checkpoint = {
        "v": 1,
        "ts": created_at.isoformat(),
        "id": checkpoint_id,
        "channel_values": {
            "messages": [
                {
                    "type": "human",
                    "content": f"Request regarding {patient_name}: {decision_type.replace('_', ' ').title()}"
                },
                {
                    "type": "ai",
                    "content": reasoning
                }
            ],
            "agent": agent_name,
            "decision_pending": is_pending
        },
        "channel_versions": {
            "__start__": 1,
            "messages": 2,
            "agent": 1
        },
        "versions_seen": {
            "__input__": {},
            "__start__": {"__start__": 1},
            "agent": {"__start__": 1, "messages": 1}
        },
        "pending_sends": []
    }
    
    return {
        "thread_id": thread_id,
        "checkpoint_id": checkpoint_id,
        "checkpoint": checkpoint,
        "metadata": metadata,
        "parent_checkpoint_id": None
    }


def populate_checkpoints():
    """Populate checkpoints using PostgresSaver API."""
    
    logger.info("=" * 60)
    logger.info("STARTING DEMO CHECKPOINTS POPULATION")
    logger.info("=" * 60)
    
    try:
        # Initialize PostgresSaver
        logger.info("\nStep 1: Connecting to PostgreSQL checkpointer...")
        with PostgresSaver.from_conn_string(settings.CHECKPOINT_DATABASE_URL) as checkpointer:
            logger.info("✅ Connected successfully")
            
            # Step 2: Check existing checkpoints
            logger.info("\nStep 2: Checking existing checkpoints...")
            existing = list(checkpointer.list({}))
            logger.info(f"Found {len(existing)} existing checkpoints")
            
            # Step 3: Generate pending decisions (20 total)
            logger.info("\nStep 3: Generating 20 pending decisions...")
            pending_decisions = []
            
            # Distribution: 3 critical, 6 high, 8 medium, 3 low
            priority_distribution = [
                ("critical", 3),
                ("high", 6),
                ("medium", 8),
                ("low", 3)
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
            
            # Step 4: Generate completed conversations (80 total)
            logger.info("\nStep 4: Generating 80 completed conversations...")
            completed_conversations = []
            
            for i in range(80):
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
            
            # Step 5: Insert all checkpoints using PostgresSaver API
            logger.info("\nStep 5: Inserting checkpoints using PostgresSaver API...")
            all_checkpoints = pending_decisions + completed_conversations
            
            inserted_count = 0
            for cp_data in all_checkpoints:
                try:
                    # Use PostgresSaver.put() to insert checkpoint
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
            
            # Step 6: Verify insertion
            logger.info("\nStep 6: Verifying insertion...")
            all_checkpoints_after = list(checkpointer.list({}))
            logger.info(f"Total checkpoints now: {len(all_checkpoints_after)}")
            
            # Count by status
            pending_count = sum(1 for cp in all_checkpoints_after if cp.metadata.get("status") == "pending")
            completed_count = sum(1 for cp in all_checkpoints_after if cp.metadata.get("status") == "completed")
            logger.info(f"  Pending: {pending_count}")
            logger.info(f"  Completed: {completed_count}")
            
            # Show breakdown by agent
            logger.info("\nBreakdown by agent:")
            agent_counts = {}
            agent_pending = {}
            for cp in all_checkpoints_after:
                agent = cp.metadata.get("agent_name", "Unknown")
                status = cp.metadata.get("status", "unknown")
                
                agent_counts[agent] = agent_counts.get(agent, 0) + 1
                if status == "pending":
                    agent_pending[agent] = agent_pending.get(agent, 0) + 1
            
            for agent in sorted(agent_counts.keys()):
                total = agent_counts[agent]
                pending = agent_pending.get(agent, 0)
                logger.info(f"  {agent}: {total} total ({pending} pending)")
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ DEMO CHECKPOINTS POPULATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            
    except Exception as e:
        logger.error(f"❌ Error during population: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    populate_checkpoints()
