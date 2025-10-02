# Git Hooks Documentation

This document explains the Git hooks used in the Dental Clinic AI project.

## Overview

Git hooks are scripts that run automatically at certain points in the Git workflow. We use them to enforce code quality, consistency, and prevent common mistakes.

## Installed Hooks

### 1. **pre-commit** Hook

Runs **before** a commit is created. Validates:

#### ✅ Checks Performed

1. **Python Syntax**
   - Validates all `.py` files have valid Python syntax
   - Prevents committing code with syntax errors

2. **Work Plan Sync**
   - Checks if modified agents are documented in work plan
   - Warns if agent changes are not reflected in `WORK_PLAN_V19.0_UNIFIED.md`

3. **Frontend-Backend Sync**
   - Warns if backend agent changes might affect frontend
   - Lists frontend files that reference agents

4. **Test Coverage**
   - Checks if new agents have corresponding test files
   - Warns if `test_<agent>.py` is missing

5. **Large File Detection**
   - Warns about files >1MB being committed
   - Suggests using Git LFS or external storage

6. **Secrets Detection**
   - Scans for potential secrets (passwords, API keys, tokens)
   - Warns if hardcoded secrets are found

7. **.env File Protection**
   - **Blocks** commits that include `.env` file
   - `.env` should never be committed (contains secrets)

#### 🚨 Example Output

```bash
$ git commit -m "feat(agents): Add CFO agent"

🔍 Running pre-commit checks...
ℹ️ Checking Python syntax...
✅ Python syntax is valid
ℹ️ Checking work plan sync...
⚠️  Warning: Agent 'cfo' is being modified but not found in WORK_PLAN_V19.0_UNIFIED.md

Consider updating the work plan to reflect this change.
✅ All pre-commit checks passed!

💡 Tip: To bypass these checks, use: git commit --no-verify
```

---

### 2. **commit-msg** Hook

Runs **after** commit message is written. Validates:

#### ✅ Checks Performed

1. **Conventional Commits Format**
   - Enforces format: `<type>(<scope>): <subject>`
   - Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`, `revert`
   
   **Examples:**
   ```
   ✅ feat(agents): Add CFO agent
   ✅ fix(telegram): Fix webhook parsing
   ✅ docs(adr): Add ADR-005
   ❌ Added CFO agent
   ❌ fix: bug
   ```

2. **Manus-Session-ID Presence**
   - Warns if `Manus-Session-ID:` is missing
   - Helps track which Manus session made the change
   
   **Example:**
   ```
   feat(agents): Add CFO agent
   
   Implements CFO agent with financial analysis capabilities.
   
   Manus-Session-ID: abc123xyz
   Human-Initiator: scubapro711
   ```

3. **ADR Requirement for Deletions**
   - **Blocks** commits that delete important files without ADR reference
   - Important files: agents, integrations, API endpoints, models
   
   **Example:**
   ```
   ❌ Deleting backend/app/agents/dana.py without ADR reference
   
   Steps:
   1. Create ADR: docs/adr/ADR-XXX-remove-dana.md
   2. Reference in commit: "See ADR-XXX for rationale."
   ```

4. **Subject Line Length**
   - Warns if subject >72 characters
   - Recommended: Keep subject concise

5. **Body Line Length**
   - Warns if body lines >80 characters
   - Recommended: Wrap long lines

#### 🚨 Example Output

```bash
$ git commit -m "Add CFO"

🔍 Validating commit message...
❌ Commit rejected: Commit message must follow Conventional Commits format:

<type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert

Examples:
- feat(agents): Add CFO agent
- fix(telegram): Fix webhook parsing
- docs(adr): Add ADR-005

Your message:
Add CFO
```

---

## Installation

### Automatic Installation

Run the installation script:

```bash
./scripts/install-hooks.sh
```

This will:
1. Copy hooks from `scripts/hooks/` to `.git/hooks/`
2. Make them executable
3. Activate them for your local repo

### Manual Installation

```bash
# Copy hooks
cp scripts/hooks/pre-commit .git/hooks/pre-commit
cp scripts/hooks/commit-msg .git/hooks/commit-msg

# Make executable
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/commit-msg
```

---

## Bypassing Hooks

**⚠️ Not recommended!** But sometimes necessary for quick fixes:

```bash
# Bypass all hooks
git commit --no-verify -m "fix: emergency fix"

# Or use alias
git commit -n -m "fix: emergency fix"
```

**When to bypass:**
- Emergency hotfixes
- WIP commits on feature branches
- Experimental changes

**When NOT to bypass:**
- Commits to `main` branch
- Production deployments
- Merging pull requests

---

## Uninstalling Hooks

```bash
# Remove hooks
rm .git/hooks/pre-commit
rm .git/hooks/commit-msg

# Or disable temporarily
chmod -x .git/hooks/pre-commit
chmod -x .git/hooks/commit-msg
```

---

## Troubleshooting

### Hook not running

**Problem:** Hooks don't execute when committing

**Solutions:**
1. Check if hooks are executable:
   ```bash
   ls -la .git/hooks/
   ```
   Should show: `-rwxr-xr-x` (executable)

2. Re-install hooks:
   ```bash
   ./scripts/install-hooks.sh
   ```

3. Check if hooks are in correct location:
   ```bash
   ls .git/hooks/pre-commit
   ls .git/hooks/commit-msg
   ```

### Hook fails with error

**Problem:** Hook script has errors

**Solutions:**
1. Check hook syntax:
   ```bash
   bash -n .git/hooks/pre-commit
   bash -n .git/hooks/commit-msg
   ```

2. Run hook manually to see full error:
   ```bash
   .git/hooks/pre-commit
   .git/hooks/commit-msg .git/COMMIT_EDITMSG
   ```

3. Check if required tools are installed:
   ```bash
   which python3
   which grep
   which git
   ```

### False positives

**Problem:** Hook incorrectly flags valid code

**Solutions:**
1. Review the warning/error message
2. Fix the issue if valid
3. Bypass with `--no-verify` if false positive
4. Update hook script if pattern is wrong

---

## Customization

### Adding New Checks

Edit hook scripts in `scripts/hooks/`:

```bash
# Edit pre-commit
nano scripts/hooks/pre-commit

# Edit commit-msg
nano scripts/hooks/commit-msg

# Re-install
./scripts/install-hooks.sh
```

### Disabling Specific Checks

Comment out sections in hook scripts:

```bash
# In scripts/hooks/pre-commit

# Check 5: Large file check (>1MB)
# LARGE_FILES=$(git diff --cached --name-only --diff-filter=ACM | while read file; do
#     ...
# done)
```

---

## Best Practices

### 1. **Always run hooks**
- Don't bypass unless absolutely necessary
- Hooks prevent common mistakes

### 2. **Keep hooks fast**
- Hooks should run in <5 seconds
- Slow hooks discourage use

### 3. **Make hooks helpful**
- Provide clear error messages
- Suggest fixes, not just errors

### 4. **Test hooks before committing**
```bash
# Test pre-commit
.git/hooks/pre-commit

# Test commit-msg
echo "test: message" > /tmp/test-msg
.git/hooks/commit-msg /tmp/test-msg
```

### 5. **Update hooks regularly**
- Keep hooks in sync with project needs
- Review and improve based on team feedback

---

## Integration with CI/CD

Hooks run **locally** only. For CI/CD:

1. **GitHub Actions** - Run same checks in CI:
   ```yaml
   - name: Check commit format
     run: |
       git log -1 --pretty=%B | grep -E "^(feat|fix|docs):"
   ```

2. **Pre-receive hooks** - Enforce on server:
   ```bash
   # .git/hooks/pre-receive (on GitHub/GitLab)
   # Reject pushes that don't meet standards
   ```

---

## Related Documentation

- **ADR System:** [docs/adr/README.md](./adr/README.md)
- **Framework:** [IMPROVED_FRAMEWORK_V2.md](../IMPROVED_FRAMEWORK_V2.md)
- **Work Plan:** [WORK_PLAN_V19.0_UNIFIED.md](../WORK_PLAN_V19.0_UNIFIED.md)
- **Conventional Commits:** https://www.conventionalcommits.org/

---

**Last Updated:** 2025-10-02  
**Maintainer:** scubapro711
