"""
Basic tests for Open Dental API Client
Component 3.1 Testing Suite
"""

import pytest
from datetime import datetime
from cryptography.fernet import Fernet

# Import the module under test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from integrations.opendental_client import (
    OpenDentalClient,
    Patient,
    Appointment,
    OpenDentalConnectionError,
    OpenDentalDataError
)

class TestPatientDataStructure:
    """Test Patient data structure and serialization"""
    
    def test_patient_creation(self):
        """Test Patient object creation with required fields"""
        patient = Patient(
            patient_num=123,
            last_name="Smith",
            first_name="John",
            email="john.smith@email.com"
        )
        
        assert patient.patient_num == 123
        assert patient.last_name == "Smith"
        assert patient.first_name == "John"
        assert patient.email == "john.smith@email.com"
        assert patient.pat_status == "Patient"  # Default value
    
    def test_patient_to_dict(self):
        """Test Patient serialization to dictionary"""
        birthdate = datetime(1990, 5, 15)
        patient = Patient(
            patient_num=456,
            last_name="Doe",
            first_name="Jane",
            birthdate=birthdate
        )
        
        patient_dict = patient.to_dict()
        
        assert patient_dict['patient_num'] == 456
        assert patient_dict['last_name'] == "Doe"
        assert patient_dict['first_name'] == "Jane"
        assert patient_dict['birthdate'] == birthdate.isoformat()
    
    def test_patient_with_all_fields(self):
        """Test Patient with comprehensive field set"""
        patient = Patient(
            patient_num=789,
            last_name="Johnson",
            first_name="Bob",
            middle_initial="A",
            preferred="Bobby",
            home_phone="555-1234",
            wk_phone="555-5678",
            wireless_phone="555-9012",
            email="bob@email.com",
            address="123 Main St",
            address2="Apt 4B",
            city="Anytown",
            state="CA",
            zip="12345",
            birthdate=datetime(1985, 3, 20),
            gender="M",
            pat_status="Patient"
        )
        
        assert patient.middle_initial == "A"
        assert patient.preferred == "Bobby"
        assert patient.address2 == "Apt 4B"
        assert patient.gender == "M"

class TestAppointmentDataStructure:
    """Test Appointment data structure and serialization"""
    
    def test_appointment_creation(self):
        """Test Appointment object creation"""
        apt_datetime = datetime(2024, 1, 15, 10, 30)
        appointment = Appointment(
            apt_num=101,
            patient_num=123,
            apt_status="Scheduled",
            pattern="XXXX",
            confirmed=1,
            apt_date_time=apt_datetime,
            apt_length=60
        )
        
        assert appointment.apt_num == 101
        assert appointment.patient_num == 123
        assert appointment.apt_status == "Scheduled"
        assert appointment.apt_date_time == apt_datetime
        assert appointment.apt_length == 60
    
    def test_appointment_to_dict(self):
        """Test Appointment serialization to dictionary"""
        apt_datetime = datetime(2024, 2, 20, 14, 0)
        appointment = Appointment(
            apt_num=202,
            patient_num=456,
            apt_status="Confirmed",
            pattern="XXXX",
            confirmed=1,
            apt_date_time=apt_datetime
        )
        
        apt_dict = appointment.to_dict()
        
        assert apt_dict['apt_num'] == 202
        assert apt_dict['patient_num'] == 456
        assert apt_dict['apt_status'] == "Confirmed"
        assert apt_dict['apt_date_time'] == apt_datetime.isoformat()
    
    def test_appointment_with_all_fields(self):
        """Test Appointment with comprehensive field set"""
        appointment = Appointment(
            apt_num=303,
            patient_num=789,
            apt_status="Confirmed",
            pattern="XXXXXXXX",
            confirmed=1,
            op=2,
            provider_num=5,
            provider_hyg=3,
            apt_date_time=datetime(2024, 3, 10, 9, 0),
            apt_length=120,
            apt_note="Root canal procedure",
            is_new_patient=False,
            clinic_num=1
        )
        
        assert appointment.op == 2
        assert appointment.provider_num == 5
        assert appointment.provider_hyg == 3
        assert appointment.apt_note == "Root canal procedure"
        assert appointment.is_new_patient == False
        assert appointment.clinic_num == 1

class TestOpenDentalClientInitialization:
    """Test OpenDentalClient initialization and configuration"""
    
    def test_client_initialization_defaults(self):
        """Test client initialization with default parameters"""
        client = OpenDentalClient()
        
        assert client.host == "localhost"
        assert client.port == 3306
        assert client.database == "opendental"
        assert client.username == "root"
        assert client.connection_pool_size == 10
        assert client.cipher is not None
        assert client.pool is None  # Not connected yet
        assert client.query_count == 0
        assert client.connection_errors == 0
    
    def test_client_initialization_custom(self):
        """Test client initialization with custom parameters"""
        client = OpenDentalClient(
            host="192.168.1.100",
            port=3307,
            database="dental_db",
            username="dental_user",
            password="secure_pass",
            connection_pool_size=20
        )
        
        assert client.host == "192.168.1.100"
        assert client.port == 3307
        assert client.database == "dental_db"
        assert client.username == "dental_user"
        assert client.connection_pool_size == 20
    
    def test_encryption_key_handling(self):
        """Test encryption key initialization"""
        test_key = Fernet.generate_key().decode()
        client = OpenDentalClient(encryption_key=test_key)
        
        assert client.cipher is not None
        # Test that cipher can encrypt/decrypt
        test_data = b"test data"
        encrypted = client.cipher.encrypt(test_data)
        decrypted = client.cipher.decrypt(encrypted)
        assert decrypted == test_data
    
    def test_encryption_key_generation(self):
        """Test automatic encryption key generation"""
        client1 = OpenDentalClient()
        client2 = OpenDentalClient()
        
        # Each client should have its own cipher
        assert client1.cipher is not None
        assert client2.cipher is not None
        
        # Test that each cipher works independently
        test_data = b"test message"
        encrypted1 = client1.cipher.encrypt(test_data)
        encrypted2 = client2.cipher.encrypt(test_data)
        
        # Encrypted data should be different (different keys)
        assert encrypted1 != encrypted2
        
        # But each can decrypt its own data
        assert client1.cipher.decrypt(encrypted1) == test_data
        assert client2.cipher.decrypt(encrypted2) == test_data

class TestPerformanceMetrics:
    """Test performance monitoring functionality"""
    
    @pytest.mark.asyncio
    async def test_performance_metrics_initial_state(self):
        """Test initial performance metrics"""
        client = OpenDentalClient()
        
        metrics = await client.get_performance_metrics()
        
        assert metrics['query_count'] == 0
        assert metrics['connection_errors'] == 0
        assert metrics['connection_pool_size'] == 10
        assert metrics['is_connected'] == False
    
    @pytest.mark.asyncio
    async def test_performance_metrics_after_operations(self):
        """Test performance metrics after simulated operations"""
        client = OpenDentalClient()
        
        # Simulate some operations
        client.query_count = 15
        client.connection_errors = 2
        
        metrics = await client.get_performance_metrics()
        
        assert metrics['query_count'] == 15
        assert metrics['connection_errors'] == 2
        assert metrics['connection_pool_size'] == 10

class TestDataValidation:
    """Test data validation and edge cases"""
    
    def test_patient_with_none_values(self):
        """Test Patient creation with None values"""
        patient = Patient(
            patient_num=123,
            last_name="Smith",
            first_name="John",
            birthdate=None,
            email=""
        )
        
        assert patient.birthdate is None
        assert patient.email == ""
        
        # Serialization should handle None values
        patient_dict = patient.to_dict()
        assert patient_dict['birthdate'] is None
        assert patient_dict['email'] == ""
    
    def test_appointment_with_none_values(self):
        """Test Appointment creation with None values"""
        appointment = Appointment(
            apt_num=101,
            patient_num=123,
            apt_status="Scheduled",
            pattern="XXXX",
            confirmed=1,
            apt_date_time=None
        )
        
        assert appointment.apt_date_time is None
        
        # Serialization should handle None values
        apt_dict = appointment.to_dict()
        assert apt_dict['apt_date_time'] is None
    
    def test_patient_empty_strings(self):
        """Test Patient with empty string values"""
        patient = Patient(
            patient_num=456,
            last_name="",
            first_name="",
            email="",
            home_phone=""
        )
        
        assert patient.last_name == ""
        assert patient.first_name == ""
        assert patient.email == ""
    
    def test_appointment_zero_values(self):
        """Test Appointment with zero values"""
        appointment = Appointment(
            apt_num=0,
            patient_num=0,
            apt_status="",
            pattern="",
            confirmed=0,
            apt_length=0
        )
        
        assert appointment.apt_num == 0
        assert appointment.patient_num == 0
        assert appointment.confirmed == 0
        assert appointment.apt_length == 0

class TestExceptionHandling:
    """Test custom exception classes"""
    
    def test_opendental_connection_error(self):
        """Test OpenDentalConnectionError exception"""
        error_message = "Failed to connect to database"
        
        with pytest.raises(OpenDentalConnectionError) as exc_info:
            raise OpenDentalConnectionError(error_message)
        
        assert str(exc_info.value) == error_message
        assert isinstance(exc_info.value, Exception)
    
    def test_opendental_data_error(self):
        """Test OpenDentalDataError exception"""
        error_message = "Failed to retrieve patient data"
        
        with pytest.raises(OpenDentalDataError) as exc_info:
            raise OpenDentalDataError(error_message)
        
        assert str(exc_info.value) == error_message
        assert isinstance(exc_info.value, Exception)

class TestUtilityFunctions:
    """Test utility and helper functions"""
    
    def test_patient_dict_serialization_consistency(self):
        """Test that Patient dict serialization is consistent"""
        patient = Patient(
            patient_num=123,
            last_name="Test",
            first_name="User",
            birthdate=datetime(1990, 1, 1),
            email="test@example.com"
        )
        
        dict1 = patient.to_dict()
        dict2 = patient.to_dict()
        
        # Should produce identical dictionaries
        assert dict1 == dict2
        
        # Should contain all expected keys
        expected_keys = [
            'patient_num', 'last_name', 'first_name', 'middle_initial',
            'preferred', 'home_phone', 'wk_phone', 'wireless_phone',
            'email', 'address', 'address2', 'city', 'state', 'zip',
            'birthdate', 'gender', 'pat_status'
        ]
        
        for key in expected_keys:
            assert key in dict1
    
    def test_appointment_dict_serialization_consistency(self):
        """Test that Appointment dict serialization is consistent"""
        appointment = Appointment(
            apt_num=101,
            patient_num=123,
            apt_status="Scheduled",
            pattern="XXXX",
            confirmed=1,
            apt_date_time=datetime(2024, 1, 15, 10, 0)
        )
        
        dict1 = appointment.to_dict()
        dict2 = appointment.to_dict()
        
        # Should produce identical dictionaries
        assert dict1 == dict2
        
        # Should contain all expected keys
        expected_keys = [
            'apt_num', 'patient_num', 'apt_status', 'pattern', 'confirmed',
            'op', 'provider_num', 'provider_hyg', 'apt_date_time', 'apt_length',
            'apt_note', 'is_new_patient', 'clinic_num'
        ]
        
        for key in expected_keys:
            assert key in dict1

class TestDateTimeHandling:
    """Test datetime handling in data structures"""
    
    def test_patient_datetime_serialization(self):
        """Test Patient datetime field serialization"""
        birthdate = datetime(1985, 6, 15, 14, 30, 45)
        patient = Patient(
            patient_num=123,
            last_name="DateTime",
            first_name="Test",
            birthdate=birthdate
        )
        
        patient_dict = patient.to_dict()
        
        # Should be serialized as ISO format string
        assert patient_dict['birthdate'] == "1985-06-15T14:30:45"
        assert isinstance(patient_dict['birthdate'], str)
    
    def test_appointment_datetime_serialization(self):
        """Test Appointment datetime field serialization"""
        apt_datetime = datetime(2024, 3, 20, 9, 15, 0)
        appointment = Appointment(
            apt_num=101,
            patient_num=123,
            apt_status="Scheduled",
            pattern="XXXX",
            confirmed=1,
            apt_date_time=apt_datetime
        )
        
        apt_dict = appointment.to_dict()
        
        # Should be serialized as ISO format string
        assert apt_dict['apt_date_time'] == "2024-03-20T09:15:00"
        assert isinstance(apt_dict['apt_date_time'], str)
    
    def test_multiple_datetime_fields(self):
        """Test handling of multiple datetime fields"""
        birthdate = datetime(1990, 1, 1)
        patient = Patient(
            patient_num=123,
            last_name="Multi",
            first_name="DateTime",
            birthdate=birthdate
        )
        
        patient_dict = patient.to_dict()
        
        # All datetime fields should be properly serialized
        if patient_dict['birthdate'] is not None:
            assert isinstance(patient_dict['birthdate'], str)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
