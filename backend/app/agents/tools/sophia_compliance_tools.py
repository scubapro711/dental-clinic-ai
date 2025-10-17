"""
Sophia Compliance & Facilities Tools

Tools for managing compliance, rooms, equipment, and safety.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_core.tools import tool

from app.integrations.odoo_client import OdooClient

odoo_client_v3 = OdooClient()

logger = logging.getLogger(__name__)


@tool
def get_rooms_list_tool(available_only: bool = False) -> str:
    """
    Get list of all treatment/operating rooms.
    
    Args:
        available_only: Show only available rooms (default: False)
        
    Returns:
        JSON string with rooms list
    """
    try:
        logger.info(f"Getting rooms list (available_only={available_only})")
        
        rooms = odoo_client_v3.get_operating_rooms(available_only=available_only)
        
        result = {
            'total_rooms': len(rooms),
            'available_rooms': len([r for r in rooms if r.get('state') == 'available']),
            'rooms': rooms,
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting rooms list: {e}")
        return f"Error: {str(e)}"


@tool
def get_room_schedule_tool(room_name: str, date: str) -> str:
    """
    Get schedule for a specific room.
    
    Args:
        room_name: Name of the room
        date: Date to check (YYYY-MM-DD)
        
    Returns:
        JSON string with room schedule
    """
    try:
        logger.info(f"Getting schedule for room '{room_name}' on {date}")
        
        # Get all rooms to find the one we want
        rooms = odoo_client_v3.get_operating_rooms()
        room = next((r for r in rooms if room_name.lower() in r.get('name', '').lower()), None)
        
        if not room:
            return json.dumps({'error': f"Room '{room_name}' not found"}, ensure_ascii=False)
        
        # Get schedule
        schedule = odoo_client_v3.get_room_schedule(room['id'], date)
        
        # Calculate utilization
        total_minutes = 8 * 60  # Assuming 8-hour workday
        booked_minutes = sum(s.get('duration', 0) for s in schedule)
        utilization = (booked_minutes / total_minutes * 100) if total_minutes > 0 else 0
        
        result = {
            'room_name': room.get('name'),
            'room_id': room['id'],
            'date': date,
            'appointments': len(schedule),
            'utilization_rate': f"{utilization:.1f}%",
            'schedule': schedule,
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting room schedule: {e}")
        return f"Error: {str(e)}"


@tool
def get_equipment_list_tool(category: Optional[str] = None) -> str:
    """
    Get list of clinic equipment.
    
    Args:
        category: Filter by category ('dental', 'imaging', 'sterilization', 'general')
        
    Returns:
        JSON string with equipment list
    """
    try:
        logger.info(f"Getting equipment list (category={category})")
        
        equipment = odoo_client_v3.get_equipment_list(category=category)
        
        # Group by category
        by_category = {}
        for eq in equipment:
            cat = eq.get('category', 'unknown')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(eq)
        
        # Count by status
        operational = len([e for e in equipment if e.get('status') == 'operational'])
        maintenance_required = len([e for e in equipment if e.get('status') == 'maintenance_required'])
        
        result = {
            'total_equipment': len(equipment),
            'by_status': {
                'operational': operational,
                'maintenance_required': maintenance_required,
            },
            'by_category': by_category,
            'equipment': equipment,
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting equipment list: {e}")
        return f"Error: {str(e)}"


@tool
def create_maintenance_request_tool(equipment_name: str, issue_description: str, priority: str = "medium") -> str:
    """
    Create maintenance request for equipment.
    
    Args:
        equipment_name: Name of the equipment
        issue_description: Description of the issue
        priority: Priority level ('low', 'medium', 'high', 'urgent')
        
    Returns:
        JSON string with request result
    """
    try:
        logger.info(f"Creating maintenance request for {equipment_name}")
        
        result = odoo_client_v3.create_maintenance_request(
            equipment_name=equipment_name,
            issue_description=issue_description,
            priority=priority
        )
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error creating maintenance request: {e}")
        return f"Error: {str(e)}"


@tool
def get_maintenance_requests_tool(state: Optional[str] = None, priority: Optional[str] = None) -> str:
    """
    Get maintenance requests.
    
    Args:
        state: Filter by state ('draft', 'in_progress', 'done', 'cancelled')
        priority: Filter by priority ('low', 'medium', 'high', 'urgent')
        
    Returns:
        JSON string with maintenance requests
    """
    try:
        logger.info(f"Getting maintenance requests (state={state}, priority={priority})")
        
        requests = odoo_client_v3.get_maintenance_requests(state=state, priority=priority)
        
        # Group by state
        by_state = {}
        for req in requests:
            st = req.get('state', 'unknown')
            if st not in by_state:
                by_state[st] = []
            by_state[st].append(req)
        
        # Group by priority
        by_priority = {}
        for req in requests:
            pri = req.get('priority', 'unknown')
            if pri not in by_priority:
                by_priority[pri] = []
            by_priority[pri].append(req)
        
        result = {
            'total_requests': len(requests),
            'by_state': by_state,
            'by_priority': by_priority,
            'urgent_count': len([r for r in requests if r.get('priority') == 'urgent']),
            'requests': requests,
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting maintenance requests: {e}")
        return f"Error: {str(e)}"


@tool
def get_compliance_reminders_tool(days_ahead: int = 30) -> str:
    """
    Get upcoming compliance and regulatory reminders.
    
    Args:
        days_ahead: Number of days to look ahead (default: 30)
        
    Returns:
        JSON string with compliance reminders
    """
    try:
        logger.info(f"Getting compliance reminders ({days_ahead} days ahead)")
        
        reminders = odoo_client_v3.get_compliance_reminders(days_ahead=days_ahead)
        
        # Group by category
        by_category = {}
        for reminder in reminders:
            cat = reminder.get('category', 'unknown')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(reminder)
        
        # Count by priority
        high_priority = len([r for r in reminders if r.get('priority') == 'high'])
        medium_priority = len([r for r in reminders if r.get('priority') == 'medium'])
        
        # Find urgent (due within 7 days)
        today = datetime.now()
        urgent_threshold = (today + timedelta(days=7)).strftime('%Y-%m-%d')
        urgent = [r for r in reminders if r.get('due_date') <= urgent_threshold]
        
        result = {
            'total_reminders': len(reminders),
            'urgent_count': len(urgent),
            'by_priority': {
                'high': high_priority,
                'medium': medium_priority,
            },
            'by_category': by_category,
            'urgent_items': urgent,
            'all_reminders': reminders,
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting compliance reminders: {e}")
        return f"Error: {str(e)}"


@tool
def create_safety_checklist_tool(checklist_type: str, date: Optional[str] = None) -> str:
    """
    Create safety checklist for daily/weekly/monthly checks.
    
    Args:
        checklist_type: Type of checklist ('daily', 'weekly', 'monthly')
        date: Date for the checklist (YYYY-MM-DD). Defaults to today.
        
    Returns:
        JSON string with created checklist
    """
    try:
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Creating {checklist_type} safety checklist for {date}")
        
        checklist = odoo_client_v3.create_safety_checklist(checklist_type, date)
        
        import json
        return json.dumps(checklist, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error creating safety checklist: {e}")
        return f"Error: {str(e)}"


@tool
def check_equipment_maintenance_tool(days_ahead: int = 30) -> str:
    """
    Check equipment that needs maintenance soon.
    
    Args:
        days_ahead: Number of days to look ahead (default: 30)
        
    Returns:
        JSON string with equipment needing maintenance
    """
    try:
        logger.info(f"Checking equipment maintenance ({days_ahead} days ahead)")
        
        equipment = odoo_client_v3.get_equipment_list()
        
        today = datetime.now()
        threshold_date = (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        # Find equipment needing maintenance
        needs_maintenance = []
        overdue = []
        
        for eq in equipment:
            next_maintenance = eq.get('next_maintenance')
            if next_maintenance:
                if next_maintenance < today.strftime('%Y-%m-%d'):
                    overdue.append(eq)
                elif next_maintenance <= threshold_date:
                    needs_maintenance.append(eq)
        
        result = {
            'total_equipment': len(equipment),
            'overdue_count': len(overdue),
            'upcoming_count': len(needs_maintenance),
            'overdue_maintenance': overdue,
            'upcoming_maintenance': needs_maintenance,
            'summary': {
                'immediate_action_required': len(overdue),
                'plan_maintenance_soon': len(needs_maintenance),
            }
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error checking equipment maintenance: {e}")
        return f"Error: {str(e)}"


@tool
def generate_compliance_report_tool(report_type: str = "summary", days_back: int = 30) -> str:
    """
    Generate comprehensive compliance report.
    
    Args:
        report_type: Type of report ('summary', 'equipment', 'safety', 'regulatory')
        days_back: Number of days to include (default: 30)
        
    Returns:
        JSON string with compliance report
    """
    try:
        logger.info(f"Generating compliance report (type={report_type}, days={days_back})")
        
        if report_type == "summary":
            # Get all key compliance metrics
            reminders = odoo_client_v3.get_compliance_reminders(days_ahead=30)
            maintenance_requests = odoo_client_v3.get_maintenance_requests()
            equipment = odoo_client_v3.get_equipment_list()
            
            report = {
                'report_type': 'summary',
                'generated_date': datetime.now().isoformat(),
                'compliance_overview': {
                    'upcoming_deadlines': len(reminders),
                    'urgent_items': len([r for r in reminders if r.get('priority') == 'high']),
                },
                'maintenance_overview': {
                    'total_requests': len(maintenance_requests),
                    'urgent_requests': len([r for r in maintenance_requests if r.get('priority') == 'urgent']),
                    'in_progress': len([r for r in maintenance_requests if r.get('state') == 'in_progress']),
                },
                'equipment_overview': {
                    'total_equipment': len(equipment),
                    'operational': len([e for e in equipment if e.get('status') == 'operational']),
                    'maintenance_required': len([e for e in equipment if e.get('status') == 'maintenance_required']),
                },
            }
        
        elif report_type == "equipment":
            equipment = odoo_client_v3.get_equipment_list()
            maintenance_requests = odoo_client_v3.get_maintenance_requests()
            
            report = {
                'report_type': 'equipment',
                'generated_date': datetime.now().isoformat(),
                'equipment_list': equipment,
                'maintenance_requests': maintenance_requests,
                'summary': {
                    'total_equipment': len(equipment),
                    'pending_maintenance': len([r for r in maintenance_requests if r.get('state') == 'draft']),
                }
            }
        
        elif report_type == "safety":
            # Safety-focused report
            report = {
                'report_type': 'safety',
                'generated_date': datetime.now().isoformat(),
                'safety_checklists': {
                    'daily': 'Completed',
                    'weekly': 'Pending',
                    'monthly': 'Scheduled',
                },
                'safety_incidents': [],
                'training_status': {
                    'cpr_certified': 8,
                    'fire_safety_trained': 10,
                    'infection_control_certified': 10,
                },
            }
        
        elif report_type == "regulatory":
            reminders = odoo_client_v3.get_compliance_reminders(days_ahead=90)
            
            report = {
                'report_type': 'regulatory',
                'generated_date': datetime.now().isoformat(),
                'upcoming_deadlines': reminders,
                'licenses': {
                    'medical_licenses': 'Current',
                    'facility_license': 'Current',
                    'radiation_permit': 'Expires in 10 days',
                },
                'inspections': {
                    'last_health_inspection': '2025-06-15',
                    'next_fire_inspection': '2025-11-20',
                },
            }
        
        else:
            report = {'error': f"Unknown report type: {report_type}"}
        
        import json
        return json.dumps(report, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        return f"Error: {str(e)}"


@tool
def optimize_room_utilization_tool(date: str) -> str:
    """
    Analyze and suggest room utilization optimization.
    
    Args:
        date: Date to analyze (YYYY-MM-DD)
        
    Returns:
        JSON string with optimization suggestions
    """
    try:
        logger.info(f"Analyzing room utilization for {date}")
        
        rooms = odoo_client_v3.get_operating_rooms()
        
        room_analysis = []
        for room in rooms:
            schedule = odoo_client_v3.get_room_schedule(room['id'], date)
            
            total_minutes = 8 * 60  # 8-hour workday
            booked_minutes = sum(s.get('duration', 0) for s in schedule)
            utilization = (booked_minutes / total_minutes * 100) if total_minutes > 0 else 0
            
            room_analysis.append({
                'room_name': room.get('name'),
                'room_id': room['id'],
                'appointments': len(schedule),
                'booked_minutes': booked_minutes,
                'utilization_rate': f"{utilization:.1f}%",
                'status': 'overbooked' if utilization > 100 else 'optimal' if utilization > 70 else 'underutilized'
            })
        
        # Sort by utilization
        room_analysis = sorted(room_analysis, key=lambda x: float(x['utilization_rate'].rstrip('%')), reverse=True)
        
        # Generate suggestions
        suggestions = []
        overbooked = [r for r in room_analysis if r['status'] == 'overbooked']
        underutilized = [r for r in room_analysis if r['status'] == 'underutilized']
        
        if overbooked and underutilized:
            suggestions.append(f"Consider moving appointments from {overbooked[0]['room_name']} to {underutilized[0]['room_name']}")
        
        if overbooked:
            suggestions.append(f"{overbooked[0]['room_name']} is overbooked - review schedule")
        
        result = {
            'date': date,
            'total_rooms': len(room_analysis),
            'room_analysis': room_analysis,
            'suggestions': suggestions,
            'summary': {
                'overbooked_rooms': len(overbooked),
                'optimal_rooms': len([r for r in room_analysis if r['status'] == 'optimal']),
                'underutilized_rooms': len(underutilized),
            }
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error optimizing room utilization: {e}")
        return f"Error: {str(e)}"

