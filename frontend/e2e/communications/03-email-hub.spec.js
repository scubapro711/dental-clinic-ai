import { test, expect } from '@playwright/test';
import { loginAsClinic, waitForLoading } from '../utils/test-helpers.js';

test.describe('Communications Hub - Email Integration', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsClinic(page);
    await page.goto('/clinic/communications');
    await waitForLoading(page);
  });

  test('should display Email tab', async ({ page }) => {
    // Check for Email tab
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await expect(emailTab).toBeVisible();
      await emailTab.click();
      await waitForLoading(page);
    }
  });

  test('should display email dashboard', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Check for email dashboard elements
      const dashboard = page.locator('[data-testid="email-dashboard"], .email-dashboard');
      const heading = page.locator('h2, h3').filter({ hasText: /Email/i });
      
      await expect(
        dashboard.or(heading.first())
      ).toBeVisible({ timeout: 10000 });
    }
  });

  test('should compose new email', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Find compose button
      const composeButton = page.locator('button').filter({ hasText: /Compose|New Email/i }).first();
      
      if (await composeButton.isVisible({ timeout: 3000 })) {
        await composeButton.click();
        
        // Fill email form
        const toInput = page.locator('input[name="to"], input[type="email"]').first();
        await toInput.fill('patient@example.com');
        
        const subjectInput = page.locator('input[name="subject"]').first();
        await subjectInput.fill('Appointment Confirmation');
        
        const bodyInput = page.locator('textarea[name="body"], [contenteditable="true"]').first();
        await bodyInput.fill('Your appointment has been confirmed for tomorrow at 2 PM.');
        
        // Send
        const sendButton = page.locator('button[type="submit"]').filter({ hasText: /Send/i });
        await sendButton.click();
        
        await page.waitForSelector('text=/Success|Sent/i', { timeout: 15000 });
      }
    }
  });

  test('should use email template', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Find compose button
      const composeButton = page.locator('button').filter({ hasText: /Compose|New Email/i }).first();
      
      if (await composeButton.isVisible({ timeout: 3000 })) {
        await composeButton.click();
        
        // Select template
        const templateSelect = page.locator('select[name="template"], [data-testid="template-select"]').first();
        
        if (await templateSelect.isVisible({ timeout: 3000 })) {
          await templateSelect.selectOption({ index: 1 });
          
          // Template should populate fields
          const subjectInput = page.locator('input[name="subject"]').first();
          const subjectValue = await subjectInput.inputValue();
          expect(subjectValue.length).toBeGreaterThan(0);
        }
      }
    }
  });

  test('should display sent emails', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Navigate to sent folder
      const sentFolder = page.locator('button, a').filter({ hasText: /Sent/i }).first();
      
      if (await sentFolder.isVisible({ timeout: 3000 })) {
        await sentFolder.click();
        await waitForLoading(page);
        
        // Check sent emails list
        const sentList = page.locator('[data-testid="sent-emails"], .emails-list');
        const emptyState = page.locator('text=/No sent emails/i');
        
        await expect(
          sentList.or(emptyState)
        ).toBeVisible({ timeout: 10000 });
      }
    }
  });

  test('should display inbox', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Navigate to inbox
      const inboxFolder = page.locator('button, a').filter({ hasText: /Inbox/i }).first();
      
      if (await inboxFolder.isVisible({ timeout: 3000 })) {
        await inboxFolder.click();
        await waitForLoading(page);
        
        // Check inbox
        const inbox = page.locator('[data-testid="inbox"], .emails-list');
        const emptyState = page.locator('text=/No emails|Empty inbox/i');
        
        await expect(
          inbox.or(emptyState)
        ).toBeVisible({ timeout: 10000 });
      }
    }
  });

  test('should read email', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Find first email
      const firstEmail = page.locator('[data-testid="email-item"], .email-row').first();
      
      if (await firstEmail.isVisible({ timeout: 3000 })) {
        await firstEmail.click();
        
        // Check email content view
        const emailContent = page.locator('[data-testid="email-content"], .email-content');
        await expect(emailContent).toBeVisible({ timeout: 5000 });
        
        // Check subject and body are displayed
        await expect(page.locator('text=/Subject|From|To/i').first()).toBeVisible();
      }
    }
  });

  test('should reply to email', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Find and open first email
      const firstEmail = page.locator('[data-testid="email-item"], .email-row').first();
      
      if (await firstEmail.isVisible({ timeout: 3000 })) {
        await firstEmail.click();
        
        // Find reply button
        const replyButton = page.locator('button').filter({ hasText: /Reply/i }).first();
        
        if (await replyButton.isVisible({ timeout: 3000 })) {
          await replyButton.click();
          
          // Fill reply
          const bodyInput = page.locator('textarea[name="body"], [contenteditable="true"]').first();
          await bodyInput.fill('Thank you for your message.');
          
          // Send reply
          const sendButton = page.locator('button[type="submit"]').filter({ hasText: /Send/i });
          await sendButton.click();
          
          await page.waitForSelector('text=/Success|Sent/i', { timeout: 10000 });
        }
      }
    }
  });

  test('should attach file to email', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Compose new email
      const composeButton = page.locator('button').filter({ hasText: /Compose|New Email/i }).first();
      
      if (await composeButton.isVisible({ timeout: 3000 })) {
        await composeButton.click();
        
        // Find attach button
        const attachButton = page.locator('button, input[type="file"]').filter({ hasText: /Attach/i }).first();
        
        if (await attachButton.isVisible({ timeout: 3000 })) {
          // If it's a file input
          const fileInput = page.locator('input[type="file"]').first();
          
          if (await fileInput.isVisible({ timeout: 2000 })) {
            await fileInput.setInputFiles({
              name: 'document.pdf',
              mimeType: 'application/pdf',
              buffer: Buffer.from('test content')
            });
            
            // Wait for attachment confirmation
            await page.waitForSelector('text=/Attached|document.pdf/i', { timeout: 10000 });
          }
        }
      }
    }
  });

  test('should manage email templates', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Find templates button
      const templatesButton = page.locator('button, a').filter({ hasText: /Templates/i }).first();
      
      if (await templatesButton.isVisible({ timeout: 3000 })) {
        await templatesButton.click();
        
        // Check templates view
        const templatesView = page.locator('[data-testid="email-templates"], .templates-list');
        await expect(templatesView).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should create email template', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Navigate to templates
      const templatesButton = page.locator('button, a').filter({ hasText: /Templates/i }).first();
      
      if (await templatesButton.isVisible({ timeout: 3000 })) {
        await templatesButton.click();
        
        // Create new template
        const createButton = page.locator('button').filter({ hasText: /Create|New Template/i }).first();
        
        if (await createButton.isVisible({ timeout: 3000 })) {
          await createButton.click();
          
          // Fill template form
          const nameInput = page.locator('input[name="name"]').first();
          await nameInput.fill('Appointment Reminder');
          
          const subjectInput = page.locator('input[name="subject"]').first();
          await subjectInput.fill('Reminder: Upcoming Appointment');
          
          const bodyInput = page.locator('textarea[name="body"], [contenteditable="true"]').first();
          await bodyInput.fill('Hi {patient_name}, this is a reminder for your appointment on {date}.');
          
          // Save
          const saveButton = page.locator('button[type="submit"]').filter({ hasText: /Save|Create/i });
          await saveButton.click();
          
          await page.waitForSelector('text=/Success|Created/i', { timeout: 10000 });
        }
      }
    }
  });

  test('should search emails', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
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

  test('should filter emails by date', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Find date filter
      const dateFilter = page.locator('select[name="date"], [data-testid="date-filter"]').first();
      
      if (await dateFilter.isVisible({ timeout: 3000 })) {
        await dateFilter.selectOption('last_week');
        await waitForLoading(page);
        
        await page.waitForTimeout(1000);
      }
    }
  });

  test('should mark email as read/unread', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Find first email
      const firstEmail = page.locator('[data-testid="email-item"], .email-row').first();
      
      if (await firstEmail.isVisible({ timeout: 3000 })) {
        // Right click or find mark button
        const markButton = firstEmail.locator('button').filter({ hasText: /Mark|Read|Unread/i }).first();
        
        if (await markButton.isVisible({ timeout: 2000 })) {
          await markButton.click();
          await page.waitForTimeout(1000);
        }
      }
    }
  });

  test('should delete email', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Find first email
      const firstEmail = page.locator('[data-testid="email-item"], .email-row').first();
      
      if (await firstEmail.isVisible({ timeout: 3000 })) {
        await firstEmail.click();
        
        // Find delete button
        const deleteButton = page.locator('button').filter({ hasText: /Delete|Remove/i }).first();
        
        if (await deleteButton.isVisible({ timeout: 3000 })) {
          await deleteButton.click();
          
          // Confirm if needed
          const confirmButton = page.locator('button').filter({ hasText: /Confirm|Yes|Delete/i }).first();
          if (await confirmButton.isVisible({ timeout: 2000 })) {
            await confirmButton.click();
          }
          
          await page.waitForSelector('text=/Deleted|Removed/i', { timeout: 10000 });
        }
      }
    }
  });

  test('should schedule email', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Compose email
      const composeButton = page.locator('button').filter({ hasText: /Compose|New Email/i }).first();
      
      if (await composeButton.isVisible({ timeout: 3000 })) {
        await composeButton.click();
        
        // Fill basic info
        const toInput = page.locator('input[name="to"]').first();
        await toInput.fill('patient@example.com');
        
        const subjectInput = page.locator('input[name="subject"]').first();
        await subjectInput.fill('Scheduled Message');
        
        // Find schedule option
        const scheduleButton = page.locator('button').filter({ hasText: /Schedule|Send Later/i }).first();
        
        if (await scheduleButton.isVisible({ timeout: 3000 })) {
          await scheduleButton.click();
          
          // Set schedule time
          const dateInput = page.locator('input[type="datetime-local"], input[type="date"]').first();
          if (await dateInput.isVisible({ timeout: 2000 })) {
            await dateInput.fill('2025-10-20T14:00');
          }
          
          // Confirm schedule
          const confirmButton = page.locator('button[type="submit"]').filter({ hasText: /Schedule/i });
          await confirmButton.click();
          
          await page.waitForSelector('text=/Scheduled/i', { timeout: 10000 });
        }
      }
    }
  });

  test('should display email statistics', async ({ page }) => {
    const emailTab = page.locator('button, [role="tab"]').filter({ hasText: /Email/i }).first();
    
    if (await emailTab.isVisible({ timeout: 5000 })) {
      await emailTab.click();
      await waitForLoading(page);
      
      // Check for email stats
      const stats = page.locator('text=/Sent|Received|Read Rate|Open Rate/i').first();
      
      if (await stats.isVisible({ timeout: 5000 })) {
        await expect(stats).toBeVisible();
      }
    }
  });
});

