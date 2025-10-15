# DentaFlow E2E Testing Suite

Comprehensive end-to-end testing suite for DentaFlow dental clinic management system using Playwright.

## Overview

This E2E testing suite covers three main areas:
1. **Patient Portal** - Patient-facing features and workflows
2. **Clinic Portal** - Clinic administration and management
3. **Communications Hub** - Multi-channel patient communication

## Test Structure

```
e2e/
├── patient-portal/
│   ├── 01-login.spec.js              # Authentication and session management
│   ├── 02-dashboard.spec.js          # Dashboard functionality
│   ├── 03-appointments.spec.js       # Appointment booking and management
│   ├── 04-profile.spec.js            # Profile and medical information
│   ├── 05-ai-chat.spec.js            # AI assistant interactions
│   └── 06-medical-records.spec.js    # Medical records and documents
├── clinic-portal/
│   ├── 01-login.spec.js              # Clinic authentication
│   ├── 02-agentic-dashboard.spec.js  # Agentic dashboard features
│   ├── 03-patient-management.spec.js # Basic patient management
│   ├── 04-patient-management-advanced.spec.js # Advanced patient features
│   ├── 05-settings.spec.js           # Clinic settings and configuration
│   └── 06-analytics.spec.js          # Analytics and reporting
├── communications/
│   ├── 01-telegram-hub.spec.js       # Telegram integration
│   ├── 02-sms-hub.spec.js            # SMS communications
│   └── 03-email-hub.spec.js          # Email communications
├── fixtures/
│   └── test-data.js                  # Test data and constants
└── utils/
    └── test-helpers.js               # Reusable test utilities

```

## Prerequisites

- Node.js 18+
- npm or pnpm
- Backend server running (or use CI/CD setup)
- Test database configured

## Installation

```bash
# Install dependencies
npm install

# Install Playwright browsers
npm run test:e2e:install
```

## Running Tests

### Run all E2E tests
```bash
npm run test:e2e
```

### Run with UI mode (interactive)
```bash
npm run test:e2e:ui
```

### Run in headed mode (see browser)
```bash
npm run test:e2e:headed
```

### Run with debugger
```bash
npm run test:e2e:debug
```

### Run specific test suites
```bash
# Patient Portal tests only
npm run test:e2e:patient

# Clinic Portal tests only
npm run test:e2e:clinic

# Communications Hub tests only
npm run test:e2e:communications
```

### Run on specific browsers
```bash
# Chromium only
npm run test:e2e:chromium

# Firefox only
npm run test:e2e:firefox

# WebKit (Safari) only
npm run test:e2e:webkit

# Mobile browsers
npm run test:e2e:mobile
```

### View test report
```bash
npm run test:e2e:report
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
# Base URL for E2E tests
E2E_BASE_URL=http://localhost:5173

# Test user credentials
TEST_PATIENT_EMAIL=test.patient@example.com
TEST_PATIENT_PASSWORD=TestPassword123!
TEST_CLINIC_ADMIN_EMAIL=admin@clinic.example.com
TEST_CLINIC_ADMIN_PASSWORD=AdminPassword123!
```

## Test Configuration

The test configuration is in `playwright.config.js`:

- **Parallel execution**: Enabled for faster test runs
- **Retries**: 2 retries on CI, 0 locally
- **Timeout**: 30 seconds per test
- **Screenshots**: Captured on failure
- **Videos**: Recorded on failure
- **Trace**: Captured on first retry

## CI/CD Integration

E2E tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

### GitHub Actions Workflows

1. **e2e-tests.yml** - Main E2E test workflow
   - Runs on Chromium for all test suites
   - Uploads test reports and artifacts
   - Generates test summary

2. **Cross-browser testing** - Runs on main branch only
   - Tests on Chromium, Firefox, and WebKit
   - Matrix strategy for parallel execution

## Test Data Management

Test data is managed in `fixtures/test-data.js`:

- **testUsers**: Predefined user credentials
- **testAppointment**: Sample appointment data
- **testPatient**: Sample patient information
- **testTelegramInvite**: Telegram invite code data
- **apiEndpoints**: API endpoint constants
- **timeouts**: Standard timeout values
- **viewports**: Responsive design breakpoints

## Test Helpers

Reusable utilities in `utils/test-helpers.js`:

- `loginAsPatient()` - Patient portal login
- `loginAsClinic()` - Clinic portal login
- `waitForAPI()` - Wait for API responses
- `waitForLoading()` - Wait for loading indicators
- `takeTimestampedScreenshot()` - Capture screenshots
- `fillForm()` - Fill form fields from object
- `setupConsoleErrorTracking()` - Track console errors
- `mockAPIResponse()` - Mock API responses

## Writing New Tests

### Basic Test Structure

```javascript
import { test, expect } from '@playwright/test';
import { loginAsPatient, waitForLoading } from '../utils/test-helpers.js';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsPatient(page);
    await waitForLoading(page);
  });

  test('should do something', async ({ page }) => {
    // Navigate
    await page.goto('/patient/feature');
    
    // Interact
    await page.click('button');
    
    // Assert
    await expect(page.locator('h1')).toBeVisible();
  });
});
```

### Best Practices

1. **Use data-testid attributes** for reliable selectors
2. **Wait for elements** before interacting
3. **Use soft assertions** for optional elements
4. **Handle loading states** explicitly
5. **Test error scenarios** and edge cases
6. **Keep tests independent** and isolated
7. **Use descriptive test names** that explain intent
8. **Group related tests** in describe blocks

## Debugging Tests

### Debug a specific test
```bash
npx playwright test --debug e2e/patient-portal/01-login.spec.js
```

### Run with trace viewer
```bash
npx playwright test --trace on
npx playwright show-trace trace.zip
```

### Generate test code
```bash
npx playwright codegen http://localhost:5173
```

## Test Coverage

Current test coverage includes:

### Patient Portal (6 test files, ~80+ tests)
- ✅ Authentication and session management
- ✅ Dashboard navigation and widgets
- ✅ Appointment booking and management
- ✅ Profile and medical information
- ✅ AI chat interactions
- ✅ Medical records and documents

### Clinic Portal (6 test files, ~90+ tests)
- ✅ Clinic authentication
- ✅ Agentic dashboard features
- ✅ Patient management (basic and advanced)
- ✅ Clinic settings and configuration
- ✅ Analytics and reporting
- ✅ Staff management

### Communications Hub (3 test files, ~50+ tests)
- ✅ Telegram integration and invite codes
- ✅ SMS communications and templates
- ✅ Email management and templates
- ✅ Multi-channel messaging

**Total: ~220+ comprehensive E2E tests**

## Troubleshooting

### Tests failing locally but passing in CI
- Ensure backend and frontend servers are running
- Check environment variables are set correctly
- Verify database is in clean state

### Timeout errors
- Increase timeout in playwright.config.js
- Check if backend is responding slowly
- Verify network conditions

### Element not found errors
- Check if selectors are correct
- Wait for element to be visible
- Verify page has loaded completely

### Browser installation issues
```bash
# Reinstall browsers
npx playwright install --force

# Install system dependencies
npx playwright install-deps
```

## Performance Optimization

- Tests run in parallel by default
- Use `test.describe.configure({ mode: 'serial' })` for dependent tests
- Reuse authentication state with `storageState`
- Mock external API calls when appropriate

## Reporting

Test results are available in multiple formats:

- **HTML Report**: `playwright-report/index.html`
- **JSON Report**: `test-results/results.json`
- **JUnit XML**: `test-results/junit.xml`

## Contributing

When adding new tests:

1. Follow existing test structure and naming conventions
2. Add test data to `fixtures/test-data.js`
3. Create reusable helpers in `utils/test-helpers.js`
4. Update this README with new test coverage
5. Ensure tests pass locally before committing

## Support

For issues or questions:
- Check Playwright documentation: https://playwright.dev
- Review existing test examples
- Contact the development team

---

**Last Updated**: October 2025
**Playwright Version**: 1.56.0
**Test Count**: 220+ comprehensive E2E tests

