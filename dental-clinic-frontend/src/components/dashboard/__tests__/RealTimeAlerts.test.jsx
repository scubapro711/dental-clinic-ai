import React from 'react';
import { render, screen } from '@testing-library/react';
import RealTimeAlerts from '../RealTimeAlerts';

describe('RealTimeAlerts', () => {
  it('renders the component with alerts', () => {
    render(<RealTimeAlerts />);

    // Check for the title
    expect(screen.getByText('Real-time Alerts')).toBeInTheDocument();

    // Check for the alerts
    expect(screen.getByText('Emergency detected in conversation #123')).toBeInTheDocument();
    expect(screen.getByText('High patient volume detected')).toBeInTheDocument();
    expect(screen.getByText('Agent #2 is offline')).toBeInTheDocument();
  });
});

