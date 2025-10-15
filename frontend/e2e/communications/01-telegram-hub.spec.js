import { test, expect } from '@playwright/test';
import { loginAsClinic, waitForLoading, waitForAPI } from '../utils/test-helpers.js';
import { testTelegramInvite } from '../fixtures/test-data.js';

test.describe('Communications Hub - Telegram Integration', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsClinic(page);
    await page.goto('/clinic/communications');
    await waitForLoading(page);
  });

  test('should display communications hub with agentic design', async ({ page }) => {
    // Check page title
    await expect(page.locator('h1, h2').filter({ hasText: /Communications/i }).first()).toBeVisible();
    
    // Check for gradient/agentic design elements
    const gradientElement = page.locator('[class*="gradient"], [style*="gradient"]').first();
    await expect(gradientElement).toBeVisible({ timeout: 5000 });
  });

  test('should display Telegram tab', async ({ page }) => {
    // Check for Telegram tab
    const telegramTab = page.locator('button, [role="tab"]').filter({ hasText: /Telegram/i }).first();
    await expect(telegramTab).toBeVisible();
    
    // Click Telegram tab if not active
    if (!(await telegramTab.getAttribute('aria-selected') === 'true')) {
      await telegramTab.click();
      await waitForLoading(page);
    }
  });

  test('should display invite codes widget', async ({ page }) => {
    // Navigate to Telegram tab
    const telegramTab = page.locator('button, [role="tab"]').filter({ hasText: /Telegram/i }).first();
    await telegramTab.click();
    await waitForLoading(page);
    
    // Check for invite codes section
    const inviteCodesWidget = page.locator('text=/Invite Codes|Invitation Codes/i').first();
    await expect(inviteCodesWidget).toBeVisible({ timeout: 10000 });
  });

  test('should create a new invite code', async ({ page }) => {
    // Navigate to Telegram tab
    const telegramTab = page.locator('button, [role="tab"]').filter({ hasText: /Telegram/i }).first();
    await telegramTab.click();
    await waitForLoading(page);
    
    // Find create invite code button
    const createButton = page.locator('button').filter({ hasText: /Create|New|Generate/i }).first();
    await createButton.click();
    
    // Wait for dialog or form
    const dialog = page.locator('[role="dialog"], .modal, form').first();
    await expect(dialog).toBeVisible({ timeout: 5000 });
    
    // Fill form if needed
    const notesInput = page.locator('input[name="notes"], textarea[name="notes"]').first();
    if (await notesInput.isVisible()) {
      await notesInput.fill(testTelegramInvite.notes);
    }
    
    // Submit
    const submitButton = page.locator('button[type="submit"]').filter({ hasText: /Create|Generate|Save/i });
    await submitButton.click();
    
    // Wait for success and code to be displayed
    await page.waitForSelector('text=/Success|Created|Generated/i, [data-testid="invite-code"], .invite-code', { timeout: 15000 });
    
    // Check that invite code is displayed
    const inviteCode = page.locator('[data-testid="invite-code"], .invite-code, code').first();
    await expect(inviteCode).toBeVisible();
  });

  test('should copy invite code to clipboard', async ({ page }) => {
    // Navigate to Telegram tab
    const telegramTab = page.locator('button, [role="tab"]').filter({ hasText: /Telegram/i }).first();
    await telegramTab.click();
    await waitForLoading(page);
    
    // Find first invite code
    const firstCode = page.locator('[data-testid="invite-code-item"], .invite-code-card').first();
    
    if (await firstCode.isVisible()) {
      // Find copy button
      const copyButton = firstCode.locator('button').filter({ hasText: /Copy/i }).first();
      
      if (await copyButton.isVisible()) {
        // Grant clipboard permissions
        await page.context().grantPermissions(['clipboard-read', 'clipboard-write']);
        
        await copyButton.click();
        
        // Wait for success message
        await page.waitForSelector('text=/Copied|Copy successful/i', { timeout: 5000 });
      }
    }
  });

  test('should display Telegram users widget', async ({ page }) => {
    // Navigate to Telegram tab
    const telegramTab = page.locator('button, [role="tab"]').filter({ hasText: /Telegram/i }).first();
    await telegramTab.click();
    await waitForLoading(page);
    
    // Check for users section
    const usersWidget = page.locator('text=/Users|Telegram Users|Connected Users/i').first();
    await expect(usersWidget).toBeVisible({ timeout: 10000 });
  });

  test('should display list of connected Telegram users', async ({ page }) => {
    // Navigate to Telegram tab
    const telegramTab = page.locator('button, [role="tab"]').filter({ hasText: /Telegram/i }).first();
    await telegramTab.click();
    await waitForLoading(page);
    
    // Check for users list or empty state
    const usersList = page.locator('[data-testid="telegram-users-list"], .users-table');
    const emptyState = page.locator('text=/No users|No connected users/i');
    
    await expect(
      usersList.or(emptyState)
    ).toBeVisible({ timeout: 10000 });
  });

  test('should view Telegram user details', async ({ page }) => {
    // Navigate to Telegram tab
    const telegramTab = page.locator('button, [role="tab"]').filter({ hasText: /Telegram/i }).first();
    await telegramTab.click();
    await waitForLoading(page);
    
    // Find first user
    const firstUser = page.locator('[data-testid="telegram-user-item"], .user-row').first();
    
    if (await firstUser.isVisible()) {
      await firstUser.click();
      
      // Check details view
      const detailsView = page.locator('[data-testid="user-details"], .user-details');
      await expect(detailsView).toBeVisible({ timeout: 5000 });
      
      // Check user information
      await expect(page.locator('text=/Username|User ID|Status/i').first()).toBeVisible();
    }
  });

  test('should display conversations widget', async ({ page }) => {
    // Navigate to Telegram tab
    const telegramTab = page.locator('button, [role="tab"]').filter({ hasText: /Telegram/i }).first();
    await telegramTab.click();
    await waitForLoading(page);
    
    // Check for conversations section
    const conversationsWidget = page.locator('text=/Conversations|Messages|Chats/i').first();
    await expect(conversationsWidget).toBeVisible({ timeout: 10000 });
  });

  test('should display active conversations', async ({ page }) => {
    // Navigate to Telegram tab
    const telegramTab = page.locator('button, [role="tab"]').filter({ hasText: /Telegram/i }).first();
    await telegramTab.click();
    await waitForLoading(page);
    
    // Check for conversations list or empty state
    const conversationsList = page.locator('[data-testid="conversations-list"], .conversations-table');
    const emptyState = page.locator('text=/No conversations|No active chats/i');
    
    await expect(
      conversationsList.or(emptyState)
    ).toBeVisible({ timeout: 10000 });
  });

  test('should filter users by status', async ({ page }) => {
    // Navigate to Telegram tab
    const telegramTab = page.locator('button, [role="tab"]').filter({ hasText: /Telegram/i }).first();
    await telegramTab.click();
    await waitForLoading(page);
    
    // Check for status filter
    const statusFilter = page.locator('select[name="status"], [data-testid="status-filter"]').first();
    
    if (await statusFilter.isVisible()) {
      await statusFilter.selectOption('linked');
      await waitForLoading(page);
      
      // Verify filtered results
      const usersList = page.locator('[data-testid="telegram-users-list"]');
      await expect(usersList).toBeVisible();
    }
  });

  test('should search for Telegram users', async ({ page }) => {
    // Navigate to Telegram tab
    const telegramTab = page.locator('button, [role="tab"]').filter({ hasText: /Telegram/i }).first();
    await telegramTab.click();
    await waitForLoading(page);
    
    // Find search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]').first();
    
    if (await searchInput.isVisible()) {
      await searchInput.fill('test');
      await page.keyboard.press('Enter');
      
      await waitForLoading(page);
      
      // Check search results
      const results = page.locator('[data-testid="search-results"], .users-table');
      await expect(results).toBeVisible({ timeout: 10000 });
    }
  });

  test('should display SMS tab (coming soon)', async ({ page }) => {
    // Check for SMS tab
    const smsTab = page.locator('button, [role="tab"]').filter({ hasText: /SMS/i }).first();
    
    if (await smsTab.isVisible()) {
      await smsTab.click();
      
      // Check for coming soon message
      const comingSoon = page.locator('text=/Coming soon|Available soon/i');
      await expect(comingSoon).toBeVisible({ timeout: 5000 });
    }
  });

  test('should display WhatsApp tab (coming soon)', async ({ page }) => {
    // Check for WhatsApp tab
    const whatsappTab = page.locator('button, [role="tab"]').filter({ hasText: /WhatsApp/i }).first();
    
    if (await whatsappTab.isVisible()) {
      await whatsappTab.click();
      
      // Check for coming soon message
      const comingSoon = page.locator('text=/Coming soon|Available soon/i');
      await expect(comingSoon).toBeVisible({ timeout: 5000 });
    }
  });

  test('should handle responsive design in communications hub', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await waitForLoading(page);
    
    // Tabs should still be accessible
    const telegramTab = page.locator('button, [role="tab"]').filter({ hasText: /Telegram/i }).first();
    await expect(telegramTab).toBeVisible();
    
    // Widgets should be stacked vertically
    const widgets = page.locator('[data-testid*="widget"], .widget, .card');
    await expect(widgets.first()).toBeVisible();
  });
});

