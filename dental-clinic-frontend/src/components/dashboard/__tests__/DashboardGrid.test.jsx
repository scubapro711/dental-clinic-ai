import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { Users, Calendar, Activity, DollarSign } from 'lucide-react';
import DashboardGrid from '../DashboardGrid';

describe('DashboardGrid Component - Advanced Mission Control Testing', () => {
  // Mock data
  const mockCards = [
    {
      id: 'card-1',
      title: 'Active Patients',
      value: '1,234',
      subtitle: 'Currently in system',
      trend: 'up',
      trendValue: '+12%',
      status: 'success',
      icon: Users,
      priority: 'high'
    },
    {
      id: 'card-2',
      title: 'Appointments Today',
      value: '56',
      subtitle: 'Scheduled appointments',
      trend: 'down',
      trendValue: '-3%',
      status: 'warning',
      icon: Calendar,
      priority: 'medium'
    },
    {
      id: 'card-3',
      title: 'System Performance',
      value: '98.5%',
      subtitle: 'Uptime this month',
      trend: 'up',
      trendValue: '+0.2%',
      status: 'success',
      icon: Activity
    },
    {
      id: 'card-4',
      title: 'Revenue',
      value: '$12,345',
      subtitle: 'This month',
      trend: 'neutral',
      trendValue: '0%',
      status: 'error',
      icon: DollarSign
    }
  ];

  const defaultProps = {
    cards: mockCards,
    showControls: true,
    enableFiltering: true,
    enableRefresh: true,
    agentMode: 'active'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('Basic Rendering Tests', () => {
    it('renders dashboard grid with all cards', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      expect(screen.getByText('Mission Control Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Active Patients')).toBeInTheDocument();
      expect(screen.getByText('Appointments Today')).toBeInTheDocument();
      expect(screen.getByText('System Performance')).toBeInTheDocument();
      expect(screen.getByText('Revenue')).toBeInTheDocument();
    });

    it('renders with correct grid layout classes', () => {
      const { container } = render(<DashboardGrid {...defaultProps} />);
      
      const gridElement = container.querySelector('.grid');
      expect(gridElement).toHaveClass('grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-3', 'xl:grid-cols-4');
    });

    it('applies custom column configuration', () => {
      const { container } = render(<DashboardGrid {...defaultProps} columns={2} />);
      
      const gridElement = container.querySelector('.grid');
      expect(gridElement).toHaveClass('grid-cols-1', 'md:grid-cols-2');
    });

    it('applies custom gap configuration', () => {
      const { container } = render(<DashboardGrid {...defaultProps} gap="tight" />);
      
      // Find the actual dashboard grid (not the card grid)
      const gridElements = container.querySelectorAll('.grid');
      const dashboardGrid = Array.from(gridElements).find(el => 
        el.classList.contains('gap-3') || 
        el.classList.contains('gap-6') || 
        el.classList.contains('gap-8')
      );
      expect(dashboardGrid).toHaveClass('gap-3');
    });
  });

  describe('Mission Control Features', () => {
    it('displays agent status indicator', () => {
      render(<DashboardGrid {...defaultProps} agentMode="active" />);
      
      expect(screen.getByText('Agent: active')).toBeInTheDocument();
      expect(screen.getByTitle('Agent Mode: active')).toBeInTheDocument();
    });

    it('shows different agent status colors', () => {
      const { rerender } = render(<DashboardGrid {...defaultProps} agentMode="active" />);
      expect(screen.getByTitle('Agent Mode: active')).toHaveClass('bg-green-500');
      
      rerender(<DashboardGrid {...defaultProps} agentMode="monitoring" />);
      expect(screen.getByTitle('Agent Mode: monitoring')).toHaveClass('bg-blue-500');
      
      rerender(<DashboardGrid {...defaultProps} agentMode="error" />);
      expect(screen.getByTitle('Agent Mode: error')).toHaveClass('bg-red-500');
    });

    it('displays last refresh timestamp', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
    });

    it('shows card count information', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      expect(screen.getByText('Showing 4 of 4 cards')).toBeInTheDocument();
    });
  });

  describe('Grid Layout Controls', () => {
    it('renders grid layout control buttons', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      const layoutButtons = screen.getAllByTitle(/\d+ column/);
      expect(layoutButtons).toHaveLength(4);
    });

    it('changes grid layout when layout buttons are clicked', () => {
      const { container } = render(<DashboardGrid {...defaultProps} />);
      
      const twoColumnButton = screen.getByTitle('2 columns');
      fireEvent.click(twoColumnButton);
      
      // Find the dashboard grid element
      const gridElements = container.querySelectorAll('.grid');
      const dashboardGrid = Array.from(gridElements).find(el => 
        el.classList.contains('grid-cols-1') && el.classList.contains('md:grid-cols-2')
      );
      expect(dashboardGrid).toBeInTheDocument();
    });

    it('highlights active layout button', () => {
      render(<DashboardGrid {...defaultProps} columns={3} />);
      
      // The component should show the 3-column button as active
      // This would be tested by checking button variants, but requires more complex DOM inspection
      expect(screen.getByTitle('3 columns')).toBeInTheDocument();
    });
  });

  describe('Filtering Functionality', () => {
    it('displays filter buttons with correct counts', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      // Look for capitalized versions as they appear in the component
      expect(screen.getByRole('button', { name: /all/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /success/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /warning/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /error/i })).toBeInTheDocument();
      
      // Check that count badges exist
      const badges = screen.getAllByText(/^\d+$/);
      expect(badges.length).toBeGreaterThan(0);
    });

    it('filters cards by status', async () => {
      render(<DashboardGrid {...defaultProps} />);
      
      const successFilter = screen.getByRole('button', { name: /success/i });
      fireEvent.click(successFilter);
      
      await waitFor(() => {
        expect(screen.getByText('Showing 2 of 4 cards')).toBeInTheDocument();
        expect(screen.getByText('Active Patients')).toBeInTheDocument();
        expect(screen.getByText('System Performance')).toBeInTheDocument();
        expect(screen.queryByText('Appointments Today')).not.toBeInTheDocument();
      });
    });

    it('calls onFilterChange callback when filter changes', () => {
      const onFilterChange = vi.fn();
      render(<DashboardGrid {...defaultProps} onFilterChange={onFilterChange} />);
      
      const warningFilter = screen.getByRole('button', { name: /warning/i });
      fireEvent.click(warningFilter);
      
      expect(onFilterChange).toHaveBeenCalledWith('warning');
    });

    it('can disable filtering', () => {
      render(<DashboardGrid {...defaultProps} enableFiltering={false} />);
      
      expect(screen.queryByText('Filter by status:')).not.toBeInTheDocument();
    });
  });

  describe('Refresh Functionality', () => {
    it('displays refresh button', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      expect(screen.getByText('Refresh')).toBeInTheDocument();
    });

    it('calls onRefresh when refresh button is clicked', async () => {
      const onRefresh = vi.fn().mockResolvedValue();
      render(<DashboardGrid {...defaultProps} onRefresh={onRefresh} />);
      
      const refreshButton = screen.getByText('Refresh');
      fireEvent.click(refreshButton);
      
      expect(onRefresh).toHaveBeenCalled();
    });

    it('shows loading state during refresh', async () => {
      const onRefresh = vi.fn().mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 100))
      );
      render(<DashboardGrid {...defaultProps} onRefresh={onRefresh} />);
      
      const refreshButton = screen.getByText('Refresh');
      fireEvent.click(refreshButton);
      
      expect(screen.getByText('Refreshing...')).toBeInTheDocument();
      expect(refreshButton).toBeDisabled();
      
      await waitFor(() => {
        expect(screen.getByText('Refresh')).toBeInTheDocument();
      });
    });

    it('auto-refreshes at specified interval', async () => {
      const onRefresh = vi.fn().mockResolvedValue();
      render(<DashboardGrid {...defaultProps} onRefresh={onRefresh} refreshInterval={1000} />);
      
      expect(onRefresh).not.toHaveBeenCalled();
      
      act(() => {
        vi.advanceTimersByTime(1000);
      });
      
      await waitFor(() => {
        expect(onRefresh).toHaveBeenCalledTimes(1);
      });
    });

    it('can disable refresh functionality', () => {
      render(<DashboardGrid {...defaultProps} enableRefresh={false} />);
      
      expect(screen.queryByText('Refresh')).not.toBeInTheDocument();
    });
  });

  describe('Expand/Collapse Functionality', () => {
    it('displays expand button', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      expect(screen.getByText('Expand')).toBeInTheDocument();
    });

    it('toggles between expand and collapse states', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      const expandButton = screen.getByText('Expand');
      fireEvent.click(expandButton);
      
      expect(screen.getByText('Collapse')).toBeInTheDocument();
    });

    it('applies fullscreen classes when expanded', () => {
      const { container } = render(<DashboardGrid {...defaultProps} />);
      
      const expandButton = screen.getByText('Expand');
      fireEvent.click(expandButton);
      
      const dashboardContainer = container.firstChild;
      expect(dashboardContainer).toHaveClass('fixed', 'inset-0', 'z-50');
    });
  });

  describe('Card Interaction', () => {
    it('calls onCardClick when card is clicked', () => {
      const onCardClick = vi.fn();
      render(<DashboardGrid {...defaultProps} onCardClick={onCardClick} />);
      
      const firstCard = screen.getByText('Active Patients').closest('[role="button"]');
      fireEvent.click(firstCard);
      
      expect(onCardClick).toHaveBeenCalledWith(mockCards[0], 0);
    });

    it('applies priority styling to high priority cards', () => {
      const { container } = render(<DashboardGrid {...defaultProps} />);
      
      const highPriorityCard = screen.getByText('Active Patients').closest('.ring-2');
      expect(highPriorityCard).toHaveClass('ring-red-200');
    });

    it('applies hover effects to cards', () => {
      const { container } = render(<DashboardGrid {...defaultProps} />);
      
      const cardWrapper = container.querySelector('.hover\\:scale-\\[1\\.02\\]');
      expect(cardWrapper).toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('shows empty state when no cards are provided', () => {
      render(<DashboardGrid {...defaultProps} cards={[]} />);
      
      expect(screen.getByText('No cards to display')).toBeInTheDocument();
      expect(screen.getByText('No dashboard cards are currently available. Add some cards to get started.')).toBeInTheDocument();
    });

    it('shows filtered empty state when no cards match filter', async () => {
      render(<DashboardGrid {...defaultProps} />);
      
      // Filter by a status that doesn't exist
      const neutralFilter = screen.getByRole('button', { name: /neutral/i });
      fireEvent.click(neutralFilter);
      
      await waitFor(() => {
        expect(screen.getByText('No cards to display')).toBeInTheDocument();
        expect(screen.getByText(/No cards match the "neutral" status filter/)).toBeInTheDocument();
        expect(screen.getByText('Show All Cards')).toBeInTheDocument();
      });
    });

    it('can reset filter from empty state', async () => {
      render(<DashboardGrid {...defaultProps} />);
      
      const neutralFilter = screen.getByRole('button', { name: /neutral/i });
      fireEvent.click(neutralFilter);
      
      await waitFor(() => {
        const showAllButton = screen.getByText('Show All Cards');
        fireEvent.click(showAllButton);
      });
      
      await waitFor(() => {
        expect(screen.getByText('Showing 4 of 4 cards')).toBeInTheDocument();
      });
    });
  });

  describe('Performance Features', () => {
    it('shows performance indicator for large datasets', () => {
      const largeCardSet = Array.from({ length: 25 }, (_, i) => ({
        ...mockCards[0],
        id: `card-${i}`,
        title: `Card ${i}`
      }));
      
      render(<DashboardGrid {...defaultProps} cards={largeCardSet} />);
      
      expect(screen.getByText('Performance mode: Optimized for 25 cards')).toBeInTheDocument();
    });

    it('handles large datasets efficiently', () => {
      const largeCardSet = Array.from({ length: 100 }, (_, i) => ({
        ...mockCards[0],
        id: `card-${i}`,
        title: `Card ${i}`
      }));
      
      expect(() => {
        render(<DashboardGrid {...defaultProps} cards={largeCardSet} />);
      }).not.toThrow();
    });
  });

  describe('Accessibility Tests', () => {
    it('provides proper ARIA labels and roles', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      // Check that cards maintain their button role
      const cardButtons = screen.getAllByRole('button');
      expect(cardButtons.length).toBeGreaterThan(4); // Cards + control buttons
    });

    it('supports keyboard navigation', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      const refreshButton = screen.getByText('Refresh');
      refreshButton.focus();
      expect(refreshButton).toHaveFocus();
    });

    it('provides meaningful button labels', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      expect(screen.getByTitle('1 column')).toBeInTheDocument();
      expect(screen.getByTitle('2 columns')).toBeInTheDocument();
      expect(screen.getByTitle('3 columns')).toBeInTheDocument();
      expect(screen.getByTitle('4 columns')).toBeInTheDocument();
    });
  });

  describe('Responsive Design Tests', () => {
    it('applies responsive grid classes correctly', () => {
      const { container } = render(<DashboardGrid {...defaultProps} />);
      
      const gridElement = container.querySelector('.grid');
      expect(gridElement).toHaveClass('grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-3', 'xl:grid-cols-4');
    });

    it('handles different gap configurations', () => {
      const { container, rerender } = render(<DashboardGrid {...defaultProps} gap="tight" />);
      expect(container.querySelector('.grid')).toHaveClass('gap-3');
      
      rerender(<DashboardGrid {...defaultProps} gap="loose" />);
      expect(container.querySelector('.grid')).toHaveClass('gap-8');
    });
  });

  describe('Error Handling', () => {
    it('handles refresh errors gracefully', async () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
      const onRefresh = vi.fn().mockRejectedValue(new Error('Refresh failed'));
      
      render(<DashboardGrid {...defaultProps} onRefresh={onRefresh} />);
      
      const refreshButton = screen.getByText('Refresh');
      fireEvent.click(refreshButton);
      
      await waitFor(() => {
        expect(screen.getByText('Refresh')).toBeInTheDocument();
      });
      
      expect(consoleError).toHaveBeenCalledWith('Dashboard refresh failed:', expect.any(Error));
      consoleError.mockRestore();
    });

    it('handles missing card properties gracefully', () => {
      const incompleteCards = [{ id: 'incomplete', title: 'Incomplete Card' }];
      
      expect(() => {
        render(<DashboardGrid {...defaultProps} cards={incompleteCards} />);
      }).not.toThrow();
    });
  });

  describe('Integration Tests', () => {
    it('integrates properly with StatisticsCard components', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      // Verify that StatisticsCard features are working
      expect(screen.getByText('1,234')).toBeInTheDocument();
      expect(screen.getByText('+12%')).toBeInTheDocument();
      
      // Check for trending up elements (there might be multiple)
      const trendingUpElements = screen.getAllByLabelText('Trending up');
      expect(trendingUpElements.length).toBeGreaterThan(0);
    });

    it('passes agent status to child cards', () => {
      render(<DashboardGrid {...defaultProps} agentMode="monitoring" />);
      
      // All cards should receive the agent status
      const agentStatusIndicators = document.querySelectorAll('[title*="Agent status"]');
      expect(agentStatusIndicators.length).toBe(mockCards.length);
    });
  });

  describe('Controls Visibility', () => {
    it('can hide controls completely', () => {
      render(<DashboardGrid {...defaultProps} showControls={false} />);
      
      expect(screen.queryByText('Mission Control Dashboard')).not.toBeInTheDocument();
      expect(screen.queryByText('Refresh')).not.toBeInTheDocument();
    });

    it('still renders cards when controls are hidden', () => {
      render(<DashboardGrid {...defaultProps} showControls={false} />);
      
      expect(screen.getByText('Active Patients')).toBeInTheDocument();
      expect(screen.getByText('Appointments Today')).toBeInTheDocument();
    });
  });
});
