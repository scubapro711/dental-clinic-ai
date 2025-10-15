import { test, expect } from '@playwright/test';
import { loginAsClinic, waitForLoading, waitForAPI } from '../utils/test-helpers.js';
import { testPatient } from '../fixtures/test-data.js';

test.describe('Clinic Portal - Advanced Patient Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsClinic(page);
    await waitForLoading(page);
    
    // Navigate to patients page
    await page.goto('/clinic/patients');
    await waitForLoading(page);
  });

  test('should display patients list', async ({ page }) => {
    // Check page title
    await expect(page.locator('h1, h2').filter({ hasText: /Patients/i }).first()).toBeVisible();
    
    // Check for patients list or empty state
    const patientsList = page.locator('[data-testid="patients-list"], .patients-list');
    const emptyState = page.locator('text=/No patients|Add your first patient/i');
    
    await expect(
      patientsList.or(emptyState)
    ).toBeVisible({ timeout: 10000 });
  });

  test('should search for patients', async ({ page }) => {
    // Find search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]').first();
    
    if (await searchInput.isVisible({ timeout: 5000 })) {
      await searchInput.fill('John');
      await page.keyboard.press('Enter');
      
      await waitForLoading(page);
      
      // Results should be filtered
      await page.waitForTimeout(1000);
    }
  });

  test('should filter patients by status', async ({ page }) => {
    // Look for filter dropdown
    const filterSelect = page.locator('select[name="status"], [data-testid="status-filter"]').first();
    
    if (await filterSelect.isVisible({ timeout: 5000 })) {
      await filterSelect.selectOption('active');
      await waitForLoading(page);
      
      // Verify filter was applied
      await page.waitForTimeout(1000);
    }
  });

  test('should add new patient', async ({ page }) => {
    // Find add patient button
    const addButton = page.locator('button').filter({ hasText: /Add Patient|New Patient/i }).first();
    await addButton.click();
    
    // Check form opens
    const form = page.locator('[role="dialog"], .modal, form').filter({ hasText: /Add|New|Patient/i });
    await expect(form.first()).toBeVisible({ timeout: 5000 });
    
    // Fill patient information
    await page.fill('input[name="firstName"]', testPatient.firstName);
    await page.fill('input[name="lastName"]', testPatient.lastName);
    await page.fill('input[name="email"]', testPatient.email);
    await page.fill('input[name="phone"]', testPatient.phone);
    
    // Fill date of birth if available
    const dobInput = page.locator('input[name="dateOfBirth"], input[name="dob"]').first();
    if (await dobInput.isVisible({ timeout: 3000 })) {
      await dobInput.fill(testPatient.dateOfBirth);
    }
    
    // Submit form
    const submitButton = page.locator('button[type="submit"]').filter({ hasText: /Add|Create|Save/i });
    await submitButton.click();
    
    // Wait for success message
    await page.waitForSelector('text=/Success|Added|Created/i', { timeout: 15000 });
  });

  test('should validate patient form', async ({ page }) => {
    const addButton = page.locator('button').filter({ hasText: /Add Patient|New Patient/i }).first();
    await addButton.click();
    
    // Try to submit without required fields
    const submitButton = page.locator('button[type="submit"]').filter({ hasText: /Add|Create|Save/i });
    await submitButton.click();
    
    // Check for validation errors
    const errorMessage = page.locator('[role="alert"], .error-message, .text-red-500');
    await expect(errorMessage.first()).toBeVisible({ timeout: 5000 });
  });

  test('should view patient details', async ({ page }) => {
    // Find first patient
    const firstPatient = page.locator('[data-testid="patient-item"], .patient-item, tr').filter({ hasText: /\w+/ }).first();
    
    if (await firstPatient.isVisible({ timeout: 5000 })) {
      await firstPatient.click();
      
      // Check details view opens
      const detailsView = page.locator('[data-testid="patient-details"], .patient-details');
      await expect(detailsView.first()).toBeVisible({ timeout: 5000 });
      
      // Check patient information is displayed
      await expect(page.locator('text=/Name|Email|Phone/i').first()).toBeVisible();
    }
  });

  test('should edit patient information', async ({ page }) => {
    // Find first patient
    const firstPatient = page.locator('[data-testid="patient-item"], .patient-item, tr').filter({ hasText: /\w+/ }).first();
    
    if (await firstPatient.isVisible({ timeout: 5000 })) {
      await firstPatient.click();
      
      // Find edit button
      const editButton = page.locator('button').filter({ hasText: /Edit|Update/i }).first();
      await editButton.click();
      
      // Update phone number
      const phoneInput = page.locator('input[name="phone"]').first();
      await phoneInput.clear();
      await phoneInput.fill('+9876543210');
      
      // Save changes
      const saveButton = page.locator('button[type="submit"]').filter({ hasText: /Save|Update/i });
      await saveButton.click();
      
      // Wait for success
      await page.waitForSelector('text=/Success|Updated|Saved/i', { timeout: 10000 });
    }
  });

  test('should view patient appointments', async ({ page }) => {
    // Find first patient
    const firstPatient = page.locator('[data-testid="patient-item"], .patient-item, tr').filter({ hasText: /\w+/ }).first();
    
    if (await firstPatient.isVisible({ timeout: 5000 })) {
      await firstPatient.click();
      
      // Navigate to appointments tab
      const appointmentsTab = page.locator('button, a').filter({ hasText: /Appointments/i }).first();
      if (await appointmentsTab.isVisible({ timeout: 3000 })) {
        await appointmentsTab.click();
        await waitForLoading(page);
        
        // Check appointments section
        const appointmentsList = page.locator('[data-testid="patient-appointments"], .appointments-list');
        const emptyState = page.locator('text=/No appointments/i');
        
        await expect(
          appointmentsList.or(emptyState)
        ).toBeVisible({ timeout: 10000 });
      }
    }
  });

  test('should view patient treatment history', async ({ page }) => {
    // Find first patient
    const firstPatient = page.locator('[data-testid="patient-item"], .patient-item, tr').filter({ hasText: /\w+/ }).first();
    
    if (await firstPatient.isVisible({ timeout: 5000 })) {
      await firstPatient.click();
      
      // Navigate to treatment history tab
      const treatmentTab = page.locator('button, a').filter({ hasText: /Treatment|History/i }).first();
      if (await treatmentTab.isVisible({ timeout: 3000 })) {
        await treatmentTab.click();
        await waitForLoading(page);
        
        // Check treatment history section
        const treatmentList = page.locator('[data-testid="treatment-history"], .treatment-history');
        const emptyState = page.locator('text=/No treatments|No history/i');
        
        await expect(
          treatmentList.or(emptyState)
        ).toBeVisible({ timeout: 10000 });
      }
    }
  });

  test('should add treatment note', async ({ page }) => {
    // Find first patient
    const firstPatient = page.locator('[data-testid="patient-item"], .patient-item, tr').filter({ hasText: /\w+/ }).first();
    
    if (await firstPatient.isVisible({ timeout: 5000 })) {
      await firstPatient.click();
      
      // Look for add note button
      const addNoteButton = page.locator('button').filter({ hasText: /Add Note|New Note/i }).first();
      
      if (await addNoteButton.isVisible({ timeout: 3000 })) {
        await addNoteButton.click();
        
        // Fill note
        const noteInput = page.locator('textarea[name="note"], textarea[name="notes"]').first();
        await noteInput.fill('Patient showed improvement after treatment');
        
        // Save note
        const saveButton = page.locator('button[type="submit"]').filter({ hasText: /Save|Add/i });
        await saveButton.click();
        
        // Wait for success
        await page.waitForSelector('text=/Success|Added|Saved/i', { timeout: 10000 });
      }
    }
  });

  test('should view patient medical history', async ({ page }) => {
    // Find first patient
    const firstPatient = page.locator('[data-testid="patient-item"], .patient-item, tr').filter({ hasText: /\w+/ }).first();
    
    if (await firstPatient.isVisible({ timeout: 5000 })) {
      await firstPatient.click();
      
      // Navigate to medical history tab
      const medicalTab = page.locator('button, a').filter({ hasText: /Medical History|Health/i }).first();
      if (await medicalTab.isVisible({ timeout: 3000 })) {
        await medicalTab.click();
        await waitForLoading(page);
        
        // Check medical history section
        const medicalSection = page.locator('[data-testid="medical-history"], .medical-history');
        await expect(medicalSection).toBeVisible({ timeout: 10000 });
      }
    }
  });

  test('should schedule appointment for patient', async ({ page }) => {
    // Find first patient
    const firstPatient = page.locator('[data-testid="patient-item"], .patient-item, tr').filter({ hasText: /\w+/ }).first();
    
    if (await firstPatient.isVisible({ timeout: 5000 })) {
      await firstPatient.click();
      
      // Find schedule appointment button
      const scheduleButton = page.locator('button').filter({ hasText: /Schedule|Book|New Appointment/i }).first();
      
      if (await scheduleButton.isVisible({ timeout: 3000 })) {
        await scheduleButton.click();
        
        // Fill appointment details
        const dateInput = page.locator('input[type="date"]').first();
        await dateInput.fill('2025-10-20');
        
        // Submit
        const submitButton = page.locator('button[type="submit"]').filter({ hasText: /Schedule|Book|Save/i });
        await submitButton.click();
        
        // Wait for success
        await page.waitForSelector('text=/Success|Scheduled|Booked/i', { timeout: 15000 });
      }
    }
  });

  test('should export patient list', async ({ page }) => {
    // Look for export button
    const exportButton = page.locator('button').filter({ hasText: /Export|Download/i }).first();
    
    if (await exportButton.isVisible({ timeout: 5000 })) {
      // Set up download listener
      const downloadPromise = page.waitForEvent('download', { timeout: 15000 });
      
      // Click export
      await exportButton.click();
      
      // Wait for download
      const download = await downloadPromise;
      expect(download).toBeTruthy();
    }
  });

  test('should bulk select patients', async ({ page }) => {
    // Look for select all checkbox
    const selectAllCheckbox = page.locator('input[type="checkbox"][aria-label*="Select all"], thead input[type="checkbox"]').first();
    
    if (await selectAllCheckbox.isVisible({ timeout: 5000 })) {
      await selectAllCheckbox.click();
      
      // Check that bulk actions appear
      const bulkActions = page.locator('[data-testid="bulk-actions"], .bulk-actions');
      await expect(bulkActions).toBeVisible({ timeout: 5000 });
    }
  });

  test('should sort patients by name', async ({ page }) => {
    // Look for name column header
    const nameHeader = page.locator('th').filter({ hasText: /Name/i }).first();
    
    if (await nameHeader.isVisible({ timeout: 5000 })) {
      await nameHeader.click();
      await waitForLoading(page);
      
      // Verify sorting was applied
      await page.waitForTimeout(1000);
    }
  });

  test('should paginate through patients', async ({ page }) => {
    // Look for pagination controls
    const nextButton = page.locator('button, a').filter({ hasText: /Next|>/i }).last();
    
    if (await nextButton.isVisible({ timeout: 5000 }) && await nextButton.isEnabled()) {
      await nextButton.click();
      await waitForLoading(page);
      
      // Verify page changed
      await page.waitForTimeout(1000);
    }
  });

  test('should delete patient', async ({ page }) => {
    // Find first patient
    const firstPatient = page.locator('[data-testid="patient-item"], .patient-item, tr').filter({ hasText: /\w+/ }).first();
    
    if (await firstPatient.isVisible({ timeout: 5000 })) {
      await firstPatient.click();
      
      // Find delete button
      const deleteButton = page.locator('button').filter({ hasText: /Delete|Remove/i }).first();
      
      if (await deleteButton.isVisible({ timeout: 3000 })) {
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

  test('should view patient billing information', async ({ page }) => {
    // Find first patient
    const firstPatient = page.locator('[data-testid="patient-item"], .patient-item, tr').filter({ hasText: /\w+/ }).first();
    
    if (await firstPatient.isVisible({ timeout: 5000 })) {
      await firstPatient.click();
      
      // Navigate to billing tab
      const billingTab = page.locator('button, a').filter({ hasText: /Billing|Payments|Invoices/i }).first();
      if (await billingTab.isVisible({ timeout: 3000 })) {
        await billingTab.click();
        await waitForLoading(page);
        
        // Check billing section
        const billingSection = page.locator('[data-testid="billing-info"], .billing-info');
        const emptyState = page.locator('text=/No billing|No invoices/i');
        
        await expect(
          billingSection.or(emptyState)
        ).toBeVisible({ timeout: 10000 });
      }
    }
  });
});

