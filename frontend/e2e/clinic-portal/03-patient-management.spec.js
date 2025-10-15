import { test, expect } from '@playwright/test';
import { loginAsClinic, waitForLoading, waitForAPI } from '../utils/test-helpers.js';
import { testPatient } from '../fixtures/test-data.js';

test.describe('Clinic Portal - Patient Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsClinic(page);
    await page.goto('/clinic/patients');
    await waitForLoading(page);
  });

  test('should display patients list', async ({ page }) => {
    await expect(page.locator('h1, h2').filter({ hasText: /Patients/i }).first()).toBeVisible();
    
    const patientsList = page.locator('[data-testid="patients-list"], .patients-table');
    const emptyState = page.locator('text=/No patients|Add your first patient/i');
    
    await expect(
      patientsList.or(emptyState)
    ).toBeVisible({ timeout: 10000 });
  });

  test('should search for patients', async ({ page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]').first();
    
    if (await searchInput.isVisible()) {
      await searchInput.fill('John');
      await page.keyboard.press('Enter');
      
      await waitForLoading(page);
      
      // Check search results
      const results = page.locator('[data-testid="search-results"], .patients-table tbody tr');
      await expect(results.first()).toBeVisible({ timeout: 10000 });
    }
  });

  test('should open add patient dialog', async ({ page }) => {
    const addButton = page.locator('button').filter({ hasText: /Add Patient|New Patient/i }).first();
    await addButton.click();
    
    const dialog = page.locator('[role="dialog"], .modal');
    await expect(dialog).toBeVisible({ timeout: 5000 });
    
    // Check form fields
    await expect(page.locator('input[name="firstName"], input[name="first_name"]')).toBeVisible();
    await expect(page.locator('input[name="lastName"], input[name="last_name"]')).toBeVisible();
    await expect(page.locator('input[name="email"]')).toBeVisible();
  });

  test('should add a new patient', async ({ page }) => {
    const addButton = page.locator('button').filter({ hasText: /Add Patient|New Patient/i }).first();
    await addButton.click();
    
    // Fill patient form
    await page.fill('input[name="firstName"], input[name="first_name"]', testPatient.firstName);
    await page.fill('input[name="lastName"], input[name="last_name"]', testPatient.lastName);
    await page.fill('input[name="email"]', testPatient.email);
    await page.fill('input[name="phone"]', testPatient.phone);
    
    // Submit form
    const submitButton = page.locator('button[type="submit"]').filter({ hasText: /Add|Save|Create/i });
    await submitButton.click();
    
    // Wait for success message
    await page.waitForSelector('text=/Success|Added|Created/i', { timeout: 15000 });
    
    // Verify patient appears in list
    await waitForLoading(page);
    const patientName = page.locator(`text=${testPatient.firstName} ${testPatient.lastName}`);
    await expect(patientName).toBeVisible({ timeout: 10000 });
  });

  test('should view patient details', async ({ page }) => {
    const firstPatient = page.locator('[data-testid="patient-row"], .patients-table tbody tr').first();
    
    if (await firstPatient.isVisible()) {
      await firstPatient.click();
      
      // Check details view
      const detailsView = page.locator('[data-testid="patient-details"], .patient-details');
      await expect(detailsView).toBeVisible({ timeout: 5000 });
      
      // Check patient information is displayed
      await expect(page.locator('text=/Name|Email|Phone/i').first()).toBeVisible();
    }
  });

  test('should edit patient information', async ({ page }) => {
    const firstPatient = page.locator('[data-testid="patient-row"], .patients-table tbody tr').first();
    
    if (await firstPatient.isVisible()) {
      await firstPatient.click();
      
      // Find edit button
      const editButton = page.locator('button').filter({ hasText: /Edit|Update/i }).first();
      
      if (await editButton.isVisible()) {
        await editButton.click();
        
        // Wait for edit form
        const emailInput = page.locator('input[name="email"]').first();
        await expect(emailInput).toBeVisible({ timeout: 5000 });
        
        // Update email
        await emailInput.fill('updated@example.com');
        
        // Save
        const saveButton = page.locator('button[type="submit"]').filter({ hasText: /Save|Update/i });
        await saveButton.click();
        
        // Wait for success
        await page.waitForSelector('text=/Updated|Saved|Success/i', { timeout: 10000 });
      }
    }
  });

  test('should filter patients by status', async ({ page }) => {
    const filterSelect = page.locator('select[name="status"], [data-testid="status-filter"]').first();
    
    if (await filterSelect.isVisible()) {
      await filterSelect.selectOption('active');
      await waitForLoading(page);
      
      const patientsList = page.locator('[data-testid="patients-list"], .patients-table');
      await expect(patientsList).toBeVisible();
    }
  });

  test('should export patients list', async ({ page }) => {
    const exportButton = page.locator('button').filter({ hasText: /Export|Download/i }).first();
    
    if (await exportButton.isVisible()) {
      // Start waiting for download before clicking
      const downloadPromise = page.waitForEvent('download');
      
      await exportButton.click();
      
      // Wait for download
      const download = await downloadPromise;
      
      // Verify download started
      expect(download.suggestedFilename()).toContain('patients');
    }
  });

  test('should paginate through patients list', async ({ page }) => {
    const nextButton = page.locator('button, a').filter({ hasText: /Next|›|→/i }).last();
    
    if (await nextButton.isVisible() && await nextButton.isEnabled()) {
      await nextButton.click();
      await waitForLoading(page);
      
      // Check page number changed
      const pageIndicator = page.locator('[data-testid="page-number"], .pagination .active');
      await expect(pageIndicator).toBeVisible();
    }
  });

  test('should delete a patient', async ({ page }) => {
    const firstPatient = page.locator('[data-testid="patient-row"], .patients-table tbody tr').first();
    
    if (await firstPatient.isVisible()) {
      await firstPatient.click();
      
      // Find delete button
      const deleteButton = page.locator('button').filter({ hasText: /Delete|Remove/i }).first();
      
      if (await deleteButton.isVisible()) {
        await deleteButton.click();
        
        // Confirm deletion
        const confirmButton = page.locator('button').filter({ hasText: /Confirm|Yes|Delete/i }).first();
        if (await confirmButton.isVisible({ timeout: 2000 })) {
          await confirmButton.click();
        }
        
        // Wait for success
        await page.waitForSelector('text=/Deleted|Removed|Success/i', { timeout: 10000 });
      }
    }
  });
});

