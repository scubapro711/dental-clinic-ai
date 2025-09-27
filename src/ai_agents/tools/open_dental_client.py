"""
Open Dental API Client
Handles authentication and API calls to Open Dental system
"""

import os
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OpenDentalAPIClient:
    """Client for interacting with Open Dental API"""
    
    def __init__(self):
        self.api_key = os.getenv('OPEN_DENTAL_API_KEY', '1qvk4L2HHJs55Y3Z')
        self.base_url = os.getenv('OPEN_DENTAL_BASE_URL', 'https://api.opendental.com')
        self.timeout = int(os.getenv('OPEN_DENTAL_TIMEOUT', '30'))
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        logger.info(f"OpenDental API Client initialized with base URL: {self.base_url}")
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Open Dental API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.info(f"Making {method} request to: {url}")
            logger.debug(f"Headers: {self.headers}")
            logger.debug(f"Params: {params}")
            logger.debug(f"Data: {data}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=self.timeout
            )
            
            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Log response content for debugging
            if response.status_code == 404:
                logger.error(f"404 Error - Endpoint not found: {url}")
                logger.error(f"Response content: {response.text[:500]}")
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            else:
                return {}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            logger.error(f"URL: {url}")
            logger.error(f"Method: {method}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text[:500]}")
            raise
    
    def test_connection(self) -> Dict[str, Any]:
        """Test API connection and authentication"""
        try:
            # Try different endpoints to test connection
            test_endpoints = [
                'appointments',
                'patients', 
                'providers',
                'clinics'
            ]
            
            results = {}
            
            for endpoint in test_endpoints:
                try:
                    logger.info(f"Testing endpoint: {endpoint}")
                    result = self._make_request('GET', f'{endpoint}?Limit=1')
                    results[endpoint] = {
                        'status': 'success',
                        'data': result
                    }
                    logger.info(f"✅ {endpoint} endpoint working")
                    break  # If one works, connection is good
                    
                except Exception as e:
                    results[endpoint] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    logger.warning(f"❌ {endpoint} endpoint failed: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_appointments(self, limit: int = 10, **filters) -> List[Dict[str, Any]]:
        """Get appointments with optional filters"""
        params = {'Limit': limit}
        params.update(filters)
        
        result = self._make_request('GET', 'appointments', params=params)
        return result if isinstance(result, list) else [result]
    
    def get_appointment(self, apt_num: int) -> Dict[str, Any]:
        """Get single appointment by AptNum"""
        return self._make_request('GET', f'appointments/{apt_num}')
    
    def get_patients(self, limit: int = 10, **filters) -> List[Dict[str, Any]]:
        """Get patients with optional filters"""
        params = {'Limit': limit}
        params.update(filters)
        
        result = self._make_request('GET', 'patients', params=params)
        return result if isinstance(result, list) else [result]
    
    def get_providers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get providers/doctors"""
        params = {'Limit': limit}
        
        result = self._make_request('GET', 'providers', params=params)
        return result if isinstance(result, list) else [result]
    
    def get_available_slots(self, date: str, provider_num: Optional[int] = None, 
                           duration_minutes: int = 60) -> List[Dict[str, Any]]:
        """Get available appointment slots for a specific date"""
        params = {
            'date': date,
            'lengthMinutes': duration_minutes
        }
        
        if provider_num:
            params['ProvNum'] = provider_num
        
        result = self._make_request('GET', 'appointments/slots', params=params)
        return result if isinstance(result, list) else [result]
    
    def create_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new appointment"""
        return self._make_request('POST', 'appointments', data=appointment_data)
    
    def update_appointment(self, apt_num: int, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing appointment"""
        return self._make_request('PUT', f'appointments/{apt_num}', data=appointment_data)


# Test the client
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    client = OpenDentalAPIClient()
    
    print("🔍 Testing Open Dental API Connection...")
    results = client.test_connection()
    
    print("\n📊 Test Results:")
    for endpoint, result in results.items():
        status = result['status']
        if status == 'success':
            print(f"✅ {endpoint}: Connected successfully")
        else:
            print(f"❌ {endpoint}: {result['error']}")
    
    print(f"\n🔑 API Key: {client.api_key}")
    print(f"🌐 Base URL: {client.base_url}")
