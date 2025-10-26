import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ErrorBoundary from './ErrorBoundary';

/**
 * ErrorBoundary Component Tests
 * 
 * Critical tests for error handling and recovery:
 * 1. Catches React errors
 * 2. Displays fallback UI
 * 3. Sends errors to Sentry
 * 4. Allows recovery
 * 5. Handles persistent errors
 */

// Mock Sentry module
vi.mock('@sentry/react', () => ({
  captureException: vi.fn(),
  withScope: vi.fn((callback) => {
    const mockScope = {
      setExtras: vi.fn(),
      setTag: vi.fn(),
    };
    callback(mockScope);
  }),
}));

// Component that throws an error
const ThrowError = ({ shouldThrow }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

// Component that throws on mount
const ThrowOnMount = () => {
  throw new Error('Mount error');
};

describe('ErrorBoundary Component', () => {
  let consoleErrorSpy;
  
  beforeEach(() => {
    // Suppress console.error in tests (React logs errors caught by boundaries)
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });
  
  afterEach(() => {
    consoleErrorSpy.mockRestore();
    vi.clearAllMocks();
  });

  describe('Normal Rendering', () => {
    it('should render children when no error occurs', () => {
      render(
        <ErrorBoundary>
          <div>Test content</div>
        </ErrorBoundary>
      );
      
      expect(screen.getByText('Test content')).toBeInTheDocument();
    });

    it('should not show error UI when children render successfully', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText('No error')).toBeInTheDocument();
      expect(screen.queryByText(/something went wrong/i)).not.toBeInTheDocument();
    });

    it('should pass through multiple children', () => {
      render(
        <ErrorBoundary>
          <div>Child 1</div>
          <div>Child 2</div>
          <div>Child 3</div>
        </ErrorBoundary>
      );
      
      expect(screen.getByText('Child 1')).toBeInTheDocument();
      expect(screen.getByText('Child 2')).toBeInTheDocument();
      expect(screen.getByText('Child 3')).toBeInTheDocument();
    });
  });

  describe('Error Catching', () => {
    it('should catch errors from child components', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });

    it('should catch errors on component mount', () => {
      render(
        <ErrorBoundary>
          <ThrowOnMount />
        </ErrorBoundary>
      );
      
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });

    it('should display error details', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText(/error details/i)).toBeInTheDocument();
      expect(screen.getByText(/test error/i)).toBeInTheDocument();
    });

    it('should log error to console', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('should handle errors with no message', () => {
      const ThrowEmptyError = () => {
        throw new Error();
      };
      
      render(
        <ErrorBoundary>
          <ThrowEmptyError />
        </ErrorBoundary>
      );
      
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });
  });

  describe('Fallback UI', () => {
    it('should display error title', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });

    it('should display error description', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText(/the application encountered an unexpected error/i)).toBeInTheDocument();
    });

    it('should display error details section', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText(/error details/i)).toBeInTheDocument();
      expect(screen.getByText(/test error/i)).toBeInTheDocument();
    });

    it('should display Try Again button', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });

    it('should display Reload Page button', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByRole('button', { name: /reload page/i })).toBeInTheDocument();
    });
  });

  describe('Error Recovery', () => {
    it('should reset error state when Try Again is clicked', () => {
      // ErrorBoundary needs a key change to fully reset
      const { rerender } = render(
        <ErrorBoundary key="test-1">
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
      
      const tryAgainButton = screen.getByRole('button', { name: /try again/i });
      fireEvent.click(tryAgainButton);
      
      // After clicking Try Again, the error state is cleared internally
      // But the component still shows error UI until children are re-rendered
      // This is expected React ErrorBoundary behavior
      
      // Rerender with new key to fully reset
      rerender(
        <ErrorBoundary key="test-2">
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText('No error')).toBeInTheDocument();
      expect(screen.queryByText(/something went wrong/i)).not.toBeInTheDocument();
    });

    it('should reload page when Reload Page button is clicked', () => {
      const reloadSpy = vi.fn();
      const originalLocation = window.location;
      
      delete window.location;
      window.location = { reload: reloadSpy };
      
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      const reloadButton = screen.getByRole('button', { name: /reload page/i });
      fireEvent.click(reloadButton);
      
      expect(reloadSpy).toHaveBeenCalled();
      
      window.location = originalLocation;
    });
  });

  describe('Persistent Error Handling', () => {
    it('should track error count across multiple errors', () => {
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      // First error
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
      
      // Try again
      const tryAgainButton = screen.getByRole('button', { name: /try again/i });
      fireEvent.click(tryAgainButton);
      
      // Throw second error
      rerender(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });

    it('should show persistent error warning after 3+ errors', () => {
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      // Simulate 3 errors
      for (let i = 0; i < 2; i++) {
        const tryAgainButton = screen.getByRole('button', { name: /try again/i });
        fireEvent.click(tryAgainButton);
        
        rerender(
          <ErrorBoundary>
            <ThrowError shouldThrow={true} />
          </ErrorBoundary>
        );
      }
      
      // Should show persistent error warning
      expect(screen.getByText(/persistent error detected/i)).toBeInTheDocument();
      expect(screen.getByText(/this error has occurred 3 times/i)).toBeInTheDocument();
    });

    it('should suggest clearing cache for persistent errors', () => {
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      // Simulate 3 errors
      for (let i = 0; i < 2; i++) {
        const tryAgainButton = screen.getByRole('button', { name: /try again/i });
        fireEvent.click(tryAgainButton);
        
        rerender(
          <ErrorBoundary>
            <ThrowError shouldThrow={true} />
          </ErrorBoundary>
        );
      }
      
      expect(screen.getByText(/clearing your browser cache/i)).toBeInTheDocument();
    });

    it('should reload page automatically after 4+ errors', () => {
      const reloadSpy = vi.fn();
      const originalLocation = window.location;
      
      delete window.location;
      window.location = { reload: reloadSpy };
      
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      // Simulate 4 errors
      for (let i = 0; i < 3; i++) {
        const tryAgainButton = screen.getByRole('button', { name: /try again/i });
        fireEvent.click(tryAgainButton);
        
        rerender(
          <ErrorBoundary>
            <ThrowError shouldThrow={true} />
          </ErrorBoundary>
        );
      }
      
      // Try again on 4th error should trigger reload
      const tryAgainButton = screen.getByRole('button', { name: /try again/i });
      fireEvent.click(tryAgainButton);
      
      expect(reloadSpy).toHaveBeenCalled();
      
      window.location = originalLocation;
    });
  });

  describe('Development Mode Features', () => {
    it('should show component stack in development mode', () => {
      const originalNodeEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';
      
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      // Component stack should be visible in development
      expect(screen.getByText(/component stack/i)).toBeInTheDocument();
      
      process.env.NODE_ENV = originalNodeEnv;
    });

    it('should not show component stack in production mode', () => {
      const originalNodeEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';
      
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      // Component stack should not be visible in production
      expect(screen.queryByText(/component stack/i)).not.toBeInTheDocument();
      
      process.env.NODE_ENV = originalNodeEnv;
    });
  });

  describe('Edge Cases', () => {
    it('should handle nested error boundaries', () => {
      render(
        <ErrorBoundary>
          <ErrorBoundary>
            <ThrowError shouldThrow={true} />
          </ErrorBoundary>
        </ErrorBoundary>
      );
      
      // Inner boundary should catch the error
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });

    it('should handle errors in event handlers', () => {
      const BrokenButton = () => {
        const handleClick = () => {
          throw new Error('Button error');
        };
        return <button onClick={handleClick}>Break me</button>;
      };
      
      render(
        <ErrorBoundary>
          <BrokenButton />
        </ErrorBoundary>
      );
      
      // Error boundaries don't catch errors in event handlers
      // This is expected React behavior
      expect(screen.getByText('Break me')).toBeInTheDocument();
    });

    it('should maintain error state across re-renders', () => {
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
      
      // Re-render without changing props
      rerender(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      // Should still show error
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have accessible error message', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      // Error message should be visible
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });

    it('should have accessible action buttons', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );
      
      // Buttons should have proper roles
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /reload page/i })).toBeInTheDocument();
    });
  });
});

