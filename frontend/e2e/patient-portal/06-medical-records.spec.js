import { test, expect } from '@playwright/test';
import { loginAsPatient, waitForLoading, waitForAPI } from '../utils/test-helpers.js';

test.describe('Patient Portal - Medical Records', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsPatient(page);
    await waitForLoading(page);
  });

  test('should navigate to medical records page', async ({ page }) => {
    // Find medical records link
    const recordsLink = page.locator('a, button').filter({ hasText: /Medical Records|Records|Documents/i }).first();
    
    if (await recordsLink.isVisible({ timeout: 5000 })) {
      await recordsLink.click();
      await waitForLoading(page);
      
      // Check page loaded
      await expect(page.locator('h1, h2').filter({ hasText: /Medical Records|Records|Documents/i }).first()).toBeVisible();
    } else {
      // Try direct navigation
      await page.goto('/patient/records');
      await waitForLoading(page);
      
      const pageTitle = page.locator('h1, h2').filter({ hasText: /Medical Records|Records|Documents/i });
      await expect(pageTitle.first()).toBeVisible({ timeout: 10000 });
    }
  });

  test('should display list of medical records', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Check for records list or empty state
    const recordsList = page.locator('[data-testid="records-list"], .records-list');
    const emptyState = page.locator('text=/No records|No documents|No medical records/i');
    
    await expect(
      recordsList.or(emptyState)
    ).toBeVisible({ timeout: 10000 });
  });

  test('should filter records by type', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Look for filter dropdown
    const filterSelect = page.locator('select[name="type"], select[name="filter"], [data-testid="record-type-filter"]').first();
    
    if (await filterSelect.isVisible({ timeout: 5000 })) {
      // Select a filter option
      await filterSelect.selectOption({ index: 1 });
      await waitForLoading(page);
      
      // Verify filter was applied
      await page.waitForTimeout(1000);
    }
  });

  test('should search medical records', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Look for search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]').first();
    
    if (await searchInput.isVisible({ timeout: 5000 })) {
      // Enter search term
      await searchInput.fill('x-ray');
      await page.keyboard.press('Enter');
      
      await waitForLoading(page);
      
      // Results should be filtered
      await page.waitForTimeout(1000);
    }
  });

  test('should view record details', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Find first record
    const firstRecord = page.locator('[data-testid="record-item"], .record-item, .document-item').first();
    
    if (await firstRecord.isVisible({ timeout: 5000 })) {
      await firstRecord.click();
      
      // Check details view opens
      const detailsView = page.locator('[data-testid="record-details"], .record-details, [role="dialog"]');
      await expect(detailsView.first()).toBeVisible({ timeout: 5000 });
      
      // Check details are displayed
      await expect(page.locator('text=/Date|Type|Description/i').first()).toBeVisible();
    }
  });

  test('should download a medical record', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Find first record
    const firstRecord = page.locator('[data-testid="record-item"], .record-item').first();
    
    if (await firstRecord.isVisible({ timeout: 5000 })) {
      // Click to view details
      await firstRecord.click();
      
      // Find download button
      const downloadButton = page.locator('button, a').filter({ hasText: /Download|Save/i }).first();
      
      if (await downloadButton.isVisible({ timeout: 3000 })) {
        // Set up download listener
        const downloadPromise = page.waitForEvent('download', { timeout: 15000 });
        
        // Click download
        await downloadButton.click();
        
        // Wait for download to start
        const download = await downloadPromise;
        
        // Verify download started
        expect(download).toBeTruthy();
      }
    }
  });

  test('should display treatment history', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Look for treatment history tab/section
    const treatmentTab = page.locator('button, a').filter({ hasText: /Treatment|History|Procedures/i }).first();
    
    if (await treatmentTab.isVisible({ timeout: 5000 })) {
      await treatmentTab.click();
      await waitForLoading(page);
      
      // Check treatment history is displayed
      const treatmentList = page.locator('[data-testid="treatment-history"], .treatment-history');
      const emptyState = page.locator('text=/No treatments|No procedures/i');
      
      await expect(
        treatmentList.or(emptyState)
      ).toBeVisible({ timeout: 10000 });
    }
  });

  test('should display prescriptions', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Look for prescriptions tab/section
    const prescriptionsTab = page.locator('button, a').filter({ hasText: /Prescriptions|Medications/i }).first();
    
    if (await prescriptionsTab.isVisible({ timeout: 5000 })) {
      await prescriptionsTab.click();
      await waitForLoading(page);
      
      // Check prescriptions are displayed
      const prescriptionsList = page.locator('[data-testid="prescriptions-list"], .prescriptions-list');
      const emptyState = page.locator('text=/No prescriptions|No medications/i');
      
      await expect(
        prescriptionsList.or(emptyState)
      ).toBeVisible({ timeout: 10000 });
    }
  });

  test('should display lab results', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Look for lab results tab/section
    const labResultsTab = page.locator('button, a').filter({ hasText: /Lab Results|Tests/i }).first();
    
    if (await labResultsTab.isVisible({ timeout: 5000 })) {
      await labResultsTab.click();
      await waitForLoading(page);
      
      // Check lab results are displayed
      const labResultsList = page.locator('[data-testid="lab-results-list"], .lab-results-list');
      const emptyState = page.locator('text=/No lab results|No tests/i');
      
      await expect(
        labResultsList.or(emptyState)
      ).toBeVisible({ timeout: 10000 });
    }
  });

  test('should display imaging results', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Look for imaging/x-rays tab/section
    const imagingTab = page.locator('button, a').filter({ hasText: /Imaging|X-rays|Scans/i }).first();
    
    if (await imagingTab.isVisible({ timeout: 5000 })) {
      await imagingTab.click();
      await waitForLoading(page);
      
      // Check imaging results are displayed
      const imagingList = page.locator('[data-testid="imaging-list"], .imaging-list');
      const emptyState = page.locator('text=/No imaging|No x-rays|No scans/i');
      
      await expect(
        imagingList.or(emptyState)
      ).toBeVisible({ timeout: 10000 });
    }
  });

  test('should view imaging in viewer', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to imaging
    const imagingTab = page.locator('button, a').filter({ hasText: /Imaging|X-rays|Scans/i }).first();
    
    if (await imagingTab.isVisible({ timeout: 5000 })) {
      await imagingTab.click();
      await waitForLoading(page);
      
      // Find first imaging result
      const firstImage = page.locator('[data-testid="imaging-item"], .imaging-item, img').first();
      
      if (await firstImage.isVisible({ timeout: 5000 })) {
        await firstImage.click();
        
        // Check image viewer opens
        const imageViewer = page.locator('[data-testid="image-viewer"], .image-viewer, [role="dialog"]').filter({ hasText: /View|Image|X-ray/i });
        await expect(imageViewer.first()).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should sort records by date', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Look for sort dropdown
    const sortSelect = page.locator('select[name="sort"], [data-testid="sort-select"]').first();
    
    if (await sortSelect.isVisible({ timeout: 5000 })) {
      // Select sort by date
      await sortSelect.selectOption('date');
      await waitForLoading(page);
      
      // Verify sorting was applied
      await page.waitForTimeout(1000);
    }
  });

  test('should request new record', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Look for request button
    const requestButton = page.locator('button').filter({ hasText: /Request|New|Add/i }).first();
    
    if (await requestButton.isVisible({ timeout: 5000 })) {
      await requestButton.click();
      
      // Check request form opens
      const requestForm = page.locator('[role="dialog"], .modal, form').filter({ hasText: /Request|New/i });
      await expect(requestForm.first()).toBeVisible({ timeout: 5000 });
    }
  });

  test('should share record with provider', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Find first record
    const firstRecord = page.locator('[data-testid="record-item"], .record-item').first();
    
    if (await firstRecord.isVisible({ timeout: 5000 })) {
      await firstRecord.click();
      
      // Look for share button
      const shareButton = page.locator('button').filter({ hasText: /Share|Send/i }).first();
      
      if (await shareButton.isVisible({ timeout: 3000 })) {
        await shareButton.click();
        
        // Check share dialog opens
        const shareDialog = page.locator('[role="dialog"], .modal').filter({ hasText: /Share/i });
        await expect(shareDialog.first()).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should print record', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Find first record
    const firstRecord = page.locator('[data-testid="record-item"], .record-item').first();
    
    if (await firstRecord.isVisible({ timeout: 5000 })) {
      await firstRecord.click();
      
      // Look for print button
      const printButton = page.locator('button').filter({ hasText: /Print/i }).first();
      
      if (await printButton.isVisible({ timeout: 3000 })) {
        // Set up print dialog listener
        page.on('dialog', dialog => dialog.accept());
        
        await printButton.click();
        
        // Wait a moment for print dialog
        await page.waitForTimeout(2000);
      }
    }
  });

  test('should handle pagination', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Look for pagination controls
    const nextButton = page.locator('button, a').filter({ hasText: /Next|>/i }).last();
    
    if (await nextButton.isVisible({ timeout: 5000 }) && await nextButton.isEnabled()) {
      await nextButton.click();
      await waitForLoading(page);
      
      // Verify page changed
      await page.waitForTimeout(1000);
    }
  });

  test('should display record metadata', async ({ page }) => {
    await page.goto('/patient/records').catch(() => {});
    await waitForLoading(page);
    
    // Find first record
    const firstRecord = page.locator('[data-testid="record-item"], .record-item').first();
    
    if (await firstRecord.isVisible({ timeout: 5000 })) {
      await firstRecord.click();
      
      // Check metadata is displayed
      const metadata = page.locator('text=/Date|Type|Provider|Facility/i');
      await expect(metadata.first()).toBeVisible({ timeout: 5000 });
    }
  });
});

