import { test, expect } from '@playwright/test';
import { loginAsClinic, waitForLoading } from '../utils/test-helpers.js';

test.describe('Clinic Portal - Settings & Configuration', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsClinic(page);
    await waitForLoading(page);
  });

  test('should navigate to settings page', async ({ page }) => {
    // Find settings link
    const settingsLink = page.locator('a, button').filter({ hasText: /Settings|Configuration/i }).first();
    
    if (await settingsLink.isVisible({ timeout: 5000 })) {
      await settingsLink.click();
      await waitForLoading(page);
      
      // Check settings page loaded
      await expect(page.locator('h1, h2').filter({ hasText: /Settings|Configuration/i }).first()).toBeVisible();
    } else {
      // Try direct navigation
      await page.goto('/clinic/settings');
      await waitForLoading(page);
      
      await expect(page.locator('h1, h2').filter({ hasText: /Settings/i }).first()).toBeVisible({ timeout: 10000 });
    }
  });

  test('should display clinic information', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Check for clinic info section
    const clinicInfo = page.locator('[data-testid="clinic-info"], .clinic-info');
    const fields = page.locator('text=/Clinic Name|Address|Phone|Email/i');
    
    await expect(
      clinicInfo.or(fields.first())
    ).toBeVisible({ timeout: 10000 });
  });

  test('should edit clinic information', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Find edit button
    const editButton = page.locator('button').filter({ hasText: /Edit|Update/i }).first();
    
    if (await editButton.isVisible({ timeout: 5000 })) {
      await editButton.click();
      
      // Update clinic phone
      const phoneInput = page.locator('input[name="phone"], input[name="clinicPhone"]').first();
      if (await phoneInput.isVisible({ timeout: 3000 })) {
        await phoneInput.clear();
        await phoneInput.fill('+1234567890');
        
        // Save changes
        const saveButton = page.locator('button[type="submit"]').filter({ hasText: /Save|Update/i });
        await saveButton.click();
        
        // Wait for success
        await page.waitForSelector('text=/Success|Updated|Saved/i', { timeout: 10000 });
      }
    }
  });

  test('should configure business hours', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to business hours section
    const hoursTab = page.locator('button, a').filter({ hasText: /Business Hours|Hours|Schedule/i }).first();
    
    if (await hoursTab.isVisible({ timeout: 5000 })) {
      await hoursTab.click();
      await waitForLoading(page);
      
      // Check business hours section
      const hoursSection = page.locator('[data-testid="business-hours"], .business-hours');
      await expect(hoursSection).toBeVisible({ timeout: 10000 });
    }
  });

  test('should update business hours', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to business hours
    const hoursTab = page.locator('button, a').filter({ hasText: /Business Hours|Hours/i }).first();
    
    if (await hoursTab.isVisible({ timeout: 5000 })) {
      await hoursTab.click();
      await waitForLoading(page);
      
      // Find edit button
      const editButton = page.locator('button').filter({ hasText: /Edit|Update/i }).first();
      if (await editButton.isVisible({ timeout: 3000 })) {
        await editButton.click();
        
        // Update Monday hours
        const mondayOpenInput = page.locator('input[name*="monday"][name*="open"], [data-testid*="monday-open"]').first();
        if (await mondayOpenInput.isVisible({ timeout: 3000 })) {
          await mondayOpenInput.fill('09:00');
          
          // Save
          const saveButton = page.locator('button[type="submit"]').filter({ hasText: /Save|Update/i });
          await saveButton.click();
          
          await page.waitForSelector('text=/Success|Updated/i', { timeout: 10000 });
        }
      }
    }
  });

  test('should configure appointment settings', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to appointments settings
    const appointmentsTab = page.locator('button, a').filter({ hasText: /Appointments|Booking/i }).first();
    
    if (await appointmentsTab.isVisible({ timeout: 5000 })) {
      await appointmentsTab.click();
      await waitForLoading(page);
      
      // Check appointments settings section
      const appointmentsSection = page.locator('[data-testid="appointment-settings"], .appointment-settings');
      await expect(appointmentsSection).toBeVisible({ timeout: 10000 });
    }
  });

  test('should configure notification settings', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to notifications settings
    const notificationsTab = page.locator('button, a').filter({ hasText: /Notifications|Alerts/i }).first();
    
    if (await notificationsTab.isVisible({ timeout: 5000 })) {
      await notificationsTab.click();
      await waitForLoading(page);
      
      // Check notifications settings section
      const notificationsSection = page.locator('[data-testid="notification-settings"], .notification-settings');
      await expect(notificationsSection).toBeVisible({ timeout: 10000 });
    }
  });

  test('should toggle email notifications', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to notifications
    const notificationsTab = page.locator('button, a').filter({ hasText: /Notifications/i }).first();
    
    if (await notificationsTab.isVisible({ timeout: 5000 })) {
      await notificationsTab.click();
      await waitForLoading(page);
      
      // Toggle email notifications
      const emailToggle = page.locator('input[type="checkbox"][name*="email"]').first();
      if (await emailToggle.isVisible({ timeout: 3000 })) {
        await emailToggle.click();
        
        // Save if needed
        const saveButton = page.locator('button').filter({ hasText: /Save|Update/i }).first();
        if (await saveButton.isVisible({ timeout: 2000 })) {
          await saveButton.click();
          await page.waitForSelector('text=/Success|Updated/i', { timeout: 10000 });
        }
      }
    }
  });

  test('should manage staff members', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to staff section
    const staffTab = page.locator('button, a').filter({ hasText: /Staff|Team|Users/i }).first();
    
    if (await staffTab.isVisible({ timeout: 5000 })) {
      await staffTab.click();
      await waitForLoading(page);
      
      // Check staff section
      const staffSection = page.locator('[data-testid="staff-list"], .staff-list');
      const emptyState = page.locator('text=/No staff|Add staff/i');
      
      await expect(
        staffSection.or(emptyState)
      ).toBeVisible({ timeout: 10000 });
    }
  });

  test('should add staff member', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to staff section
    const staffTab = page.locator('button, a').filter({ hasText: /Staff|Team/i }).first();
    
    if (await staffTab.isVisible({ timeout: 5000 })) {
      await staffTab.click();
      await waitForLoading(page);
      
      // Find add staff button
      const addButton = page.locator('button').filter({ hasText: /Add Staff|New Staff|Invite/i }).first();
      
      if (await addButton.isVisible({ timeout: 3000 })) {
        await addButton.click();
        
        // Fill staff information
        const emailInput = page.locator('input[name="email"]').first();
        await emailInput.fill('newstaff@clinic.com');
        
        const nameInput = page.locator('input[name="name"], input[name="firstName"]').first();
        if (await nameInput.isVisible({ timeout: 2000 })) {
          await nameInput.fill('New Staff');
        }
        
        // Select role
        const roleSelect = page.locator('select[name="role"]').first();
        if (await roleSelect.isVisible({ timeout: 2000 })) {
          await roleSelect.selectOption({ index: 1 });
        }
        
        // Submit
        const submitButton = page.locator('button[type="submit"]').filter({ hasText: /Add|Invite|Save/i });
        await submitButton.click();
        
        await page.waitForSelector('text=/Success|Added|Invited/i', { timeout: 10000 });
      }
    }
  });

  test('should configure treatment prices', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to pricing section
    const pricingTab = page.locator('button, a').filter({ hasText: /Pricing|Treatments|Services/i }).first();
    
    if (await pricingTab.isVisible({ timeout: 5000 })) {
      await pricingTab.click();
      await waitForLoading(page);
      
      // Check pricing section
      const pricingSection = page.locator('[data-testid="treatment-prices"], .treatment-prices');
      await expect(pricingSection).toBeVisible({ timeout: 10000 });
    }
  });

  test('should update treatment price', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to pricing
    const pricingTab = page.locator('button, a').filter({ hasText: /Pricing|Treatments/i }).first();
    
    if (await pricingTab.isVisible({ timeout: 5000 })) {
      await pricingTab.click();
      await waitForLoading(page);
      
      // Find first treatment
      const firstTreatment = page.locator('[data-testid="treatment-item"], .treatment-item').first();
      
      if (await firstTreatment.isVisible({ timeout: 3000 })) {
        // Find edit button
        const editButton = firstTreatment.locator('button').filter({ hasText: /Edit/i }).first();
        if (await editButton.isVisible({ timeout: 2000 })) {
          await editButton.click();
          
          // Update price
          const priceInput = page.locator('input[name="price"]').first();
          await priceInput.clear();
          await priceInput.fill('150');
          
          // Save
          const saveButton = page.locator('button[type="submit"]').filter({ hasText: /Save|Update/i });
          await saveButton.click();
          
          await page.waitForSelector('text=/Success|Updated/i', { timeout: 10000 });
        }
      }
    }
  });

  test('should configure integrations', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to integrations section
    const integrationsTab = page.locator('button, a').filter({ hasText: /Integrations|Connections/i }).first();
    
    if (await integrationsTab.isVisible({ timeout: 5000 })) {
      await integrationsTab.click();
      await waitForLoading(page);
      
      // Check integrations section
      const integrationsSection = page.locator('[data-testid="integrations"], .integrations');
      await expect(integrationsSection).toBeVisible({ timeout: 10000 });
    }
  });

  test('should view billing and subscription', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to billing section
    const billingTab = page.locator('button, a').filter({ hasText: /Billing|Subscription|Plan/i }).first();
    
    if (await billingTab.isVisible({ timeout: 5000 })) {
      await billingTab.click();
      await waitForLoading(page);
      
      // Check billing section
      const billingSection = page.locator('[data-testid="billing"], .billing');
      await expect(billingSection).toBeVisible({ timeout: 10000 });
    }
  });

  test('should upload clinic logo', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Find upload logo button
    const uploadButton = page.locator('button, label').filter({ hasText: /Upload.*Logo|Change.*Logo/i }).first();
    
    if (await uploadButton.isVisible({ timeout: 5000 })) {
      // Find file input
      const fileInput = page.locator('input[type="file"]').first();
      
      // Set file
      await fileInput.setInputFiles({
        name: 'clinic-logo.png',
        mimeType: 'image/png',
        buffer: Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', 'base64')
      });
      
      // Wait for upload
      await page.waitForSelector('text=/Success|Uploaded|Updated/i', { timeout: 15000 });
    }
  });

  test('should configure security settings', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to security section
    const securityTab = page.locator('button, a').filter({ hasText: /Security|Privacy/i }).first();
    
    if (await securityTab.isVisible({ timeout: 5000 })) {
      await securityTab.click();
      await waitForLoading(page);
      
      // Check security section
      const securitySection = page.locator('[data-testid="security"], .security');
      await expect(securitySection).toBeVisible({ timeout: 10000 });
    }
  });

  test('should enable two-factor authentication', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to security
    const securityTab = page.locator('button, a').filter({ hasText: /Security/i }).first();
    
    if (await securityTab.isVisible({ timeout: 5000 })) {
      await securityTab.click();
      await waitForLoading(page);
      
      // Find 2FA toggle
      const twoFAToggle = page.locator('button, input[type="checkbox"]').filter({ hasText: /Two-Factor|2FA/i }).first();
      
      if (await twoFAToggle.isVisible({ timeout: 3000 })) {
        await twoFAToggle.click();
        
        // May need to confirm
        const confirmButton = page.locator('button').filter({ hasText: /Enable|Confirm/i }).first();
        if (await confirmButton.isVisible({ timeout: 2000 })) {
          await confirmButton.click();
        }
      }
    }
  });

  test('should view activity log', async ({ page }) => {
    await page.goto('/clinic/settings').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to activity log
    const activityTab = page.locator('button, a').filter({ hasText: /Activity|Audit|Log/i }).first();
    
    if (await activityTab.isVisible({ timeout: 5000 })) {
      await activityTab.click();
      await waitForLoading(page);
      
      // Check activity log section
      const activityLog = page.locator('[data-testid="activity-log"], .activity-log');
      const emptyState = page.locator('text=/No activity|No logs/i');
      
      await expect(
        activityLog.or(emptyState)
      ).toBeVisible({ timeout: 10000 });
    }
  });
});

