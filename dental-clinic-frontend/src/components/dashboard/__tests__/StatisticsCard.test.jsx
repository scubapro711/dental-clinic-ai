import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Users, Calendar, Activity } from 'lucide-react';
import StatisticsCard from '../StatisticsCard';

describe('StatisticsCard Component - Advanced Agentic UX Testing', () => {
  const defaultProps = {
    title: 'Active Patients',
    value: '1,234',
    subtitle: 'Currently in system',
    trend: 'up',
    trendValue: '+12%',
    status: 'success',
    icon: Users,
    agentStatus: 'active',
    lastUpdated: '2 minutes ago',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Basic Rendering Tests', () => {
    it('renders all required elements correctly', () => {
      render(<StatisticsCard {...defaultProps} />);
      
      expect(screen.getByText('Active Patients')).toBeInTheDocument();
      expect(screen.getByText('1,234')).toBeInTheDocument();
      expect(screen.getByText('Currently in system')).toBeInTheDocument();
      expect(screen.getByText('+12%')).toBeInTheDocument();
      expect(screen.getByText('Last updated: 2 minutes ago')).toBeInTheDocument();
    });

    it('renders with correct ARIA attributes', () => {
      render(<StatisticsCard {...defaultProps} />);
      
      const card = screen.getByRole('button');
      expect(card).toHaveAttribute('aria-label', 'Statistics card: Active Patients, value: 1,234');
      expect(card).toHaveAttribute('tabIndex', '0');
    });

    it('displays agent status indicator', () => {
      render(<StatisticsCard {...defaultProps} agentStatus="active" />);
      
      const statusIndicator = screen.getByLabelText('Agent status: active');
      expect(statusIndicator).toBeInTheDocument();
      expect(statusIndicator).toHaveClass('bg-green-500');
    });
  });

  describe('Agent Status Tests (Agentic UX)', () => {
    it('shows correct colors for different agent statuses', () => {
      const { rerender } = render(<StatisticsCard {...defaultProps} agentStatus="active" />);
      expect(screen.getByLabelText('Agent status: active')).toHaveClass('bg-green-500');
      
      rerender(<StatisticsCard {...defaultProps} agentStatus="idle" />);
      expect(screen.getByLabelText('Agent status: idle')).toHaveClass('bg-yellow-500');
      
      rerender(<StatisticsCard {...defaultProps} agentStatus="error" />);
      expect(screen.getByLabelText('Agent status: error')).toHaveClass('bg-red-500');
      
      rerender(<StatisticsCard {...defaultProps} agentStatus="offline" />);
      expect(screen.getByLabelText('Agent status: offline')).toHaveClass('bg-gray-500');
    });

    it('provides accessible status information', () => {
      render(<StatisticsCard {...defaultProps} agentStatus="active" />);
      
      const statusIndicator = screen.getByLabelText('Agent status: active');
      expect(statusIndicator).toHaveAttribute('title', 'Agent status: active');
    });
  });

  describe('Status Badge Tests', () => {
    it('displays correct status badges', () => {
      const { rerender } = render(<StatisticsCard {...defaultProps} status="success" />);
      expect(screen.getByLabelText('Status: Success')).toBeInTheDocument();
      
      rerender(<StatisticsCard {...defaultProps} status="warning" />);
      expect(screen.getByLabelText('Status: Warning')).toBeInTheDocument();
      
      rerender(<StatisticsCard {...defaultProps} status="error" />);
      expect(screen.getByLabelText('Status: Error')).toBeInTheDocument();
      
      rerender(<StatisticsCard {...defaultProps} status="neutral" />);
      expect(screen.getByLabelText('Status: Neutral')).toBeInTheDocument();
    });

    it('applies correct styling for status badges', () => {
      const { rerender } = render(<StatisticsCard {...defaultProps} status="success" />);
      expect(screen.getByLabelText('Status: Success')).toHaveClass('bg-green-100', 'text-green-800');
      
      rerender(<StatisticsCard {...defaultProps} status="warning" />);
      expect(screen.getByLabelText('Status: Warning')).toHaveClass('bg-yellow-100', 'text-yellow-800');
      
      rerender(<StatisticsCard {...defaultProps} status="error" />);
      expect(screen.getByLabelText('Status: Error')).toHaveClass('bg-red-100', 'text-red-800');
    });
  });

  describe('Trend Indicator Tests', () => {
    it('displays correct trend icons and colors', () => {
      const { rerender } = render(<StatisticsCard {...defaultProps} trend="up" trendValue="+12%" />);
      expect(screen.getByLabelText('Trending up')).toBeInTheDocument();
      expect(screen.getByText('+12%')).toHaveClass('text-green-600');
      
      rerender(<StatisticsCard {...defaultProps} trend="down" trendValue="-5%" />);
      expect(screen.getByLabelText('Trending down')).toBeInTheDocument();
      expect(screen.getByText('-5%')).toHaveClass('text-red-600');
      
      rerender(<StatisticsCard {...defaultProps} trend="neutral" trendValue="0%" />);
      expect(screen.getByLabelText('No change')).toBeInTheDocument();
      expect(screen.getByText('0%')).toHaveClass('text-gray-600');
    });

    it('provides accessible trend information', () => {
      render(<StatisticsCard {...defaultProps} trend="up" trendValue="+12%" />);
      
      expect(screen.getByLabelText('Trend: up by +12%')).toBeInTheDocument();
    });
  });

  describe('Loading State Tests', () => {
    it('shows loading state correctly', () => {
      render(<StatisticsCard {...defaultProps} isLoading={true} />);
      
      expect(screen.getByText('Loading...')).toBeInTheDocument();
      expect(screen.getByRole('button')).toHaveClass('opacity-50', 'pointer-events-none');
    });

    it('shows skeleton loader for value when loading', () => {
      render(<StatisticsCard {...defaultProps} isLoading={true} />);
      
      const skeleton = document.querySelector('.animate-pulse');
      expect(skeleton).toBeInTheDocument();
      expect(skeleton).toHaveClass('h-8', 'w-16', 'bg-gray-200');
    });

    it('hides trend when loading', () => {
      render(<StatisticsCard {...defaultProps} isLoading={true} trend="up" trendValue="+12%" />);
      
      expect(screen.queryByLabelText('Trending up')).not.toBeInTheDocument();
      expect(screen.queryByText('+12%')).not.toBeInTheDocument();
    });
  });

  describe('Interaction Tests', () => {
    it('handles click events', () => {
      const onClickMock = vi.fn();
      render(<StatisticsCard {...defaultProps} onClick={onClickMock} />);
      
      const card = screen.getByRole('button');
      fireEvent.click(card);
      
      expect(onClickMock).toHaveBeenCalledTimes(1);
    });

    it('handles keyboard navigation', () => {
      const onClickMock = vi.fn();
      render(<StatisticsCard {...defaultProps} onClick={onClickMock} />);
      
      const card = screen.getByRole('button');
      card.focus();
      expect(card).toHaveFocus();
      
      fireEvent.keyDown(card, { key: 'Enter' });
      expect(onClickMock).toHaveBeenCalledTimes(1);
      
      fireEvent.keyDown(card, { key: ' ' });
      expect(onClickMock).toHaveBeenCalledTimes(2);
    });

    it('shows hover effects', async () => {
      render(<StatisticsCard {...defaultProps} />);
      
      const card = screen.getByRole('button');
      expect(card).toHaveClass('hover:shadow-md');
    });
  });

  describe('Icon Tests', () => {
    it('renders custom icons correctly', () => {
      const { rerender } = render(<StatisticsCard {...defaultProps} icon={Users} />);
      expect(document.querySelector('.lucide-users')).toBeInTheDocument();
      
      rerender(<StatisticsCard {...defaultProps} icon={Calendar} />);
      expect(document.querySelector('.lucide-calendar')).toBeInTheDocument();
      
      rerender(<StatisticsCard {...defaultProps} icon={Activity} />);
      expect(document.querySelector('.lucide-activity')).toBeInTheDocument();
    });

    it('handles missing icon gracefully', () => {
      expect(() => {
        render(<StatisticsCard {...defaultProps} icon={null} />);
      }).not.toThrow();
    });
  });

  describe('Responsive Design Tests', () => {
    it('maintains proper spacing and layout', () => {
      const { container } = render(<StatisticsCard {...defaultProps} />);
      const card = container.firstChild;
      
      expect(card).toHaveClass('transition-all', 'duration-200');
    });

    it('shows border accent correctly', () => {
      const { container } = render(<StatisticsCard {...defaultProps} />);
      const card = container.firstChild;
      
      expect(card).toHaveClass('border-l-4', 'border-l-blue-500');
    });
  });

  describe('Accessibility Tests', () => {
    it('provides comprehensive screen reader support', () => {
      render(<StatisticsCard {...defaultProps} />);
      
      expect(screen.getByLabelText('Main value: 1,234')).toBeInTheDocument();
      expect(screen.getByLabelText('Subtitle: Currently in system')).toBeInTheDocument();
      expect(screen.getByLabelText('Last updated: 2 minutes ago')).toBeInTheDocument();
    });

    it('has proper semantic structure', () => {
      render(<StatisticsCard {...defaultProps} />);
      
      expect(screen.getByRole('button')).toBeInTheDocument();
      
      // Check for sr-only elements by their content (status badge has sr-only text)
      const srOnlyElements = document.querySelectorAll('.sr-only');
      expect(srOnlyElements.length).toBeGreaterThan(0);
    });
  });

  describe('Performance Tests', () => {
    it('renders within performance budget', async () => {
      const startTime = performance.now();
      render(<StatisticsCard {...defaultProps} />);
      const endTime = performance.now();
      
      expect(endTime - startTime).toBeLessThan(25); // Reasonable performance budget
    });

    it('handles rapid prop updates efficiently', async () => {
      const { rerender } = render(<StatisticsCard {...defaultProps} />);
      
      for (let i = 0; i < 100; i++) {
        rerender(<StatisticsCard {...defaultProps} value={`${1000 + i}`} />);
      }
      
      expect(screen.getByText('1,099')).toBeInTheDocument();
    });
  });

  describe('Edge Cases Tests', () => {
    it('handles missing props gracefully', () => {
      expect(() => {
        render(<StatisticsCard />);
      }).not.toThrow();
    });

    it('handles extremely long values', () => {
      render(<StatisticsCard {...defaultProps} value="999,999,999,999" />);
      expect(screen.getByText('999,999,999,999')).toBeInTheDocument();
    });

    it('handles special characters in title', () => {
      render(<StatisticsCard {...defaultProps} title="Patients (Active) - 2024 & More" />);
      expect(screen.getByText('Patients (Active) - 2024 & More')).toBeInTheDocument();
    });

    it('handles negative values correctly', () => {
      render(<StatisticsCard {...defaultProps} value="-1,234" trend="down" trendValue="-50%" />);
      expect(screen.getByText('-1,234')).toBeInTheDocument();
      expect(screen.getByText('-50%')).toHaveClass('text-red-600');
    });
  });

  describe('Integration Tests', () => {
    it('integrates properly with dashboard layout', () => {
      const DashboardGrid = () => (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatisticsCard {...defaultProps} />
          <StatisticsCard {...defaultProps} title="Appointments" value="56" />
          <StatisticsCard {...defaultProps} title="Revenue" value="$12,345" />
        </div>
      );
      
      render(<DashboardGrid />);
      expect(screen.getByText('Active Patients')).toBeInTheDocument();
      expect(screen.getByText('Appointments')).toBeInTheDocument();
      expect(screen.getByText('Revenue')).toBeInTheDocument();
    });
  });

  describe('Stress Tests', () => {
    it('handles rapid status changes', async () => {
      const { rerender } = render(<StatisticsCard {...defaultProps} />);
      
      const statuses = ['active', 'idle', 'error', 'offline'];
      
      for (let i = 0; i < 50; i++) {
        const status = statuses[i % statuses.length];
        rerender(<StatisticsCard {...defaultProps} agentStatus={status} />);
        
        if (i % 10 === 0) {
          await new Promise(resolve => setTimeout(resolve, 1));
        }
      }
      
      expect(screen.getByLabelText('Agent status: idle')).toBeInTheDocument();
    });

    it('maintains performance under memory pressure', () => {
      // Create multiple instances
      const MultipleCards = () => (
        <div>
          {Array.from({ length: 100 }, (_, i) => (
            <StatisticsCard 
              key={i}
              {...defaultProps} 
              title={`Card ${i}`}
              value={`${1000 + i}`}
            />
          ))}
        </div>
      );
      
      expect(() => {
        render(<MultipleCards />);
      }).not.toThrow();
    });
  });

  describe('Real-time Update Simulation', () => {
    it('simulates real-time data updates', async () => {
      const { rerender } = render(<StatisticsCard {...defaultProps} />);
      
      // Simulate real-time updates every 100ms
      const updates = [
        { value: '1,235', trendValue: '+13%' },
        { value: '1,236', trendValue: '+14%' },
        { value: '1,237', trendValue: '+15%' },
      ];
      
      for (const update of updates) {
        rerender(<StatisticsCard {...defaultProps} {...update} />);
        await waitFor(() => {
          expect(screen.getByText(update.value)).toBeInTheDocument();
        });
      }
    });
  });
});
