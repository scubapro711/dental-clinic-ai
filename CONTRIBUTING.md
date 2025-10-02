# Contributing to DentalAI

Thank you for your interest in contributing to DentalAI! This document provides guidelines for development.

---

## 📋 Table of Contents

1. [Development Philosophy](#development-philosophy)
2. [Getting Started](#getting-started)
3. [Code Style Guidelines](#code-style-guidelines)
4. [Git Workflow](#git-workflow)
5. [Testing Requirements](#testing-requirements)
6. [Pull Request Process](#pull-request-process)
7. [Repository Hygiene](#repository-hygiene)

---

## 🎯 Development Philosophy

### Core Principles

**1. Follow the Work Plan**
- **NEVER deviate from [WORK_PLAN_V14.0.md](./WORK_PLAN_V14.0.md)** without explicit approval
- If deviation seems necessary, STOP and propose updating the Work Plan first
- Every feature must have a corresponding User Story and Tasks

**2. Context Refresh**
- At the start of each User Story, refresh context by reading:
  - Master Prompt (Part I of Work Plan)
  - Relevant Architectural Pillar (Part II of Work Plan)
  - Definition of Ready (DoR) checklist
- Confirm all dependencies are met before starting

**3. Best Code Practices (Mandatory)**
- Follow language/framework best practices religiously
- Write clean, readable, maintainable code
- Prefer composition over inheritance
- Keep functions small and focused (single responsibility principle)
- Use meaningful variable/function names
- Avoid premature optimization
- Document complex logic with comments

**4. MVP Focus**
- Every feature must contribute to a **working, deployable MVP on AWS**
- Prioritize functionality over perfection
- Avoid scope creep (stick to acceptance criteria)
- Ensure integration with other MVP components

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 22+
- Docker & Docker Compose
- Git
- Pre-commit hooks (installed automatically)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/scubapro711/dental-clinic-ai.git
cd dental-clinic-ai

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Start development environment
docker-compose up
```

---

## 🎨 Code Style Guidelines

### Python (Backend)

**Style Guide:** PEP 8 + Black

```python
# Good
def calculate_appointment_duration(
    start_time: datetime,
    end_time: datetime
) -> timedelta:
    """Calculate the duration of an appointment.
    
    Args:
        start_time: Appointment start time
        end_time: Appointment end time
        
    Returns:
        Duration as timedelta
        
    Raises:
        ValueError: If end_time is before start_time
    """
    if end_time < start_time:
        raise ValueError("End time must be after start time")
    return end_time - start_time

# Bad
def calc_dur(s, e):
    return e - s  # No validation, no types, no docs
```

**Key Rules:**
- Use type hints for all function parameters and return values
- Write docstrings for all public functions (Google style)
- Maximum line length: 88 characters (Black default)
- Use f-strings for string formatting
- Use Pydantic models for data validation
- Prefer explicit over implicit (e.g., `is not None` over `if x:`)

**Imports:**
```python
# Standard library
import os
from datetime import datetime, timedelta

# Third-party
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# Local
from app.models.appointment import Appointment
from app.services.odoo import OdooClient
```

### TypeScript (Frontend)

**Style Guide:** Airbnb + Prettier

```typescript
// Good
interface AppointmentProps {
  id: string;
  patientName: string;
  startTime: Date;
  onCancel: (id: string) => void;
}

export function AppointmentCard({
  id,
  patientName,
  startTime,
  onCancel,
}: AppointmentProps): JSX.Element {
  const formattedTime = startTime.toLocaleString('he-IL');
  
  return (
    <div className="appointment-card">
      <h3>{patientName}</h3>
      <p>{formattedTime}</p>
      <button onClick={() => onCancel(id)}>Cancel</button>
    </div>
  );
}

// Bad
function Card(props) {
  return <div>{props.name}</div>;  // No types, no formatting
}
```

**Key Rules:**
- Use TypeScript strict mode
- Define interfaces for all props
- Use functional components with hooks (no class components)
- Use const for all variables unless reassignment is needed
- Prefer named exports over default exports
- Use Tailwind CSS classes (no inline styles)

---

## 🌿 Git Workflow

### Branch Naming

```
feature/epic-0-user-story-1-task-2-description
bugfix/issue-123-fix-authentication
hotfix/critical-security-patch
```

**Format:** `<type>/<epic>-<user-story>-<task>-<short-description>`

**Types:**
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical production fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test additions/updates

### Commit Messages

**Format:** Conventional Commits

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Example:**
```
feat(auth): add MFA support with TOTP

- Implement TOTP generation and verification
- Add MFA setup flow in user settings
- Update authentication middleware to check MFA

Closes #42
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting (no code change)
- `refactor` - Code refactoring
- `test` - Adding tests
- `chore` - Maintenance

### Workflow

1. **Create branch from `main`:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/epic-0-user-story-1-task-2-setup-github
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat(setup): initialize GitHub repository structure"
   ```

3. **Push and create PR:**
   ```bash
   git push origin feature/epic-0-user-story-1-task-2-setup-github
   # Create PR on GitHub
   ```

4. **After PR approval, merge and delete branch:**
   ```bash
   git checkout main
   git pull origin main
   git branch -d feature/epic-0-user-story-1-task-2-setup-github
   ```

---

## 🧪 Testing Requirements

### Testing Philosophy

**"If it's not tested, it's broken."**

- Write tests BEFORE or ALONGSIDE code (TDD encouraged)
- Every feature must have tests (unit, integration, E2E)
- Frontend tests are **especially critical** (user-facing)
- Testing is YOUR responsibility - do not skip or defer

### Backend Testing

**Framework:** pytest

```python
# tests/test_appointment_service.py
import pytest
from datetime import datetime, timedelta
from app.services.appointment import AppointmentService

def test_create_appointment_success(db_session):
    """Test successful appointment creation."""
    service = AppointmentService(db_session)
    appointment = service.create_appointment(
        patient_id=1,
        dentist_id=2,
        start_time=datetime.now() + timedelta(days=1),
        duration=timedelta(hours=1)
    )
    assert appointment.id is not None
    assert appointment.patient_id == 1

def test_create_appointment_conflict(db_session):
    """Test appointment creation with time conflict."""
    service = AppointmentService(db_session)
    # Create first appointment
    service.create_appointment(...)
    # Try to create conflicting appointment
    with pytest.raises(AppointmentConflictError):
        service.create_appointment(...)
```

**Coverage Requirements:**
- Minimum 80% code coverage
- 100% coverage for critical paths (auth, billing, medical data)

**Run tests:**
```bash
cd backend
pytest tests/ --cov=app --cov-report=html
```

### Frontend Testing

**Frameworks:** Vitest + React Testing Library + Playwright

```typescript
// tests/AppointmentCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { AppointmentCard } from '@/components/AppointmentCard';

describe('AppointmentCard', () => {
  it('renders appointment details', () => {
    render(
      <AppointmentCard
        id="1"
        patientName="John Doe"
        startTime={new Date('2025-10-03T10:00:00')}
        onCancel={jest.fn()}
      />
    );
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('calls onCancel when cancel button clicked', () => {
    const onCancel = jest.fn();
    render(
      <AppointmentCard
        id="1"
        patientName="John Doe"
        startTime={new Date()}
        onCancel={onCancel}
      />
    );
    fireEvent.click(screen.getByText('Cancel'));
    expect(onCancel).toHaveBeenCalledWith('1');
  });
});
```

**Frontend Testing Requirements:**
- **All user interactions** (clicks, inputs, navigation)
- **All edge cases** (empty states, error states, loading states)
- **Accessibility** (keyboard navigation, screen readers)
- **Responsive design** (mobile, tablet, desktop)

**Run tests:**
```bash
cd frontend
npm run test              # Unit tests
npm run test:e2e          # E2E tests with Playwright
```

---

## 🔀 Pull Request Process

### Before Creating PR

1. ✅ All tests pass locally
2. ✅ Code coverage meets requirements (80%+)
3. ✅ Pre-commit hooks pass (no secrets, no large files)
4. ✅ No linting errors
5. ✅ Documentation updated (if needed)
6. ✅ Acceptance criteria met (from User Story)

### PR Template

```markdown
## Description
Brief description of changes

## Related User Story
Epic X, User Story Y, Task Z

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tests added/updated (if applicable)
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
- [ ] Coverage requirements met
```

### Review Process

1. **Automated checks must pass:**
   - CI/CD pipeline (tests, linting, security scans)
   - Code coverage threshold
   - No merge conflicts

2. **Code review:**
   - At least 1 approval required
   - Reviewer checks:
     - Code quality and readability
     - Test coverage
     - Security considerations
     - Performance implications

3. **Merge:**
   - Use "Squash and merge" for feature branches
   - Use "Rebase and merge" for hotfixes
   - Delete branch after merge

---

## 🧹 Repository Hygiene

### Pre-commit Hooks

Pre-commit hooks automatically run before each commit to ensure code quality:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: check-added-large-files  # Prevent files >500KB
      - id: check-merge-conflict
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
  - repo: https://github.com/Yelp/detect-secrets
    hooks:
      - id: detect-secrets  # Prevent secrets in code
```

**Install:**
```bash
pip install pre-commit
pre-commit install
```

**Run manually:**
```bash
pre-commit run --all-files
```

### What NOT to Commit

❌ **Secrets:**
- API keys, passwords, tokens
- `.env` files with real credentials
- Private keys (`.pem`, `.key`)

❌ **Large Files:**
- Files >500KB
- Videos, large images
- Database dumps

❌ **Generated Files:**
- `node_modules/`
- `__pycache__/`
- Build artifacts (`dist/`, `build/`)

❌ **IDE/OS Files:**
- `.vscode/` (except shared settings)
- `.idea/`
- `.DS_Store`

### Repository Cleanliness

**Keep the repository clean:**
- Only commit source code and configuration
- Use `.gitignore` to exclude unnecessary files
- Delete merged branches
- Keep commit history clean (squash feature branches)
- Remove unused dependencies regularly

**Check cleanliness:**
```bash
# List untracked files
git status

# Check for large files
find . -type f -size +500k

# Check for secrets (manual review)
git secrets --scan
```

---

## 📚 Additional Resources

- [Work Plan V14.0](./WORK_PLAN_V14.0.md) - Complete development plan
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [TypeScript Style Guide (Airbnb)](https://github.com/airbnb/javascript)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Testing Best Practices](https://testingjavascript.com/)

---

## ❓ Questions?

If you have questions about contributing, please:
1. Check the Work Plan V14.0
2. Review existing code for examples
3. Ask in the team chat

---

**Thank you for contributing to DentalAI!** 🎉
