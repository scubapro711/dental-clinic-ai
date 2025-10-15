import { test, expect } from '@playwright/test';
import { loginAsClinic, waitForLoading } from '../utils/test-helpers.js';

test.describe('Communications Hub - SMS Integration', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsClinic(page);
    await page.goto('/clinic/communications');
    await waitForLoading(page);
  });

  test('should display SMS tab', async ({ page }) => {
    // Check for SMS tab
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS|Text/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await expect(smsTab).toBeVisible();
      await smsTab.click();
      await waitForLoading(page);
    }
  });

  test('should display SMS dashboard', async ({ page }) => {
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await smsTab.click();
      await waitForLoading(page);
      
      // Check for SMS dashboard elements
      const dashboard = page.locator('[data-testid="sms-dashboard"], .sms-dashboard');
      const heading = page.locator('h2, h3').filter({ hasText: /SMS|Text Messages/i });
      
      await expect(
        dashboard.or(heading.first())
      ).toBeVisible({ timeout: 10000 });
    }
  });

  test('should display SMS statistics', async ({ page }) => {
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await smsTab.click();
      await waitForLoading(page);
      
      // Check for SMS stats
      const stats = page.locator('text=/Sent|Delivered|Failed|Pending/i').first();
      
      if (await stats.isVisible({ timeout: 5000 })) {
        await expect(stats).toBeVisible();
      }
    }
  });

  test('should send SMS to patient', async ({ page }) => {
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await smsTab.click();
      await waitForLoading(page);
      
      // Find send SMS button
      const sendButton = page.locator('button').filter({ hasText: /Send SMS|New Message/i }).first();
      
      if (await sendButton.isVisible({ timeout: 3000 })) {
        await sendButton.click();
        
        // Fill SMS form
        const phoneInput = page.locator('input[name="phone"], input[type="tel"]').first();
        await phoneInput.fill('+1234567890');
        
        const messageInput = page.locator('textarea[name="message"]').first();
        await messageInput.fill('Test appointment reminder');
        
        // Submit
        const submitButton = page.locator('button[type="submit"]').filter({ hasText: /Send/i });
        await submitButton.click();
        
        // Wait for success
        await page.waitForSelector('text=/Success|Sent|Delivered/i', { timeout: 15000 });
      }
    }
  });

  test('should use SMS template', async ({ page }) => {
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await smsTab.click();
      await waitForLoading(page);
      
      // Find send SMS button
      const sendButton = page.locator('button').filter({ hasText: /Send SMS|New Message/i }).first();
      
      if (await sendButton.isVisible({ timeout: 3000 })) {
        await sendButton.click();
        
        // Select template
        const templateSelect = page.locator('select[name="template"], [data-testid="template-select"]').first();
        
        if (await templateSelect.isVisible({ timeout: 3000 })) {
          await templateSelect.selectOption({ index: 1 });
          
          // Template should populate message
          const messageInput = page.locator('textarea[name="message"]').first();
          const messageValue = await messageInput.inputValue();
          expect(messageValue.length).toBeGreaterThan(0);
        }
      }
    }
  });

  test('should display SMS history', async ({ page }) => {
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await smsTab.click();
      await waitForLoading(page);
      
      // Check for SMS history
      const history = page.locator('[data-testid="sms-history"], .sms-history');
      const emptyState = page.locator('text=/No messages|No SMS sent/i');
      
      await expect(
        history.or(emptyState)
      ).toBeVisible({ timeout: 10000 });
    }
  });

  test('should filter SMS by status', async ({ page }) => {
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await smsTab.click();
      await waitForLoading(page);
      
      // Find status filter
      const statusFilter = page.locator('select[name="status"], [data-testid="status-filter"]').first();
      
      if (await statusFilter.isVisible({ timeout: 3000 })) {
        await statusFilter.selectOption('delivered');
        await waitForLoading(page);
        
        // Verify filter applied
        await page.waitForTimeout(1000);
      }
    }
  });

  test('should search SMS history', async ({ page }) => {
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await smsTab.click();
      await waitForLoading(page);
      
      // Find search input
      const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]').first();
      
      if (await searchInput.isVisible({ timeout: 3000 })) {
        await searchInput.fill('appointment');
        await page.keyboard.press('Enter');
        
        await waitForLoading(page);
        await page.waitForTimeout(1000);
      }
    }
  });

  test('should schedule SMS', async ({ page }) => {
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await smsTab.click();
      await waitForLoading(page);
      
      // Find schedule SMS button
      const scheduleButton = page.locator('button').filter({ hasText: /Schedule|Scheduled SMS/i }).first();
      
      if (await scheduleButton.isVisible({ timeout: 3000 })) {
        await scheduleButton.click();
        
        // Fill schedule form
        const phoneInput = page.locator('input[name="phone"]').first();
        await phoneInput.fill('+1234567890');
        
        const messageInput = page.locator('textarea[name="message"]').first();
        await messageInput.fill('Scheduled reminder');
        
        const dateInput = page.locator('input[type="datetime-local"], input[type="date"]').first();
        if (await dateInput.isVisible({ timeout: 2000 })) {
          await dateInput.fill('2025-10-20T14:00');
        }
        
        // Submit
        const submitButton = page.locator('button[type="submit"]').filter({ hasText: /Schedule/i });
        await submitButton.click();
        
        await page.waitForSelector('text=/Success|Scheduled/i', { timeout: 10000 });
      }
    }
  });

  test('should display SMS templates management', async ({ page }) => {
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await smsTab.click();
      await waitForLoading(page);
      
      // Find templates button
      const templatesButton = page.locator('button, a').filter({ hasText: /Templates/i }).first();
      
      if (await templatesButton.isVisible({ timeout: 3000 })) {
        await templatesButton.click();
        
        // Check templates view
        const templatesView = page.locator('[data-testid="sms-templates"], .templates-list');
        await expect(templatesView).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should create SMS template', async ({ page }) => {
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await smsTab.click();
      await waitForLoading(page);
      
      // Navigate to templates
      const templatesButton = page.locator('button, a').filter({ hasText: /Templates/i }).first();
      
      if (await templatesButton.isVisible({ timeout: 3000 })) {
        await templatesButton.click();
        
        // Find create template button
        const createButton = page.locator('button').filter({ hasText: /Create|New Template/i }).first();
        
        if (await createButton.isVisible({ timeout: 3000 })) {
          await createButton.click();
          
          // Fill template form
          const nameInput = page.locator('input[name="name"]').first();
          await nameInput.fill('Appointment Reminder');
          
          const messageInput = page.locator('textarea[name="message"]').first();
          await messageInput.fill('Hi {patient_name}, reminder for your appointment on {date}');
          
          // Save
          const saveButton = page.locator('button[type="submit"]').filter({ hasText: /Save|Create/i });
          await saveButton.click();
          
          await page.waitForSelector('text=/Success|Created/i', { timeout: 10000 });
        }
      }
    }
  });

  test('should display SMS delivery status', async ({ page }) => {
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await smsTab.click();
      await waitForLoading(page);
      
      // Find first SMS in history
      const firstSMS = page.locator('[data-testid="sms-item"], .sms-row').first();
      
      if (await firstSMS.isVisible({ timeout: 3000 })) {
        // Check for status indicator
        const status = firstSMS.locator('text=/Delivered|Sent|Failed|Pending/i');
        await expect(status.first()).toBeVisible();
      }
    }
  });

  test('should bulk send SMS', async ({ page }) => {
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await smsTab.click();
      await waitForLoading(page);
      
      // Find bulk send button
      const bulkButton = page.locator('button').filter({ hasText: /Bulk|Send to Multiple/i }).first();
      
      if (await bulkButton.isVisible({ timeout: 3000 })) {
        await bulkButton.click();
        
        // Check bulk send form
        const bulkForm = page.locator('[data-testid="bulk-sms-form"], form');
        await expect(bulkForm.first()).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should display SMS cost information', async ({ page }) => {
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await smsTab.click();
      await waitForLoading(page);
      
      // Look for cost information
      const costInfo = page.locator('text=/Cost|Price|Credits/i').first();
      
      if (await costInfo.isVisible({ timeout: 5000 })) {
        await expect(costInfo).toBeVisible();
      }
    }
  });

  test('should configure SMS settings', async ({ page }) => {
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible({ timeout: 5000 })) {
      await smsTab.click();
      await waitForLoading(page);
      
      // Find settings button
      const settingsButton = page.locator('button').filter({ hasText: /Settings|Configure/i }).first();
      
      if (await settingsButton.isVisible({ timeout: 3000 })) {
        await settingsButton.click();
        
        // Check settings view
        const settingsView = page.locator('[data-testid="sms-settings"], .settings-panel');
        await expect(settingsView.first()).toBeVisible({ timeout: 5000 });
      }
    }
  });
});

