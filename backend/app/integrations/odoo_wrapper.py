"""
Real Odoo XML-RPC Wrapper

This wrapper provides a clean interface to connect to Odoo 19 on AWS
using XML-RPC protocol.

Usage:
    from app.integrations.odoo_wrapper import get_odoo_client
    
    odoo = get_odoo_client()
    
    # Search patients
    patient_ids = odoo.env['res.partner'].search([('customer_rank', '>', 0)])
    
    # Read patient data
    patients = odoo.env['res.partner'].browse(patient_ids)
    
    # Create appointment
    odoo.env['calendar.event'].create({
        'name': 'Dental Checkup',
        'partner_ids': [(4, patient_id)],
        'start': '2025-10-10 10:00:00',
        'stop': '2025-10-10 11:00:00'
    })
"""

import os
import xmlrpc.client
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OdooXMLRPCClient:
    """
    Real Odoo XML-RPC client for connecting to Odoo 19 on AWS.
    """
    
    def __init__(self, url: str, db: str, username: str, password: str):
        """
        Initialize Odoo XML-RPC client.
        
        Args:
            url: Odoo URL (e.g., http://3.87.175.126:8069)
            db: Database name (e.g., dental_prod)
            username: Username (e.g., admin)
            password: Password
        """
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        
        # XML-RPC endpoints
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Authenticate
        self.uid = self.authenticate()
        
        if not self.uid:
            raise ConnectionError(f"Failed to authenticate to Odoo at {url}")
        
        print(f"✅ Connected to Odoo at {url} (User ID: {self.uid})")
    
    def authenticate(self) -> int:
        """
        Authenticate with Odoo.
        
        Returns:
            User ID if successful, None otherwise
        """
        try:
            uid = self.common.authenticate(self.db, self.username, self.password, {})
            return uid
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return None
    
    def execute_kw(self, model: str, method: str, args: list, kwargs: dict = None) -> Any:
        """
        Execute a method on an Odoo model.
        
        Args:
            model: Model name (e.g., 'res.partner')
            method: Method name (e.g., 'search', 'read', 'create')
            args: Positional arguments
            kwargs: Keyword arguments
        
        Returns:
            Method result
        """
        if kwargs is None:
            kwargs = {}
        
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, args, kwargs
            )
        except Exception as e:
            print(f"❌ Error executing {model}.{method}: {e}")
            raise


class OdooModel:
    """
    Represents an Odoo model (like res.partner, calendar.event).
    Provides OdooRPC-like methods: search, read, browse, create, write, unlink.
    """
    
    def __init__(self, model_name: str, client: OdooXMLRPCClient):
        self.model_name = model_name
        self.client = client
    
    def search(self, domain: List[tuple], limit: Optional[int] = None, offset: int = 0) -> List[int]:
        """
        Search for records matching the domain.
        
        Args:
            domain: List of tuples like [('name', '=', 'John'), ('age', '>', 18)]
            limit: Maximum number of records to return
            offset: Number of records to skip
        
        Returns:
            List of record IDs
        
        Example:
            patient_ids = odoo.env['res.partner'].search([('customer_rank', '>', 0)], limit=10)
        """
        kwargs = {'offset': offset}
        if limit:
            kwargs['limit'] = limit
        
        return self.client.execute_kw(self.model_name, 'search', [domain], kwargs)
    
    def search_count(self, domain: List[tuple]) -> int:
        """
        Count records matching the domain.
        
        Args:
            domain: List of tuples
        
        Returns:
            Number of matching records
        """
        return self.client.execute_kw(self.model_name, 'search_count', [domain])
    
    def read(self, ids: Union[int, List[int]], fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Read records by IDs.
        
        Args:
            ids: Single ID or list of IDs
            fields: List of field names to read (None = all fields)
        
        Returns:
            List of dictionaries with record data
        
        Example:
            patients = odoo.env['res.partner'].read([1, 2, 3], ['name', 'email'])
        """
        if isinstance(ids, int):
            ids = [ids]
        
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        
        return self.client.execute_kw(self.model_name, 'read', [ids], kwargs)
    
    def browse(self, ids: Union[int, List[int]]) -> 'RecordSet':
        """
        Browse records by IDs (returns RecordSet).
        
        Args:
            ids: Single ID or list of IDs
        
        Returns:
            RecordSet object
        
        Example:
            patients = odoo.env['res.partner'].browse([1, 2, 3])
            for patient in patients:
                print(patient.name, patient.email)
        """
        if isinstance(ids, int):
            ids = [ids]
        
        records = self.read(ids)
        return RecordSet(records, self.model_name, self)
    
    def create(self, values: Dict[str, Any]) -> int:
        """
        Create a new record.
        
        Args:
            values: Dictionary of field values
        
        Returns:
            ID of created record
        
        Example:
            appt_id = odoo.env['calendar.event'].create({
                'name': 'Dental Checkup',
                'start': '2025-10-10 10:00:00'
            })
        """
        return self.client.execute_kw(self.model_name, 'create', [values])
    
    def write(self, ids: Union[int, List[int]], values: Dict[str, Any]) -> bool:
        """
        Update records.
        
        Args:
            ids: Single ID or list of IDs
            values: Dictionary of field values to update
        
        Returns:
            True if successful
        
        Example:
            odoo.env['res.partner'].write([1, 2], {'phone': '123-456-7890'})
        """
        if isinstance(ids, int):
            ids = [ids]
        
        return self.client.execute_kw(self.model_name, 'write', [ids, values])
    
    def unlink(self, ids: Union[int, List[int]]) -> bool:
        """
        Delete records.
        
        Args:
            ids: Single ID or list of IDs
        
        Returns:
            True if successful
        
        Example:
            odoo.env['calendar.event'].unlink([123, 456])
        """
        if isinstance(ids, int):
            ids = [ids]
        
        return self.client.execute_kw(self.model_name, 'unlink', [ids])
    
    def search_read(self, domain: List[tuple], fields: Optional[List[str]] = None, 
                    limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Search and read in one call (more efficient).
        
        Args:
            domain: Search domain
            fields: Fields to read
            limit: Maximum records
            offset: Skip records
        
        Returns:
            List of record dictionaries
        
        Example:
            patients = odoo.env['res.partner'].search_read(
                [('customer_rank', '>', 0)], 
                ['name', 'email'], 
                limit=10
            )
        """
        kwargs = {'offset': offset}
        if limit:
            kwargs['limit'] = limit
        if fields:
            kwargs['fields'] = fields
        
        return self.client.execute_kw(self.model_name, 'search_read', [domain], kwargs)


class RecordSet:
    """
    Represents a set of Odoo records.
    Allows iteration and indexing.
    """
    
    def __init__(self, records: List[Dict[str, Any]], model_name: str, model: OdooModel):
        self.records = records
        self.model_name = model_name
        self.model = model
        self._index = 0
    
    def __iter__(self):
        self._index = 0
        return self
    
    def __next__(self):
        if self._index < len(self.records):
            record = Record(self.records[self._index], self.model_name, self.model)
            self._index += 1
            return record
        else:
            raise StopIteration
    
    def __len__(self):
        return len(self.records)
    
    def __getitem__(self, index):
        return Record(self.records[index], self.model_name, self.model)


class Record:
    """
    Represents a single Odoo record.
    Allows attribute access to fields.
    """
    
    def __init__(self, data: Dict[str, Any], model_name: str, model: OdooModel):
        self._data = data
        self.model_name = model_name
        self.model = model
    
    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        return self._data.get(name)
    
    def __getitem__(self, key):
        return self._data.get(key)
    
    def write(self, values: Dict[str, Any]) -> bool:
        """Update this record."""
        return self.model.write(self._data['id'], values)
    
    def unlink(self) -> bool:
        """Delete this record."""
        return self.model.unlink(self._data['id'])


class OdooEnvironment:
    """
    Represents the Odoo environment (odoo.env).
    Provides access to models.
    """
    
    def __init__(self, client: OdooXMLRPCClient):
        self.client = client
    
    def __getitem__(self, model_name: str) -> OdooModel:
        """
        Get a model by name.
        
        Example:
            patients_model = odoo.env['res.partner']
        """
        return OdooModel(model_name, self.client)


class OdooWrapper:
    """
    Wrapper for Odoo XML-RPC client.
    
    Provides the same interface as OdooRPC:
    - odoo.env['model.name'].search(domain)
    - odoo.env['model.name'].read(ids, fields)
    - odoo.env['model.name'].browse(ids)
    - odoo.env['model.name'].create(values)
    - odoo.env['model.name'].write(ids, values)
    - odoo.env['model.name'].unlink(ids)
    """
    
    def __init__(self, url: str, db: str, username: str, password: str):
        """
        Initialize Odoo wrapper.
        
        Args:
            url: Odoo URL
            db: Database name
            username: Username
            password: Password
        """
        self.client = OdooXMLRPCClient(url, db, username, password)
        self.env = OdooEnvironment(self.client)


# Singleton instance
_odoo_client = None


def get_odoo_client() -> OdooWrapper:
    """
    Get Odoo client (singleton).
    
    Returns:
        OdooWrapper instance
    
    Example:
        odoo = get_odoo_client()
        patient_ids = odoo.env['res.partner'].search([('customer_rank', '>', 0)])
    """
    global _odoo_client
    
    if _odoo_client is None:
        # Get credentials from environment
        url = os.getenv('ODOO_URL', 'http://3.87.175.126:8069')
        db = os.getenv('ODOO_DB', 'dental_prod')
        username = os.getenv('ODOO_USERNAME', 'admin')
        password = os.getenv('ODOO_PASSWORD', 'Goline055#')
        
        _odoo_client = OdooWrapper(url, db, username, password)
    
    return _odoo_client
