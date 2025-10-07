"""
Human Handoff API Endpoints
Handles items that require human decision/intervention
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

router = APIRouter()

# Mock data for human handoff items
def generate_handoff_items(odoo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate realistic handoff items from Odoo data"""
    
    handoff_items = []
    
    # Get some appointments from Odoo
    appointments = odoo_data.get('appointments', [])[:50]
    
    # Type 1: Emergency appointment requests (5% of appointments)
    emergency_count = max(1, len(appointments) // 20)
    for i in range(emergency_count):
        apt = random.choice(appointments)
        handoff_items.append({
            "id": f"handoff_{len(handoff_items)+1}",
            "type": "emergency_appointment",
            "priority": "urgent",
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(5, 60))).isoformat(),
            "patient_name": apt.get('patient_name', 'Unknown'),
            "patient_phone": apt.get('patient_phone', ''),
            "title": "Emergency Appointment Request",
            "description": f"Patient reports severe toothache. Requested emergency appointment today.",
            "alex_message": f"Patient {apt.get('patient_name')} contacted via {random.choice(['WhatsApp', 'Phone', 'Telegram'])} with severe pain. I have a 30-min slot available at {random.choice(['2:30 PM', '3:00 PM', '4:15 PM'])}. Should I schedule?",
            "context": {
                "last_visit": "3 months ago (cleaning)",
                "allergies": random.choice(["None", "Penicillin", "Latex"]),
                "payment_history": random.choice(["Good", "Excellent", "Fair"]),
                "suggested_time": random.choice(['2:30 PM', '3:00 PM', '4:15 PM'])
            },
            "actions": [
                {"id": "approve", "label": "Approve Suggested Time", "type": "success"},
                {"id": "call", "label": "Call Patient First", "type": "info"},
                {"id": "decline", "label": "Decline", "type": "danger"},
                {"id": "alternative", "label": "Suggest Alternative", "type": "warning"}
            ]
        })
    
    # Type 2: Medical questions (3% of appointments)
    medical_count = max(1, len(appointments) // 33)
    for i in range(medical_count):
        apt = random.choice(appointments)
        questions = [
            ("Am I a candidate for dental implants? I have diabetes.", "Type 2 Diabetes (controlled)"),
            ("Can I get teeth whitening while pregnant?", "Pregnant (2nd trimester)"),
            ("Is it safe to extract tooth while on blood thinners?", "On Warfarin"),
            ("Can I do root canal with my heart condition?", "Heart disease"),
        ]
        question, condition = random.choice(questions)
        
        handoff_items.append({
            "id": f"handoff_{len(handoff_items)+1}",
            "type": "medical_question",
            "priority": "normal",
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(10, 120))).isoformat(),
            "patient_name": apt.get('patient_name', 'Unknown'),
            "patient_phone": apt.get('patient_phone', ''),
            "title": "Medical Question Requires Doctor",
            "description": question,
            "alex_message": f"Patient {apt.get('patient_name')} asked: '{question}' I cannot provide medical advice. Please respond.",
            "context": {
                "age": random.randint(35, 70),
                "medical_condition": condition,
                "last_visit": f"{random.randint(1, 6)} months ago",
                "question": question
            },
            "actions": [
                {"id": "respond", "label": "Respond via Alex", "type": "success"},
                {"id": "call", "label": "Call Patient", "type": "info"},
                {"id": "schedule_consult", "label": "Schedule Consultation", "type": "warning"}
            ]
        })
    
    # Type 3: Schedule conflicts (2% of appointments)
    conflict_count = max(1, len(appointments) // 50)
    for i in range(conflict_count):
        apt1 = random.choice(appointments)
        apt2 = random.choice(appointments)
        
        handoff_items.append({
            "id": f"handoff_{len(handoff_items)+1}",
            "type": "schedule_conflict",
            "priority": "normal",
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(15, 90))).isoformat(),
            "patient_name": f"{apt1.get('patient_name', 'Patient A')} vs {apt2.get('patient_name', 'Patient B')}",
            "patient_phone": "",
            "title": "Schedule Conflict",
            "description": f"Two patients want the same time slot (3:00 PM today)",
            "alex_message": f"{apt1.get('patient_name')} wants to reschedule to 3:00 PM, but {apt2.get('patient_name')} (new patient) also requested the same time. Who gets priority?",
            "context": {
                "option_a": f"{apt1.get('patient_name')} (existing patient, regular visits)",
                "option_b": f"{apt2.get('patient_name')} (new patient, first visit)",
                "time_slot": "3:00 PM today"
            },
            "actions": [
                {"id": "choose_a", "label": f"Choose {apt1.get('patient_name', 'Patient A')}", "type": "success"},
                {"id": "choose_b", "label": f"Choose {apt2.get('patient_name', 'Patient B')}", "type": "success"},
                {"id": "alternative", "label": "Find Alternative for Both", "type": "warning"}
            ]
        })
    
    # Sort by priority and timestamp
    handoff_items.sort(key=lambda x: (
        0 if x['priority'] == 'urgent' else 1,
        x['timestamp']
    ), reverse=True)
    
    return handoff_items[:10]  # Return top 10 items


@router.get("/pending")
async def get_pending_handoffs():
    """Get items requiring human decision"""
    try:
        # Import Mock Odoo client
        from app.integrations.mock_odoo_realistic import RealisticMockOdooClient
        
        odoo = RealisticMockOdooClient()
        
        # Get appointments using search_appointments
        appointment_ids = odoo.search_appointments()
        appointments = []
        for apt_id in appointment_ids[:100]:  # Limit to 100
            apt = odoo.get_appointment(apt_id)
            if apt:
                appointments.append(apt)
        
        # Get Odoo data
        odoo_data = {
            'appointments': appointments
        }
        
        # Generate handoff items
        items = generate_handoff_items(odoo_data)
        
        return {
            "total": len(items),
            "urgent": len([i for i in items if i['priority'] == 'urgent']),
            "items": items
        }
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Handoff API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to load handoff items: {str(e)}")


@router.get("/resolved")
async def get_resolved_handoffs():
    """Get recently resolved handoff items"""
    try:
        # Mock resolved items
        resolved = [
            {
                "id": "resolved_1",
                "type": "emergency_appointment",
                "patient_name": "Rachel Mizrahi",
                "title": "Emergency slot approved",
                "resolution": "Approved 2:30 PM slot",
                "resolved_at": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "resolved_by": "Dr. Cohen"
            },
            {
                "id": "resolved_2",
                "type": "medical_question",
                "patient_name": "David Levi",
                "title": "Medical question answered",
                "resolution": "Scheduled consultation for implant evaluation",
                "resolved_at": (datetime.now() - timedelta(hours=1)).isoformat(),
                "resolved_by": "Dr. Cohen"
            }
        ]
        
        return {
            "total": len(resolved),
            "items": resolved
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load resolved items: {str(e)}")


@router.get("/alex/activity")
async def get_alex_activity():
    """Get Alex's recent activity"""
    try:
        # Import Mock Odoo client
        from app.integrations.mock_odoo_realistic import RealisticMockOdooClient
        
        odoo = RealisticMockOdooClient()
        
        # Get some real data using search_appointments
        appointment_ids = odoo.search_appointments()
        appointments = []
        for apt_id in appointment_ids[:20]:  # Limit to 20
            apt = odoo.get_appointment(apt_id)
            if apt:
                appointments.append(apt)
        
        # Generate activity log
        activities = []
        
        # Scheduled appointments
        for i, apt in enumerate(appointments[:3]):
            activities.append({
                "id": f"activity_{len(activities)+1}",
                "type": "appointment_scheduled",
                "icon": "✅",
                "timestamp": (datetime.now() - timedelta(minutes=random.randint(10, 60))).isoformat(),
                "description": f"Scheduled {apt.get('treatment', 'appointment')} for {apt.get('patient_name', 'patient')}",
                "details": f"{apt.get('date', 'today')} at {apt.get('time', 'TBD')}"
            })
        
        # Answered questions
        activities.append({
            "id": f"activity_{len(activities)+1}",
            "type": "question_answered",
            "icon": "💬",
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(15, 90))).isoformat(),
            "description": "Answered 12 patient questions",
            "details": "Office hours, pricing, preparation instructions"
        })
        
        # Sent reminders
        activities.append({
            "id": f"activity_{len(activities)+1}",
            "type": "reminders_sent",
            "icon": "📨",
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(20, 120))).isoformat(),
            "description": "Sent 8 appointment reminders",
            "details": "For tomorrow's appointments"
        })
        
        # Escalated to doctor
        activities.append({
            "id": f"activity_{len(activities)+1}",
            "type": "escalated",
            "icon": "⚠️",
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(5, 45))).isoformat(),
            "description": "Escalated 2 items to doctor",
            "details": "1 emergency, 1 medical question"
        })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            "total": len(activities),
            "activities": activities
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load Alex activity: {str(e)}")


@router.get("/alex/performance")
async def get_alex_performance():
    """Get Alex's performance metrics"""
    try:
        # Import Mock Odoo client
        from app.integrations.mock_odoo_realistic import RealisticMockOdooClient
        
        odoo = RealisticMockOdooClient()
        
        # Get statistics
        stats = odoo.get_statistics()
        
        # Calculate Alex performance
        total_conversations = 150
        handled_automatically = 141
        escalated_to_human = 9
        success_rate = (handled_automatically / total_conversations) * 100
        
        return {
            "status": "active",
            "active_conversations": 5,
            "today": {
                "total_conversations": total_conversations,
                "handled_automatically": handled_automatically,
                "escalated_to_human": escalated_to_human,
                "success_rate": round(success_rate, 1),
                "appointments_scheduled": 8,
                "questions_answered": 47,
                "reminders_sent": 23
            },
            "this_week": {
                "total_conversations": 892,
                "handled_automatically": 839,
                "escalated_to_human": 53,
                "success_rate": 94.1,
                "appointments_scheduled": 56,
                "questions_answered": 324,
                "reminders_sent": 167
            },
            "trends": [
                {
                    "observation": "More emergency requests this week (+15%)",
                    "suggestion": "Consider adding 2 emergency slots per day"
                },
                {
                    "observation": "Common question: 'Do you accept my insurance?'",
                    "suggestion": "Add insurance info to website FAQ"
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load Alex performance: {str(e)}")
