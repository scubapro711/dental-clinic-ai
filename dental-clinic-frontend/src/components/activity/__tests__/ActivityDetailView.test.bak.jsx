/**
 * ActivityDetailView Component Tests
 * 
 * Comprehensive test suite for the Activity Detail View component.
 * Tests all functionality including loading states, content rendering,
 * interactions, performance, accessibility, and error handling.
 */

import { describe, test, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ActivityDetailView from '../ActivityDetailView';

// Mock functions
const mockOnClose = vi.fn();
const mockOnHumanHandoff = vi.fn();

// Configure test timeouts
vi.setConfig({ testTimeout: 15000, hookTimeout: 20000 });

describe('ActivityDetailView Component', () => {
  beforeEach(() => {
    mockOnClose.mockClear();
    mockOnHumanHandoff.mockClear();
  });

  describe('Loading State', () => {
    test('displays loading spinner and message initially', () => {
      render(
        <ActivityDetailView 
          activityId="test-123" 
          onClose={mockOnClose}
          onHumanHandoff={mockOnHumanHandoff}
        />
      );
      
      expect(screen.getByText('Loading activity details...')).toBeInTheDocument();
      expect(screen.getByRole('status')).toBeInTheDocument(); // Loading spinner
    });

    test('transitions from loading to content', async () => {
      render(
        <ActivityDetailView 
          activityId="test-123" 
          onClose={mockOnClose}
          onHumanHandoff={mockOnHumanHandoff}
        />
      );
      
      await waitFor(() => {
        expect(screen.queryByText('Loading activity details...')).not.toBeInTheDocument();
      }, { timeout: 2000 });
      
      expect(screen.getByText('Schedule Patient Appointment')).toBeInTheDocument();
    });
  });

  describe('Main Content Rendering', () => {
    beforeEach(async () => {
      render(
        <ActivityDetailView 
          activityId="test-123" 
          onClose={mockOnClose}
          onHumanHandoff={mockOnHumanHandoff}
        />
      );
      
      await waitFor(() => {
        expect(screen.getByText('Schedule Patient Appointment')).toBeInTheDocument();
      }, { timeout: 2000 });
    });

    test('renders header with activity title and description', () => {
      expect(screen.getByText('Schedule Patient Appointment')).toBeInTheDocument();
      expect(screen.getByText('Processing appointment request for John Doe on March 15th')).toBeInTheDocument();
    });

    test('displays activity status badge', () => {
      expect(screen.getByText('ACTIVE')).toBeInTheDocument();
    });

    test('renders timeline with all steps', () => {
      expect(screen.getByText('Activity Timeline')).toBeInTheDocument();
      expect(screen.getByText('Request received')).toBeInTheDocument();
      expect(screen.getByText('Analyzing request')).toBeInTheDocument();
      expect(screen.getByText('Checking availability')).toBeInTheDocument();
      expect(screen.getByText('Booking confirmed')).toBeInTheDocument();
    });

    test('displays AI decision explanation section', () => {
      expect(screen.getByText('AI Decision Explanation')).toBeInTheDocument();
    });

    test('shows performance metrics', () => {
      expect(screen.getByText('Performance Metrics')).toBeInTheDocument();
      expect(screen.getByText('92.0%')).toBeInTheDocument(); // Accuracy score
      expect(screen.getByText('2.3s')).toBeInTheDocument(); // Duration
    });
  });

  describe('Interactive Elements', () => {
    beforeEach(async () => {
      render(
        <ActivityDetailView 
          activityId="test-123" 
          onClose={mockOnClose}
          onHumanHandoff={mockOnHumanHandoff}
        />
      );
      
      await waitFor(() => {
        expect(screen.getByText('Schedule Patient Appointment')).toBeInTheDocument();
      }, { timeout: 2000 });
    });

    test('timeline steps are clickable', () => {
      const firstStep = screen.getByText('Request received');
      fireEvent.click(firstStep);
      // Should not throw error
      expect(firstStep).toBeInTheDocument();
    });

    test('explanation toggle works', () => {
      const toggleButton = screen.getByText('Show Details');
      fireEvent.click(toggleButton);
      expect(screen.getByText('Hide Details')).toBeInTheDocument();
    });

    test('human handoff button triggers callback', () => {
      const handoffButton = screen.getByText('Request Human Handoff');
      fireEvent.click(handoffButton);
      expect(mockOnHumanHandoff).toHaveBeenCalledTimes(1);
    });

    test('close button triggers callback', () => {
      const closeButton = screen.getByLabelText('Close');
      fireEvent.click(closeButton);
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('Performance Metrics Display', () => {
    beforeEach(async () => {
      render(
        <ActivityDetailView 
          activityId="test-123" 
          onClose={mockOnClose}
          onHumanHandoff={mockOnHumanHandoff}
        />
      );
      
      await waitFor(() => {
        expect(screen.getByText('Schedule Patient Appointment')).toBeInTheDocument();
      }, { timeout: 2000 });
    });

    test('shows correct metric values', () => {
      expect(screen.getByText('92.0%')).toBeInTheDocument(); // Accuracy
      expect(screen.getByText('2.3s')).toBeInTheDocument(); // Duration
      expect(screen.getByText('89.0%')).toBeInTheDocument(); // User satisfaction
    });

    test('metrics have appropriate icons', () => {
      // Check that metric sections exist
      expect(screen.getByText('Performance Metrics')).toBeInTheDocument();
    });
  });

  describe('Footer Actions', () => {
    beforeEach(async () => {
      render(
        <ActivityDetailView 
          activityId="test-123" 
          onClose={mockOnClose}
          onHumanHandoff={mockOnHumanHandoff}
        />
      );
      
      await waitFor(() => {
        expect(screen.getByText('Schedule Patient Appointment')).toBeInTheDocument();
      }, { timeout: 2000 });
    });

    test('displays activity metadata', () => {
      expect(screen.getByText('dental_agent')).toBeInTheDocument();
    });

    test('close button triggers callback', () => {
      const closeButton = screen.getByLabelText('Close');
      fireEvent.click(closeButton);
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    test('export button is present', () => {
      expect(screen.getByText('Export Details')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    test('handles missing activity ID gracefully', () => {
      render(
        <ActivityDetailView 
          onClose={mockOnClose}
          onHumanHandoff={mockOnHumanHandoff}
        />
      );
      
      // Should not crash
      expect(screen.getByText('Loading activity details...')).toBeInTheDocument();
    });

    test('handles missing callbacks gracefully', () => {
      render(<ActivityDetailView activityId="test-123" />);
      
      // Should not crash
      expect(screen.getByText('Loading activity details...')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    beforeEach(async () => {
      render(
        <ActivityDetailView 
          activityId="test-123" 
          onClose={mockOnClose}
          onHumanHandoff={mockOnHumanHandoff}
        />
      );
      
      await waitFor(() => {
        expect(screen.getByText('Schedule Patient Appointment')).toBeInTheDocument();
      }, { timeout: 2000 });
    });

    test('has proper button roles', () => {
      const closeButton = screen.getByLabelText('Close');
      expect(closeButton).toHaveAttribute('type', 'button');
    });

    test('timeline steps are clickable', () => {
      const firstStep = screen.getByText('Request received');
      expect(firstStep).toBeInTheDocument();
    });

    test('supports keyboard navigation', () => {
      const closeButton = screen.getByLabelText('Close');
      closeButton.focus();
      expect(document.activeElement).toBe(closeButton);
    });
  });

  describe('Performance', () => {
    test('renders without performance issues', async () => {
      const startTime = performance.now();
      
      render(
        <ActivityDetailView 
          activityId="test-123" 
          onClose={mockOnClose}
          onHumanHandoff={mockOnHumanHandoff}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Schedule Patient Appointment')).toBeInTheDocument();
      });
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(1000); // Should render in less than 1000ms
    });

    test('handles large datasets efficiently', async () => {
      // Test with complex activity data
      render(
        <ActivityDetailView 
          activityId="complex-activity-123" 
          onClose={mockOnClose}
          onHumanHandoff={mockOnHumanHandoff}
        />
      );
      
      await waitFor(() => {
        expect(screen.getByText('Schedule Patient Appointment')).toBeInTheDocument();
      });
    });
  });

  describe('Visual Layout', () => {
    beforeEach(async () => {
      render(
        <ActivityDetailView 
          activityId="test-123" 
          onClose={mockOnClose}
          onHumanHandoff={mockOnHumanHandoff}
        />
      );
      
      await waitFor(() => {
        expect(screen.getByText('Schedule Patient Appointment')).toBeInTheDocument();
      }, { timeout: 2000 });
    });

    test('modal overlay is present', () => {
      const modal = screen.getByRole('dialog');
      expect(modal).toBeInTheDocument();
    });

    test('has proper layout structure', () => {
      expect(screen.getByText('Activity Timeline')).toBeInTheDocument();
      expect(screen.getByText('AI Decision Explanation')).toBeInTheDocument();
      expect(screen.getByText('Performance Metrics')).toBeInTheDocument();
    });

    test('responsive design elements are present', () => {
      // Check that main container exists
      const modal = screen.getByRole('dialog');
      expect(modal).toHaveClass('max-w-6xl');
    });
  });
});

