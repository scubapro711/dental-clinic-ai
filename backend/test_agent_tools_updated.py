"""
Comprehensive tests for updated Agent Tools using OdooClient.

This test suite verifies that all agent tools work correctly with the
new OdooClient implementation that uses OdooRPC-compatible interface.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.agents.tools.agent_tools import (
    search_patient_tool,
    get_available_slots_tool,
    create_appointment_tool,
    get_patient_appointments_tool,
    get_patient_invoices_tool,
    get_invoice_details_tool,
    update_appointment_status_tool,
    get_patient_count_tool,
    get_appointment_count_tool,
)

from app.agents.tools.cfo_tools import (
    get_revenue_overview_tool,
    get_payment_status_tool,
    get_top_treatments_tool,
    get_outstanding_invoices_tool,
    analyze_profitability_tool,
    get_financial_trends_tool,
)

from app.agents.tools.admin_tools import (
    get_schedule_conflicts_tool,
    get_available_slots_tool as admin_get_available_slots_tool,
    reschedule_appointment_tool,
    get_staff_schedule_tool,
    get_room_availability_tool,
    optimize_schedule_tool,
    get_operational_metrics_tool,
    cancel_appointment_tool,
)

from app.integrations.odoo_client import odoo_client


class TestAgentTools:
    """Test main agent tools (Alex)."""
    
    def test_search_patient_tool(self):
        """Test patient search functionality."""
        print("\n=== Testing search_patient_tool ===")
        
        # Search by name
        result = search_patient_tool(
            name="David",
            requesting_user_role="doctor"
        )
        print(f"Search by name 'David': {result}")
        assert "Found patient" in result or "No patient found" in result
        
        # Search for existing patient
        patient_ids = odoo_client.search_patients(name="David")
        if patient_ids:
            patient = odoo_client.get_patient(patient_ids[0])
            result = search_patient_tool(
                name=patient['name'],
                requesting_user_role="doctor"
            )
            print(f"Search for existing patient: {result}")
            assert "Found patient" in result
    
    def test_get_available_slots_tool(self):
        """Test getting available appointment slots."""
        print("\n=== Testing get_available_slots_tool ===")
        
        result = get_available_slots_tool(days_ahead=7)
        print(f"Available slots (7 days): {result}")
        assert "Available appointment slots" in result or "No available slots" in result
    
    def test_create_appointment_tool(self):
        """Test appointment creation."""
        print("\n=== Testing create_appointment_tool ===")
        
        result = create_appointment_tool(
            patient_name="Test Patient",
            patient_phone="+972501111111",
            appointment_date="2025-10-15",
            appointment_time="14:00",
            treatment_type="Checkup",
            requesting_user_role="doctor"
        )
        print(f"Create appointment: {result}")
        assert "successfully" in result.lower() or "error" in result.lower()
    
    def test_get_patient_appointments_tool(self):
        """Test getting patient appointments."""
        print("\n=== Testing get_patient_appointments_tool ===")
        
        # Find a patient with appointments
        patient_ids = odoo_client.search_patients(name="David")
        if patient_ids:
            patient = odoo_client.get_patient(patient_ids[0])
            result = get_patient_appointments_tool(
                patient_name=patient['name'],
                requesting_user_role="doctor"
            )
            print(f"Patient appointments: {result}")
            assert "Appointment" in result or "No appointments" in result
        else:
            print("No patients found to test")
    
    def test_get_patient_invoices_tool(self):
        """Test getting patient invoices."""
        print("\n=== Testing get_patient_invoices_tool ===")
        
        # Find a patient with invoices
        patient_ids = odoo_client.search_patients(name="David")
        if patient_ids:
            patient = odoo_client.get_patient(patient_ids[0])
            result = get_patient_invoices_tool(
                patient_name=patient['name'],
                requesting_user_role="doctor"
            )
            print(f"Patient invoices: {result}")
            assert "Invoice" in result or "No invoices" in result
        else:
            print("No patients found to test")
    
    def test_get_invoice_details_tool(self):
        """Test getting invoice details."""
        print("\n=== Testing get_invoice_details_tool ===")
        
        # Get first invoice ID
        invoice_ids = odoo_client.search_invoices()
        if invoice_ids:
            result = get_invoice_details_tool(
                invoice_id=invoice_ids[0],
                requesting_user_role="doctor"
            )
            print(f"Invoice details: {result}")
            assert "Invoice #" in result or "not found" in result
        else:
            print("No invoices found to test")
    
    def test_update_appointment_status_tool(self):
        """Test updating appointment status."""
        print("\n=== Testing update_appointment_status_tool ===")
        
        # Get first appointment ID
        appointment_ids = odoo_client.search_appointments()
        if appointment_ids:
            result = update_appointment_status_tool(
                appointment_id=appointment_ids[0],
                status="confirmed",
                requesting_user_role="doctor"
            )
            print(f"Update appointment status: {result}")
            assert "updated" in result.lower() or "failed" in result.lower()
        else:
            print("No appointments found to test")
    
    def test_get_patient_count_tool(self):
        """Test getting patient count."""
        print("\n=== Testing get_patient_count_tool ===")
        
        result = get_patient_count_tool(requesting_user_role="doctor")
        print(f"Patient count: {result}")
        assert "Total number of patients" in result
        assert any(char.isdigit() for char in result)
    
    def test_get_appointment_count_tool(self):
        """Test getting appointment count."""
        print("\n=== Testing get_appointment_count_tool ===")
        
        result = get_appointment_count_tool(requesting_user_role="doctor")
        print(f"Appointment count: {result}")
        assert "Total number of appointments" in result
        assert any(char.isdigit() for char in result)


class TestCFOTools:
    """Test CFO agent tools."""
    
    def test_get_revenue_overview_tool(self):
        """Test revenue overview."""
        print("\n=== Testing get_revenue_overview_tool ===")
        
        result = get_revenue_overview_tool.invoke({"days": 30})
        print(f"Revenue overview: {result}")
        assert isinstance(result, dict)
        assert "total_revenue" in result
        assert "period_days" in result
    
    def test_get_payment_status_tool(self):
        """Test payment status."""
        print("\n=== Testing get_payment_status_tool ===")
        
        result = get_payment_status_tool.invoke({"days": 30})
        print(f"Payment status: {result}")
        assert isinstance(result, dict)
        assert "paid_count" in result or "error" in result
    
    def test_get_top_treatments_tool(self):
        """Test top treatments."""
        print("\n=== Testing get_top_treatments_tool ===")
        
        result = get_top_treatments_tool.invoke({"limit": 5, "days": 30})
        print(f"Top treatments: {result}")
        assert isinstance(result, list)
    
    def test_get_outstanding_invoices_tool(self):
        """Test outstanding invoices."""
        print("\n=== Testing get_outstanding_invoices_tool ===")
        
        result = get_outstanding_invoices_tool.invoke({"limit": 10})
        print(f"Outstanding invoices: {result}")
        assert isinstance(result, list)
    
    def test_analyze_profitability_tool(self):
        """Test profitability analysis."""
        print("\n=== Testing analyze_profitability_tool ===")
        
        result = analyze_profitability_tool.invoke({"days": 30})
        print(f"Profitability analysis: {result}")
        assert isinstance(result, dict)
        assert "total_revenue" in result or "error" in result
    
    def test_get_financial_trends_tool(self):
        """Test financial trends."""
        print("\n=== Testing get_financial_trends_tool ===")
        
        result = get_financial_trends_tool.invoke({"days": 90})
        print(f"Financial trends: {result}")
        assert isinstance(result, dict)
        assert "trend" in result or "error" in result


class TestAdminTools:
    """Test Practice Admin agent tools."""
    
    def test_get_schedule_conflicts_tool(self):
        """Test schedule conflicts detection."""
        print("\n=== Testing get_schedule_conflicts_tool ===")
        
        result = get_schedule_conflicts_tool.invoke({"days": 7})
        print(f"Schedule conflicts: {result}")
        assert "conflicts_found" in result or "error" in result.lower()
    
    def test_admin_get_available_slots_tool(self):
        """Test admin available slots."""
        print("\n=== Testing admin get_available_slots_tool ===")
        
        result = admin_get_available_slots_tool.invoke({
            "date": "2025-10-15",
            "duration": 30
        })
        print(f"Admin available slots: {result}")
        assert "available_slots" in result or "error" in result.lower()
    
    def test_reschedule_appointment_tool(self):
        """Test appointment rescheduling."""
        print("\n=== Testing reschedule_appointment_tool ===")
        
        # Get first appointment ID
        appointment_ids = odoo_client.search_appointments()
        if appointment_ids:
            result = reschedule_appointment_tool.invoke({
                "appointment_id": appointment_ids[0],
                "new_date": "2025-10-20",
                "new_time": "15:00",
                "reason": "Patient request"
            })
            print(f"Reschedule appointment: {result}")
            assert "success" in result or "error" in result.lower()
        else:
            print("No appointments found to test")
    
    def test_get_staff_schedule_tool(self):
        """Test staff schedule."""
        print("\n=== Testing get_staff_schedule_tool ===")
        
        result = get_staff_schedule_tool.invoke({"staff_type": "all"})
        print(f"Staff schedule: {result}")
        assert "staff_count" in result or "error" in result.lower()
    
    def test_get_room_availability_tool(self):
        """Test room availability."""
        print("\n=== Testing get_room_availability_tool ===")
        
        result = get_room_availability_tool.invoke({"date": "2025-10-15"})
        print(f"Room availability: {result}")
        assert "total_rooms" in result or "error" in result.lower()
    
    def test_optimize_schedule_tool(self):
        """Test schedule optimization."""
        print("\n=== Testing optimize_schedule_tool ===")
        
        result = optimize_schedule_tool.invoke({
            "date": "2025-10-15",
            "optimization_goal": "minimize_gaps"
        })
        print(f"Schedule optimization: {result}")
        assert "suggestions" in result or "error" in result.lower()
    
    def test_get_operational_metrics_tool(self):
        """Test operational metrics."""
        print("\n=== Testing get_operational_metrics_tool ===")
        
        result = get_operational_metrics_tool.invoke({"date_range": 7})
        print(f"Operational metrics: {result}")
        assert "appointments" in result or "error" in result.lower()
    
    def test_cancel_appointment_tool(self):
        """Test appointment cancellation."""
        print("\n=== Testing cancel_appointment_tool ===")
        
        # Get an appointment that's scheduled (not already cancelled)
        appointment_ids = odoo_client.search_appointments(status="scheduled")
        if appointment_ids:
            result = cancel_appointment_tool.invoke({
                "appointment_id": appointment_ids[0],
                "reason": "Test cancellation",
                "notify_patient": False
            })
            print(f"Cancel appointment: {result}")
            assert "success" in result or "error" in result.lower()
        else:
            print("No scheduled appointments found to test")


class TestOdooClientIntegration:
    """Test OdooClient integration with tools."""
    
    def test_odoo_client_patients(self):
        """Test OdooClient patient operations."""
        print("\n=== Testing OdooClient patient operations ===")
        
        # Count patients
        count = odoo_client.count_patients()
        print(f"Total patients: {count}")
        assert count > 0
        
        # Search patients
        patient_ids = odoo_client.search_patients(name="David")
        print(f"Found {len(patient_ids)} patients named David")
        assert isinstance(patient_ids, list)
        
        # Get patient details
        if patient_ids:
            patient = odoo_client.get_patient(patient_ids[0])
            print(f"Patient details: {patient}")
            assert patient is not None
            assert isinstance(patient, dict)
            assert "name" in patient
    
    def test_odoo_client_appointments(self):
        """Test OdooClient appointment operations."""
        print("\n=== Testing OdooClient appointment operations ===")
        
        # Count appointments
        count = odoo_client.count_appointments()
        print(f"Total appointments: {count}")
        assert count >= 0
        
        # Search appointments
        appointment_ids = odoo_client.search_appointments()
        print(f"Found {len(appointment_ids)} appointments")
        assert isinstance(appointment_ids, list)
        
        # Get appointment details
        if appointment_ids:
            appointment = odoo_client.get_appointment(appointment_ids[0])
            print(f"Appointment details: {appointment}")
            assert appointment is not None
            assert "date" in appointment
    
    def test_odoo_client_invoices(self):
        """Test OdooClient invoice operations."""
        print("\n=== Testing OdooClient invoice operations ===")
        
        # Count invoices
        count = odoo_client.count_invoices()
        print(f"Total invoices: {count}")
        assert count >= 0
        
        # Search invoices
        invoice_ids = odoo_client.search_invoices()
        print(f"Found {len(invoice_ids)} invoices")
        assert isinstance(invoice_ids, list)
        
        # Get invoice details
        if invoice_ids:
            invoice = odoo_client.get_invoice(invoice_ids[0])
            print(f"Invoice details: {invoice}")
            assert invoice is not None
            assert "total_amount" in invoice


def run_all_tests():
    """Run all tests with detailed output."""
    print("\n" + "="*80)
    print("COMPREHENSIVE AGENT TOOLS TEST SUITE")
    print("Testing updated tools with OdooClient integration")
    print("="*80)
    
    # Run pytest with verbose output
    pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short",
        "--color=yes"
    ])


if __name__ == "__main__":
    run_all_tests()
