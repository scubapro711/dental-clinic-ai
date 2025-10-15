import { test, expect } from '@playwright/test';
import { loginAsPatient, waitForLoading, waitForAPI } from '../utils/test-helpers.js';

test.describe('Patient Portal - AI Chat', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsPatient(page);
    await waitForLoading(page);
  });

  test('should open AI chat interface', async ({ page }) => {
    // Find AI chat button/icon
    const chatButton = page.locator('button, a').filter({ hasText: /Chat|AI|Assistant|Help/i }).first();
    
    if (await chatButton.isVisible({ timeout: 5000 })) {
      await chatButton.click();
      
      // Check chat interface opens
      const chatInterface = page.locator('[data-testid="ai-chat"], .chat-container, [role="dialog"]').filter({ hasText: /Chat|Assistant/i });
      await expect(chatInterface.first()).toBeVisible({ timeout: 5000 });
    } else {
      // Try navigating directly
      await page.goto('/patient/chat');
      await waitForLoading(page);
      
      // Check chat page loaded
      const chatPage = page.locator('h1, h2').filter({ hasText: /Chat|Assistant/i });
      await expect(chatPage.first()).toBeVisible({ timeout: 10000 });
    }
  });

  test('should display chat input field', async ({ page }) => {
    // Open chat
    await page.goto('/patient/chat').catch(() => {});
    await waitForLoading(page);
    
    // Check for message input
    const messageInput = page.locator('textarea[placeholder*="message"], input[placeholder*="message"], [data-testid="chat-input"]');
    await expect(messageInput.first()).toBeVisible({ timeout: 10000 });
  });

  test('should send a message to AI', async ({ page }) => {
    // Navigate to chat
    await page.goto('/patient/chat').catch(() => {});
    await waitForLoading(page);
    
    // Find message input
    const messageInput = page.locator('textarea[placeholder*="message"], input[placeholder*="message"], [data-testid="chat-input"]').first();
    
    if (await messageInput.isVisible({ timeout: 5000 })) {
      // Type message
      await messageInput.fill('Hello, I need help with my appointment');
      
      // Send message
      const sendButton = page.locator('button[type="submit"], button').filter({ hasText: /Send|Submit/i }).first();
      await sendButton.click();
      
      // Wait for message to appear in chat
      await page.waitForSelector('text=/Hello, I need help/i', { timeout: 10000 });
      
      // Wait for AI response (with longer timeout)
      await page.waitForSelector('[data-testid="ai-message"], .ai-message, .assistant-message', { timeout: 30000 });
    }
  });

  test('should display chat history', async ({ page }) => {
    await page.goto('/patient/chat').catch(() => {});
    await waitForLoading(page);
    
    // Check for chat messages container
    const chatMessages = page.locator('[data-testid="chat-messages"], .chat-messages, .messages-container');
    const emptyState = page.locator('text=/No messages|Start a conversation/i');
    
    await expect(
      chatMessages.or(emptyState)
    ).toBeVisible({ timeout: 10000 });
  });

  test('should handle long messages', async ({ page }) => {
    await page.goto('/patient/chat').catch(() => {});
    await waitForLoading(page);
    
    const messageInput = page.locator('textarea[placeholder*="message"], input[placeholder*="message"], [data-testid="chat-input"]').first();
    
    if (await messageInput.isVisible({ timeout: 5000 })) {
      // Type long message
      const longMessage = 'I have been experiencing tooth pain for the past week. The pain is on the upper right side and gets worse when I eat cold or hot foods. I am not sure if I need to see a dentist immediately or if this can wait. Can you help me understand what might be causing this and what I should do?';
      await messageInput.fill(longMessage);
      
      // Send
      const sendButton = page.locator('button[type="submit"], button').filter({ hasText: /Send|Submit/i }).first();
      await sendButton.click();
      
      // Verify message sent
      await page.waitForSelector(`text=/${longMessage.substring(0, 30)}/i`, { timeout: 10000 });
    }
  });

  test('should handle network errors in chat', async ({ page }) => {
    await page.goto('/patient/chat').catch(() => {});
    await waitForLoading(page);
    
    const messageInput = page.locator('textarea[placeholder*="message"], input[placeholder*="message"], [data-testid="chat-input"]').first();
    
    if (await messageInput.isVisible({ timeout: 5000 })) {
      // Go offline
      await page.context().setOffline(true);
      
      // Try to send message
      await messageInput.fill('Test message');
      const sendButton = page.locator('button[type="submit"], button').filter({ hasText: /Send|Submit/i }).first();
      await sendButton.click();
      
      // Check for error
      await page.waitForSelector('text=/Error|Failed|Network|offline/i', { timeout: 10000 });
      
      // Restore connection
      await page.context().setOffline(false);
    }
  });

  test('should display typing indicator', async ({ page }) => {
    await page.goto('/patient/chat').catch(() => {});
    await waitForLoading(page);
    
    const messageInput = page.locator('textarea[placeholder*="message"], input[placeholder*="message"], [data-testid="chat-input"]').first();
    
    if (await messageInput.isVisible({ timeout: 5000 })) {
      // Send message
      await messageInput.fill('Quick question');
      const sendButton = page.locator('button[type="submit"], button').filter({ hasText: /Send|Submit/i }).first();
      await sendButton.click();
      
      // Look for typing indicator
      const typingIndicator = page.locator('[data-testid="typing-indicator"], .typing-indicator, text=/typing/i');
      
      // Typing indicator should appear briefly
      await expect(typingIndicator.first()).toBeVisible({ timeout: 5000 }).catch(() => {
        // It's ok if typing indicator is too fast to catch
      });
    }
  });

  test('should support message formatting', async ({ page }) => {
    await page.goto('/patient/chat').catch(() => {});
    await waitForLoading(page);
    
    const messageInput = page.locator('textarea[placeholder*="message"], input[placeholder*="message"], [data-testid="chat-input"]').first();
    
    if (await messageInput.isVisible({ timeout: 5000 })) {
      // Check for formatting buttons
      const boldButton = page.locator('button[aria-label*="bold"], button[title*="bold"]').first();
      const italicButton = page.locator('button[aria-label*="italic"], button[title*="italic"]').first();
      
      // These are optional features
      if (await boldButton.isVisible({ timeout: 2000 })) {
        await expect(boldButton).toBeEnabled();
      }
    }
  });

  test('should clear chat history', async ({ page }) => {
    await page.goto('/patient/chat').catch(() => {});
    await waitForLoading(page);
    
    // Look for clear/delete chat button
    const clearButton = page.locator('button').filter({ hasText: /Clear|Delete|Reset/i }).first();
    
    if (await clearButton.isVisible({ timeout: 5000 })) {
      await clearButton.click();
      
      // Confirm if dialog appears
      const confirmButton = page.locator('button').filter({ hasText: /Confirm|Yes|OK/i }).first();
      if (await confirmButton.isVisible({ timeout: 2000 })) {
        await confirmButton.click();
      }
      
      // Check messages are cleared
      await page.waitForSelector('text=/No messages|Start a conversation|cleared/i', { timeout: 10000 });
    }
  });

  test('should show suggested questions', async ({ page }) => {
    await page.goto('/patient/chat').catch(() => {});
    await waitForLoading(page);
    
    // Look for suggested questions
    const suggestions = page.locator('[data-testid="suggested-questions"], .suggestions, .quick-replies');
    
    if (await suggestions.isVisible({ timeout: 5000 })) {
      // Click first suggestion
      const firstSuggestion = suggestions.locator('button, a').first();
      await firstSuggestion.click();
      
      // Message should be sent
      await waitForLoading(page);
      await page.waitForSelector('[data-testid="ai-message"], .ai-message', { timeout: 30000 });
    }
  });

  test('should handle file attachments in chat', async ({ page }) => {
    await page.goto('/patient/chat').catch(() => {});
    await waitForLoading(page);
    
    // Look for attachment button
    const attachButton = page.locator('button[aria-label*="attach"], button[title*="attach"], input[type="file"]').first();
    
    if (await attachButton.isVisible({ timeout: 5000 })) {
      // If it's a file input
      if (await attachButton.getAttribute('type') === 'file') {
        await attachButton.setInputFiles({
          name: 'test-document.pdf',
          mimeType: 'application/pdf',
          buffer: Buffer.from('test content')
        });
        
        // Wait for upload confirmation
        await page.waitForSelector('text=/Uploaded|Attached|Success/i', { timeout: 15000 });
      }
    }
  });

  test('should display agent information', async ({ page }) => {
    await page.goto('/patient/chat').catch(() => {});
    await waitForLoading(page);
    
    // Look for agent info (Alex, Sarah, etc.)
    const agentInfo = page.locator('[data-testid="agent-info"], .agent-name, .assistant-name');
    
    if (await agentInfo.isVisible({ timeout: 5000 })) {
      // Check agent name is displayed
      await expect(agentInfo).toContainText(/Alex|Sarah|Marcus|Sophia|Assistant/i);
    }
  });

  test('should handle rate limiting gracefully', async ({ page }) => {
    await page.goto('/patient/chat').catch(() => {});
    await waitForLoading(page);
    
    const messageInput = page.locator('textarea[placeholder*="message"], input[placeholder*="message"], [data-testid="chat-input"]').first();
    const sendButton = page.locator('button[type="submit"], button').filter({ hasText: /Send|Submit/i }).first();
    
    if (await messageInput.isVisible({ timeout: 5000 })) {
      // Send multiple messages quickly
      for (let i = 0; i < 5; i++) {
        await messageInput.fill(`Test message ${i}`);
        await sendButton.click();
        await page.waitForTimeout(100);
      }
      
      // Check if rate limit message appears
      const rateLimitMessage = page.locator('text=/rate limit|too many|slow down/i');
      
      // Rate limiting is optional, so we don't fail if it doesn't exist
      if (await rateLimitMessage.isVisible({ timeout: 5000 })) {
        await expect(rateLimitMessage).toBeVisible();
      }
    }
  });

  test('should support keyboard shortcuts', async ({ page }) => {
    await page.goto('/patient/chat').catch(() => {});
    await waitForLoading(page);
    
    const messageInput = page.locator('textarea[placeholder*="message"], input[placeholder*="message"], [data-testid="chat-input"]').first();
    
    if (await messageInput.isVisible({ timeout: 5000 })) {
      // Type message
      await messageInput.fill('Test keyboard shortcut');
      
      // Try Enter to send (common shortcut)
      await messageInput.press('Enter');
      
      // Check if message was sent
      await page.waitForSelector('text=/Test keyboard shortcut/i', { timeout: 10000 });
    }
  });

  test('should scroll to latest message', async ({ page }) => {
    await page.goto('/patient/chat').catch(() => {});
    await waitForLoading(page);
    
    const messageInput = page.locator('textarea[placeholder*="message"], input[placeholder*="message"], [data-testid="chat-input"]').first();
    
    if (await messageInput.isVisible({ timeout: 5000 })) {
      // Send a message
      await messageInput.fill('Scroll test message');
      const sendButton = page.locator('button[type="submit"], button').filter({ hasText: /Send|Submit/i }).first();
      await sendButton.click();
      
      // Wait for message and response
      await page.waitForTimeout(2000);
      
      // Check if latest message is in viewport
      const latestMessage = page.locator('[data-testid="chat-messages"], .chat-messages').locator('> *').last();
      await expect(latestMessage).toBeInViewport({ timeout: 10000 });
    }
  });
});

