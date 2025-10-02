# Odoo 17 External API - Learning Notes

**Date:** 2025-10-02  
**Epic:** L - Deep Learning Phase  
**User Story:** L.2 - Master Odoo Integration  
**Source:** https://www.odoo.com/documentation/17.0/developer/reference/external_api.html

---

## Overview

Odoo's features and data are available from the outside via **XML-RPC** for external analysis or integration.

**Important:** Access to data via the external API is only available on **Custom** Odoo pricing plans (not available on One App Free or Standard plans).

---

## Connection & Authentication

### Configuration

For Odoo Online instances (<domain>.odoo.com):

```python
url = "https://mycompany.odoo.com"
db = "mycompany"
username = "admin"
password = "<password or API key>"
```

### API Keys (Recommended)

**New in version 14.0**

Odoo supports **API keys** which should be used instead of passwords for webservice operations.

**How to create an API key:**
1. Go to Preferences (or My Profile)
2. Open Account Security tab
3. Click "New API Key"
4. Input a clear description
5. Click "Generate Key"
6. **Copy and store the key carefully** (cannot be retrieved later)

**Usage:** Simply replace your password with the API key in scripts. The login remains the same.

**Security:** API keys provide the same access as passwords but cannot be used to log in via the interface.

### Authentication

Two endpoints:
1. **xmlrpc/2/common** - Meta-calls (no authentication required)
2. **xmlrpc/2/object** - Model methods (authentication required)

**Step 1: Check server version (optional)**

```python
import xmlrpc.client

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
version_info = common.version()
```

Returns:
```python
{
    "server_version": "17.0",
    "server_version_info": [17, 0, 0, "final", 0],
    "server_serie": "17.0",
    "protocol_version": 1,
}
```

**Step 2: Authenticate**

```python
uid = common.authenticate(db, username, password, {})
```

Returns: User ID (integer) used in all subsequent calls

---

## Calling Methods

Use `execute_kw` RPC function to call methods of Odoo models.

**Parameters:**
1. Database name (string)
2. User ID (integer)
3. Password or API key (string)
4. Model name (string)
5. Method name (string)
6. Positional parameters (array/list)
7. Keyword parameters (dict, optional)

**Example: Check access rights**

```python
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
models.execute_kw(
    db, uid, password,
    'res.partner', 'check_access_rights',
    ['read'],
    {'raise_exception': False}
)
```

Returns: `True` or `False`

---

## CRUD Operations

### 1. Search (List Records)

Search for records matching a domain filter.

```python
# Search for all companies
ids = models.execute_kw(
    db, uid, password,
    'res.partner', 'search',
    [[['is_company', '=', True]]]
)
```

Returns: List of IDs `[7, 18, 12, 14, ...]`

**Pagination:**

```python
ids = models.execute_kw(
    db, uid, password,
    'res.partner', 'search',
    [[['is_company', '=', True]]],
    {'offset': 10, 'limit': 5}
)
```

### 2. Count Records

```python
count = models.execute_kw(
    db, uid, password,
    'res.partner', 'search_count',
    [[['is_company', '=', True]]]
)
```

Returns: Integer count

### 3. Read Records

Read data for specific record IDs.

```python
# Read all fields
records = models.execute_kw(
    db, uid, password,
    'res.partner', 'read',
    [ids]
)

# Read specific fields only
records = models.execute_kw(
    db, uid, password,
    'res.partner', 'read',
    [ids],
    {'fields': ['name', 'email', 'phone']}
)
```

Returns: List of dictionaries with field values

**Example result:**
```python
[{
    "id": 7,
    "name": "Agrolait",
    "email": "contact@agrolait.com",
    "phone": "+32 2 290 34 90"
}]
```

### 4. Search and Read (Combined)

Combines search() and read() in one call.

```python
records = models.execute_kw(
    db, uid, password,
    'res.partner', 'search_read',
    [[['is_company', '=', True]]],
    {'fields': ['name', 'email'], 'limit': 5}
)
```

### 5. Create Records

```python
id = models.execute_kw(
    db, uid, password,
    'res.partner', 'create',
    [{
        'name': 'New Partner',
        'email': 'partner@example.com',
        'phone': '+1 234 567 8900'
    }]
)
```

Returns: ID of created record

### 6. Update Records

```python
models.execute_kw(
    db, uid, password,
    'res.partner', 'write',
    [[id], {
        'email': 'newemail@example.com'
    }]
)
```

Returns: `True` if successful

### 7. Delete Records

```python
models.execute_kw(
    db, uid, password,
    'res.partner', 'unlink',
    [[id]]
)
```

Returns: `True` if successful

---

## Search Domains

Domains are lists of criteria used to filter records.

**Basic format:** `[['field', 'operator', 'value']]`

**Operators:**
- `=` - equals
- `!=` - not equals
- `>` - greater than
- `>=` - greater than or equal
- `<` - less than
- `<=` - less than or equal
- `like` - pattern match (case-insensitive)
- `ilike` - pattern match (case-insensitive)
- `in` - value in list
- `not in` - value not in list

**Logical operators:**
- `&` - AND (default, prefix form)
- `|` - OR (prefix form)
- `!` - NOT (prefix form)

**Examples:**

```python
# Simple: is_company = True
[['is_company', '=', True]]

# AND (implicit): is_company = True AND country_id = 21
[['is_company', '=', True], ['country_id', '=', 21]]

# OR: is_company = True OR is_customer = True
['|', ['is_company', '=', True], ['is_customer', '=', True]]

# Complex: (is_company = True OR is_customer = True) AND country_id = 21
['&', '|', ['is_company', '=', True], ['is_customer', '=', True], ['country_id', '=', 21]]

# IN: country_id in [21, 22, 23]
[['country_id', 'in', [21, 22, 23]]]

# LIKE: name contains "dental"
[['name', 'ilike', 'dental']]
```

---

## Key Odoo Models for DentalAI

### 1. res.partner (Patients/Contacts)

**Key fields:**
- `name` - Full name
- `email` - Email address
- `phone` - Phone number
- `mobile` - Mobile number
- `street`, `city`, `zip`, `country_id` - Address
- `is_company` - Boolean (True for companies, False for individuals)
- `parent_id` - Parent company (for contacts)
- `comment` - Internal notes

### 2. calendar.event (Appointments)

**Key fields:**
- `name` - Appointment title
- `start` - Start datetime
- `stop` - End datetime
- `partner_ids` - Related partners (Many2many)
- `user_id` - Responsible user
- `description` - Appointment notes
- `location` - Location
- `allday` - Boolean (all-day event)

### 3. account.move (Invoices)

**Key fields:**
- `name` - Invoice number
- `partner_id` - Customer
- `invoice_date` - Invoice date
- `invoice_date_due` - Due date
- `amount_total` - Total amount
- `amount_residual` - Amount due
- `state` - Status (draft, posted, cancel)
- `payment_state` - Payment status (not_paid, in_payment, paid)
- `invoice_line_ids` - Invoice lines (One2many)

---

## Best Practices

### 1. Use API Keys
- Never hardcode passwords
- Use API keys for all external integrations
- Store keys securely (environment variables, secrets manager)

### 2. Optimize Queries
- Use `search_read` instead of `search` + `read`
- Specify only needed fields in `fields` parameter
- Use pagination for large result sets

### 3. Error Handling
- Wrap all API calls in try-except blocks
- Handle authentication failures
- Handle network errors
- Log all errors for debugging

### 4. Caching
- Cache frequently accessed data (e.g., country_id mappings)
- Invalidate cache when data changes
- Use TTL for cache entries

### 5. Rate Limiting
- Implement exponential backoff for retries
- Respect Odoo's rate limits
- Batch operations when possible

---

## Example: Complete Integration Pattern

```python
import xmlrpc.client
from typing import List, Dict, Optional

class OdooClient:
    def __init__(self, url: str, db: str, username: str, api_key: str):
        self.url = url
        self.db = db
        self.username = username
        self.api_key = api_key
        self.uid = None
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    def authenticate(self) -> int:
        """Authenticate and return user ID"""
        self.uid = self.common.authenticate(
            self.db, self.username, self.api_key, {}
        )
        return self.uid
    
    def search_read(
        self,
        model: str,
        domain: List,
        fields: List[str],
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict]:
        """Search and read records"""
        params = {'fields': fields, 'offset': offset}
        if limit:
            params['limit'] = limit
        
        return self.models.execute_kw(
            self.db, self.uid, self.api_key,
            model, 'search_read',
            [domain],
            params
        )
    
    def create(self, model: str, values: Dict) -> int:
        """Create a record"""
        return self.models.execute_kw(
            self.db, self.uid, self.api_key,
            model, 'create',
            [values]
        )
    
    def write(self, model: str, ids: List[int], values: Dict) -> bool:
        """Update records"""
        return self.models.execute_kw(
            self.db, self.uid, self.api_key,
            model, 'write',
            [ids, values]
        )
    
    def unlink(self, model: str, ids: List[int]) -> bool:
        """Delete records"""
        return self.models.execute_kw(
            self.db, self.uid, self.api_key,
            model, 'unlink',
            [ids]
        )

# Usage
client = OdooClient(
    url="https://mycompany.odoo.com",
    db="mycompany",
    username="admin",
    api_key="your_api_key_here"
)

client.authenticate()

# Search for patients
patients = client.search_read(
    model='res.partner',
    domain=[['is_company', '=', False]],
    fields=['name', 'email', 'phone'],
    limit=10
)

# Create appointment
appointment_id = client.create(
    model='calendar.event',
    values={
        'name': 'Dental Checkup',
        'start': '2025-10-05 10:00:00',
        'stop': '2025-10-05 11:00:00',
        'partner_ids': [(6, 0, [patient_id])]
    }
)
```

---

## Key Takeaways for DentalAI

1. **Use API keys** instead of passwords for security
2. **Authenticate once** and reuse uid for all calls
3. **Use search_read** for efficient queries
4. **Specify fields** to reduce data transfer
5. **Implement error handling** for all API calls
6. **Cache frequently accessed data** (countries, users, etc.)
7. **Use domains** for complex filtering
8. **Batch operations** when possible

---

**Status:** Odoo API basics learned ✅  
**Next:** Research specific Odoo models for dental clinic (calendar.event, res.partner, account.move)
