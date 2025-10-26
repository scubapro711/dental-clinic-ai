# DentaFlow Testing Guide

**Last Updated:** October 26, 2025

This guide provides a comprehensive overview of the testing strategy for the DentaFlow project, including how to run tests, add new tests, and understand the CI/CD pipeline.

For a broader strategic overview, see [Phase 4 Comprehensive Guide](PHASE_4_COMPREHENSIVE_GUIDE.md).

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Testing Frameworks](#testing-frameworks)
3. [How to Run Tests](#how-to-run-tests)
   - [Frontend Unit Tests (Vitest)](#frontend-unit-tests-vitest)
   - [Frontend End-to-End (E2E) Tests (Playwright)](#frontend-end-to-end-e2e-tests-playwright)
   - [Backend Tests (Pytest)](#backend-tests-pytest)
4. [CI/CD Integration](#cicd-integration)
5. [How to Add New Tests](#how-to-add-new-tests)
6. [Test Coverage](#test-coverage)

---

## Testing Philosophy

Our testing philosophy is based on the **Testing Pyramid**:

- **Unit Tests (Fast & Cheap):** The foundation of our testing strategy. These tests are fast, isolated, and verify the smallest units of code (components, functions).
- **Integration Tests (Medium):** Verify that multiple units work together as expected.
- **End-to-End (E2E) Tests (Slow & Expensive):** Simulate real user workflows from start to finish. These tests are critical for catching bugs that unit tests miss.

We aim for high coverage at the unit test level, with targeted integration and E2E tests for critical paths.

## Testing Frameworks

### Frontend

| Type | Framework | Location | Naming Convention |
|---|---|---|---|
| Unit | Vitest | `frontend/src/**/*.test.jsx` | `*.test.jsx` |
| E2E | Playwright | `frontend/e2e/**/*.spec.js` | `*.spec.js` |

### Backend

| Type | Framework | Location | Naming Convention |
|---|---|---|---|
| Unit/Integration | Pytest | `backend/tests/**/*.py` | `test_*.py` |
| Security | Bandit | `backend/app` | N/A |
| Load | Locust | `backend/tests/load_test.py` | N/A |

## How to Run Tests

### Frontend Unit Tests (Vitest)

To run unit tests, navigate to the `frontend` directory:

```bash
cd frontend
```

**Run all unit tests:**
```bash
pnpm test:run
```

**Run a specific test file:**
```bash
pnpm test:run <path-to-file>
# Example:
pnpm test:run src/components/AIChat.test.jsx
```

**Run tests in watch mode:**
```bash
pnpm test
```

**Run tests with UI:**
```bash
pnpm test:ui
```

### Frontend End-to-End (E2E) Tests (Playwright)

To run E2E tests, navigate to the `frontend` directory:

```bash
cd frontend
```

**Run all E2E tests:**
```bash
pnpm test:e2e
```

**Run tests for a specific portal:**
```bash
# Patient Portal
pnpm test:e2e:patient

# Clinic Portal
pnpm test:e2e:clinic
```

**Run tests in headed mode (shows browser):**
```bash
pnpm test:e2e:headed
```

**Run tests with UI:**
```bash
pnpm test:e2e:ui
```

### Backend Tests (Pytest)

To run backend tests, navigate to the `backend` directory:

```bash
cd backend
```

**Run all backend tests:**
```bash
pytest tests/
```

**Run a specific test file:**
```bash
pytest tests/test_agents.py
```

## CI/CD Integration

All tests are automatically run in our Cloud Build CI/CD pipelines before any deployment.

- **Staging (`develop` branch):** `frontend/cloudbuild-staging.yaml` runs `pnpm test:run` before building the Docker image. If tests fail, the deployment is blocked.
- **Production (`main` branch):** `frontend/cloudbuild.yaml` runs `pnpm test:run` before building the Docker image. If tests fail, the deployment is blocked.

This ensures that no code with failing tests reaches production.

## How to Add New Tests

### Adding a New Frontend Unit Test

1. Create a new file with the `.test.jsx` extension next to the component you want to test.
2. Import `describe`, `it`, `expect` from `vitest`.
3. Import the component you want to test.
4. Write your tests!

**Example: `MyComponent.test.jsx`**
```jsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  it('should render correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });
});
```

### Adding a New Frontend E2E Test

1. Create a new file with the `.spec.js` extension in the appropriate `frontend/e2e` subdirectory.
2. Import `test`, `expect` from `@playwright/test`.
3. Write your tests!

**Example: `frontend/e2e/my-feature.spec.js`**
```javascript
import { test, expect } from '@playwright/test';

test('My Feature', async ({ page }) => {
  await page.goto('/my-feature');
  await expect(page.locator('h1')).toHaveText('My Feature');
});
```

### Adding a New Backend Test

1. Create a new file with the `test_` prefix in the `backend/tests` directory.
2. Import `pytest`.
3. Write your test functions!

**Example: `backend/tests/test_new_feature.py`**
```python
import pytest

def test_new_feature():
    assert 1 + 1 == 2
```

## Test Coverage

We aim for high test coverage, especially for critical components.

### Frontend Coverage

To check frontend test coverage locally, run:

```bash
cd frontend
pnpm test:coverage
```

This will generate a coverage report in the `frontend/coverage` directory.

### Backend Coverage

To check backend test coverage locally, run:

```bash
cd backend
pytest --cov=app
```

This will generate a coverage report in the console.

