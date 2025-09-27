import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ActivityFeed from '../ActivityFeed';

// Mock WebSocket
class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = WebSocket.CONNECTING;
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      if (this.onopen) this.onopen();
    }, 10);
  }

  close() {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) this.onclose();
  }

  send(data) {
    // Mock send functionality
  }
}

global.WebSocket = MockWebSocket;

const mockActivities = [
  {
    id: '1',
    title: 'תור חדש נקבע',
    description: 'תור לחולה יוסי כהן נקבע ליום ראשון',
    type: 'appointment',
    status: 'completed',
    agent: 'dental_agent_1',
    timestamp: '2025-09-27T18:00:00Z',
    duration: '2.3s'
  },
  {
    id: '2',
    title: 'עדכון פרטי חולה',
    description: 'פרטי החולה שרה לוי עודכנו במערכת',
    type: 'patient',
    status: 'in_progress',
    agent: 'dental_agent_2',
    timestamp: '2025-09-27T18:01:00Z',
    duration: '1.5s'
  },
  {
    id: '3',
    title: 'שגיאה במערכת',
    description: 'שגיאה בחיבור למסד הנתונים',
    type: 'error',
    status: 'failed',
    agent: 'dental_agent_1',
    timestamp: '2025-09-27T18:02:00Z',
    duration: '0.1s'
  }
];

describe('ActivityFeed Component', () => {
  let mockOnActivityClick;

  beforeEach(() => {
    mockOnActivityClick = vi.fn();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial Rendering', () => {
    it('renders the component with header and empty state', () => {
      render(<ActivityFeed activities={[]} onActivityClick={mockOnActivityClick} />);
      
      expect(screen.getByText('פיד פעילות הסוכן')).toBeInTheDocument();
      expect(screen.getByText('אין פעילויות להצגה')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('חיפוש פעילויות...')).toBeInTheDocument();
    });

    it('renders activities when provided', () => {
      render(<ActivityFeed activities={mockActivities} onActivityClick={mockOnActivityClick} />);
      
      expect(screen.getByText('תור חדש נקבע')).toBeInTheDocument();
      expect(screen.getByText('עדכון פרטי חולה')).toBeInTheDocument();
      expect(screen.getByText('שגיאה במערכת')).toBeInTheDocument();
    });

    it('displays connection status', () => {
      render(<ActivityFeed activities={[]} onActivityClick={mockOnActivityClick} />);
      
      expect(screen.getByText('לא מחובר')).toBeInTheDocument();
    });
  });

  describe('Filtering Functionality', () => {
    it('filters activities by search term', async () => {
      render(<ActivityFeed activities={mockActivities} onActivityClick={mockOnActivityClick} />);
      
      const searchInput = screen.getByPlaceholderText('חיפוש פעילויות...');
      fireEvent.change(searchInput, { target: { value: 'תור' } });

      await waitFor(() => {
        expect(screen.getByText('תור חדש נקבע')).toBeInTheDocument();
        expect(screen.queryByText('עדכון פרטי חולה')).not.toBeInTheDocument();
      });
    });

    it('filters activities by agent', async () => {
      render(<ActivityFeed activities={mockActivities} onActivityClick={mockOnActivityClick} />);
      
      const agentSelect = screen.getByDisplayValue('כל הסוכנים');
      fireEvent.change(agentSelect, { target: { value: 'dental_agent_1' } });

      await waitFor(() => {
        expect(screen.getByText('תור חדש נקבע')).toBeInTheDocument();
        expect(screen.getByText('שגיאה במערכת')).toBeInTheDocument();
        expect(screen.queryByText('עדכון פרטי חולה')).not.toBeInTheDocument();
      });
    });

    it('filters activities by type', async () => {
      render(<ActivityFeed activities={mockActivities} onActivityClick={mockOnActivityClick} />);
      
      const typeSelect = screen.getByDisplayValue('כל הסוגים');
      fireEvent.change(typeSelect, { target: { value: 'appointment' } });

      await waitFor(() => {
        expect(screen.getByText('תור חדש נקבע')).toBeInTheDocument();
        expect(screen.queryByText('עדכון פרטי חולה')).not.toBeInTheDocument();
        expect(screen.queryByText('שגיאה במערכת')).not.toBeInTheDocument();
      });
    });

    it('shows correct count in footer', () => {
      render(<ActivityFeed activities={mockActivities} onActivityClick={mockOnActivityClick} />);
      
      expect(screen.getByText('מציג 3 מתוך 3 פעילויות')).toBeInTheDocument();
    });
  });

  describe('UI Interactions', () => {
    it('calls onActivityClick when activity is clicked', () => {
      render(<ActivityFeed activities={mockActivities} onActivityClick={mockOnActivityClick} />);
      
      const firstActivity = screen.getByText('תור חדש נקבע');
      fireEvent.click(firstActivity.closest('.cursor-pointer'));

      expect(mockOnActivityClick).toHaveBeenCalledWith(mockActivities[0]);
    });

    it('updates search input value', () => {
      render(<ActivityFeed activities={mockActivities} onActivityClick={mockOnActivityClick} />);
      
      const searchInput = screen.getByPlaceholderText('חיפוש פעילויות...');
      fireEvent.change(searchInput, { target: { value: 'test search' } });

      expect(searchInput.value).toBe('test search');
    });
  });

  describe('Performance', () => {
    it('renders quickly with large dataset', () => {
      const largeDataset = Array.from({ length: 1000 }, (_, i) => ({
        id: `activity-${i}`,
        title: `פעילות ${i}`,
        description: `תיאור פעילות ${i}`,
        type: 'system',
        status: 'completed',
        agent: `agent_${i % 10}`,
        timestamp: new Date().toISOString()
      }));

      const startTime = performance.now();
      render(<ActivityFeed activities={largeDataset} onActivityClick={mockOnActivityClick} />);
      const endTime = performance.now();

      expect(endTime - startTime).toBeLessThan(3000); // Should render in less than 3 seconds
    });

    it('handles props changes efficiently', () => {
      const { rerender } = render(<ActivityFeed activities={mockActivities} onActivityClick={mockOnActivityClick} />);
      
      const newActivities = [...mockActivities, {
        id: '4',
        title: 'פעילות חדשה',
        type: 'system',
        status: 'completed',
        agent: 'dental_agent_1',
        timestamp: new Date().toISOString()
      }];

      rerender(<ActivityFeed activities={newActivities} onActivityClick={mockOnActivityClick} />);
      
      expect(screen.getByText('פעילות חדשה')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels and roles', () => {
      render(<ActivityFeed activities={mockActivities} onActivityClick={mockOnActivityClick} />);
      
      const searchInput = screen.getByPlaceholderText('חיפוש פעילויות...');
      expect(searchInput).toHaveAttribute('type', 'text');
      
      const activities = screen.getAllByRole('generic');
      expect(activities.length).toBeGreaterThan(0);
    });

    it('supports keyboard navigation', () => {
      render(<ActivityFeed activities={mockActivities} onActivityClick={mockOnActivityClick} />);
      
      const searchInput = screen.getByPlaceholderText('חיפוש פעילויות...');
      searchInput.focus();
      expect(document.activeElement).toBe(searchInput);
    });
  });

  describe('WebSocket Integration', () => {
    it('shows connected status when WebSocket is provided', async () => {
      render(<ActivityFeed 
        activities={[]} 
        onActivityClick={mockOnActivityClick} 
        websocketUrl="ws://localhost:8000/ws"
      />);
      
      await waitFor(() => {
        expect(screen.getByText('מחובר')).toBeInTheDocument();
      });
    });

    it('displays real-time updates indicator when connected', async () => {
      render(<ActivityFeed 
        activities={[]} 
        onActivityClick={mockOnActivityClick} 
        websocketUrl="ws://localhost:8000/ws"
      />);
      
      await waitFor(() => {
        expect(screen.getByText('עדכונים בזמן אמת')).toBeInTheDocument();
      });
    });
  });

  describe('Component Props', () => {
    it('handles missing onActivityClick gracefully', () => {
      render(<ActivityFeed activities={mockActivities} />);
      
      const firstActivity = screen.getByText('תור חדש נקבע');
      expect(() => {
        fireEvent.click(firstActivity.closest('.cursor-pointer'));
      }).not.toThrow();
    });

    it('respects maxActivities prop', () => {
      const manyActivities = Array.from({ length: 50 }, (_, i) => ({
        id: `activity-${i}`,
        title: `פעילות ${i}`,
        type: 'system',
        status: 'completed',
        agent: 'agent_1',
        timestamp: new Date().toISOString()
      }));

      render(<ActivityFeed activities={manyActivities} maxActivities={10} />);
      
      // Should show only 10 activities due to maxActivities limit
      const activityElements = screen.getAllByText(/פעילות \d+/);
      expect(activityElements.length).toBeLessThanOrEqual(10);
    });
  });
});
