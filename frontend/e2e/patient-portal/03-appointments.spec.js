import { test, expect } from '@playwright/test';
import { loginAsPatient, waitForLoading, waitForAPI } from '../utils/test-helpers.js';
import { testAppointment } from '../fixtures/test-data.js';

test.describe('Patient Portal - Appointments', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsPatient(page);
    await waitForLoading(page);
    
    // Navigate to appointments page
    await page.goto('/patient/appointments');
    await waitForLoading(page);
  });

  test('should display appointments list', async ({ page }) => {
    // Check page title
    await expect(page.locator('h1, h2').filter({ hasText: /Appointments/i }).first()).toBeVisible();
    
    // Check for appointments list or empty state
    const appointmentsList = page.locator('[data-testid="appointments-list"]');
    const emptyState = page.locator('text=/No appointments|Schedule your first/i');
    
    await expect(
      appointmentsList.or(emptyState)
    ).toBeVisible({ timeout: 10000 });
  });

  test('should open book appointment dialog', async ({ page }) => {
    // Find and click book appointment button
    const bookButton = page.locator('button, a').filter({ hasText: /Book|Schedule|New Appointment/i }).first();
    await bookButton.click();
    
    // Check dialog/modal opens
    const dialog = page.locator('[role="dialog"], .modal, .dialog');
    await expect(dialog).toBeVisible({ timeout: 5000 });
    
    // Check form fields exist
    await expect(page.locator('input[type="date"], [data-testid="date-picker"]')).toBeVisible();
  });

  test('should validate appointment booking form', async ({ page }) => {
    // Open booking dialog
    const bookButton = page.locator('button, a').filter({ hasText: /Book|Schedule|New Appointment/i }).first();
    await bookButton.click();
    
    // Try to submit without filling required fields
    const submitButton = page.locator('button[type="submit"]').filter({ hasText: /Book|Schedule|Confirm/i });
    await submitButton.click();
    
    // Check for validation errors
    const errorMessage = page.locator('[role="alert"], .error-message, .text-red-500');
    await expect(errorMessage.first()).toBeVisible({ timeout: 5000 });
  });

  test('should book an appointment successfully', async ({ page }) => {
    // Open booking dialog
    const bookButton = page.locator('button, a').filter({ hasText: /Book|Schedule|New Appointment/i }).first();
    await bookButton.click();
    
    // Fill appointment details
    const dateInput = page.locator('input[type="date"], [data-testid="date-picker"]').first();
    await dateInput.fill(testAppointment.date);
    
    // Select time if available
    const timeSelect = page.locator('select[name="time"], input[type="time"]').first();
    if (await timeSelect.isVisible()) {
      await timeSelect.fill(testAppointment.time);
    }
    
    // Select appointment type if available
    const typeSelect = page.locator('select[name="type"], [data-testid="appointment-type"]').first();
    if (await typeSelect.isVisible()) {
      await typeSelect.selectOption(testAppointment.type);
    }
    
    // Add notes if available
    const notesInput = page.locator('textarea[name="notes"], input[name="notes"]').first();
    if (await notesInput.isVisible()) {
      await notesInput.fill(testAppointment.notes);
    }
    
    // Submit form
    const submitButton = page.locator('button[type="submit"]').filter({ hasText: /Book|Schedule|Confirm/i });
    await submitButton.click();
    
    // Wait for success message or redirect
    await page.waitForSelector('text=/Success|Confirmed|Booked/i', { timeout: 15000 });
    
    // Verify appointment appears in list
    await waitForLoading(page);
    const appointmentItem = page.locator(`text=${testAppointment.date}`);
    await expect(appointmentItem).toBeVisible({ timeout: 10000 });
  });

  test('should filter appointments by status', async ({ page }) => {
    // Check if filter exists
    const filterSelect = page.locator('select[name="status"], [data-testid="status-filter"]').first();
    
    if (await filterSelect.isVisible()) {
      // Select "Upcoming" filter
      await filterSelect.selectOption('upcoming');
      await waitForLoading(page);
      
      // Verify filtered results
      const appointmentsList = page.locator('[data-testid="appointments-list"]');
      await expect(appointmentsList).toBeVisible();
    }
  });

  test('should view appointment details', async ({ page }) => {
    // Find first appointment in list
    const firstAppointment = page.locator('[data-testid="appointment-item"], .appointment-card').first();
    
    if (await firstAppointment.isVisible()) {
      await firstAppointment.click();
      
      // Check details modal/page opens
      const detailsView = page.locator('[data-testid="appointment-details"], .appointment-details');
      await expect(detailsView).toBeVisible({ timeout: 5000 });
      
      // Check details are displayed
      await expect(page.locator('text=/Date|Time|Type|Status/i').first()).toBeVisible();
    }
  });

  test('should cancel an appointment', async ({ page }) => {
    // Find first appointment
    const firstAppointment = page.locator('[data-testid="appointment-item"], .appointment-card').first();
    
    if (await firstAppointment.isVisible()) {
      // Click to view details
      await firstAppointment.click();
      
      // Find cancel button
      const cancelButton = page.locator('button').filter({ hasText: /Cancel|Delete/i }).first();
      
      if (await cancelButton.isVisible()) {
        await cancelButton.click();
        
        // Confirm cancellation if confirmation dialog appears
        const confirmButton = page.locator('button').filter({ hasText: /Confirm|Yes|OK/i }).first();
        if (await confirmButton.isVisible({ timeout: 2000 })) {
          await confirmButton.click();
        }
        
        // Wait for success message
        await page.waitForSelector('text=/Cancelled|Deleted|Removed/i', { timeout: 10000 });
      }
    }
  });

  test('should reschedule an appointment', async ({ page }) => {
    // Find first appointment
    const firstAppointment = page.locator('[data-testid="appointment-item"], .appointment-card').first();
    
    if (await firstAppointment.isVisible()) {
      // Click to view details
      await firstAppointment.click();
      
      // Find reschedule button
      const rescheduleButton = page.locator('button').filter({ hasText: /Reschedule|Change/i }).first();
      
      if (await rescheduleButton.isVisible()) {
        await rescheduleButton.click();
        
        // Wait for reschedule form
        const dateInput = page.locator('input[type="date"]').first();
        await expect(dateInput).toBeVisible({ timeout: 5000 });
        
        // Change date
        const newDate = '2025-10-25';
        await dateInput.fill(newDate);
        
        // Submit
        const submitButton = page.locator('button[type="submit"]').filter({ hasText: /Save|Confirm|Update/i });
        await submitButton.click();
        
        // Wait for success
        await page.waitForSelector('text=/Updated|Rescheduled|Success/i', { timeout: 10000 });
      }
    }
  });

  test('should display appointment history', async ({ page }) => {
    // Check for history tab/section
    const historyTab = page.locator('button, a').filter({ hasText: /History|Past/i }).first();
    
    if (await historyTab.isVisible()) {
      await historyTab.click();
      await waitForLoading(page);
      
      // Check past appointments are displayed
      const pastAppointments = page.locator('[data-testid="past-appointments"]');
      const emptyState = page.locator('text=/No past appointments/i');
      
      await expect(
        pastAppointments.or(emptyState)
      ).toBeVisible({ timeout: 10000 });
    }
  });
});

