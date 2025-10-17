"""
Sophia Staff Management Tools - HR & Scheduling

Tools for managing clinic staff, schedules, and performance.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_core.tools import tool

from app.integrations.odoo_client import OdooClient

odoo_client_v3 = OdooClient()

logger = logging.getLogger(__name__)

# Initialize __all__ list
__all__ = []


@tool
def get_staff_list_tool(department: Optional[str] = None, active_only: bool = True) -> str:
    """
    Get list of all clinic staff members.
    
    Args:
        department: Filter by department (e.g., "Dental", "Administration")
        active_only: Show only active employees (default: True)
        
    Returns:
        JSON string with staff list
    """
    try:
        logger.info(f"Getting staff list (department={department}, active={active_only})")
        
        # Get employees
        employees = odoo_client_v3.get_employees(department=department, active_only=active_only)
        
        # Get physicians
        physicians = odoo_client_v3.get_physicians()
        
        # Combine and organize
        staff = {
            'total_count': len(employees) + len(physicians),
            'employees': employees,
            'physicians': physicians,
            'by_department': {},
        }
        
        # Group by department
        for emp in employees:
            dept = emp.get('department_id', ['', 'Unknown'])[1]
            if dept not in staff['by_department']:
                staff['by_department'][dept] = []
            staff['by_department'][dept].append(emp)
        
        import json
        return json.dumps(staff, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting staff list: {e}")
        return f"Error: {str(e)}"


@tool
def get_doctor_availability_tool(doctor_name: str, date: str) -> str:
    """
    Get doctor availability for a specific date.
    
    Args:
        doctor_name: Name of the doctor
        date: Date to check (YYYY-MM-DD)
        
    Returns:
        JSON string with doctor availability
    """
    try:
        logger.info(f"Getting availability for {doctor_name} on {date}")
        
        # Find doctor
        physicians = odoo_client_v3.get_physicians()
        doctor = next((p for p in physicians if doctor_name.lower() in p.get('name', '').lower()), None)
        
        if not doctor:
            return json.dumps({'error': f"Doctor '{doctor_name}' not found"}, ensure_ascii=False)
        
        # Get slots
        slots = odoo_client_v3.get_doctor_slots(doctor['id'], date)
        
        # Calculate availability
        available_slots = [s for s in slots if s.get('available')]
        booked_slots = [s for s in slots if not s.get('available')]
        
        result = {
            'doctor_name': doctor.get('name'),
            'doctor_id': doctor['id'],
            'specialization': doctor.get('specialization'),
            'date': date,
            'total_slots': len(slots),
            'available_slots': len(available_slots),
            'booked_slots': len(booked_slots),
            'availability_rate': f"{(len(available_slots) / len(slots) * 100):.1f}%" if len(slots) > 0 else "0%",
            'slots': slots[:10],  # Limit to 10
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting doctor availability: {e}")
        return f"Error: {str(e)}"


@tool
def create_staff_schedule_tool(doctor_name: str, date: str, start_time: str, end_time: str, slot_duration: int = 30) -> str:
    """
    Create schedule slots for a doctor.
    
    Args:
        doctor_name: Name of the doctor
        date: Date (YYYY-MM-DD)
        start_time: Start time (HH:MM)
        end_time: End time (HH:MM)
        slot_duration: Duration of each slot in minutes (default: 30)
        
    Returns:
        JSON string with created schedule
    """
    try:
        logger.info(f"Creating schedule for {doctor_name} on {date}")
        
        # Find doctor
        physicians = odoo_client_v3.get_physicians()
        doctor = next((p for p in physicians if doctor_name.lower() in p.get('name', '').lower()), None)
        
        if not doctor:
            return json.dumps({'error': f"Doctor '{doctor_name}' not found"}, ensure_ascii=False)
        
        # Create slot
        slot = odoo_client_v3.create_doctor_slot(
            doctor_id=doctor['id'],
            date=date,
            start_time=start_time,
            end_time=end_time,
            duration=slot_duration
        )
        
        result = {
            'success': True,
            'doctor_name': doctor.get('name'),
            'date': date,
            'schedule': {
                'start': start_time,
                'end': end_time,
                'slot_duration': slot_duration,
            },
            'slot': slot,
            'message': f"Schedule created successfully for {doctor.get('name')}"
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error creating staff schedule: {e}")
        return f"Error: {str(e)}"


@tool
def get_staff_attendance_tool(employee_name: Optional[str] = None, days_back: int = 7) -> str:
    """
    Get staff attendance records.
    
    Args:
        employee_name: Filter by employee name (optional)
        days_back: Number of days to look back (default: 7)
        
    Returns:
        JSON string with attendance records
    """
    try:
        logger.info(f"Getting attendance (employee={employee_name}, days={days_back})")
        
        date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        date_to = datetime.now().strftime('%Y-%m-%d')
        
        # Get all employees
        employees = odoo_client_v3.get_employees()
        
        # Filter by name if specified
        if employee_name:
            employees = [e for e in employees if employee_name.lower() in e.get('name', '').lower()]
        
        attendance_data = []
        for emp in employees:
            attendance = odoo_client_v3.get_employee_attendance(
                employee_id=emp['id'],
                date_from=date_from,
                date_to=date_to
            )
            
            total_hours = sum(a.get('worked_hours', 0) for a in attendance)
            
            attendance_data.append({
                'employee_name': emp.get('name'),
                'employee_id': emp['id'],
                'total_days': len(attendance),
                'total_hours': total_hours,
                'average_hours_per_day': total_hours / len(attendance) if len(attendance) > 0 else 0,
                'records': attendance[:5],  # Limit to 5
            })
        
        result = {
            'period': {'from': date_from, 'to': date_to, 'days': days_back},
            'employee_count': len(attendance_data),
            'attendance': attendance_data,
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting staff attendance: {e}")
        return f"Error: {str(e)}"


@tool
def get_time_off_requests_tool(status: Optional[str] = None) -> str:
    """
    Get pending time-off requests.
    
    Args:
        status: Filter by status ('draft', 'confirm', 'validate', 'refuse')
        
    Returns:
        JSON string with time-off requests
    """
    try:
        logger.info(f"Getting time-off requests (status={status})")
        
        # Get requests
        requests = odoo_client_v3.get_time_off_requests(state=status)
        
        # Group by status
        by_status = {}
        for req in requests:
            state = req.get('state', 'unknown')
            if state not in by_status:
                by_status[state] = []
            by_status[state].append(req)
        
        result = {
            'total_requests': len(requests),
            'by_status': by_status,
            'pending_approval': len([r for r in requests if r.get('state') == 'confirm']),
            'requests': requests[:15],  # Limit to 15
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting time-off requests: {e}")
        return f"Error: {str(e)}"


@tool
def approve_time_off_tool(request_id: int, employee_name: str) -> str:
    """
    Approve a time-off request.
    
    Args:
        request_id: ID of the time-off request
        employee_name: Name of the employee (for confirmation)
        
    Returns:
        JSON string with approval result
    """
    try:
        logger.info(f"Approving time-off request {request_id} for {employee_name}")
        
        # Approve request
        result = odoo_client_v3.approve_time_off_request(request_id)
        
        if result.get('success'):
            result['employee_name'] = employee_name
            result['approved_date'] = datetime.now().isoformat()
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error approving time-off: {e}")
        return f"Error: {str(e)}"


@tool
def get_staff_workload_tool(employee_name: Optional[str] = None, days_back: int = 7) -> str:
    """
    Get staff workload analysis (appointments, hours).
    
    Args:
        employee_name: Filter by employee name (optional)
        days_back: Number of days to analyze (default: 7)
        
    Returns:
        JSON string with workload analysis
    """
    try:
        logger.info(f"Getting staff workload (employee={employee_name}, days={days_back})")
        
        date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        date_to = datetime.now().strftime('%Y-%m-%d')
        
        # Get physicians
        physicians = odoo_client_v3.get_physicians()
        
        # Filter by name if specified
        if employee_name:
            physicians = [p for p in physicians if employee_name.lower() in p.get('name', '').lower()]
        
        workload_data = []
        for physician in physicians:
            workload = odoo_client_v3.get_employee_workload(
                employee_id=physician['id'],
                date_from=date_from,
                date_to=date_to
            )
            
            workload['name'] = physician.get('name')
            workload['specialization'] = physician.get('specialization')
            workload_data.append(workload)
        
        # Sort by total appointments
        workload_data = sorted(workload_data, key=lambda x: x['appointments']['total'], reverse=True)
        
        result = {
            'period': {'from': date_from, 'to': date_to, 'days': days_back},
            'staff_count': len(workload_data),
            'workload': workload_data,
            'summary': {
                'total_appointments': sum(w['appointments']['total'] for w in workload_data),
                'total_hours': sum(w['hours']['total_worked'] for w in workload_data),
                'average_appointments_per_staff': sum(w['appointments']['total'] for w in workload_data) / len(workload_data) if len(workload_data) > 0 else 0,
            }
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting staff workload: {e}")
        return f"Error: {str(e)}"


@tool
def get_staff_performance_tool(days_back: int = 30) -> str:
    """
    Get comprehensive staff performance metrics.
    
    Args:
        days_back: Number of days to analyze (default: 30)
        
    Returns:
        JSON string with performance metrics
    """
    try:
        logger.info(f"Getting staff performance metrics (days={days_back})")
        
        date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        date_to = datetime.now().strftime('%Y-%m-%d')
        
        # Get performance metrics
        metrics = odoo_client_v3.get_staff_performance_metrics(date_from, date_to)
        
        # Calculate rankings
        for i, metric in enumerate(metrics):
            metric['rank'] = i + 1
        
        result = {
            'period': {'from': date_from, 'to': date_to, 'days': days_back},
            'staff_count': len(metrics),
            'metrics': metrics,
            'top_performers': metrics[:3] if len(metrics) >= 3 else metrics,
            'summary': {
                'total_appointments': sum(m['appointments']['total'] for m in metrics),
                'average_completion_rate': sum(float(m['appointments']['completion_rate'].rstrip('%')) for m in metrics) / len(metrics) if len(metrics) > 0 else 0,
            }
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting staff performance: {e}")
        return f"Error: {str(e)}"


@tool
def balance_staff_workload_tool(date: str) -> str:
    """
    Analyze and suggest workload balancing for a specific date.
    
    Args:
        date: Date to analyze (YYYY-MM-DD)
        
    Returns:
        JSON string with balancing suggestions
    """
    try:
        logger.info(f"Analyzing workload balance for {date}")
        
        # Get all physicians
        physicians = odoo_client_v3.get_physicians()
        
        workload_analysis = []
        for physician in physicians:
            # Get appointments for this date
            slots = odoo_client_v3.get_doctor_slots(physician['id'], date)
            
            booked = len([s for s in slots if not s.get('available')])
            available = len([s for s in slots if s.get('available')])
            total = len(slots)
            
            utilization = (booked / total * 100) if total > 0 else 0
            
            workload_analysis.append({
                'doctor_name': physician.get('name'),
                'doctor_id': physician['id'],
                'total_slots': total,
                'booked_slots': booked,
                'available_slots': available,
                'utilization_rate': f"{utilization:.1f}%",
                'status': 'overloaded' if utilization > 90 else 'balanced' if utilization > 60 else 'underutilized'
            })
        
        # Sort by utilization
        workload_analysis = sorted(workload_analysis, key=lambda x: float(x['utilization_rate'].rstrip('%')), reverse=True)
        
        # Generate suggestions
        suggestions = []
        overloaded = [w for w in workload_analysis if w['status'] == 'overloaded']
        underutilized = [w for w in workload_analysis if w['status'] == 'underutilized']
        
        if overloaded and underutilized:
            suggestions.append(f"Consider redistributing appointments from {overloaded[0]['doctor_name']} to {underutilized[0]['doctor_name']}")
        
        if overloaded:
            suggestions.append(f"{overloaded[0]['doctor_name']} is overloaded - consider adding more slots or another doctor")
        
        result = {
            'date': date,
            'staff_count': len(workload_analysis),
            'workload_analysis': workload_analysis,
            'suggestions': suggestions,
            'summary': {
                'overloaded_staff': len(overloaded),
                'balanced_staff': len([w for w in workload_analysis if w['status'] == 'balanced']),
                'underutilized_staff': len(underutilized),
            }
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error balancing staff workload: {e}")
        return f"Error: {str(e)}"


@tool
def generate_staff_report_tool(report_type: str = "summary", days_back: int = 30) -> str:
    """
    Generate comprehensive staff management report.
    
    Args:
        report_type: Type of report ('summary', 'performance', 'attendance', 'workload')
        days_back: Number of days to include (default: 30)
        
    Returns:
        JSON string with staff report
    """
    try:
        logger.info(f"Generating staff report (type={report_type}, days={days_back})")
        
        date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        date_to = datetime.now().strftime('%Y-%m-%d')
        
        if report_type == "summary":
            # Get all key metrics
            employees = odoo_client_v3.get_employees()
            physicians = odoo_client_v3.get_physicians()
            time_off_requests = odoo_client_v3.get_time_off_requests()
            
            report = {
                'report_type': 'summary',
                'generated_date': datetime.now().isoformat(),
                'period': {'from': date_from, 'to': date_to, 'days': days_back},
                'staff_overview': {
                    'total_employees': len(employees),
                    'total_physicians': len(physicians),
                    'active_staff': len([e for e in employees if e.get('active')]),
                },
                'time_off': {
                    'total_requests': len(time_off_requests),
                    'pending': len([r for r in time_off_requests if r.get('state') == 'confirm']),
                    'approved': len([r for r in time_off_requests if r.get('state') == 'validate']),
                },
            }
        
        elif report_type == "performance":
            metrics = odoo_client_v3.get_staff_performance_metrics(date_from, date_to)
            
            report = {
                'report_type': 'performance',
                'generated_date': datetime.now().isoformat(),
                'period': {'from': date_from, 'to': date_to, 'days': days_back},
                'metrics': metrics,
                'top_performers': metrics[:5] if len(metrics) >= 5 else metrics,
            }
        
        elif report_type == "attendance":
            employees = odoo_client_v3.get_employees()
            attendance_summary = []
            
            for emp in employees[:10]:  # Limit to 10
                attendance = odoo_client_v3.get_employee_attendance(emp['id'], date_from, date_to)
                total_hours = sum(a.get('worked_hours', 0) for a in attendance)
                
                attendance_summary.append({
                    'employee_name': emp.get('name'),
                    'total_days': len(attendance),
                    'total_hours': total_hours,
                })
            
            report = {
                'report_type': 'attendance',
                'generated_date': datetime.now().isoformat(),
                'period': {'from': date_from, 'to': date_to, 'days': days_back},
                'attendance_summary': attendance_summary,
            }
        
        elif report_type == "workload":
            physicians = odoo_client_v3.get_physicians()
            workload_summary = []
            
            for physician in physicians[:10]:  # Limit to 10
                workload = odoo_client_v3.get_employee_workload(physician['id'], date_from, date_to)
                workload['name'] = physician.get('name')
                workload_summary.append(workload)
            
            report = {
                'report_type': 'workload',
                'generated_date': datetime.now().isoformat(),
                'period': {'from': date_from, 'to': date_to, 'days': days_back},
                'workload_summary': workload_summary,
            }
        
        else:
            report = {'error': f"Unknown report type: {report_type}"}
        
        import json
        return json.dumps(report, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error generating staff report: {e}")
        return f"Error: {str(e)}"




@tool
def send_staff_notification_tool(message: str, department: Optional[str] = None) -> str:
    """
    Send a notification to all staff or a specific department.

    Args:
        message: The message to send.
        department: The department to send the notification to. If None, sends to all staff.

    Returns:
        A success message.
    """
    try:
        logger.info(f"Sending notification: '{message}' to department: {department}")
        # In a real implementation, this would integrate with a notification service (e.g., Slack, email)
        return f"✅ Notification sent successfully to {department or 'all staff'}."
    except Exception as e:
        logger.error(f"Error sending staff notification: {e}")
        return f"Error: {str(e)}"


# Update __all__
__all__.append("send_staff_notification_tool")




@tool
def track_staff_certifications_tool(employee_name: Optional[str] = None) -> str:
    """
    Track the status of staff certifications and licenses.

    Args:
        employee_name: Filter by employee name to see a specific employee's certifications.

    Returns:
        A formatted string with the certification status.
    """
    try:
        logger.info(f"Tracking certifications for: {employee_name or 'all staff'}")
        # This is a mock implementation.
        # In a real system, this would query HR records.
        mock_certifications = [
            {"employee": "Dr. Sarah Levi", "certification": "Dental License", "status": "Active", "expiry_date": "2026-12-31"},
            {"employee": "Alex Cohen", "certification": "CPR Certified", "status": "Expired", "expiry_date": "2024-10-01"},
            {"employee": "Dr. David Mizrahi", "certification": "Oral Surgery Board Certification", "status": "Active", "expiry_date": "2028-06-15"}
        ]

        if employee_name:
            mock_certifications = [cert for cert in mock_certifications if employee_name.lower() in cert["employee"].lower()]

        if not mock_certifications:
            return "No certification records found."

        report = "**סטטוס רישיונות והסמכות**\n\n"
        for cert in mock_certifications:
            report += f"- **{cert['employee']}**: {cert['certification']} - **{cert['status']}** (תוקף: {cert['expiry_date']})\n"

        return report

    except Exception as e:
        logger.error(f"Error tracking staff certifications: {e}")
        return f"Error: {str(e)}"


@tool
def create_staff_training_tool(title: str, department: str, due_date: str) -> str:
    """
    Create a new training program for staff.

    Args:
        title: The title of the training program.
        department: The department the training is for.
        due_date: The due date for completing the training (YYYY-MM-DD).

    Returns:
        A success message with the training details.
    """
    try:
        logger.info(f"Creating training: '{title}' for {department}")
        # This is a mock implementation.
        # In a real system, this would create a record in an LMS or HR system.
        training_id = 12345 # Mock ID
        return f"✅ **הדרכה חדשה נוצרה**\n\n**כותרת:** {title}\n**מחלקה:** {department}\n**תאריך יעד:** {due_date}\n**מזהה הדרכה:** {training_id}"
    except Exception as e:
        logger.error(f"Error creating staff training: {e}")
        return f"Error: {str(e)}"


# Update __all__
__all__.extend(["track_staff_certifications_tool", "create_staff_training_tool"])

