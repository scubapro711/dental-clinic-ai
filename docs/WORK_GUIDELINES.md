# DentaFlow SaaS - Work Guidelines
**Version:** 2.0  
**Last Updated:** October 23, 2025  
**Status:** Active

---

## 🎯 Core Principles

### The Iron Rules

These rules govern all development work on the DentaFlow SaaS platform:

#### 1. Professionalism Over Time Constraints ⏰
- Quality is paramount
- Take the time needed to do things right
- Never rush at the expense of correctness
- Thorough testing is mandatory

#### 2. Don't Break Existing Code 🚫
- Preserve all existing functionality
- No regressions allowed
- Backward compatibility is critical
- User experience must not degrade

#### 3. Always Check for Regressions ✅
- Run regression tests after every change
- Verify all existing tests still pass
- Check for side effects
- Document any breaking changes (if absolutely necessary)

#### 4. Never Remove Functionality 📉
- Don't delete features
- Don't reduce capabilities
- Don't remove user-facing options
- Only add or improve, never subtract

---

## 📂 Code vs Tests: Different Rules

### Source Code (`app/` directory)

**Strict Rules Apply:**

✅ **Allowed:**
- Fix bugs (with caution and testing)
- Add new features (without breaking existing ones)
- Improve performance (if no functionality changes)
- Refactor (if behavior remains identical)
- Add documentation

❌ **Not Allowed:**
- Break existing functionality
- Remove features
- Change APIs without backward compatibility
- Introduce regressions

**Process for Source Code Changes:**

1. **Identify the Issue**
   - What's the problem?
   - What's the impact?
   - Is it critical?

2. **Write Tests First**
   - Create tests that expose the bug
   - Verify tests fail before fix
   - Document expected behavior

3. **Implement the Fix**
   - Minimal changes
   - Clear, readable code
   - Follow existing patterns
   - Add comments if needed

4. **Run Regression Tests**
   - All existing tests must pass
   - New tests must pass
   - No new warnings/errors
   - Performance unchanged or better

5. **Document Changes**
   - What was changed
   - Why it was changed
   - Impact assessment
   - Migration notes (if needed)

### Test Code (`app/tests/` directory)

**Flexible Rules:**

✅ **Full Freedom:**
- Change tests as needed
- Fix broken tests
- Add new tests
- Remove obsolete tests
- Refactor test code
- Update fixtures
- Modify mocks
- Change test data

**No Restrictions:**
- Tests can be completely rewritten
- Fixtures can be redesigned
- Test structure can change
- No backward compatibility needed

**Best Practices:**
- Keep tests readable
- Maintain good coverage
- Document complex test scenarios
- Use descriptive test names

---

## 🔧 Bug Fixing Workflow

### Step 1: Bug Identification

**Questions to Ask:**
- What is the expected behavior?
- What is the actual behavior?
- Is this a regression or existing bug?
- What's the severity? (Critical/High/Medium/Low)
- Does it affect production?

**Documentation:**
```markdown
## Bug Report
- **Title:** Brief description
- **Severity:** Critical/High/Medium/Low
- **Component:** Which module/service
- **Expected:** What should happen
- **Actual:** What actually happens
- **Impact:** Who/what is affected
- **Reproduction:** Steps to reproduce
```

### Step 2: Test Creation

**Write Failing Test:**
```python
def test_bug_description():
    """Test that exposes the bug"""
    # Setup
    # Execute
    # Assert expected behavior
    # This should FAIL before the fix
```

**Run Test:**
```bash
pytest app/tests/path/to/test.py::test_bug_description -v
```

**Expected Result:** Test should FAIL (proving bug exists)

### Step 3: Bug Fix Implementation

**Guidelines:**
- Minimal changes only
- Fix root cause, not symptoms
- Maintain code style
- Add comments if logic is complex
- Consider edge cases

**Example:**
```python
# Before (buggy)
def process_payment(amount):
    return amount * 1.1  # Bug: wrong calculation

# After (fixed)
def process_payment(amount):
    """Process payment with 10% tax"""
    tax_rate = 0.10
    return amount * (1 + tax_rate)  # Fixed: correct calculation
```

### Step 4: Regression Testing

**Run Full Test Suite:**
```bash
# Run all tests
pytest app/tests/ -v --tb=short

# Check for regressions
pytest app/tests/critical/ -v
pytest app/tests/integration/ -v
```

**Checklist:**
- [ ] All existing tests pass
- [ ] New test passes
- [ ] No new warnings
- [ ] No performance degradation
- [ ] Coverage maintained or improved

### Step 5: Documentation

**Update Documentation:**
```markdown
## Changelog
### Fixed
- Bug in payment processing calculation
- Issue: Tax was calculated incorrectly
- Impact: Payments were 10% higher than expected
- Fix: Corrected tax calculation formula
- Tests: Added test_payment_tax_calculation
```

---

## 🧪 Testing Strategy

### Test Pyramid

```
        ┌─────────────┐
        │   E2E (5%)  │  ← Manual testing in staging
        ├─────────────┤
        │ Integration │  ← Workflow tests
        │   (15%)     │
        ├─────────────┤
        │    Unit     │  ← Service tests
        │   (80%)     │
        └─────────────┘
```

### Coverage Goals

| Component | Target | Priority |
|-----------|--------|----------|
| **Services** | 100% | Critical |
| **Models** | 90% | High |
| **API** | 60% | Medium |
| **RBAC** | 80% | High |
| **Agents** | 30% | Low |
| **Tools** | 40% | Low |
| **Integrations** | 20% | Low |
| **Overall** | 60% | Medium |

### When to Write Tests

**Always:**
- Before fixing bugs (TDD)
- For new features
- For critical business logic
- For security-sensitive code

**Sometimes:**
- For infrastructure code
- For agent tools
- For external integrations

**Rarely:**
- For test fixtures
- For mocks
- For development utilities

---

## 🚀 Development Workflow

### Daily Workflow

1. **Pull Latest Code**
   ```bash
   git pull origin main
   ```

2. **Run Tests**
   ```bash
   pytest app/tests/ -v
   ```

3. **Make Changes**
   - Follow Iron Rules
   - Write tests first
   - Implement changes
   - Document changes

4. **Test Changes**
   ```bash
   pytest app/tests/ -v --cov=app
   ```

5. **Commit**
   ```bash
   git add .
   git commit -m "Fix: Description of fix"
   ```

### Feature Development

1. **Plan Feature**
   - Write specification
   - Design API
   - Plan tests

2. **Write Tests**
   - Unit tests
   - Integration tests
   - Edge cases

3. **Implement Feature**
   - Follow existing patterns
   - Add documentation
   - Handle errors

4. **Test Feature**
   - All tests pass
   - Coverage adequate
   - Performance acceptable

5. **Document Feature**
   - API documentation
   - User documentation
   - Changelog entry

---

## 📊 Quality Metrics

### Code Quality

**Mandatory:**
- [ ] All tests pass
- [ ] No regressions
- [ ] Coverage maintained
- [ ] No new warnings

**Recommended:**
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Performance tested
- [ ] Security reviewed

### Test Quality

**Good Tests:**
- Clear, descriptive names
- Single responsibility
- Independent (no dependencies)
- Fast execution
- Deterministic (no flakiness)

**Bad Tests:**
- Vague names
- Multiple assertions
- Dependent on other tests
- Slow execution
- Flaky (random failures)

---

## 🔒 Security Guidelines

### When Fixing Security Bugs

**Critical Priority:**
1. Assess severity immediately
2. Write test that exposes vulnerability
3. Implement fix
4. Verify fix works
5. Check for similar vulnerabilities
6. Document security impact

**Never:**
- Commit security vulnerabilities
- Leave TODO comments for security
- Skip security tests
- Ignore security warnings

---

## 📝 Documentation Standards

### Code Comments

**When to Comment:**
- Complex algorithms
- Non-obvious logic
- Security-sensitive code
- Performance optimizations
- Bug fixes (reference issue)

**When Not to Comment:**
- Obvious code
- Self-explanatory functions
- Standard patterns

### Commit Messages

**Format:**
```
Type: Brief description (50 chars max)

Detailed explanation (if needed):
- What changed
- Why it changed
- Impact of change

Refs: #issue-number
```

**Types:**
- `Fix:` Bug fixes
- `Feat:` New features
- `Test:` Test changes
- `Docs:` Documentation
- `Refactor:` Code refactoring
- `Perf:` Performance improvements

---

## 🎯 Summary Checklist

### Before Every Commit

- [ ] All tests pass
- [ ] No regressions
- [ ] Coverage maintained
- [ ] Documentation updated
- [ ] Code reviewed (if possible)
- [ ] Commit message clear

### Before Every Release

- [ ] All tests pass
- [ ] Integration tests pass
- [ ] Performance tests pass
- [ ] Security review done
- [ ] Documentation complete
- [ ] Changelog updated

---

## 📚 References

- **Test Reports:** `/backend/TEST_COMPLETION_REPORT.md`
- **Coverage Report:** `/backend/COVERAGE_ANALYSIS_REPORT.md`
- **Phase 3 Plan:** `/docs/phases/PHASE_3_UNIFIED_WORKING_PLAN.md`
- **Session Reports:** `/backend/SESSION_SUMMARY_*.md`

---

**Remember:** Quality over speed. Correctness over convenience. Tests over trust.

---

**Version History:**
- v2.0 (2025-10-23): Added distinction between source code and test code rules
- v1.0 (2025-10-17): Initial version with Iron Rules

