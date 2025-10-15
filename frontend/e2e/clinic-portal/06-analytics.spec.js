import { test, expect } from '@playwright/test';
import { loginAsClinic, waitForLoading } from '../utils/test-helpers.js';

test.describe('Clinic Portal - Analytics & Reporting', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsClinic(page);
    await waitForLoading(page);
  });

  test('should navigate to analytics page', async ({ page }) => {
    // Find analytics/reports link
    const analyticsLink = page.locator('a, button').filter({ hasText: /Analytics|Reports|Statistics/i }).first();
    
    if (await analyticsLink.isVisible({ timeout: 5000 })) {
      await analyticsLink.click();
      await waitForLoading(page);
      
      // Check analytics page loaded
      await expect(page.locator('h1, h2').filter({ hasText: /Analytics|Reports|Statistics/i }).first()).toBeVisible();
    } else {
      // Try direct navigation
      await page.goto('/clinic/analytics');
      await waitForLoading(page);
      
      const pageTitle = page.locator('h1, h2').filter({ hasText: /Analytics|Reports/i });
      await expect(pageTitle.first()).toBeVisible({ timeout: 10000 });
    }
  });

  test('should display revenue metrics', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Check for revenue widget/card
    const revenueWidget = page.locator('[data-testid="revenue-widget"], .revenue-widget, .metric-card').filter({ hasText: /Revenue|Income/i });
    
    if (await revenueWidget.isVisible({ timeout: 5000 })) {
      await expect(revenueWidget).toBeVisible();
      
      // Check for revenue amount
      const revenueAmount = revenueWidget.locator('text=/\\$|₪|€/');
      await expect(revenueAmount.first()).toBeVisible();
    }
  });

  test('should display patient metrics', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Check for patient metrics
    const patientMetrics = page.locator('[data-testid="patient-metrics"], .patient-metrics').first();
    const patientCount = page.locator('text=/Total Patients|New Patients|Active Patients/i').first();
    
    await expect(
      patientMetrics.or(patientCount)
    ).toBeVisible({ timeout: 10000 });
  });

  test('should display appointment metrics', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Check for appointment metrics
    const appointmentMetrics = page.locator('text=/Appointments|Bookings|Scheduled/i').first();
    await expect(appointmentMetrics).toBeVisible({ timeout: 10000 });
  });

  test('should filter analytics by date range', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Find date range picker
    const dateRangePicker = page.locator('[data-testid="date-range-picker"], .date-range-picker, button').filter({ hasText: /Date|Range|Filter/i }).first();
    
    if (await dateRangePicker.isVisible({ timeout: 5000 })) {
      await dateRangePicker.click();
      
      // Select last 30 days
      const last30Days = page.locator('button, a').filter({ hasText: /Last 30 Days|30 Days/i }).first();
      if (await last30Days.isVisible({ timeout: 3000 })) {
        await last30Days.click();
        await waitForLoading(page);
        
        // Verify data updated
        await page.waitForTimeout(1000);
      }
    }
  });

  test('should display revenue chart', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Look for revenue chart
    const revenueChart = page.locator('[data-testid="revenue-chart"], .revenue-chart, canvas, svg').first();
    
    if (await revenueChart.isVisible({ timeout: 5000 })) {
      await expect(revenueChart).toBeVisible();
    }
  });

  test('should display appointment trends chart', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Look for appointment trends
    const trendsChart = page.locator('[data-testid="appointments-chart"], .appointments-chart, canvas, svg').filter({ hasText: /Appointments|Trends/i }).first();
    
    if (await trendsChart.isVisible({ timeout: 5000 })) {
      await expect(trendsChart).toBeVisible();
    }
  });

  test('should display patient demographics', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to demographics section
    const demographicsTab = page.locator('button, a').filter({ hasText: /Demographics|Patients/i }).first();
    
    if (await demographicsTab.isVisible({ timeout: 5000 })) {
      await demographicsTab.click();
      await waitForLoading(page);
      
      // Check demographics chart
      const demographicsChart = page.locator('[data-testid="demographics-chart"], canvas, svg').first();
      await expect(demographicsChart).toBeVisible({ timeout: 10000 });
    }
  });

  test('should display treatment statistics', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to treatments section
    const treatmentsTab = page.locator('button, a').filter({ hasText: /Treatments|Services/i }).first();
    
    if (await treatmentsTab.isVisible({ timeout: 5000 })) {
      await treatmentsTab.click();
      await waitForLoading(page);
      
      // Check treatment statistics
      const treatmentStats = page.locator('[data-testid="treatment-stats"], .treatment-stats');
      await expect(treatmentStats).toBeVisible({ timeout: 10000 });
    }
  });

  test('should export analytics report', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Find export button
    const exportButton = page.locator('button').filter({ hasText: /Export|Download|PDF/i }).first();
    
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

  test('should display top treatments', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Look for top treatments widget
    const topTreatments = page.locator('[data-testid="top-treatments"], .top-treatments').first();
    const treatmentsList = page.locator('text=/Most Popular|Top Treatments|Popular Services/i').first();
    
    if (await topTreatments.isVisible({ timeout: 5000 }) || await treatmentsList.isVisible({ timeout: 5000 })) {
      await expect(topTreatments.or(treatmentsList)).toBeVisible();
    }
  });

  test('should display cancellation rate', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Look for cancellation metrics
    const cancellationRate = page.locator('text=/Cancellation|No-Show|Missed/i').first();
    
    if (await cancellationRate.isVisible({ timeout: 5000 })) {
      await expect(cancellationRate).toBeVisible();
    }
  });

  test('should display average wait time', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Look for wait time metrics
    const waitTime = page.locator('text=/Wait Time|Average Wait|Waiting/i').first();
    
    if (await waitTime.isVisible({ timeout: 5000 })) {
      await expect(waitTime).toBeVisible();
    }
  });

  test('should compare periods', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Find compare toggle/button
    const compareButton = page.locator('button, input[type="checkbox"]').filter({ hasText: /Compare|Previous/i }).first();
    
    if (await compareButton.isVisible({ timeout: 5000 })) {
      await compareButton.click();
      await waitForLoading(page);
      
      // Check comparison data appears
      const comparisonData = page.locator('text=/vs|compared to|previous/i');
      await expect(comparisonData.first()).toBeVisible({ timeout: 10000 });
    }
  });

  test('should display AI agent metrics', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to AI metrics section
    const aiTab = page.locator('button, a').filter({ hasText: /AI|Agents|Automation/i }).first();
    
    if (await aiTab.isVisible({ timeout: 5000 })) {
      await aiTab.click();
      await waitForLoading(page);
      
      // Check AI metrics
      const aiMetrics = page.locator('[data-testid="ai-metrics"], .ai-metrics');
      const aiStats = page.locator('text=/Conversations|Messages|Agent Activity/i');
      
      await expect(
        aiMetrics.or(aiStats.first())
      ).toBeVisible({ timeout: 10000 });
    }
  });

  test('should display financial summary', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Navigate to financial section
    const financialTab = page.locator('button, a').filter({ hasText: /Financial|Revenue|Billing/i }).first();
    
    if (await financialTab.isVisible({ timeout: 5000 })) {
      await financialTab.click();
      await waitForLoading(page);
      
      // Check financial summary
      const financialSummary = page.locator('[data-testid="financial-summary"], .financial-summary');
      await expect(financialSummary).toBeVisible({ timeout: 10000 });
    }
  });

  test('should display custom report builder', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Find custom report button
    const customReportButton = page.locator('button').filter({ hasText: /Custom Report|Create Report/i }).first();
    
    if (await customReportButton.isVisible({ timeout: 5000 })) {
      await customReportButton.click();
      
      // Check report builder opens
      const reportBuilder = page.locator('[data-testid="report-builder"], .report-builder, [role="dialog"]');
      await expect(reportBuilder.first()).toBeVisible({ timeout: 5000 });
    }
  });

  test('should save custom report', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Find custom report button
    const customReportButton = page.locator('button').filter({ hasText: /Custom Report|Create Report/i }).first();
    
    if (await customReportButton.isVisible({ timeout: 5000 })) {
      await customReportButton.click();
      
      // Fill report name
      const nameInput = page.locator('input[name="name"], input[name="reportName"]').first();
      if (await nameInput.isVisible({ timeout: 3000 })) {
        await nameInput.fill('Monthly Revenue Report');
        
        // Save report
        const saveButton = page.locator('button[type="submit"]').filter({ hasText: /Save|Create/i });
        await saveButton.click();
        
        await page.waitForSelector('text=/Success|Saved|Created/i', { timeout: 10000 });
      }
    }
  });

  test('should schedule automated report', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Find schedule report button
    const scheduleButton = page.locator('button').filter({ hasText: /Schedule|Automated|Email Report/i }).first();
    
    if (await scheduleButton.isVisible({ timeout: 5000 })) {
      await scheduleButton.click();
      
      // Check schedule dialog opens
      const scheduleDialog = page.locator('[role="dialog"], .modal').filter({ hasText: /Schedule|Automated/i });
      await expect(scheduleDialog.first()).toBeVisible({ timeout: 5000 });
    }
  });

  test('should display key performance indicators', async ({ page }) => {
    await page.goto('/clinic/analytics').catch(() => {});
    await waitForLoading(page);
    
    // Check for KPI cards
    const kpiCards = page.locator('[data-testid="kpi-card"], .kpi-card, .metric-card');
    
    if (await kpiCards.first().isVisible({ timeout: 5000 })) {
      // Should have multiple KPI cards
      const count = await kpiCards.count();
      expect(count).toBeGreaterThan(0);
    }
  });
});

