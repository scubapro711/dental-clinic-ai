import { test, expect } from '@playwright/test';
import { testUsers } from '../fixtures/test-data.js';
import { waitForLoading, setupConsoleErrorTracking } from '../utils/test-helpers.js';

test.describe('Clinic Portal - Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    setupConsoleErrorTracking(page);
  });

  test('should load clinic login page successfully', async ({ page }) => {
    await page.goto('/clinic/login');
    
    // Check page title
    await expect(page).toHaveTitle(/DentaFlow|Clinic|Login/);
    
    // Check login form elements
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show validation errors for empty fields', async ({ page }) => {
    await page.goto('/clinic/login');
    
    await page.click('button[type="submit"]');
    
    const errorMessages = page.locator('[role="alert"], .error-message, .text-red-500');
    await expect(errorMessages.first()).toBeVisible({ timeout: 5000 });
  });

  test('should login successfully as clinic admin', async ({ page }) => {
    await page.goto('/clinic/login');
    
    await page.fill('input[name="email"]', testUsers.clinicAdmin.email);
    await page.fill('input[name="password"]', testUsers.clinicAdmin.password);
    await page.click('button[type="submit"]');
    
    await page.waitForURL('**/clinic/dashboard', { timeout: 15000 });
    await expect(page).toHaveURL(/\/clinic\/dashboard/);
    
    await waitForLoading(page);
    const dashboardHeading = page.locator('h1, h2').filter({ hasText: /Dashboard|Welcome|Clinic/i });
    await expect(dashboardHeading.first()).toBeVisible({ timeout: 10000 });
  });

  test('should persist clinic session after reload', async ({ page }) => {
    await page.goto('/clinic/login');
    await page.fill('input[name="email"]', testUsers.clinicAdmin.email);
    await page.fill('input[name="password"]', testUsers.clinicAdmin.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/clinic/dashboard', { timeout: 15000 });
    
    await page.reload();
    
    await expect(page).toHaveURL(/\/clinic\/dashboard/);
  });

  test('should logout from clinic portal', async ({ page }) => {
    await page.goto('/clinic/login');
    await page.fill('input[name="email"]', testUsers.clinicAdmin.email);
    await page.fill('input[name="password"]', testUsers.clinicAdmin.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/clinic/dashboard', { timeout: 15000 });
    
    const logoutButton = page.locator('button, a').filter({ hasText: /Logout|Sign out/i });
    await logoutButton.click();
    
    await page.waitForURL('**/login', { timeout: 10000 });
    await expect(page).toHaveURL(/\/login/);
  });
});

