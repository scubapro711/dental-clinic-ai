/**
 * E2E Test Helpers and Utilities
 */

/**
 * Login helper for patient portal
 */
export async function loginAsPatient(page, email = 'test@patient.com', password = 'testpass123') {
  await page.goto('/patient/login');
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL('/patient/dashboard');
}

/**
 * Login helper for clinic portal
 */
export async function loginAsClinic(page, email = 'admin@clinic.com', password = 'adminpass123') {
  await page.goto('/clinic/login');
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL('/clinic/dashboard');
}

/**
 * Wait for API response
 */
export async function waitForAPI(page, urlPattern, timeout = 10000) {
  return page.waitForResponse(
    response => response.url().includes(urlPattern) && response.status() === 200,
    { timeout }
  );
}

/**
 * Take screenshot with timestamp
 */
export async function takeTimestampedScreenshot(page, name) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await page.screenshot({ path: `test-results/screenshots/${name}-${timestamp}.png`, fullPage: true });
}

/**
 * Check if element is visible and enabled
 */
export async function isInteractive(page, selector) {
  const element = page.locator(selector);
  return (await element.isVisible()) && (await element.isEnabled());
}

/**
 * Fill form with data object
 */
export async function fillForm(page, formData) {
  for (const [name, value] of Object.entries(formData)) {
    await page.fill(`[name="${name}"]`, value);
  }
}

/**
 * Wait for loading to complete
 */
export async function waitForLoading(page) {
  // Wait for common loading indicators to disappear
  await page.waitForSelector('[data-loading="true"]', { state: 'hidden', timeout: 30000 }).catch(() => {});
  await page.waitForSelector('.loading', { state: 'hidden', timeout: 30000 }).catch(() => {});
  await page.waitForSelector('.spinner', { state: 'hidden', timeout: 30000 }).catch(() => {});
}

/**
 * Check for console errors
 */
export function setupConsoleErrorTracking(page) {
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  return errors;
}

/**
 * Mock API response
 */
export async function mockAPIResponse(page, urlPattern, responseData, status = 200) {
  await page.route(urlPattern, route => {
    route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify(responseData)
    });
  });
}

