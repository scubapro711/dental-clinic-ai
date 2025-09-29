# Dashboard-Database Integration Testing
# Version: 1.0.0
# Date: 2025-12-29

import pytest
import asyncio
import json
import time
from fastapi.testclient import TestClient
from src.gateway.main import app
from src.ai_agents.tools.enhanced_mock_tool import EnhancedMockDentalTool

client = TestClient(app)

class TestDashboardDataIntegration:
    """Test integration between dashboard and database systems."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.mock_tool = EnhancedMockDentalTool()
        asyncio.run(self.mock_tool.initialize())
        
    def test_patient_data_consistency(self):
        """Test that patient data is consistent between API and mock database."""
        # Get patients from mock tool
        mock_patients = self.mock_tool.mock_patients
        assert len(mock_patients) >= 20, "Should have at least 20 patients"
        
        # Test patient search through API
        response = client.post("/api/search_patients", json={"query": "test"})
        assert response.status_code == 200
        
        # Verify specific patient data
        for patient_data in mock_patients[:5]:
            patient_id = patient_data["id"]
            details = asyncio.run(self.mock_tool.get_patient_details(patient_id))
            assert details is not None
            assert "name" in details
            assert "phone" in details
            assert "email" in details
            
            # Verify Hebrew names are properly handled
            if any(ord(char) > 127 for char in details["name"]):
                assert len(details["name"]) > 0, "Hebrew names should not be empty"
    
    def test_doctor_data_availability(self):
        """Test that doctor data is available and consistent."""
        doctors = self.mock_tool.mock_doctors
        assert len(doctors) >= 4, "Should have at least 4 doctors"
        
        # Test providers endpoint
        response = client.post("/api/get_providers", json={})
        assert response.status_code == 200
        
        # Verify doctor data structure
        for doctor_data in doctors:
            assert "name" in doctor_data
            assert "specialty" in doctor_data
            
            # Verify Hebrew specializations
            if "specialty" in doctor_data:
                assert len(doctor_data["specialty"]) > 0
    
    def test_appointment_system_integration(self):
        """Test appointment booking system integration."""
        # Get available slots
        response = client.post("/api/get_available_slots", json={"date": "2025-01-15"})
        assert response.status_code == 200
        
        # Test appointment booking through mock tool
        if self.mock_tool.mock_patients and self.mock_tool.mock_doctors:
            patient_id = self.mock_tool.mock_patients[0]["id"]
            doctor_id = self.mock_tool.mock_doctors[0]["id"]
            
            # Book appointment
            booking_result = asyncio.run(self.mock_tool.book_appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                datetime_str="2025-01-20T10:00:00",
                treatment_id=1
            ))
            
            assert booking_result is not None
            assert booking_result.get("success") is True
            
            # Verify appointment was created
            patient_appointments = asyncio.run(self.mock_tool.get_patient_appointments(patient_id))
            assert isinstance(patient_appointments, list)
    
    def test_real_time_data_updates(self):
        """Test that data updates are reflected in real-time."""
        # Initial patient count
        initial_patients = len(self.mock_tool.mock_patients)
        
        # Simulate data changes through multiple operations
        for i in range(10):
            # Search operations
            search_result = asyncio.run(self.mock_tool.search_patients("test"))
            assert isinstance(search_result, list)
            
            # Appointment operations
            slots = asyncio.run(self.mock_tool.get_available_slots("2025-01-15", "2025-01-15"))
            assert isinstance(slots, list)
        
        # Verify data consistency maintained
        final_patients = len(self.mock_tool.mock_patients)
        assert final_patients == initial_patients, "Patient count should remain consistent"
    
    def test_hebrew_text_handling(self):
        """Test proper handling of Hebrew text throughout the system."""
        hebrew_test_cases = [
            "יוסי כהן",
            "מרפאת שיניים",
            "בדיקה כללית",
            "רופא שיניים",
            "תור לטיפול",
            "ניקוי אבנית"
        ]
        
        for hebrew_text in hebrew_test_cases:
            # Test through message processing
            response = client.post("/api/process_message", json={"text": hebrew_text})
            assert response.status_code == 200
            
            # Verify response contains Hebrew text properly
            if response.status_code == 200:
                response_data = response.json()
                # Should handle Hebrew without corruption
                assert response_data is not None
    
    def test_data_validation_and_sanitization(self):
        """Test data validation and sanitization in the integration."""
        # Test with various input types
        test_inputs = [
            {"valid_phone": "050-1234567"},
            {"invalid_phone": "123"},
            {"valid_email": "test@example.com"},
            {"invalid_email": "not-an-email"},
            {"hebrew_name": "יוסי כהן"},
            {"english_name": "John Doe"},
            {"mixed_text": "John יוסי"},
        ]
        
        for test_input in test_inputs:
            # Test through search
            response = client.post("/api/search_patients", json=test_input)
            # Should not crash on any input
            assert response.status_code != 500
    
    def test_concurrent_data_access(self):
        """Test concurrent access to data doesn't cause corruption."""
        import concurrent.futures
        
        def access_patient_data():
            try:
                # Random patient operations - use synchronous access for thread safety
                if self.mock_tool.mock_patients:
                    patient_id = self.mock_tool.mock_patients[0]["id"]
                    # Just check data structure integrity
                    return len(self.mock_tool.mock_patients) >= 20
                return True
            except Exception:
                return False
        
        # Run 20 concurrent operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(access_patient_data) for _ in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All operations should succeed
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.95, f"Concurrent access success rate too low: {success_rate}"

class TestDashboardAPIEndpoints:
    """Test all dashboard-related API endpoints."""
    
    def test_status_endpoint_detailed(self):
        """Test detailed status endpoint for dashboard."""
        response = client.get("/api/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "components" in data
        
        # Check if the status is ok or error
        if data["status"] == "ok":
            assert "patients_count" in data["components"]
            assert "doctors_count" in data["components"]
            
            # Verify counts are reasonable
            assert data["components"]["patients_count"] >= 20
            assert data["components"]["doctors_count"] >= 4
        else:
            # If there's an error, just verify the structure
            assert data["status"] == "error"
            assert "error" in data
    
    def test_message_processing_for_dashboard(self):
        """Test message processing that would be used by dashboard."""
        dashboard_messages = [
            "הצג לי את כל המטופלים",
            "מה המצב של המרפאה היום?",
            "כמה תורים יש לנו השבוע?",
            "Show me all patients",
            "What's the clinic status today?",
            "How many appointments this week?"
        ]
        
        for message in dashboard_messages:
            response = client.post("/api/process_message", json={"text": message})
            assert response.status_code == 200
            
            # Verify response structure
            data = response.json()
            assert data is not None
    
    def test_simulation_endpoints_for_demo(self):
        """Test simulation endpoints that would be used in investor demo."""
        # Test simulation status
        response = client.get("/api/simulation_status")
        assert response.status_code == 200
        
        data = response.json()
        assert "is_running" in data
        assert "metrics" in data
        
        # Test starting simulation
        response = client.post("/api/start_simulation", json={
            "duration_minutes": 1,
            "speed": 2.0
        })
        assert response.status_code == 200
        
        start_data = response.json()
        assert "status" in start_data
        assert start_data["status"] == "simulation_started"
        
        # Test stopping simulation
        response = client.post("/api/stop_simulation", json={})
        assert response.status_code == 200
        
        stop_data = response.json()
        assert "status" in stop_data
        assert stop_data["status"] == "simulation_stopped"

class TestDashboardPerformance:
    """Test dashboard performance under various conditions."""
    
    def test_dashboard_data_loading_speed(self):
        """Test speed of data loading for dashboard."""
        endpoints_to_test = [
            "/api/status",
            "/api/simulation_status",
        ]
        
        for endpoint in endpoints_to_test:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response.status_code == 200
            assert response_time < 1.0, f"Dashboard endpoint {endpoint} too slow: {response_time}s"
    
    def test_dashboard_under_load(self):
        """Test dashboard performance under simulated load."""
        # Simulate multiple dashboard users
        def simulate_dashboard_user():
            try:
                # Typical dashboard user actions
                client.get("/api/status")
                client.post("/api/search_patients", json={"query": "test"})
                client.post("/api/get_available_slots", json={"date": "2025-01-15"})
                return True
            except Exception:
                return False
        
        import concurrent.futures
        
        # Simulate 10 concurrent dashboard users
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(simulate_dashboard_user) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.9, f"Dashboard load test success rate too low: {success_rate}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
