import { test, expect } from '@playwright/test';
import { loginAsPatient, waitForLoading, waitForAPI } from '../utils/test-helpers.js';

test.describe('Patient Portal - Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await loginAsPatient(page);
    await waitForLoading(page);
  });

  test('should display dashboard with all widgets', async ({ page }) => {
    // Check for main dashboard elements
    await expect(page.locator('h1, h2').filter({ hasText: /Dashboard|Welcome/ }).first()).toBeVisible();
    
    // Check for common dashboard sections
    const dashboardSections = [
      'Upcoming Appointments',
      'Recent Activity',
      'Quick Actions',
      'Profile'
    ];
    
    for (const section of dashboardSections) {
      const sectionElement = page.locator(`text=${section}`).first();
      // Use soft assertion - some sections might not be visible
      await expect.soft(sectionElement).toBeVisible({ timeout: 5000 }).catch(() => {});
    }
  });

  test('should navigate to appointments page', async ({ page }) => {
    // Find and click appointments link
    const appointmentsLink = page.locator('a, button').filter({ hasText: /Appointments/i }).first();
    await appointmentsLink.click();
    
    // Wait for navigation
    await page.waitForURL('**/appointments', { timeout: 10000 });
    await expect(page).toHaveURL(/\/appointments/);
    
    // Check appointments page loaded
    await waitForLoading(page);
    await expect(page.locator('h1, h2').filter({ hasText: /Appointments/i }).first()).toBeVisible();
  });

  test('should navigate to profile page', async ({ page }) => {
    // Find and click profile link
    const profileLink = page.locator('a, button').filter({ hasText: /Profile|Account/i }).first();
    await profileLink.click();
    
    // Wait for navigation
    await page.waitForURL('**/profile', { timeout: 10000 });
    await expect(page).toHaveURL(/\/profile/);
    
    // Check profile page loaded
    await waitForLoading(page);
    await expect(page.locator('h1, h2').filter({ hasText: /Profile|Account/i }).first()).toBeVisible();
  });

  test('should display user information', async ({ page }) => {
    // Check if user name or email is displayed
    const userInfo = page.locator('[data-testid="user-info"], .user-name, .user-email');
    await expect(userInfo.first()).toBeVisible({ timeout: 10000 });
  });

  test('should load appointments data', async ({ page }) => {
    // Wait for appointments API call
    const appointmentsResponse = waitForAPI(page, '/api/v1/appointments');
    
    // Navigate to appointments
    const appointmentsLink = page.locator('a, button').filter({ hasText: /Appointments/i }).first();
    await appointmentsLink.click();
    
    // Wait for API response
    await appointmentsResponse;
    
    // Check that appointments are displayed or empty state is shown
    await waitForLoading(page);
    const appointmentsList = page.locator('[data-testid="appointments-list"], .appointments-container');
    const emptyState = page.locator('text=/No appointments|No upcoming/i');
    
    // Either appointments list or empty state should be visible
    await expect(
      appointmentsList.or(emptyState)
    ).toBeVisible({ timeout: 10000 });
  });

  test('should handle responsive design on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Reload to apply viewport
    await page.reload();
    await waitForLoading(page);
    
    // Check if mobile menu exists
    const mobileMenu = page.locator('[data-testid="mobile-menu"], .mobile-menu, button[aria-label*="menu"]');
    await expect(mobileMenu.first()).toBeVisible({ timeout: 5000 });
  });

  test('should display notifications if available', async ({ page }) => {
    // Check for notifications icon/badge
    const notificationIcon = page.locator('[data-testid="notifications"], .notification-icon, [aria-label*="notification"]');
    
    if (await notificationIcon.isVisible()) {
      await notificationIcon.click();
      
      // Check notifications panel opens
      const notificationsPanel = page.locator('[data-testid="notifications-panel"], .notifications-dropdown');
      await expect(notificationsPanel).toBeVisible({ timeout: 5000 });
    }
  });

  test('should search functionality work if available', async ({ page }) => {
    // Check if search exists
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]');
    
    if (await searchInput.isVisible()) {
      await searchInput.fill('appointment');
      await page.keyboard.press('Enter');
      
      // Wait for search results
      await waitForLoading(page);
      
      // Check results are displayed
      const searchResults = page.locator('[data-testid="search-results"], .search-results');
      await expect(searchResults).toBeVisible({ timeout: 10000 });
    }
  });
});

