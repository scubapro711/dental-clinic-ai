import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ActivityDetailView from '../ActivityDetailView';

// Mock data for testing
const mockActivity = {
  id: 'test-123',
  title: 'Test Activity',
  description: 'Test Description',
  status: 'COMPLETED',
  agent: 'TestAgent',
  timestamp: '2024-01-15T10:30:00Z',
  duration: 5000,
  confidence: 0.95,
  explanation: 'Test explanation',
  metadata: { test: 'data' },
  timeline: [
    {
      id: 1,
      timestamp: '2024-01-15T10:30:00Z',
      action: 'Started',
      status: 'ACTIVE',
      details: 'Activity started'
    }
  ]
};

describe('ActivityDetailView - Basic Functionality', () => {
  const mockOnClose = vi.fn();

  beforeEach(() => {
    mockOnClose.mockClear();
  });

  it('renders without crashing', () => {
    render(
      <ActivityDetailView 
        activity={mockActivity} 
        onClose={mockOnClose} 
      />
    );
    
    expect(screen.getByText('Test Activity')).toBeInTheDocument();
  });

  it('displays activity title and description', () => {
    render(
      <ActivityDetailView 
        activity={mockActivity} 
        onClose={mockOnClose} 
      />
    );
    
    expect(screen.getByText('Test Activity')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });

  it('displays activity status', () => {
    render(
      <ActivityDetailView 
        activity={mockActivity} 
        onClose={mockOnClose} 
      />
    );
    
    expect(screen.getByText('COMPLETED')).toBeInTheDocument();
  });

  it('has a close button that calls onClose when clicked', () => {
    render(
      <ActivityDetailView 
        activity={mockActivity} 
        onClose={mockOnClose} 
      />
    );
    
    const closeButton = screen.getByLabelText('Close');
    fireEvent.click(closeButton);
    
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('displays timeline information', () => {
    render(
      <ActivityDetailView 
        activity={mockActivity} 
        onClose={mockOnClose} 
      />
    );
    
    expect(screen.getByText('Timeline')).toBeInTheDocument();
    expect(screen.getByText('Started')).toBeInTheDocument();
  });

  it('displays performance metrics', () => {
    render(
      <ActivityDetailView 
        activity={mockActivity} 
        onClose={mockOnClose} 
      />
    );
    
    expect(screen.getByText('Performance Metrics')).toBeInTheDocument();
    expect(screen.getByText('95%')).toBeInTheDocument(); // confidence
  });

  it('displays decision explanation', () => {
    render(
      <ActivityDetailView 
        activity={mockActivity} 
        onClose={mockOnClose} 
      />
    );
    
    expect(screen.getByText('Decision Explanation')).toBeInTheDocument();
    expect(screen.getByText('Test explanation')).toBeInTheDocument();
  });

  it('has proper accessibility attributes', () => {
    render(
      <ActivityDetailView 
        activity={mockActivity} 
        onClose={mockOnClose} 
      />
    );
    
    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    
    const closeButton = screen.getByLabelText('Close');
    expect(closeButton).toHaveAttribute('type', 'button');
  });

  it('displays human handoff button when needed', () => {
    const activeActivity = {
      ...mockActivity,
      status: 'ACTIVE'
    };
    
    render(
      <ActivityDetailView 
        activity={activeActivity} 
        onClose={mockOnClose} 
      />
    );
    
    expect(screen.getByText('Request Human Handoff')).toBeInTheDocument();
  });
});
