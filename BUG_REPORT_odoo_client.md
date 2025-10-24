# Bug Report: odoo_client.py

**File:** `app/integrations/odoo_client.py`
**Date:** 2025-01-24
**Reviewer:** AI Agent
**Status:** Identified, Not Fixed

---

## 🔴 Critical Bugs

### Bug #1: Global Socket Timeout Modification

**Location:** Line 117
**Severity:** Critical
**Type:** Resource Leak / Side Effect

**Code:**
```python
socket.setdefaulttimeout(10.0)
```

**Problem:**
- Sets global socket timeout for the entire Python process
- Affects ALL socket connections (HTTP, DB, etc.), not just Odoo
- If multiple `OdooClient` instances are created, each one modifies the global timeout
- Race conditions in multi-threaded environments

**Impact:**
- Unexpected timeouts in unrelated parts of the system
- HTTP requests to other services may timeout prematurely
- Database connections may be affected
- Production stability issues

**Root Cause:**
- Using global `socket.setdefaulttimeout()` instead of per-connection timeout

**Reproduction:**
```python
import socket
import requests

client1 = OdooClient()  # Sets timeout to 10s
print(socket.getdefaulttimeout())  # 10.0

# Now ALL requests have 10s timeout!
requests.get("https://slow-api.com")  # Will timeout after 10s
```

**Proposed Fix:**
Use per-connection timeout instead of global:
```python
import xmlrpc.client
from xmlrpc.client import SafeTransport

class TimeoutTransport(SafeTransport):
    def __init__(self, timeout=10.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout
    
    def make_connection(self, host):
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn

# In __init__:
transport = TimeoutTransport(timeout=10.0)
self.common = xmlrpc.client.ServerProxy(
    f"{self.url}/xmlrpc/2/common",
    allow_none=True,
    transport=transport
)
```

**Test Plan:**
1. Create test that checks global socket timeout before/after OdooClient creation
2. Verify timeout doesn't affect other connections
3. Verify Odoo connections still timeout correctly

---

### Bug #2: Password Stored in Plain Text

**Location:** Lines 99-100, 196
**Severity:** Critical
**Type:** Security Vulnerability

**Code:**
```python
self.password = settings.ODOO_PASSWORD  # Line 100
# Used in every request:
result = self.models.execute_kw(
    self.db, self.uid, self.password,  # Line 196
    model, method, args, kwargs
)
```

**Problem:**
- Password stored in plain text in memory
- Password sent with EVERY request to Odoo
- If logging is enabled for requests, password appears in logs
- Memory dumps will contain password

**Impact:**
- **HIPAA Violation** - credentials exposure
- **Security Risk** - password in logs/memory dumps
- **Compliance Issue** - PCI-DSS, SOC 2

**Root Cause:**
- Odoo XML-RPC API requires password in every request
- No session token mechanism

**Reproduction:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

client = OdooClient()
client.search('res.partner', [])  # Password logged in DEBUG mode
```

**Proposed Fix:**
1. **Short-term:** Ensure password is never logged
   ```python
   # Add to logger configuration
   logging.getLogger('xmlrpc').setLevel(logging.WARNING)
   ```

2. **Long-term:** Use Odoo's session-based authentication (if available)
   ```python
   # Use session token instead of password
   self.session_token = self._get_session_token()
   ```

**Test Plan:**
1. Enable DEBUG logging
2. Make Odoo requests
3. Verify password doesn't appear in logs
4. Check memory dumps don't contain password

---

### Bug #3: SQL Injection via Domain Parameter

**Location:** Lines 222-258 (search method)
**Severity:** Critical
**Type:** Security Vulnerability

**Code:**
```python
def search(
    self,
    model: str,
    domain: List = None,  # No validation!
    ...
) -> List[int]:
    if domain is None:
        domain = []
    
    return self._execute(model, 'search', [domain], kwargs)
```

**Problem:**
- `domain` parameter passed directly to Odoo without validation
- If domain is built from user input, SQL injection is possible
- Example: `domain = [('name', '=', user_input)]` where `user_input` contains malicious SQL

**Impact:**
- **SQL Injection** - attacker can read/modify database
- **Data Breach** - access to patient data
- **HIPAA Violation** - unauthorized data access

**Root Cause:**
- No input validation on domain parameter
- Trust in caller to provide safe domain

**Reproduction:**
```python
# Malicious user input
user_input = "'; DROP TABLE patient; --"

# If code builds domain like this:
domain = [('name', '=', user_input)]
client.search('res.partner', domain)  # SQL injection!
```

**Proposed Fix:**
1. **Validate domain structure:**
   ```python
   def _validate_domain(self, domain: List) -> bool:
       """Validate domain structure to prevent injection."""
       if not isinstance(domain, list):
           raise ValueError("Domain must be a list")
       
       for clause in domain:
           if not isinstance(clause, (tuple, list, str)):
               raise ValueError("Invalid domain clause")
           
           if isinstance(clause, (tuple, list)):
               if len(clause) != 3:
                   raise ValueError("Domain clause must have 3 elements")
               
               field, operator, value = clause
               if not isinstance(field, str):
                   raise ValueError("Field name must be string")
               if operator not in ['=', '!=', '>', '<', '>=', '<=', 'like', 'ilike', 'in', 'not in']:
                   raise ValueError(f"Invalid operator: {operator}")
       
       return True
   ```

2. **Sanitize user input before building domain:**
   ```python
   def sanitize_search_value(value: str) -> str:
       """Sanitize user input for search."""
       # Remove SQL special characters
       return value.replace("'", "").replace(";", "").replace("--", "")
   ```

**Test Plan:**
1. Test with malicious SQL in domain
2. Verify validation catches invalid domains
3. Test with legitimate domains still work

---

## 🟠 High Priority Bugs

### Bug #4: Memory Leak - No Default Limit

**Location:** Lines 260-311 (search_read method)
**Severity:** High
**Type:** Resource Exhaustion

**Code:**
```python
def search_read(
    self,
    model: str,
    domain: List = None,
    fields: List[str] = None,
    offset: int = 0,
    limit: int = None,  # No default!
    order: str = None
) -> List[Dict[str, Any]]:
```

**Problem:**
- No default limit on results
- If called without limit, can return millions of records
- Out of Memory (OOM) risk

**Impact:**
- **Server Crash** - OOM kills process
- **Performance Issues** - slow response times
- **DoS Vulnerability** - attacker can crash server

**Root Cause:**
- No default limit parameter

**Reproduction:**
```python
# This can return millions of records!
client.search_read('res.partner', domain=[])
```

**Proposed Fix:**
```python
def search_read(
    self,
    model: str,
    domain: List = None,
    fields: List[str] = None,
    offset: int = 0,
    limit: int = 1000,  # Default limit
    order: str = None
) -> List[Dict[str, Any]]:
    # Add warning if limit is too high
    if limit and limit > 10000:
        logger.warning(f"Large limit requested: {limit}. Consider pagination.")
```

**Test Plan:**
1. Call search_read without limit
2. Verify default limit is applied
3. Test with large datasets

---

### Bug #5: Race Condition in get_dental_chart

**Location:** Line 482
**Severity:** High
**Type:** Runtime Error

**Code:**
```python
return {
    'patient_id': patient_id,
    'teeth': charts,
    'last_updated': max([c.get('last_treatment_date') for c in charts if c.get('last_treatment_date')] or [None])
}
```

**Problem:**
- If all `last_treatment_date` are None, `max([])` raises ValueError
- If `charts` is empty, `max([None])` raises TypeError

**Impact:**
- **Crash** - unexpected exception
- **Data Loss** - transaction rollback
- **User Experience** - error page

**Root Cause:**
- No handling for empty list in max()

**Reproduction:**
```python
# Create patient with no treatment dates
charts = [
    {'id': 1, 'last_treatment_date': None},
    {'id': 2, 'last_treatment_date': None}
]
# This will crash:
max([c.get('last_treatment_date') for c in charts if c.get('last_treatment_date')] or [None])
```

**Proposed Fix:**
```python
dates = [c.get('last_treatment_date') for c in charts if c.get('last_treatment_date')]
return {
    'patient_id': patient_id,
    'teeth': charts,
    'last_updated': max(dates) if dates else None
}
```

**Test Plan:**
1. Test with patient with no treatment dates
2. Test with empty charts
3. Test with mixed dates and None values

---

### Bug #6: No Input Validation on IDs

**Location:** Lines 346-371, 394-415, 417-436
**Severity:** High
**Type:** Input Validation

**Code:**
```python
def read(self, model: str, ids: List[int], fields: List[str] = None):
    # No validation on ids!
    return self._execute(model, 'read', [ids], kwargs)

def write(self, model: str, record_id: int, values: Dict[str, Any]):
    # No validation on record_id!
    return self._execute(model, 'write', [[record_id], values], {})
```

**Problem:**
- No validation on `ids` or `record_id`
- Can pass empty list, negative numbers, zero
- Odoo will throw cryptic errors

**Impact:**
- **Poor UX** - unclear error messages
- **Debugging Difficulty** - hard to trace issues
- **Data Integrity** - unexpected behavior

**Root Cause:**
- Missing input validation

**Reproduction:**
```python
client.read('res.partner', [])  # Empty list
client.write('res.partner', 0, {'name': 'Test'})  # Invalid ID
client.write('res.partner', -1, {'name': 'Test'})  # Negative ID
```

**Proposed Fix:**
```python
def read(self, model: str, ids: List[int], fields: List[str] = None):
    if not ids:
        raise ValueError("ids list cannot be empty")
    if any(id <= 0 for id in ids):
        raise ValueError("All IDs must be positive integers")
    return self._execute(model, 'read', [ids], kwargs)

def write(self, model: str, record_id: int, values: Dict[str, Any]):
    if record_id <= 0:
        raise ValueError("record_id must be a positive integer")
    if not values:
        raise ValueError("values dictionary cannot be empty")
    return self._execute(model, 'write', [[record_id], values], {})
```

**Test Plan:**
1. Test with empty IDs list
2. Test with zero/negative IDs
3. Test with valid IDs

---

## 🟡 Medium Priority Issues

### Issue #7: No Connection Pooling

**Location:** Lines 113-133
**Severity:** Medium
**Type:** Performance

**Problem:**
- Each `OdooClient` instance creates new connections
- No connection pooling
- Resource waste

**Impact:**
- **Performance** - slow response times
- **Scalability** - limited concurrent users
- **Resource Usage** - many open connections

**Proposed Fix:**
Implement singleton pattern or connection pool

---

### Issue #8: Unsafe Error Parsing

**Location:** Lines 202-214
**Severity:** Medium
**Type:** Error Handling

**Problem:**
- Error detection via string matching
- Not robust if Odoo changes error format

**Impact:**
- **Incorrect Error Handling** - wrong exception type
- **Debugging Difficulty** - unclear errors

**Proposed Fix:**
Use Odoo error codes instead of string matching

---

## 📊 Summary

| Severity | Count | Must Fix Before |
|----------|-------|-----------------|
| Critical | 3 | Production |
| High | 3 | Beta |
| Medium | 2 | v1.0 |
| **Total** | **8** | - |

---

## 🎯 Action Plan

### Phase 1: Critical Bugs (This Week)
1. Fix Bug #1 (Socket Timeout) - 2 hours
2. Fix Bug #2 (Password Security) - 3 hours
3. Fix Bug #3 (SQL Injection) - 4 hours

### Phase 2: High Priority (Next Week)
4. Fix Bug #4 (Memory Leak) - 1 hour
5. Fix Bug #5 (Race Condition) - 1 hour
6. Fix Bug #6 (Input Validation) - 2 hours

### Phase 3: Medium Priority (Following Week)
7. Fix Issue #7 (Connection Pooling) - 4 hours
8. Fix Issue #8 (Error Parsing) - 2 hours

**Total Estimated Time:** 19 hours

---

**Next Steps:**
1. Create GitHub Issues for each bug
2. Write tests that reproduce each bug
3. Fix bugs one by one
4. Run regression tests after each fix
5. Document all changes

---

**Created:** 2025-01-24
**Last Updated:** 2025-01-24

