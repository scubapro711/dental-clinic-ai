import { test, expect } from '@playwright/test';
import { testUsers } from '../fixtures/test-data.js';
import { waitForLoading, setupConsoleErrorTracking } from '../utils/test-helpers.js';

test.describe('Patient Portal - Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Track console errors
    setupConsoleErrorTracking(page);
  });

  test('should load login page successfully', async ({ page }) => {
    await page.goto('/patient/login');
    
    // Check page title
    await expect(page).toHaveTitle(/DentaFlow|Login/);
    
    // Check login form elements exist
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show validation errors for empty fields', async ({ page }) => {
    await page.goto('/patient/login');
    
    // Click submit without filling fields
    await page.click('button[type="submit"]');
    
    // Check for validation messages
    const errorMessages = page.locator('[role="alert"], .error-message, .text-red-500');
    await expect(errorMessages.first()).toBeVisible({ timeout: 5000 });
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/patient/login');
    
    // Fill with invalid credentials
    await page.fill('input[name="email"]', 'invalid@example.com');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    // Wait for error message
    await page.waitForSelector('text=/Invalid credentials|Login failed|Incorrect/', { timeout: 10000 });
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.goto('/patient/login');
    
    // Fill login form
    await page.fill('input[name="email"]', testUsers.patient.email);
    await page.fill('input[name="password"]', testUsers.patient.password);
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Wait for navigation to dashboard
    await page.waitForURL('**/patient/dashboard', { timeout: 15000 });
    
    // Verify we're on the dashboard
    await expect(page).toHaveURL(/\/patient\/dashboard/);
    
    // Check for dashboard elements
    await waitForLoading(page);
    const dashboardHeading = page.locator('h1, h2').filter({ hasText: /Dashboard|Welcome/ });
    await expect(dashboardHeading.first()).toBeVisible({ timeout: 10000 });
  });

  test('should persist session after page reload', async ({ page }) => {
    // Login first
    await page.goto('/patient/login');
    await page.fill('input[name="email"]', testUsers.patient.email);
    await page.fill('input[name="password"]', testUsers.patient.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/patient/dashboard', { timeout: 15000 });
    
    // Reload page
    await page.reload();
    
    // Should still be on dashboard (not redirected to login)
    await expect(page).toHaveURL(/\/patient\/dashboard/);
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.goto('/patient/login');
    await page.fill('input[name="email"]', testUsers.patient.email);
    await page.fill('input[name="password"]', testUsers.patient.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/patient/dashboard', { timeout: 15000 });
    
    // Find and click logout button
    const logoutButton = page.locator('button, a').filter({ hasText: /Logout|Sign out/i });
    await logoutButton.click();
    
    // Should redirect to login
    await page.waitForURL('**/login', { timeout: 10000 });
    await expect(page).toHaveURL(/\/login/);
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Simulate offline
    await page.context().setOffline(true);
    
    await page.goto('/patient/login');
    await page.fill('input[name="email"]', testUsers.patient.email);
    await page.fill('input[name="password"]', testUsers.patient.password);
    await page.click('button[type="submit"]');
    
    // Should show network error
    await page.waitForSelector('text=/Network error|Connection failed|offline/i', { timeout: 10000 });
    
    // Restore connection
    await page.context().setOffline(false);
  });
});

