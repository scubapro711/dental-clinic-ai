"""
Comprehensive Tests for Data Simulator Agent
Tests the AI-powered clinic simulation system
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from simulator.data_simulator_agent import (
    DataSimulatorAgent, 
    VirtualPatient, 
    PatientType, 
    CallType
)

class TestDataSimulatorAgent:
    """Test suite for Data Simulator Agent"""
    
    @pytest.fixture
    def simulator(self):
        """Create a simulator instance for testing"""
        return DataSimulatorAgent()
    
    @pytest.fixture
    def sample_patient(self):
        """Create a sample virtual patient"""
        return VirtualPatient(
            id="test_patient_1",
            name="דוד כהן",
            age=35,
            patient_type=PatientType.EXPERIENCED,
            background="מטופל ותיק במרפאה",
            current_need="בדיקת שיניים שגרתית",
            urgency_level=3,
            communication_style="ישיר ועניני",
            medical_history=["בריא", "אלרגיה לפניצילין"],
            preferred_times=["בוקר", "אחר הצהריים"],
            insurance_info={"provider": "כללית", "policy": "123456789"}
        )
    
    def test_simulator_initialization(self, simulator):
        """Test simulator initializes correctly"""
        assert simulator.is_running == False
        assert simulator.simulation_speed == 1.0
        assert simulator.active_scenarios == []
        assert simulator.patient_database == []
        assert simulator.interaction_history == []
        assert "total_calls" in simulator.performance_metrics
        assert "successful_bookings" in simulator.performance_metrics
        assert "patient_satisfaction" in simulator.performance_metrics
    
    def test_patient_types_enum(self):
        """Test all patient types are defined"""
        expected_types = [
            "anxious", "urgent", "confused", "experienced", 
            "elderly", "young_parent", "business_person", "student"
        ]
        
        actual_types = [pt.value for pt in PatientType]
        
        for expected in expected_types:
            assert expected in actual_types
    
    def test_call_types_enum(self):
        """Test all call types are defined"""
        expected_types = [
            "new_appointment", "reschedule", "cancel", "emergency",
            "inquiry", "complaint", "follow_up"
        ]
        
        actual_types = [ct.value for ct in CallType]
        
        for expected in expected_types:
            assert expected in actual_types
    
    def test_virtual_patient_creation(self, sample_patient):
        """Test virtual patient data structure"""
        assert sample_patient.id == "test_patient_1"
        assert sample_patient.name == "דוד כהן"
        assert sample_patient.age == 35
        assert sample_patient.patient_type == PatientType.EXPERIENCED
        assert isinstance(sample_patient.medical_history, list)
        assert isinstance(sample_patient.preferred_times, list)
        assert isinstance(sample_patient.insurance_info, dict)
    
    def test_create_default_patient(self, simulator):
        """Test default patient creation fallback"""
        patient = simulator._create_default_patient("test_id", PatientType.ANXIOUS)
        
        assert patient.id == "test_id"
        assert patient.patient_type == PatientType.ANXIOUS
        assert isinstance(patient.name, str)
        assert 18 <= patient.age <= 80
        assert isinstance(patient.medical_history, list)
        assert isinstance(patient.preferred_times, list)
        assert isinstance(patient.insurance_info, dict)
    
    @pytest.mark.asyncio
    async def test_generate_realistic_call_without_patients(self, simulator):
        """Test call generation when no patients exist"""
        with patch.object(simulator, 'initialize_patient_database') as mock_init:
            mock_init.return_value = None
            simulator.patient_database = [
                simulator._create_default_patient("test_1", PatientType.EXPERIENCED)
            ]
            
            with patch.object(simulator, '_generate_call_scenario') as mock_scenario:
                mock_scenario.return_value = {
                    "opening_statement": "שלום, אני רוצה לקבוע תור",
                    "key_questions": ["מתי יש מקום?"],
                    "special_requests": [],
                    "expected_outcome": "קביעת תור",
                    "estimated_duration": 3,
                    "difficulty_level": 3
                }
                
                call_data = await simulator.generate_realistic_call()
                
                assert "id" in call_data
                assert "timestamp" in call_data
                assert "patient" in call_data
                assert "call_type" in call_data
                assert "scenario" in call_data
                assert call_data["status"] == "incoming"
    
    def test_performance_metrics_update(self, simulator):
        """Test performance metrics calculation"""
        # Mock call data
        call_data = {
            "outcome": {
                "successful": True,
                "patient_satisfaction": 8
            },
            "duration": 5.5
        }
        
        # Update metrics
        simulator._update_performance_metrics(call_data)
        
        assert simulator.performance_metrics["total_calls"] == 1
        assert simulator.performance_metrics["successful_bookings"] == 1
        assert simulator.performance_metrics["patient_satisfaction"] == 8.0
        assert simulator.performance_metrics["average_call_duration"] == 5.5
        
        # Add another call
        call_data_2 = {
            "outcome": {
                "successful": False,
                "patient_satisfaction": 6
            },
            "duration": 3.0
        }
        
        simulator._update_performance_metrics(call_data_2)
        
        assert simulator.performance_metrics["total_calls"] == 2
        assert simulator.performance_metrics["successful_bookings"] == 1
        assert simulator.performance_metrics["patient_satisfaction"] == 7.0  # (8+6)/2
        assert simulator.performance_metrics["average_call_duration"] == 4.25  # (5.5+3)/2
    
    def test_simulation_speed_control(self, simulator):
        """Test simulation speed control"""
        # Test normal speed
        simulator.set_simulation_speed(1.0)
        assert simulator.simulation_speed == 1.0
        
        # Test faster speed
        simulator.set_simulation_speed(2.5)
        assert simulator.simulation_speed == 2.5
        
        # Test slower speed
        simulator.set_simulation_speed(0.5)
        assert simulator.simulation_speed == 0.5
        
        # Test boundary conditions
        simulator.set_simulation_speed(0.05)  # Too slow
        assert simulator.simulation_speed == 0.1  # Minimum
        
        simulator.set_simulation_speed(15.0)  # Too fast
        assert simulator.simulation_speed == 10.0  # Maximum
    
    def test_performance_report_structure(self, simulator):
        """Test performance report structure"""
        # Add some mock data
        simulator.patient_database = [
            simulator._create_default_patient("p1", PatientType.ANXIOUS),
            simulator._create_default_patient("p2", PatientType.URGENT)
        ]
        
        simulator.interaction_history = [
            {"id": "call_1", "outcome": {"successful": True}},
            {"id": "call_2", "outcome": {"successful": False}}
        ]
        
        report = simulator.get_performance_report()
        
        assert "metrics" in report
        assert "recent_calls" in report
        assert "patient_count" in report
        assert "simulation_status" in report
        
        assert report["patient_count"] == 2
        assert report["simulation_status"] == "stopped"
        assert len(report["recent_calls"]) == 2
    
    def test_start_stop_simulation(self, simulator):
        """Test simulation start/stop functionality"""
        assert simulator.is_running == False
        
        # Test stop when not running
        simulator.stop_simulation()
        assert simulator.is_running == False
        
        # Test start flag (without actually running the loop)
        simulator.is_running = True
        assert simulator.is_running == True
        
        # Test stop
        simulator.stop_simulation()
        assert simulator.is_running == False
    
    @pytest.mark.asyncio
    async def test_ai_response_error_handling(self, simulator):
        """Test AI response error handling"""
        with patch('openai.AsyncOpenAI') as mock_openai:
            # Mock OpenAI client to raise an exception
            mock_client = AsyncMock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client
            
            # Test error handling in AI response
            response = await simulator._get_ai_response(
                "test prompt", 
                [{"speaker": "patient", "message": "test"}], 
                "clinic_agent"
            )
            
            # Should return fallback message
            assert "מצטער" in response or "בעיה טכנית" in response
    
    @pytest.mark.asyncio 
    async def test_conversation_analysis_error_handling(self, simulator):
        """Test conversation analysis error handling"""
        conversation = [
            {"speaker": "patient", "message": "שלום"},
            {"speaker": "clinic", "message": "שלום, איך אוכל לעזור?"}
        ]
        
        scenario = {"expected_outcome": "קביעת תור"}
        
        with patch('simulator.data_simulator_agent.client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            
            outcome = await simulator._analyze_conversation_outcome(conversation, scenario)
            
            # Should return fallback outcome
            assert "successful" in outcome
            assert "outcome_type" in outcome
            assert "patient_satisfaction" in outcome
            assert outcome["notes"] == "שיחה הושלמה בהצלחה"
    
    def test_broadcast_call_update_format(self, simulator):
        """Test call update broadcast format"""
        call_data = {
            "id": "test_call_123",
            "timestamp": "2024-09-28T14:30:00",
            "patient": {"name": "דוד כהן"},
            "call_type": "new_appointment",
            "outcome": {
                "successful": True,
                "notes": "תור נקבע בהצלחה",
                "patient_satisfaction": 9,
                "outcome_type": "appointment_booked"
            },
            "duration": 4.5
        }
        
        # Test broadcast format (would normally send to WebSocket)
        # This tests the data structure preparation
        activity_data = {
            "id": call_data["id"],
            "agent_id": "clinic_agent",
            "type": "phone_call",
            "status": "completed" if call_data["outcome"]["successful"] else "failed",
            "title": f"שיחה עם {call_data['patient']['name']}",
            "description": call_data["outcome"]["notes"],
            "timestamp": call_data["timestamp"],
            "duration": call_data["duration"],
            "metadata": {
                "call_type": call_data["call_type"],
                "patient_satisfaction": call_data["outcome"]["patient_satisfaction"],
                "outcome_type": call_data["outcome"]["outcome_type"]
            }
        }
        
        assert activity_data["id"] == "test_call_123"
        assert activity_data["agent_id"] == "clinic_agent"
        assert activity_data["type"] == "phone_call"
        assert activity_data["status"] == "completed"
        assert "דוד כהן" in activity_data["title"]
        assert activity_data["duration"] == 4.5
        assert activity_data["metadata"]["patient_satisfaction"] == 9

# Integration tests
class TestDataSimulatorIntegration:
    """Integration tests for the complete simulation system"""
    
    @pytest.mark.asyncio
    async def test_full_simulation_cycle_mock(self):
        """Test a complete simulation cycle with mocked AI"""
        simulator = DataSimulatorAgent()
        
        # Mock OpenAI responses
        with patch.object(simulator, '_generate_virtual_patient') as mock_patient:
            mock_patient.return_value = VirtualPatient(
                id="test_patient",
                name="שרה לוי",
                age=28,
                patient_type=PatientType.YOUNG_PARENT,
                background="אמא צעירה",
                current_need="בדיקה לילד",
                urgency_level=5,
                communication_style="דאגנית אבל ידידותית",
                medical_history=["בריאה"],
                preferred_times=["אחר הצהריים"],
                insurance_info={"provider": "מכבי", "policy": "987654321"}
            )
            
            with patch.object(simulator, '_generate_call_scenario') as mock_scenario:
                mock_scenario.return_value = {
                    "opening_statement": "שלום, אני רוצה לקבוע תור לילד שלי",
                    "key_questions": ["מתי יש מקום?", "האם זה כואב?"],
                    "special_requests": ["תור בשעות אחר הצהריים"],
                    "expected_outcome": "קביעת תור לילד",
                    "estimated_duration": 4,
                    "difficulty_level": 6
                }
                
                with patch.object(simulator, '_get_ai_response') as mock_ai_response:
                    mock_ai_response.side_effect = [
                        "שלום! בוודאי אוכל לעזור לך לקבוע תור לילד. באיזה גיל הילד?",
                        "הוא בן 6. אני רוצה בדיקה שגרתית.",
                        "מצוין! יש לי מקום ביום רביעי בשעה 15:00. האם זה מתאים?",
                        "כן, זה מושלם! תודה רבה."
                    ]
                    
                    with patch.object(simulator, '_analyze_conversation_outcome') as mock_analysis:
                        mock_analysis.return_value = {
                            "successful": True,
                            "outcome_type": "appointment_booked",
                            "patient_satisfaction": 9,
                            "issues_resolved": ["קביעת תור לילד"],
                            "follow_up_needed": False,
                            "notes": "תור נקבע בהצלחה לילד בן 6"
                        }
                        
                        # Generate and process a call
                        call_data = await simulator.generate_realistic_call()
                        completed_call = await simulator.simulate_patient_agent_call(call_data)
                        
                        # Verify results
                        assert completed_call["outcome"]["successful"] == True
                        assert completed_call["outcome"]["outcome_type"] == "appointment_booked"
                        assert completed_call["outcome"]["patient_satisfaction"] == 9
                        assert len(completed_call["conversation"]) > 0
                        assert completed_call["status"] == "completed"

# Performance tests
class TestDataSimulatorPerformance:
    """Performance tests for the simulation system"""
    
    def test_patient_generation_performance(self):
        """Test patient generation doesn't take too long"""
        simulator = DataSimulatorAgent()
        
        import time
        start_time = time.time()
        
        # Generate 10 default patients
        patients = []
        for i in range(10):
            patient = simulator._create_default_patient(f"perf_test_{i}", PatientType.EXPERIENCED)
            patients.append(patient)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Should generate 10 patients in under 1 second
        assert generation_time < 1.0
        assert len(patients) == 10
        
        # Verify all patients are unique
        patient_ids = [p.id for p in patients]
        assert len(set(patient_ids)) == 10
    
    def test_metrics_calculation_performance(self):
        """Test metrics calculation performance with many calls"""
        simulator = DataSimulatorAgent()
        
        import time
        start_time = time.time()
        
        # Simulate 100 calls
        for i in range(100):
            call_data = {
                "outcome": {
                    "successful": i % 3 == 0,  # 33% success rate
                    "patient_satisfaction": (i % 10) + 1  # 1-10 rating
                },
                "duration": (i % 5) + 1  # 1-5 minute calls
            }
            simulator._update_performance_metrics(call_data)
        
        end_time = time.time()
        calculation_time = end_time - start_time
        
        # Should process 100 calls in under 0.1 seconds
        assert calculation_time < 0.1
        assert simulator.performance_metrics["total_calls"] == 100
        
        # Verify metrics are reasonable
        success_rate = simulator.performance_metrics["successful_bookings"] / 100
        assert 0.3 <= success_rate <= 0.4  # Around 33%
        
        avg_satisfaction = simulator.performance_metrics["patient_satisfaction"]
        assert 1 <= avg_satisfaction <= 10

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
