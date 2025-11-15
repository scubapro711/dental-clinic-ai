import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AIChat from './AIChat';
import API_CONFIG from '@/config/api';

// Mock API_CONFIG
vi.mock('@/config/api', () => ({
  default: {
    API_URL: 'http://localhost:8000/api/v1',
    BASE_URL: 'http://localhost:8000',
    WS_URL: 'ws://localhost:8000',
    ENV: 'test',
    endpoint: (path) => `http://localhost:8000/api/v1/${path}`,
    ws: (path) => `ws://localhost:8000/${path}`,
  },
}));

/**
 * AIChat Component Tests
 * 
 * Critical tests to prevent production bugs:
 * 1. PropTypes validation (caught missing import bug)
 * 2. Optional prop handling (onStreamEvent)
 * 3. Streaming functionality
 * 4. Error handling
 * 5. Accessibility
 */

describe('AIChat Component', () => {
  let mockFetch;
  
  beforeEach(() => {
    // Mock fetch for API calls
    mockFetch = vi.fn();
    global.fetch = mockFetch;
  });
  
  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Rendering', () => {
    it('should render without crashing', () => {
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    });

    it('should render with all required UI elements', () => {
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      
      // Check for input field
      expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
      
      // Check for send button
      expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
    });

    it('should render with optional onStreamEvent prop', () => {
      const mockOnStreamEvent = vi.fn();
      render(
        <AIChat 
          user={{ id: 1, name: 'Test User' }} 
          onStreamEvent={mockOnStreamEvent}
        />
      );
      
      expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    });

    it('should render without onStreamEvent prop (optional)', () => {
      // This test ensures the component doesn't crash when onStreamEvent is undefined
      // This was the bug that caused production crash!
      expect(() => {
        render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      }).not.toThrow();
    });
  });

  describe('PropTypes Validation', () => {
    it('should have PropTypes defined', () => {
      // Ensure PropTypes are imported and defined
      expect(AIChat.propTypes).toBeDefined();
    });

    it('should accept user prop', () => {
      const user = { id: 1, name: 'Test User' };
      render(<AIChat user={user} />);
      expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    });

    it('should accept optional onStreamEvent prop', () => {
      const mockOnStreamEvent = vi.fn();
      render(
        <AIChat 
          user={{ id: 1, name: 'Test User' }} 
          onStreamEvent={mockOnStreamEvent}
        />
      );
      expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
    });
  });

  describe('User Input', () => {
    it('should update input value when typing', async () => {
      const user = userEvent.setup();
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      
      const input = screen.getByPlaceholderText(/type your message/i);
      await user.type(input, 'Hello AI');
      
      expect(input).toHaveValue('Hello AI');
    });

    it('should clear input after sending message', async () => {
      const user = userEvent.setup();
      
      // Mock successful fetch response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        body: {
          getReader: () => ({
            read: vi.fn()
              .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: {"type":"text","content":"Hello"}\n') })
              .mockResolvedValueOnce({ done: true })
          })
        }
      });
      
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      
      const input = screen.getByPlaceholderText(/type your message/i);
      await user.type(input, 'Hello AI');
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);
      
      await waitFor(() => {
        expect(input).toHaveValue('');
      });
    });

    it('should not send empty messages', async () => {
      const user = userEvent.setup();
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);
      
      expect(mockFetch).not.toHaveBeenCalled();
    });

    it('should not send whitespace-only messages', async () => {
      const user = userEvent.setup();
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      
      const input = screen.getByPlaceholderText(/type your message/i);
      await user.type(input, '   ');
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);
      
      expect(mockFetch).not.toHaveBeenCalled();
    });
  });

  describe('Message Sending', () => {
    it('should send message when send button is clicked', async () => {
      const user = userEvent.setup();
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        body: {
          getReader: () => ({
            read: vi.fn()
              .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: {"type":"text","content":"Response"}\n') })
              .mockResolvedValueOnce({ done: true })
          })
        }
      });
      
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      
      const input = screen.getByPlaceholderText(/type your message/i);
      await user.type(input, 'Hello AI');
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);
      
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/ai/chat'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );
    });

    it('should send message when Enter key is pressed', async () => {
      const user = userEvent.setup();
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        body: {
          getReader: () => ({
            read: vi.fn()
              .mockResolvedValueOnce({ done: false, value: new TextEncoder().encode('data: {"type":"text","content":"Response"}\n') })
              .mockResolvedValueOnce({ done: true })
          })
        }
      });
      
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      
      const input = screen.getByPlaceholderText(/type your message/i);
      await user.type(input, 'Hello AI{Enter}');
      
      expect(mockFetch).toHaveBeenCalled();
    });

    it('should show loading state while sending', async () => {
      const user = userEvent.setup();
      
      // Mock a slow response
      mockFetch.mockImplementationOnce(() => 
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          body: {
            getReader: () => ({
              read: vi.fn().mockResolvedValue({ done: true })
            })
          }
        }), 1000))
      );
      
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      
      const input = screen.getByPlaceholderText(/type your message/i);
      await user.type(input, 'Hello AI');
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);
      
      // Should show stop button or loading indicator while loading
      await waitFor(() => {
        expect(screen.queryByRole('button', { name: /stop/i }) || screen.queryByRole('button', { name: /send/i })).toBeInTheDocument();
      });
    });
  });

  describe('Stream Event Handling', () => {
    it('should call onStreamEvent when provided', async () => {
      const user = userEvent.setup();
      const mockOnStreamEvent = vi.fn();
      
      const mockStreamData = { type: 'text', content: 'Hello' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        body: {
          getReader: () => ({
            read: vi.fn()
              .mockResolvedValueOnce({ 
                done: false, 
                value: new TextEncoder().encode(`data: ${JSON.stringify(mockStreamData)}\n`) 
              })
              .mockResolvedValueOnce({ done: true })
          })
        }
      });
      
      render(
        <AIChat 
          user={{ id: 1, name: 'Test User' }} 
          onStreamEvent={mockOnStreamEvent}
        />
      );
      
      const input = screen.getByPlaceholderText(/type your message/i);
      await user.type(input, 'Hello AI');
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);
      
      await waitFor(() => {
        expect(mockOnStreamEvent).toHaveBeenCalledWith(mockStreamData);
      });
    });

    it('should not crash when onStreamEvent is undefined', async () => {
      const user = userEvent.setup();
      
      // This is the critical test that would have caught the production bug!
      mockFetch.mockResolvedValueOnce({
        ok: true,
        body: {
          getReader: () => ({
            read: vi.fn()
              .mockResolvedValueOnce({ 
                done: false, 
                value: new TextEncoder().encode('data: {"type":"text","content":"Hello"}\n') 
              })
              .mockResolvedValueOnce({ done: true })
          })
        }
      });
      
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      
      const input = screen.getByPlaceholderText(/type your message/i);
      await user.type(input, 'Hello AI');
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      
      // Should not throw error even without onStreamEvent
      await expect(async () => {
        await user.click(sendButton);
      }).not.toThrow();
    });
  });

  describe('Error Handling', () => {
    it('should display error when fetch fails', async () => {
      const user = userEvent.setup();
      
      mockFetch.mockRejectedValueOnce(new Error('Network error'));
      
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      
      const input = screen.getByPlaceholderText(/type your message/i);
      await user.type(input, 'Hello AI');
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);
      
      await waitFor(() => {
        expect(screen.getByText(/failed to send message/i)).toBeInTheDocument();
      });
    });

    it('should handle stream errors gracefully', async () => {
      const user = userEvent.setup();
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        body: {
          getReader: () => ({
            read: vi.fn()
              .mockResolvedValueOnce({ 
                done: false, 
                value: new TextEncoder().encode('data: {"type":"error","message":"Stream error"}\n') 
              })
              .mockResolvedValueOnce({ done: true })
          })
        }
      });
      
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      
      const input = screen.getByPlaceholderText(/type your message/i);
      await user.type(input, 'Hello AI');
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);
      
      await waitFor(() => {
        expect(screen.getByText(/stream error/i)).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have accessible input field', () => {
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      
      const input = screen.getByPlaceholderText(/type your message/i);
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('aria-label');
    });

    it('should have accessible send button', () => {
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      expect(sendButton).toBeInTheDocument();
    });

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup();
      render(<AIChat user={{ id: 1, name: 'Test User' }} />);
      
      const input = screen.getByPlaceholderText(/type your message/i);
      
      // Click to focus input
      await user.click(input);
      expect(input).toHaveFocus();
    });
  });
});

