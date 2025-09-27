import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import DashboardGrid from '../DashboardGrid';

// Mock StatisticsCard component
vi.mock('../StatisticsCard', () => ({
  default: ({ title, value, change, trend, onClick, className }) => (
    <div 
      className={`statistics-card ${className || ''}`}
      onClick={onClick}
      data-testid="statistics-card"
    >
      <h3>{title}</h3>
      <div>{value}</div>
      {change && <span>{change}</span>}
      {trend && <span aria-label={`Trending ${trend}`}>{trend}</span>}
    </div>
  )
}));

const mockCards = [
  {
    id: '1',
    title: 'Total Appointments',
    value: '1,234',
    change: '+12%',
    trend: 'up',
    status: 'success',
    priority: 'high'
  },
  {
    id: '2',
    title: 'Active Patients',
    value: '856',
    change: '+5%',
    trend: 'up',
    status: 'success'
  },
  {
    id: '3',
    title: 'Pending Reviews',
    value: '23',
    change: '-2%',
    trend: 'down',
    status: 'warning'
  },
  {
    id: '4',
    title: 'System Errors',
    value: '2',
    change: '+1',
    trend: 'up',
    status: 'error'
  }
];

const defaultProps = {
  cards: mockCards,
  onCardClick: vi.fn(),
  onRefresh: vi.fn(),
  onFilterChange: vi.fn()
};

describe('DashboardGrid Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('renders without crashing', () => {
      render(<DashboardGrid {...defaultProps} />);
      expect(screen.getByText('Mission Control Dashboard')).toBeInTheDocument();
    });

    it('renders all provided cards', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      expect(screen.getByText('Total Appointments')).toBeInTheDocument();
      expect(screen.getByText('Active Patients')).toBeInTheDocument();
      expect(screen.getByText('Pending Reviews')).toBeInTheDocument();
      expect(screen.getByText('System Errors')).toBeInTheDocument();
    });

    it('displays agent status correctly', () => {
      render(<DashboardGrid {...defaultProps} agentMode="active" />);
      expect(screen.getByText('Agent: active')).toBeInTheDocument();
    });

    it('shows card count in footer', () => {
      render(<DashboardGrid {...defaultProps} />);
      expect(screen.getByText('Showing 4 of 4 cards')).toBeInTheDocument();
    });
  });

  describe('Card Interactions', () => {
    it('calls onCardClick when a card is clicked', () => {
      const onCardClick = vi.fn();
      render(<DashboardGrid {...defaultProps} onCardClick={onCardClick} />);
      
      const firstCard = screen.getAllByTestId('statistics-card')[0];
      fireEvent.click(firstCard);
      
      expect(onCardClick).toHaveBeenCalledWith(mockCards[0], 0);
    });

    it('applies priority styling to high priority cards', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      const cards = screen.getAllByTestId('statistics-card');
      expect(cards[0]).toHaveClass('ring-2', 'ring-red-200');
    });
  });

  describe('Refresh Functionality', () => {
    it('calls onRefresh when refresh button is clicked', () => {
      const onRefresh = vi.fn().mockResolvedValue();
      render(<DashboardGrid {...defaultProps} onRefresh={onRefresh} />);
      
      const refreshButton = screen.getByText('Refresh');
      fireEvent.click(refreshButton);
      
      expect(onRefresh).toHaveBeenCalled();
    });

    it('shows refresh button when enableRefresh is true', () => {
      render(<DashboardGrid {...defaultProps} enableRefresh={true} />);
      expect(screen.getByText('Refresh')).toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('shows empty state when no cards are provided', () => {
      render(<DashboardGrid {...defaultProps} cards={[]} />);
      
      expect(screen.getByText('No cards to display')).toBeInTheDocument();
      expect(screen.getByText(/No dashboard cards are currently available/)).toBeInTheDocument();
    });
  });

  describe('Performance Features', () => {
    it('shows performance indicator for large datasets', () => {
      const largeCardSet = Array.from({ length: 25 }, (_, i) => ({
        id: `card-${i}`,
        title: `Card ${i}`,
        value: `${i * 100}`,
        status: 'success'
      }));
      
      render(<DashboardGrid {...defaultProps} cards={largeCardSet} />);
      
      expect(screen.getByText('Performance mode: Optimized for 25 cards')).toBeInTheDocument();
    });

    it('handles large datasets efficiently', () => {
      const largeCardSet = Array.from({ length: 100 }, (_, i) => ({
        id: `card-${i}`,
        title: `Card ${i}`,
        value: `${i * 100}`,
        status: 'success'
      }));
      
      const startTime = performance.now();
      render(<DashboardGrid {...defaultProps} cards={largeCardSet} />);
      const endTime = performance.now();
      
      expect(endTime - startTime).toBeLessThan(1000);
    });
  });

  describe('Responsive Design Tests', () => {
    it('applies responsive grid classes correctly', () => {
      const { container } = render(<DashboardGrid {...defaultProps} />);
      
      // Look for the main grid container, not just any element with .grid class
      const gridElement = container.querySelector('div.grid.w-full');
      expect(gridElement).toHaveClass('grid-cols-1');
      expect(gridElement).toHaveClass('md:grid-cols-2');
      expect(gridElement).toHaveClass('lg:grid-cols-3');
      expect(gridElement).toHaveClass('xl:grid-cols-4');
    });

    it('handles different gap configurations', () => {
      const { container, rerender } = render(<DashboardGrid {...defaultProps} gap="tight" />);
      const gridElement = container.querySelector('div.grid.w-full');
      expect(gridElement).toHaveClass('gap-3');
      
      rerender(<DashboardGrid {...defaultProps} gap="loose" />);
      const updatedGridElement = container.querySelector('div.grid.w-full');
      expect(updatedGridElement).toHaveClass('gap-8');
    });
  });

  describe('Error Handling', () => {
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
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels and roles', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
      
      buttons.forEach(button => {
        expect(button).toBeVisible();
      });
    });

    it('supports keyboard navigation', () => {
      render(<DashboardGrid {...defaultProps} />);
      
      const refreshButton = screen.getByText('Refresh');
      refreshButton.focus();
      expect(document.activeElement).toBe(refreshButton);
    });
  });

  describe('Configuration Options', () => {
    it('hides controls when showControls is false', () => {
      render(<DashboardGrid {...defaultProps} showControls={false} />);
      
      expect(screen.queryByText('Mission Control Dashboard')).not.toBeInTheDocument();
      expect(screen.queryByText('Refresh')).not.toBeInTheDocument();
    });

    it('disables refresh when enableRefresh is false', () => {
      render(<DashboardGrid {...defaultProps} enableRefresh={false} />);
      
      expect(screen.queryByText('Refresh')).not.toBeInTheDocument();
    });
  });
});
