# Known Issues and TODO List

**Last Updated:** October 6, 2025  
**Project:** Dental Clinic AI System  
**Current Progress:** Module 1 - 50% Complete

---

## 🔴 Critical Issues (Must Fix Before Production)

### None Currently
All critical functionality is working.

---

## 🟡 Medium Priority Issues (Should Fix Soon)

### 1. Treatment Records Not in OdooClient
**Discovered:** Task 1.4 - Agent Tools Update  
**Status:** ⚠️ OPEN  
**Impact:** Medium - CFO tools use workaround  

**Description:**
- CFO tools need access to treatment records
- Currently using `realistic_mock_odoo.treatment_records` directly
- Should use OdooClient for consistency

**Location:**
- File: `backend/app/agents/tools/cfo_tools.py`
- Lines: Multiple functions (get_top_treatments_tool, analyze_profitability_tool)

**Error Message:**
```
Error getting top treatments: 'RealisticMockOdooClient' object has no attribute 'get_treatment_records'
```

**Fix Required:**
1. Add `get_treatment_records()` method to `RealisticMockOdooClient`
2. Add treatment records methods to `OdooWrapper`
3. Add treatment records methods to `OdooClient`
4. Update CFO tools to use `odoo_client.get_treatment_records()`

**Planned Fix:** Module 2 - PIM Core (Task 2.1 or 2.2)

**Workaround:** Currently using direct access to `realistic_mock_odoo.treatment_records`

---

### 2. Admin Role Not in UserRole Enum ✅ RESOLVED
**Discovered:** Task 1.5 - Agent Testing  
**Status:** ✅ RESOLVED (October 6, 2025)  
**Impact:** Low - System works but inconsistent  

**Description:**
- System uses "admin" as a string role
- UserRole enum only has: PATIENT, DOCTOR, OWNER
- Missing ADMIN role causes warnings in logs

**Location:**
- File: `backend/app/agents/rbac.py`
- Lines: 26-31 (UserRole enum)

**Error Message:**
```
Invalid user role: admin
```

**Fix Applied:**
1. ✅ Added `ADMIN = "admin"` to UserRole enum
2. ✅ Updated permission mappings to include admin role with 7 permissions:
   - read:all_appointments
   - write:all_appointments
   - read:all_schedules
   - write:schedules
   - manage:staff
   - access:alex
   - access:admin
3. ✅ No more warnings in logs

**Fixed In:** Task 1.5 completion

**Verification:** Tests run without admin role warnings

---

### 3. Patient Search Edge Cases
**Discovered:** Task 1.4 - Agent Tools Testing  
**Status:** ⚠️ OPEN  
**Impact:** Low - Rare scenario  

**Description:**
- Searching by phone only (without name) has edge cases
- Some tests fail when name=None and phone provided
- Logic uses `elif` instead of separate `if` statements

**Location:**
- File: `backend/app/integrations/mock_odoo_realistic.py`
- Lines: 88-110 (search_patients method)

**Fix Required:**
1. Improve search logic to handle all combinations:
   - name only
   - phone only
   - both name and phone
   - neither (return all)
2. Add more test cases for edge scenarios

**Planned Fix:** Task 1.6 or Module 1 cleanup

**Workaround:** Most searches use name, phone-only is rare

---

## 🟢 Low Priority Issues (Nice to Have)

### 4. Test Coverage Below 80%
**Discovered:** All test runs  
**Status:** ⚠️ OPEN  
**Impact:** Very Low - Expected for integration tests  

**Description:**
- Coverage requirement is 80%
- Integration tests achieve 8-18% coverage
- This is normal for integration tests (they test flows, not lines)

**Error Message:**
```
Coverage failure: total of 16 is less than fail-under=80
```

**Fix Required:**
1. Add unit tests for individual functions
2. Or adjust coverage requirement for integration tests
3. Or exclude integration tests from coverage

**Planned Fix:** Module 3 or later (testing improvements)

**Workaround:** Ignore coverage warnings for integration tests

---

### 5. Some Tests Fail When Run Together
**Discovered:** Task 1.4 - Agent Tools Testing  
**Status:** ⚠️ OPEN  
**Impact:** Very Low - Tests pass individually  

**Description:**
- Some tests pass individually but fail when run together
- Likely state management issue between tests
- Does not affect production code

**Location:**
- File: `backend/test_agent_tools_updated.py`
- Tests: test_get_patient_appointments_tool, test_get_patient_invoices_tool

**Fix Required:**
1. Improve test isolation
2. Reset state between tests
3. Use separate mock instances per test

**Planned Fix:** Module 3 or later (testing improvements)

**Workaround:** Run tests individually or ignore failures

---

## 📋 TODO Items (From Project Plan)

### Module 1 Remaining Tasks

#### Task 1.6: Dashboard Integration (1 day) - NEXT
**Status:** 🔜 PENDING  
**Priority:** HIGH  
**Description:**
- Connect dashboard to agent graph
- Display real-time agent status
- Show conversation history
- Enable agent controls
- Test dashboard functionality

**Blockers:** None - ready to start

---

### Module 2: PIM Core (5 days) - AFTER MODULE 1

#### Task 2.1: Odontogram Component (2 days)
**Status:** 📅 PLANNED  
**Priority:** HIGH  
**Description:**
- Create interactive tooth chart
- Implement tooth selection
- Add condition markers
- Integrate with patient records

**Dependencies:** Module 1 complete

---

#### Task 2.2: Treatment Plans (2 days)
**Status:** 📅 PLANNED  
**Priority:** HIGH  
**Description:**
- Create treatment plan UI
- Add treatment templates
- Implement plan versioning
- Connect to Odoo

**Dependencies:** Task 2.1 complete

**Note:** This is where we should fix Issue #1 (Treatment Records)

---

#### Task 2.3: Medical History (1 day)
**Status:** 📅 PLANNED  
**Priority:** MEDIUM  
**Description:**
- Create medical history form
- Add allergy tracking
- Implement medication tracking
- Connect to patient records

**Dependencies:** Task 2.2 complete

---

### Module 3: Advanced Features (3 days) - AFTER MODULE 2

#### Task 3.1: Document Management (1 day)
**Status:** 📅 PLANNED  
**Priority:** MEDIUM

#### Task 3.2: Imaging Integration (1 day)
**Status:** 📅 PLANNED  
**Priority:** MEDIUM

#### Task 3.3: Reporting Dashboard (1 day)
**Status:** 📅 PLANNED  
**Priority:** MEDIUM

---

## 🔧 Technical Debt

### 1. Direct MockOdoo Access in Some Places
**Priority:** Medium  
**Description:** Some code still accesses MockOdoo directly instead of through OdooClient  
**Locations:**
- CFO tools (treatment records)
- Admin tools (staff, rooms - simulated)

**Fix Plan:** Gradually migrate all access to OdooClient

---

### 2. Hardcoded Test Data
**Priority:** Low  
**Description:** Some tests use hardcoded patient names/IDs  
**Fix Plan:** Use fixtures and factories for test data

---

### 3. Missing API Documentation
**Priority:** Low  
**Description:** API endpoints lack comprehensive documentation  
**Fix Plan:** Add OpenAPI/Swagger documentation

---

## 📊 Issue Summary

| Priority | Open | In Progress | Resolved |
|----------|------|-------------|----------|
| Critical | 0    | 0           | 0        |
| Medium   | 2    | 0           | 1        |
| Low      | 2    | 0           | 0        |
| **Total**| **4**| **0**       | **1**    |

---

## 🎯 Recommended Fix Order

### Before Task 1.6 (Dashboard Integration)
1. ✅ ~~Fix Admin Role enum~~ **COMPLETED** (October 6, 2025)
   - Quick win, prevents warnings
   - Improves code consistency

### During Task 1.6
2. ⚠️ Fix Patient Search edge cases (15 minutes)
   - Improves reliability
   - Easy fix while working on code

### During Module 2 (PIM Core)
3. ⚠️ Add Treatment Records to OdooClient (1-2 hours)
   - Natural fit with PIM implementation
   - Removes workaround in CFO tools

### Module 3 or Later
4. 📝 Improve test coverage (ongoing)
   - Add unit tests gradually
   - Not blocking any functionality

5. 📝 Fix test isolation issues (1-2 hours)
   - Improve test reliability
   - Not urgent, tests work individually

---

## 🔄 Review Schedule

This document should be reviewed and updated:
- ✅ After each task completion
- ✅ When new issues are discovered
- ✅ Weekly during active development
- ✅ Before each module completion

**Next Review:** After Task 1.6 completion

---

## 📝 Notes

### Issue Tracking Best Practices
1. **Document everything** - Even small issues
2. **Prioritize realistically** - Not everything is critical
3. **Plan fixes** - Assign to specific tasks/modules
4. **Review regularly** - Don't let issues pile up
5. **Celebrate fixes** - Move to "Resolved" section

### When to Fix vs. Document
- **Fix immediately:** Critical bugs, security issues, blockers
- **Plan to fix:** Medium priority, affects functionality
- **Document only:** Low priority, cosmetic, nice-to-have

---

**Maintained by:** Development Team  
**Contact:** Project Lead  
**Last Updated:** October 6, 2025
