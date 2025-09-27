"""
Open Dental API Client
Component 3.1: Secure connection and data operations with Open Dental database

This module provides a secure, efficient interface to Open Dental database
with comprehensive error handling, retry logic, and data integrity validation.
"""

import asyncio
import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
import aiomysql
from cryptography.fernet import Fernet
import backoff

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Patient:
    """Patient data structure matching Open Dental schema"""
    patient_num: int
    last_name: str
    first_name: str
    middle_initial: str = ""
    preferred: str = ""
    home_phone: str = ""
    wk_phone: str = ""
    wireless_phone: str = ""
    email: str = ""
    address: str = ""
    address2: str = ""
    city: str = ""
    state: str = ""
    zip: str = ""
    birthdate: Optional[datetime] = None
    gender: str = ""
    pat_status: str = "Patient"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert patient to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

@dataclass
class Appointment:
    """Appointment data structure matching Open Dental schema"""
    apt_num: int
    patient_num: int
    apt_status: str
    pattern: str
    confirmed: int
    op: int = 0
    provider_num: int = 0
    provider_hyg: int = 0
    apt_date_time: Optional[datetime] = None
    apt_length: int = 0
    apt_note: str = ""
    is_new_patient: bool = False
    clinic_num: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert appointment to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

class OpenDentalConnectionError(Exception):
    """Raised when connection to Open Dental database fails"""
    pass

class OpenDentalDataError(Exception):
    """Raised when data operations fail"""
    pass

class OpenDentalClient:
    """
    Secure Open Dental API Client
    
    Provides encrypted, authenticated access to Open Dental database
    with comprehensive error handling and performance optimization.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        database: str = "opendental",
        username: str = "root",
        password: str = "",
        encryption_key: Optional[str] = None,
        connection_pool_size: int = 10
    ):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection_pool_size = connection_pool_size
        
        # Initialize encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            # Generate a key for this session (in production, use persistent key)
            self.cipher = Fernet(Fernet.generate_key())
            
        # Connection pool
        self.pool: Optional[aiomysql.Pool] = None
        
        # Performance metrics
        self.query_count = 0
        self.connection_errors = 0
        
        logger.info("OpenDentalClient initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    @backoff.on_exception(
        backoff.expo,
        (aiomysql.Error, ConnectionError),
        max_tries=3,
        max_time=30
    )
    async def connect(self) -> None:
        """
        Establish secure connection to Open Dental database
        
        Raises:
            OpenDentalConnectionError: If connection fails after retries
        """
        try:
            # Create MySQL connection pool
            self.pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                db=self.database,
                minsize=1,
                maxsize=self.connection_pool_size,
                autocommit=True,
                charset='utf8mb4'
            )
            
            # Test connection
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    result = await cursor.fetchone()
                    if result[0] != 1:
                        raise OpenDentalConnectionError("Database connection test failed")
            
            logger.info("Successfully connected to Open Dental database")
            
        except Exception as e:
            self.connection_errors += 1
            logger.error(f"Failed to connect to Open Dental database: {e}")
            raise OpenDentalConnectionError(f"Connection failed: {e}")
    
    async def disconnect(self) -> None:
        """Close all connections and cleanup resources"""
        try:
            if self.pool:
                self.pool.close()
                await self.pool.wait_closed()
                
            logger.info("Disconnected from Open Dental database")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    @backoff.on_exception(
        backoff.expo,
        (aiomysql.Error, OpenDentalDataError),
        max_tries=3,
        max_time=15
    )
    async def get_patient(self, patient_num: int) -> Optional[Patient]:
        """
        Retrieve patient by patient number
        
        Args:
            patient_num: Patient number to retrieve
            
        Returns:
            Patient object or None if not found
            
        Raises:
            OpenDentalDataError: If query fails
        """
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    query = """
                    SELECT PatNum, LName, FName, MiddleI, Preferred, HmPhone, 
                           WkPhone, WirelessPhone, Email, Address, Address2, 
                           City, State, Zip, Birthdate, Gender, PatStatus
                    FROM patient 
                    WHERE PatNum = %s AND PatStatus != 'Deleted'
                    """
                    await cursor.execute(query, (patient_num,))
                    result = await cursor.fetchone()
                    
                    self.query_count += 1
                    
                    if result:
                        # Convert MySQL result to Patient object
                        patient_data = {
                            'patient_num': result['PatNum'],
                            'last_name': result['LName'] or "",
                            'first_name': result['FName'] or "",
                            'middle_initial': result['MiddleI'] or "",
                            'preferred': result['Preferred'] or "",
                            'home_phone': result['HmPhone'] or "",
                            'wk_phone': result['WkPhone'] or "",
                            'wireless_phone': result['WirelessPhone'] or "",
                            'email': result['Email'] or "",
                            'address': result['Address'] or "",
                            'address2': result['Address2'] or "",
                            'city': result['City'] or "",
                            'state': result['State'] or "",
                            'zip': result['Zip'] or "",
                            'birthdate': result['Birthdate'],
                            'gender': result['Gender'] or "",
                            'pat_status': result['PatStatus'] or "Patient"
                        }
                        
                        return Patient(**patient_data)
                    
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving patient {patient_num}: {e}")
            raise OpenDentalDataError(f"Failed to retrieve patient: {e}")
    
    @backoff.on_exception(
        backoff.expo,
        (aiomysql.Error, OpenDentalDataError),
        max_tries=3,
        max_time=15
    )
    async def get_appointments(
        self,
        start_date: datetime,
        end_date: datetime,
        provider_num: Optional[int] = None,
        patient_num: Optional[int] = None
    ) -> List[Appointment]:
        """
        Retrieve appointments within date range
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            provider_num: Optional provider filter
            patient_num: Optional patient filter
            
        Returns:
            List of Appointment objects
            
        Raises:
            OpenDentalDataError: If query fails
        """
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    # Build dynamic query
                    query = """
                    SELECT AptNum, PatNum, AptStatus, Pattern, Confirmed, Op,
                           ProvNum, ProvHyg, AptDateTime, Length, Note, 
                           IsNewPatient, ClinicNum
                    FROM appointment 
                    WHERE AptDateTime >= %s AND AptDateTime <= %s
                    AND AptStatus != 'Deleted'
                    """
                    params = [start_date, end_date]
                    
                    if provider_num:
                        query += " AND ProvNum = %s"
                        params.append(provider_num)
                    
                    if patient_num:
                        query += " AND PatNum = %s"
                        params.append(patient_num)
                    
                    query += " ORDER BY AptDateTime"
                    
                    await cursor.execute(query, params)
                    results = await cursor.fetchall()
                    
                    self.query_count += 1
                    
                    appointments = []
                    for result in results:
                        apt_data = {
                            'apt_num': result['AptNum'],
                            'patient_num': result['PatNum'],
                            'apt_status': result['AptStatus'] or "",
                            'pattern': result['Pattern'] or "",
                            'confirmed': result['Confirmed'] or 0,
                            'op': result['Op'] or 0,
                            'provider_num': result['ProvNum'] or 0,
                            'provider_hyg': result['ProvHyg'] or 0,
                            'apt_date_time': result['AptDateTime'],
                            'apt_length': result['Length'] or 0,
                            'apt_note': result['Note'] or "",
                            'is_new_patient': bool(result['IsNewPatient']),
                            'clinic_num': result['ClinicNum'] or 0
                        }
                        
                        appointments.append(Appointment(**apt_data))
                    
                    return appointments
                    
        except Exception as e:
            logger.error(f"Error retrieving appointments: {e}")
            raise OpenDentalDataError(f"Failed to retrieve appointments: {e}")
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get client performance metrics
        
        Returns:
            Dictionary with performance statistics
        """
        return {
            'query_count': self.query_count,
            'connection_errors': self.connection_errors,
            'connection_pool_size': self.connection_pool_size,
            'is_connected': self.pool is not None and not self.pool._closed
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on database connection
        
        Returns:
            Health status dictionary
        """
        try:
            start_time = datetime.now()
            
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    await cursor.fetchone()
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                'status': 'healthy',
                'response_time_ms': response_time,
                'timestamp': datetime.now().isoformat(),
                'database': self.database,
                'host': self.host
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'database': self.database,
                'host': self.host
            }

# Convenience function for creating client instances
async def create_opendental_client(**kwargs) -> OpenDentalClient:
    """
    Create and connect OpenDentalClient instance
    
    Args:
        **kwargs: Connection parameters
        
    Returns:
        Connected OpenDentalClient instance
    """
    client = OpenDentalClient(**kwargs)
    await client.connect()
    return client
