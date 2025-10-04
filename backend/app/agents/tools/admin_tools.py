"""
Practice Admin Agent Tools - Operations & Scheduling Management

Tools for managing clinic operations, scheduling, and workflow optimization.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_core.tools import tool

from app.integrations.mock_odoo import mock_odoo_client

logger = logging.getLogger(__name__)


@tool
def get_schedule_conflicts_tool(date: Optional[str] = None, days: int = 7) -> str:
    """
    Find scheduling conflicts (double bookings, overlaps, etc.).
    
    Args:
        date: Start date (YYYY-MM-DD format). Defaults to today.
        days: Number of days to check. Defaults to 7.
        
    Returns:
        JSON string with conflicts found
    """
    try:
        logger.info(f"Getting schedule conflicts for {days} days from {date}")
        
        # Parse date
        if date:
            start_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            start_date = datetime.now()
        
        end_date = start_date + timedelta(days=days)
        
        # Get appointments in date range
        appointments = mock_odoo_client.get_appointments(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        
        # Find conflicts
        conflicts = []
        appointments_by_date = {}
        
        for apt in appointments:
            date_key = apt["date"]
            if date_key not in appointments_by_date:
                appointments_by_date[date_key] = []
            appointments_by_date[date_key].append(apt)
        
        # Check for overlaps
        for date_key, day_appointments in appointments_by_date.items():
            # Sort by time
            sorted_apts = sorted(day_appointments, key=lambda x: x["time"])
            
            for i in range(len(sorted_apts) - 1):
                apt1 = sorted_apts[i]
                apt2 = sorted_apts[i + 1]
                
                # Check if same doctor
                if apt1.get("doctor_id") == apt2.get("doctor_id"):
                    # Check time overlap (assuming 30min appointments)
                    time1 = datetime.strptime(apt1["time"], "%H:%M")
                    time2 = datetime.strptime(apt2["time"], "%H:%M")
                    
                    if (time2 - time1).seconds < 1800:  # Less than 30 minutes
                        conflicts.append({
                            "type": "double_booking",
                            "date": date_key,
                            "time1": apt1["time"],
                            "time2": apt2["time"],
                            "doctor": apt1.get("doctor_name", "Unknown"),
                            "patient1": apt1.get("patient_name"),
                            "patient2": apt2.get("patient_name"),
                            "severity": "high"
                        })
        
        result = {
            "conflicts_found": len(conflicts),
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            "conflicts": conflicts[:10]  # Limit to 10
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting schedule conflicts: {e}")
        return f"Error: {str(e)}"


@tool
def get_available_slots_tool(date: str, doctor_id: Optional[int] = None, duration: int = 30) -> str:
    """
    Find available appointment slots.
    
    Args:
        date: Date to check (YYYY-MM-DD format)
        doctor_id: Specific doctor ID (optional)
        duration: Appointment duration in minutes. Defaults to 30.
        
    Returns:
        JSON string with available slots
    """
    try:
        logger.info(f"Getting available slots for {date}")
        
        # Get appointments for the date
        appointments = mock_odoo_client.get_appointments(
            start_date=date,
            end_date=date
        )
        
        # Clinic hours: 8:00 - 18:00
        clinic_start = datetime.strptime("08:00", "%H:%M")
        clinic_end = datetime.strptime("18:00", "%H:%M")
        
        # Generate all possible slots
        all_slots = []
        current_time = clinic_start
        while current_time < clinic_end:
            all_slots.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=duration)
        
        # Remove booked slots
        booked_times = [apt["time"] for apt in appointments if apt["date"] == date]
        available_slots = [slot for slot in all_slots if slot not in booked_times]
        
        result = {
            "date": date,
            "total_slots": len(all_slots),
            "booked_slots": len(booked_times),
            "available_slots": len(available_slots),
            "slots": available_slots[:20]  # Limit to 20
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting available slots: {e}")
        return f"Error: {str(e)}"


@tool
def reschedule_appointment_tool(appointment_id: int, new_date: str, new_time: str, reason: str) -> str:
    """
    Reschedule an appointment.
    
    Args:
        appointment_id: Appointment ID to reschedule
        new_date: New date (YYYY-MM-DD format)
        new_time: New time (HH:MM format)
        reason: Reason for rescheduling
        
    Returns:
        JSON string with reschedule result
    """
    try:
        logger.info(f"Rescheduling appointment {appointment_id}")
        
        # In real system, this would update the database
        # For now, simulate success
        
        result = {
            "success": True,
            "appointment_id": appointment_id,
            "old_date": "2025-10-05",  # Simulated
            "old_time": "14:00",  # Simulated
            "new_date": new_date,
            "new_time": new_time,
            "reason": reason,
            "notification_sent": True,
            "message": f"Appointment {appointment_id} successfully rescheduled to {new_date} at {new_time}"
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error rescheduling appointment: {e}")
        return f"Error: {str(e)}"


@tool
def get_staff_schedule_tool(date: Optional[str] = None, staff_type: str = "all") -> str:
    """
    Get staff schedule and availability.
    
    Args:
        date: Date to check (YYYY-MM-DD format). Defaults to today.
        staff_type: Type of staff ("doctor", "hygienist", "assistant", "all")
        
    Returns:
        JSON string with staff schedule
    """
    try:
        logger.info(f"Getting staff schedule for {date}")
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Simulated staff schedule
        staff = [
            {
                "id": 1,
                "name": "Dr. Cohen",
                "type": "doctor",
                "schedule": {
                    "start": "08:00",
                    "end": "17:00",
                    "break": "12:00-13:00",
                    "available": True
                }
            },
            {
                "id": 2,
                "name": "Dr. Levi",
                "type": "doctor",
                "schedule": {
                    "start": "09:00",
                    "end": "18:00",
                    "break": "13:00-14:00",
                    "available": True
                }
            },
            {
                "id": 3,
                "name": "Sarah (Hygienist)",
                "type": "hygienist",
                "schedule": {
                    "start": "08:00",
                    "end": "16:00",
                    "break": "12:00-12:30",
                    "available": True
                }
            }
        ]
        
        # Filter by staff type
        if staff_type != "all":
            staff = [s for s in staff if s["type"] == staff_type]
        
        result = {
            "date": date,
            "staff_count": len(staff),
            "staff": staff
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting staff schedule: {e}")
        return f"Error: {str(e)}"


@tool
def get_room_availability_tool(date: str, time_slot: Optional[str] = None) -> str:
    """
    Check room availability.
    
    Args:
        date: Date to check (YYYY-MM-DD format)
        time_slot: Specific time slot (HH:MM format, optional)
        
    Returns:
        JSON string with room availability
    """
    try:
        logger.info(f"Getting room availability for {date}")
        
        # Simulated rooms
        rooms = [
            {"id": 1, "name": "Room 1", "type": "treatment", "available": True},
            {"id": 2, "name": "Room 2", "type": "treatment", "available": True},
            {"id": 3, "name": "Room 3", "type": "surgery", "available": False},
            {"id": 4, "name": "Room 4", "type": "treatment", "available": True},
        ]
        
        available_rooms = [r for r in rooms if r["available"]]
        
        result = {
            "date": date,
            "time_slot": time_slot or "all_day",
            "total_rooms": len(rooms),
            "available_rooms": len(available_rooms),
            "rooms": rooms
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting room availability: {e}")
        return f"Error: {str(e)}"


@tool
def optimize_schedule_tool(date: str, optimization_goal: str = "minimize_gaps") -> str:
    """
    Optimize daily schedule.
    
    Args:
        date: Date to optimize (YYYY-MM-DD format)
        optimization_goal: Goal ("minimize_gaps", "balance_load", "maximize_utilization")
        
    Returns:
        JSON string with optimization suggestions
    """
    try:
        logger.info(f"Optimizing schedule for {date}")
        
        # Get appointments
        appointments = mock_odoo_client.get_appointments(
            start_date=date,
            end_date=date
        )
        
        # Analyze schedule
        total_appointments = len([a for a in appointments if a["date"] == date])
        
        # Generate optimization suggestions
        suggestions = []
        
        if optimization_goal == "minimize_gaps":
            suggestions.append({
                "type": "consolidate",
                "description": "Move 10:30 appointment to 10:00 to reduce gap",
                "impact": "Save 30 minutes",
                "priority": "medium"
            })
            suggestions.append({
                "type": "consolidate",
                "description": "Move 15:00 appointment to 14:30",
                "impact": "Allow earlier closing",
                "priority": "low"
            })
        
        elif optimization_goal == "balance_load":
            suggestions.append({
                "type": "redistribute",
                "description": "Move 2 appointments from Dr. Cohen to Dr. Levi",
                "impact": "Balance workload",
                "priority": "high"
            })
        
        elif optimization_goal == "maximize_utilization":
            suggestions.append({
                "type": "fill_gaps",
                "description": "Add walk-in slots at 11:00 and 16:00",
                "impact": "Increase revenue by ₪800",
                "priority": "high"
            })
        
        result = {
            "date": date,
            "optimization_goal": optimization_goal,
            "current_appointments": total_appointments,
            "suggestions_count": len(suggestions),
            "suggestions": suggestions,
            "estimated_improvement": "15-20%"
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error optimizing schedule: {e}")
        return f"Error: {str(e)}"


@tool
def get_operational_metrics_tool(date_range: int = 7) -> str:
    """
    Get operational KPIs and metrics.
    
    Args:
        date_range: Number of days to analyze. Defaults to 7.
        
    Returns:
        JSON string with operational metrics
    """
    try:
        logger.info(f"Getting operational metrics for {date_range} days")
        
        # Get appointments
        end_date = datetime.now()
        start_date = end_date - timedelta(days=date_range)
        
        appointments = mock_odoo_client.get_appointments(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        
        # Calculate metrics
        total_appointments = len(appointments)
        completed = len([a for a in appointments if a.get("status") == "completed"])
        cancelled = len([a for a in appointments if a.get("status") == "cancelled"])
        no_shows = len([a for a in appointments if a.get("status") == "no_show"])
        
        result = {
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "days": date_range
            },
            "appointments": {
                "total": total_appointments,
                "completed": completed,
                "cancelled": cancelled,
                "no_shows": no_shows,
                "completion_rate": f"{(completed / total_appointments * 100):.1f}%" if total_appointments > 0 else "0%"
            },
            "utilization": {
                "clinic_capacity": total_appointments * 1.2,  # Simulated
                "utilization_rate": "83%",
                "peak_hours": ["10:00-12:00", "14:00-16:00"]
            },
            "efficiency": {
                "avg_appointment_duration": "35 minutes",
                "avg_wait_time": "8 minutes",
                "on_time_rate": "92%"
            },
            "recommendations": [
                "Consider adding slots during peak hours",
                "Reduce no-show rate with SMS reminders",
                "Optimize lunch break scheduling"
            ]
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting operational metrics: {e}")
        return f"Error: {str(e)}"



@tool
def cancel_appointment_tool(appointment_id: int, reason: str, notify_patient: bool = True) -> str:
    """
    Cancel an appointment.
    
    Args:
        appointment_id: Appointment ID to cancel
        reason: Reason for cancellation
        notify_patient: Whether to send notification to patient. Defaults to True.
        
    Returns:
        JSON string with cancellation result
    """
    try:
        logger.info(f"Cancelling appointment {appointment_id}")
        
        # In real system, this would:
        # 1. Update appointment status to "cancelled"
        # 2. Free up the time slot
        # 3. Send notification to patient
        # 4. Update doctor's schedule
        # 5. Log the cancellation
        
        # For now, simulate success
        result = {
            "success": True,
            "appointment_id": appointment_id,
            "status": "cancelled",
            "reason": reason,
            "cancelled_at": datetime.now().isoformat(),
            "notification_sent": notify_patient,
            "time_slot_freed": True,
            "message": f"Appointment {appointment_id} successfully cancelled. {('Patient notified.' if notify_patient else 'Patient not notified.')}"
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}")
        return f"Error: {str(e)}"
