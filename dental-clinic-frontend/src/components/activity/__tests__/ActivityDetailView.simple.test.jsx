import { describe, test, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import ActivityDetailView from '../ActivityDetailView';

const mockOnClose = vi.fn();
const mockOnHumanHandoff = vi.fn();

vi.setConfig({ testTimeout: 15000, hookTimeout: 20000 });

describe('ActivityDetailView Component (Simple)', () => {
  test('modal overlay is present and has role="dialog"', async () => {
    render(
      <ActivityDetailView 
        activityId="test-123" 
        onClose={mockOnClose}
        onHumanHandoff={mockOnHumanHandoff}
      />
    );

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });
  });

  test('displays Human Handoff button for ACTIVE status', async () => {
    render(
      <ActivityDetailView 
        activityId="test-123" 
        onClose={mockOnClose}
        onHumanHandoff={mockOnHumanHandoff}
      />
    );

    await waitFor(() => {
        expect(screen.getByText('Request Human Handoff')).toBeInTheDocument();
    });
  });
});

