import { test, expect } from '@playwright/test';
import { loginAsPatient, waitForLoading, waitForAPI } from '../utils/test-helpers.js';
import { testUsers } from '../fixtures/test-data.js';

test.describe('Patient Portal - Profile Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsPatient(page);
    await waitForLoading(page);
    
    // Navigate to profile page
    await page.goto('/patient/profile');
    await waitForLoading(page);
  });

  test('should display profile information', async ({ page }) => {
    // Check page title
    await expect(page.locator('h1, h2').filter({ hasText: /Profile|Account/i }).first()).toBeVisible();
    
    // Check personal information fields
    const fields = ['email', 'firstName', 'lastName', 'phone'];
    for (const field of fields) {
      const fieldElement = page.locator(`[name="${field}"], [data-testid="${field}"]`).first();
      await expect.soft(fieldElement).toBeVisible({ timeout: 5000 });
    }
  });

  test('should edit profile information', async ({ page }) => {
    // Find edit button
    const editButton = page.locator('button').filter({ hasText: /Edit|Update/i }).first();
    await editButton.click();
    
    // Update phone number
    const phoneInput = page.locator('input[name="phone"], [data-testid="phone"]').first();
    await phoneInput.clear();
    await phoneInput.fill('+1234567890');
    
    // Save changes
    const saveButton = page.locator('button[type="submit"], button').filter({ hasText: /Save|Update/i }).first();
    await saveButton.click();
    
    // Wait for success message
    await page.waitForSelector('text=/Success|Updated|Saved/i', { timeout: 10000 });
  });

  test('should validate profile form fields', async ({ page }) => {
    // Find edit button
    const editButton = page.locator('button').filter({ hasText: /Edit|Update/i }).first();
    await editButton.click();
    
    // Clear required field
    const emailInput = page.locator('input[name="email"], [data-testid="email"]').first();
    await emailInput.clear();
    
    // Try to save
    const saveButton = page.locator('button[type="submit"], button').filter({ hasText: /Save|Update/i }).first();
    await saveButton.click();
    
    // Check for validation error
    const errorMessage = page.locator('[role="alert"], .error-message, .text-red-500');
    await expect(errorMessage.first()).toBeVisible({ timeout: 5000 });
  });

  test('should change password', async ({ page }) => {
    // Find change password button/link
    const changePasswordButton = page.locator('button, a').filter({ hasText: /Change Password|Update Password/i }).first();
    
    if (await changePasswordButton.isVisible({ timeout: 5000 })) {
      await changePasswordButton.click();
      
      // Fill password form
      const currentPasswordInput = page.locator('input[name="currentPassword"], [data-testid="current-password"]').first();
      const newPasswordInput = page.locator('input[name="newPassword"], [data-testid="new-password"]').first();
      const confirmPasswordInput = page.locator('input[name="confirmPassword"], [data-testid="confirm-password"]').first();
      
      await currentPasswordInput.fill(testUsers.patient.password);
      await newPasswordInput.fill('NewTestPassword123!');
      await confirmPasswordInput.fill('NewTestPassword123!');
      
      // Submit
      const submitButton = page.locator('button[type="submit"]').filter({ hasText: /Change|Update|Save/i }).first();
      await submitButton.click();
      
      // Wait for success or error
      await page.waitForSelector('text=/Success|Updated|Error|Invalid/i', { timeout: 10000 });
    }
  });

  test('should validate password requirements', async ({ page }) => {
    const changePasswordButton = page.locator('button, a').filter({ hasText: /Change Password|Update Password/i }).first();
    
    if (await changePasswordButton.isVisible({ timeout: 5000 })) {
      await changePasswordButton.click();
      
      // Try weak password
      const newPasswordInput = page.locator('input[name="newPassword"], [data-testid="new-password"]').first();
      await newPasswordInput.fill('weak');
      
      // Submit
      const submitButton = page.locator('button[type="submit"]').filter({ hasText: /Change|Update|Save/i }).first();
      await submitButton.click();
      
      // Check for validation error
      const errorMessage = page.locator('text=/password.*strong|password.*requirements|at least.*characters/i');
      await expect(errorMessage.first()).toBeVisible({ timeout: 5000 });
    }
  });

  test('should display medical history', async ({ page }) => {
    // Navigate to medical history section
    const medicalHistoryTab = page.locator('button, a').filter({ hasText: /Medical History|Health/i }).first();
    
    if (await medicalHistoryTab.isVisible({ timeout: 5000 })) {
      await medicalHistoryTab.click();
      await waitForLoading(page);
      
      // Check medical history section is displayed
      const medicalSection = page.locator('[data-testid="medical-history"], .medical-history');
      const emptyState = page.locator('text=/No medical history|Add medical information/i');
      
      await expect(
        medicalSection.or(emptyState)
      ).toBeVisible({ timeout: 10000 });
    }
  });

  test('should update medical information', async ({ page }) => {
    // Navigate to medical history
    const medicalHistoryTab = page.locator('button, a').filter({ hasText: /Medical History|Health/i }).first();
    
    if (await medicalHistoryTab.isVisible({ timeout: 5000 })) {
      await medicalHistoryTab.click();
      await waitForLoading(page);
      
      // Find edit/add button
      const editButton = page.locator('button').filter({ hasText: /Edit|Add|Update/i }).first();
      await editButton.click();
      
      // Fill medical information
      const allergiesInput = page.locator('textarea[name="allergies"], input[name="allergies"]').first();
      if (await allergiesInput.isVisible({ timeout: 3000 })) {
        await allergiesInput.fill('Penicillin');
      }
      
      const medicationsInput = page.locator('textarea[name="medications"], input[name="medications"]').first();
      if (await medicationsInput.isVisible({ timeout: 3000 })) {
        await medicationsInput.fill('None');
      }
      
      // Save
      const saveButton = page.locator('button[type="submit"]').filter({ hasText: /Save|Update/i }).first();
      await saveButton.click();
      
      // Wait for success
      await page.waitForSelector('text=/Success|Updated|Saved/i', { timeout: 10000 });
    }
  });

  test('should display insurance information', async ({ page }) => {
    // Navigate to insurance section
    const insuranceTab = page.locator('button, a').filter({ hasText: /Insurance/i }).first();
    
    if (await insuranceTab.isVisible({ timeout: 5000 })) {
      await insuranceTab.click();
      await waitForLoading(page);
      
      // Check insurance section is displayed
      const insuranceSection = page.locator('[data-testid="insurance-info"], .insurance-info');
      const emptyState = page.locator('text=/No insurance|Add insurance/i');
      
      await expect(
        insuranceSection.or(emptyState)
      ).toBeVisible({ timeout: 10000 });
    }
  });

  test('should upload profile picture', async ({ page }) => {
    // Find upload button
    const uploadButton = page.locator('button, label').filter({ hasText: /Upload.*Photo|Change.*Picture/i }).first();
    
    if (await uploadButton.isVisible({ timeout: 5000 })) {
      // Create a test image file
      const fileInput = page.locator('input[type="file"]').first();
      
      // Set file input
      await fileInput.setInputFiles({
        name: 'test-avatar.png',
        mimeType: 'image/png',
        buffer: Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', 'base64')
      });
      
      // Wait for upload to complete
      await page.waitForSelector('text=/Success|Uploaded|Updated/i', { timeout: 15000 });
    }
  });

  test('should display notification preferences', async ({ page }) => {
    // Navigate to notifications/preferences
    const preferencesTab = page.locator('button, a').filter({ hasText: /Preferences|Notifications|Settings/i }).first();
    
    if (await preferencesTab.isVisible({ timeout: 5000 })) {
      await preferencesTab.click();
      await waitForLoading(page);
      
      // Check preferences section is displayed
      const preferencesSection = page.locator('[data-testid="preferences"], .preferences, .notification-settings');
      await expect(preferencesSection).toBeVisible({ timeout: 10000 });
    }
  });

  test('should update notification preferences', async ({ page }) => {
    // Navigate to preferences
    const preferencesTab = page.locator('button, a').filter({ hasText: /Preferences|Notifications|Settings/i }).first();
    
    if (await preferencesTab.isVisible({ timeout: 5000 })) {
      await preferencesTab.click();
      await waitForLoading(page);
      
      // Toggle email notifications
      const emailToggle = page.locator('input[type="checkbox"][name*="email"], [data-testid*="email-notification"]').first();
      if (await emailToggle.isVisible({ timeout: 3000 })) {
        await emailToggle.click();
        
        // Save preferences
        const saveButton = page.locator('button').filter({ hasText: /Save|Update/i }).first();
        if (await saveButton.isVisible({ timeout: 3000 })) {
          await saveButton.click();
          await page.waitForSelector('text=/Success|Updated|Saved/i', { timeout: 10000 });
        }
      }
    }
  });

  test('should handle profile data loading errors', async ({ page }) => {
    // Reload page with network offline
    await page.context().setOffline(true);
    await page.reload();
    
    // Check for error message
    await page.waitForSelector('text=/Error|Failed|Unable to load/i', { timeout: 10000 });
    
    // Restore connection
    await page.context().setOffline(false);
  });

  test('should display account activity/security', async ({ page }) => {
    // Navigate to security section
    const securityTab = page.locator('button, a').filter({ hasText: /Security|Activity|Sessions/i }).first();
    
    if (await securityTab.isVisible({ timeout: 5000 })) {
      await securityTab.click();
      await waitForLoading(page);
      
      // Check security section is displayed
      const securitySection = page.locator('[data-testid="security"], .security, .activity-log');
      await expect(securitySection).toBeVisible({ timeout: 10000 });
    }
  });
});

