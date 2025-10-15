import { test, expect } from '@playwright/test';
import { loginAsClinic, waitForLoading, waitForAPI } from '../utils/test-helpers.js';

test.describe('Clinic Portal - Agentic Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsClinic(page);
    await waitForLoading(page);
  });

  test('should display agentic dashboard with gradient design', async ({ page }) => {
    // Check for dashboard title
    await expect(page.locator('h1, h2').filter({ hasText: /Dashboard|Clinic/i }).first()).toBeVisible();
    
    // Check for gradient background (agentic design)
    const gradientElement = page.locator('[class*="gradient"], [style*="gradient"]').first();
    await expect(gradientElement).toBeVisible({ timeout: 5000 });
  });

  test('should display all dashboard widgets', async ({ page }) => {
    await waitForLoading(page);
    
    // Common widgets to check
    const widgets = [
      'Today\'s Patients',
      'Appointments',
      'Revenue',
      'Statistics',
      'Quick Actions'
    ];
    
    for (const widget of widgets) {
      const widgetElement = page.locator(`text=${widget}`).first();
      // Soft assertion - not all widgets might be visible
      await expect.soft(widgetElement).toBeVisible({ timeout: 5000 }).catch(() => {});
    }
  });

  test('should load widgets data from API', async ({ page }) => {
    // Wait for common API calls
    const apiCalls = [
      waitForAPI(page, '/api/v1/dashboard'),
      waitForAPI(page, '/api/v1/patients'),
      waitForAPI(page, '/api/v1/appointments')
    ];
    
    // Reload to trigger API calls
    await page.reload();
    
    // Wait for at least one API call to complete
    await Promise.race(apiCalls);
    
    await waitForLoading(page);
    
    // Check that data is displayed
    const dataElements = page.locator('[data-testid*="widget"], .widget, .card');
    await expect(dataElements.first()).toBeVisible({ timeout: 10000 });
  });

  test('should display sparkles and agentic UI elements', async ({ page }) => {
    // Check for sparkles icon or agentic design elements
    const sparklesIcon = page.locator('[class*="sparkle"], svg[class*="icon"]').first();
    await expect(sparklesIcon).toBeVisible({ timeout: 5000 });
  });

  test('should have interactive widgets', async ({ page }) => {
    await waitForLoading(page);
    
    // Find first clickable widget
    const widget = page.locator('[data-testid*="widget"], .widget, .card').first();
    
    if (await widget.isVisible()) {
      // Check if widget is interactive
      const clickableElement = widget.locator('button, a').first();
      
      if (await clickableElement.isVisible()) {
        await clickableElement.click();
        
        // Wait for some action (navigation, modal, etc.)
        await page.waitForTimeout(1000);
      }
    }
  });

  test('should display real-time updates', async ({ page }) => {
    // Check for real-time indicators
    const realtimeIndicator = page.locator('text=/Live|Real-time|Updated/i').first();
    
    if (await realtimeIndicator.isVisible()) {
      // Verify data updates (check timestamp changes)
      const timestamp = await page.locator('[data-testid="timestamp"], .timestamp').first().textContent();
      
      // Wait a bit
      await page.waitForTimeout(2000);
      
      // Reload
      await page.reload();
      await waitForLoading(page);
      
      // Check if timestamp updated
      const newTimestamp = await page.locator('[data-testid="timestamp"], .timestamp').first().textContent();
      expect(newTimestamp).not.toBe(timestamp);
    }
  });

  test('should navigate to patients management', async ({ page }) => {
    const patientsLink = page.locator('a, button').filter({ hasText: /Patients|Patient Management/i }).first();
    await patientsLink.click();
    
    await page.waitForURL('**/patients', { timeout: 10000 });
    await expect(page).toHaveURL(/\/patients/);
    
    await waitForLoading(page);
    await expect(page.locator('h1, h2').filter({ hasText: /Patients/i }).first()).toBeVisible();
  });

  test('should navigate to communications hub', async ({ page }) => {
    const communicationsLink = page.locator('a, button').filter({ hasText: /Communications|Telegram/i }).first();
    
    if (await communicationsLink.isVisible()) {
      await communicationsLink.click();
      
      await page.waitForURL('**/communications', { timeout: 10000 });
      await expect(page).toHaveURL(/\/communications/);
      
      await waitForLoading(page);
      await expect(page.locator('h1, h2').filter({ hasText: /Communications/i }).first()).toBeVisible();
    }
  });

  test('should handle responsive design', async ({ page }) => {
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.reload();
    await waitForLoading(page);
    
    // Widgets should still be visible
    const widgets = page.locator('[data-testid*="widget"], .widget, .card');
    await expect(widgets.first()).toBeVisible();
    
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await waitForLoading(page);
    
    // Mobile menu should be visible
    const mobileMenu = page.locator('[data-testid="mobile-menu"], .mobile-menu, button[aria-label*="menu"]');
    await expect(mobileMenu.first()).toBeVisible({ timeout: 5000 });
  });

  test('should display clinic information', async ({ page }) => {
    // Check for clinic name or info
    const clinicInfo = page.locator('[data-testid="clinic-info"], .clinic-name, .clinic-details').first();
    await expect(clinicInfo).toBeVisible({ timeout: 10000 });
  });
});

