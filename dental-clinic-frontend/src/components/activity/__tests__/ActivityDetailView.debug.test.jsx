/**
 * Debug test for ActivityDetailView Component
 * 
 * Simplified test to identify hanging issues
 */

import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import ActivityDetailView from '../ActivityDetailView';

// Mock functions
const mockOnClose = vi.fn();
const mockOnHumanHandoff = vi.fn();

describe('ActivityDetailView Debug Tests', () => {
  beforeEach(() => {
    mockOnClose.mockClear();
    mockOnHumanHandoff.mockClear();
  });

  test('renders loading state', () => {
    render(
      <ActivityDetailView 
        activityId="test-123" 
        onClose={mockOnClose}
        onHumanHandoff={mockOnHumanHandoff}
      />
    );
    
    expect(screen.getByText('Loading activity details...')).toBeInTheDocument();
  });

  test('renders content after loading', async () => {
    render(
      <ActivityDetailView 
        activityId="test-123" 
        onClose={mockOnClose}
        onHumanHandoff={mockOnHumanHandoff}
      />
    );
    
    // Wait for content to load
    await waitFor(() => {
      expect(screen.getByText('Schedule Patient Appointment')).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  test('has dialog role', async () => {
    render(
      <ActivityDetailView 
        activityId="test-123" 
        onClose={mockOnClose}
        onHumanHandoff={mockOnHumanHandoff}
      />
    );
    
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    }, { timeout: 5000 });
  });
});
