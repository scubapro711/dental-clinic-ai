"""
OdooRPC-Compatible Wrapper for MockOdoo

This wrapper provides an OdooRPC-like interface for MockOdoo,
making it easy to switch to real Odoo in the future.

Usage:
    from app.integrations.odoo_wrapper import get_odoo_client
    
    odoo = get_odoo_client()
    
    # Search patients
    patient_ids = odoo.env['res.partner'].search([('is_patient', '=', True)])
    
    # Read patient data
    patients = odoo.env['res.partner'].browse(patient_ids)
    
    # Create appointment
    odoo.env['dental.appointment'].create({
        'patient_id': 123,
        'date': '2025-10-10',
        'time': '10:00'
    })
"""

import os
from typing import List, Dict, Any, Optional, Union
from app.integrations.mock_odoo_realistic import RealisticMockOdooClient


class OdooModel:
    """
    Represents an Odoo model (like res.partner, dental.appointment).
    Provides OdooRPC-like methods: search, read, browse, create, write, unlink.
    """
    
    def __init__(self, model_name: str, client: 'OdooWrapper'):
        self.model_name = model_name
        self.client = client
        self._mock = client._mock
    
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
            patient_ids = odoo.env['res.partner'].search([('is_patient', '=', True)])
        """
        if self.model_name == 'res.partner':
            # Patient search
            results = []
            for field, operator, value in domain:
                if field == 'is_patient' and value:
                    results = [p['id'] for p in self._mock.patients]
                elif field == 'name' and operator in ['=', 'ilike', 'like']:
                    name_filter = value.lower() if isinstance(value, str) else str(value)
                    results = self._mock.search_patients(name=name_filter)
                elif field == 'phone':
                    results = self._mock.search_patients(phone=value)
            
            if limit:
                results = results[offset:offset+limit]
            return results
        
        elif self.model_name == 'dental.appointment':
            # Appointment search
            results = [a['id'] for a in self._mock.appointments]
            
            for field, operator, value in domain:
                if field == 'patient_id':
                    patient_id = value
                    results = [a['id'] for a in self._mock.appointments if a['patient_id'] == patient_id]
                elif field == 'date':
                    if operator == '=':
                        results = [a['id'] for a in self._mock.appointments if a['date'] == value]
                    elif operator == '>=':
                        results = [a['id'] for a in self._mock.appointments if a['date'] >= value]
                    elif operator == '<=':
                        results = [a['id'] for a in self._mock.appointments if a['date'] <= value]
                elif field == 'status':
                    results = [a['id'] for a in self._mock.appointments if a['status'] == value]
            
            if limit:
                results = results[offset:offset+limit]
            return results
        
        elif self.model_name == 'account.move':
            # Invoice search
            results = [i['id'] for i in self._mock.invoices]
            
            for field, operator, value in domain:
                if field == 'partner_id':
                    results = [i['id'] for i in self._mock.invoices if i['patient_id'] == value]
                elif field == 'state':
                    results = [i['id'] for i in self._mock.invoices if i['status'] == value]
            
            if limit:
                results = results[offset:offset+limit]
            return results
        
        return []
    
    def search_count(self, domain: List[tuple]) -> int:
        """
        Count records matching the domain.
        
        Args:
            domain: List of tuples
        
        Returns:
            Number of matching records
        """
        return len(self.search(domain))
    
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
        
        results = []
        
        if self.model_name == 'res.partner':
            for patient_id in ids:
                patient = self._mock.get_patient(patient_id)
                if patient:
                    # Always include 'id' field
                    if fields and 'id' not in fields:
                        fields = ['id'] + fields
                    if fields:
                        patient = {k: v for k, v in patient.items() if k in fields}
                    results.append(patient)
        
        elif self.model_name == 'dental.appointment':
            for appt_id in ids:
                appt = self._mock.get_appointment(appt_id)
                if appt:
                    # Always include 'id' field
                    if fields and 'id' not in fields:
                        fields = ['id'] + fields
                    if fields:
                        appt = {k: v for k, v in appt.items() if k in fields}
                    results.append(appt)
        
        elif self.model_name == 'account.move':
            for inv_id in ids:
                inv = self._mock.get_invoice(inv_id)
                if inv:
                    # Always include 'id' field
                    if fields and 'id' not in fields:
                        fields = ['id'] + fields
                    if fields:
                        inv = {k: v for k, v in inv.items() if k in fields}
                    results.append(inv)
        
        return results
    
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
            appt_id = odoo.env['dental.appointment'].create({
                'patient_id': 123,
                'date': '2025-10-10',
                'time': '10:00'
            })
        """
        if self.model_name == 'res.partner':
            return self._mock.create_patient(values)
        
        elif self.model_name == 'dental.appointment':
            return self._mock.create_appointment(
                patient_id=values['patient_id'],
                date=values['date'],
                time=values.get('time', '09:00'),
                treatment_type=values.get('treatment_type', 'Checkup'),
                duration_minutes=values.get('duration_minutes', 60)
            )
        
        elif self.model_name == 'account.move':
            return self._mock.create_invoice(values)
        
        return 0
    
    def write(self, ids: Union[int, List[int]], values: Dict[str, Any]) -> bool:
        """
        Update existing records.
        
        Args:
            ids: Single ID or list of IDs
            values: Dictionary of field values to update
        
        Returns:
            True if successful
        
        Example:
            odoo.env['dental.appointment'].write([123], {'status': 'confirmed'})
        """
        if isinstance(ids, int):
            ids = [ids]
        
        if self.model_name == 'res.partner':
            for patient_id in ids:
                self._mock.update_patient(patient_id, values)
            return True
        
        elif self.model_name == 'dental.appointment':
            for appt_id in ids:
                self._mock.update_appointment(appt_id, values)
            return True
        
        elif self.model_name == 'account.move':
            for inv_id in ids:
                self._mock.update_invoice(inv_id, values)
            return True
        
        return False
    
    def unlink(self, ids: Union[int, List[int]]) -> bool:
        """
        Delete records.
        
        Args:
            ids: Single ID or list of IDs
        
        Returns:
            True if successful
        
        Example:
            odoo.env['dental.appointment'].unlink([123])
        """
        if isinstance(ids, int):
            ids = [ids]
        
        if self.model_name == 'dental.appointment':
            for appt_id in ids:
                self._mock.cancel_appointment(appt_id)
            return True
        
        return False


class RecordSet:
    """
    Represents a set of Odoo records.
    Allows iteration and attribute access.
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
    
    def __init__(self, client: 'OdooWrapper'):
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
    OdooRPC-compatible wrapper for MockOdoo.
    
    Provides the same interface as OdooRPC:
    - odoo.env['model.name'].search(domain)
    - odoo.env['model.name'].read(ids, fields)
    - odoo.env['model.name'].browse(ids)
    - odoo.env['model.name'].create(values)
    - odoo.env['model.name'].write(ids, values)
    - odoo.env['model.name'].unlink(ids)
    """
    
    def __init__(self, use_mock: bool = True):
        """
        Initialize Odoo client.
        
        Args:
            use_mock: If True, use MockOdoo. If False, use real Odoo (future).
        """
        self.use_mock = use_mock
        
        if use_mock:
            self._mock = RealisticMockOdooClient()
            self.env = OdooEnvironment(self)
        else:
            # TODO: Initialize real OdooRPC client
            raise NotImplementedError("Real Odoo not implemented yet. Use use_mock=True.")
    
    def login(self, database: str, username: str, password: str) -> bool:
        """
        Login to Odoo.
        
        Args:
            database: Database name
            username: Username
            password: Password
        
        Returns:
            True if successful
        """
        if self.use_mock:
            return self._mock.authenticate()
        else:
            # TODO: Real Odoo login
            raise NotImplementedError("Real Odoo not implemented yet.")


def get_odoo_client() -> OdooWrapper:
    """
    Get Odoo client (Mock or Real based on environment variable).
    
    Environment Variables:
        USE_MOCK_ODOO: If "true", use MockOdoo. If "false", use real Odoo.
    
    Returns:
        OdooWrapper instance
    
    Example:
        odoo = get_odoo_client()
        patient_ids = odoo.env['res.partner'].search([('is_patient', '=', True)])
    """
    use_mock = os.getenv('USE_MOCK_ODOO', 'true').lower() == 'true'
    return OdooWrapper(use_mock=use_mock)
