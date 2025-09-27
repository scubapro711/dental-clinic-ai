import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Sidebar } from '../Sidebar'

// Mock console.log to avoid noise in tests
const mockConsoleLog = vi.spyOn(console, 'log').mockImplementation(() => {})

describe('Sidebar Component', () => {
  const mockOnToggle = vi.fn()
  const mockOnNavigate = vi.fn()
  
  const defaultProps = {
    isOpen: true,
    onToggle: mockOnToggle,
    activeItem: 'dashboard',
    onNavigate: mockOnNavigate
  }
  
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders all navigation items when open', () => {
      render(<Sidebar {...defaultProps} />)
      
      // Check all navigation items are present
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Conversations')).toBeInTheDocument()
      expect(screen.getByText('Appointments')).toBeInTheDocument()
      expect(screen.getByText('Patients')).toBeInTheDocument()
      expect(screen.getByText('Analytics')).toBeInTheDocument()
      expect(screen.getByText('Knowledge Base')).toBeInTheDocument()
      expect(screen.getByText('Settings')).toBeInTheDocument()
    })

    it('renders header with navigation title when open', () => {
      render(<Sidebar {...defaultProps} />)
      
      expect(screen.getByText('Navigation')).toBeInTheDocument()
      expect(screen.getByLabelText('Collapse sidebar')).toBeInTheDocument()
    })

    it('renders footer with version info when open', () => {
      render(<Sidebar {...defaultProps} />)
      
      expect(screen.getByText('Dental Clinic AI')).toBeInTheDocument()
      expect(screen.getByText('Version 2.4.0')).toBeInTheDocument()
    })

    it('applies correct width classes when open', () => {
      render(<Sidebar {...defaultProps} />)
      
      const sidebars = screen.getAllByRole('navigation')
      const mainSidebar = sidebars.find(nav => nav.getAttribute('aria-label') === 'Main navigation')
      expect(mainSidebar).toHaveClass('w-64')
    })

    it('applies correct width classes when closed', () => {
      render(<Sidebar {...defaultProps} isOpen={false} />)
      
      const sidebars = screen.getAllByRole('navigation')
      const mainSidebar = sidebars.find(nav => nav.getAttribute('aria-label') === 'Main navigation')
      expect(mainSidebar).toHaveClass('w-16')
    })

    it('hides text content when closed', () => {
      render(<Sidebar {...defaultProps} isOpen={false} />)
      
      // Navigation title should not be visible
      expect(screen.queryByText('Navigation')).not.toBeInTheDocument()
      
      // Item labels should not be visible (but icons should be)
      expect(screen.queryByText('Dashboard')).not.toBeInTheDocument()
      expect(screen.queryByText('Conversations')).not.toBeInTheDocument()
    })

    it('shows expand button when closed', () => {
      render(<Sidebar {...defaultProps} isOpen={false} />)
      
      expect(screen.getByLabelText('Expand sidebar')).toBeInTheDocument()
    })

    it('applies custom className', () => {
      const customClass = 'custom-sidebar-class'
      render(<Sidebar {...defaultProps} className={customClass} />)
      
      const sidebars = screen.getAllByRole('navigation')
      const mainSidebar = sidebars.find(nav => nav.getAttribute('aria-label') === 'Main navigation')
      expect(mainSidebar).toHaveClass(customClass)
    })
  })

  describe('Active State', () => {
    it('highlights active navigation item', () => {
      render(<Sidebar {...defaultProps} activeItem="conversations" />)
      
      const conversationsButton = screen.getByText('Conversations').closest('button')
      expect(conversationsButton).toHaveClass('bg-sidebar-primary')
      expect(conversationsButton).toHaveAttribute('aria-current', 'page')
    })

    it('does not highlight inactive items', () => {
      render(<Sidebar {...defaultProps} activeItem="dashboard" />)
      
      const conversationsButton = screen.getByText('Conversations').closest('button')
      expect(conversationsButton).not.toHaveClass('bg-sidebar-primary')
      expect(conversationsButton).not.toHaveAttribute('aria-current')
    })
  })

  describe('Interactions', () => {
    it('calls onToggle when toggle button is clicked', async () => {
      const user = userEvent.setup()
      render(<Sidebar {...defaultProps} />)
      
      const toggleButton = screen.getByLabelText('Collapse sidebar')
      await user.click(toggleButton)
      
      expect(mockOnToggle).toHaveBeenCalledTimes(1)
    })

    it('calls onNavigate when navigation item is clicked', async () => {
      const user = userEvent.setup()
      render(<Sidebar {...defaultProps} />)
      
      const dashboardButton = screen.getByText('Dashboard').closest('button')
      await user.click(dashboardButton)
      
      expect(mockOnNavigate).toHaveBeenCalledWith('dashboard', '/dashboard')
    })

    it('calls onNavigate for different navigation items', async () => {
      const user = userEvent.setup()
      render(<Sidebar {...defaultProps} />)
      
      const conversationsButton = screen.getByText('Conversations').closest('button')
      await user.click(conversationsButton)
      
      expect(mockOnNavigate).toHaveBeenCalledWith('conversations', '/conversations')
    })

    it('handles keyboard navigation with Enter key', async () => {
      const user = userEvent.setup()
      render(<Sidebar {...defaultProps} />)
      
      const dashboardButton = screen.getByText('Dashboard').closest('button')
      dashboardButton.focus()
      await user.keyboard('{Enter}')
      
      expect(mockOnNavigate).toHaveBeenCalledWith('dashboard', '/dashboard')
    })

    it('handles keyboard navigation with Space key', async () => {
      const user = userEvent.setup()
      render(<Sidebar {...defaultProps} />)
      
      const dashboardButton = screen.getByText('Dashboard').closest('button')
      dashboardButton.focus()
      await user.keyboard(' ')
      
      expect(mockOnNavigate).toHaveBeenCalledWith('dashboard', '/dashboard')
    })

    it('shows description on hover when open', async () => {
      const user = userEvent.setup()
      render(<Sidebar {...defaultProps} activeItem="conversations" />)
      
      const dashboardButton = screen.getByText('Dashboard').closest('button')
      await user.hover(dashboardButton)
      
      await waitFor(() => {
        expect(screen.getByText('Overview and metrics')).toBeInTheDocument()
      })
    })
  })

  describe('Collapsed State Behavior', () => {
    it('shows tooltips for items when collapsed', () => {
      render(<Sidebar {...defaultProps} isOpen={false} />)
      
      const buttons = screen.getAllByRole('button')
      // Skip the toggle button and find navigation buttons
      const navButtons = buttons.slice(1)
      const dashboardButton = navButtons.find(btn => btn.getAttribute('title')?.includes('Overview and metrics'))
      
      expect(dashboardButton).toBeInTheDocument()
      expect(dashboardButton).toHaveAttribute('title', 'Overview and metrics')
    })

    it('has proper aria-labels when collapsed', () => {
      render(<Sidebar {...defaultProps} isOpen={false} />)
      
      // Find button by its aria-label since text is hidden
      const dashboardButton = screen.getByLabelText('Dashboard')
      expect(dashboardButton).toBeInTheDocument()
    })

    it('centers icons when collapsed', () => {
      render(<Sidebar {...defaultProps} isOpen={false} />)
      
      const buttons = screen.getAllByRole('button')
      // Skip the toggle button (first one)
      const navButtons = buttons.slice(1)
      
      navButtons.forEach(button => {
        expect(button).toHaveClass('justify-center')
      })
    })

    it('shows minimal footer when collapsed', () => {
      render(<Sidebar {...defaultProps} isOpen={false} />)
      
      // Should not show text version info
      expect(screen.queryByText('Dental Clinic AI')).not.toBeInTheDocument()
      expect(screen.queryByText('Version 2.4.0')).not.toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      render(<Sidebar {...defaultProps} />)
      
      const sidebars = screen.getAllByRole('navigation')
      const mainSidebar = sidebars.find(nav => nav.getAttribute('aria-label') === 'Main navigation')
      expect(mainSidebar).toBeInTheDocument()
      
      const list = screen.getByRole('list')
      expect(list).toBeInTheDocument()
      
      const listItems = screen.getAllByRole('listitem')
      expect(listItems).toHaveLength(7) // 7 navigation items
    })

    it('supports keyboard navigation between items', async () => {
      const user = userEvent.setup()
      render(<Sidebar {...defaultProps} />)
      
      // Tab to first navigation item (skip toggle button)
      await user.tab()
      await user.tab()
      
      const dashboardButton = screen.getByText('Dashboard').closest('button')
      expect(dashboardButton).toHaveFocus()
      
      // Tab to next item
      await user.tab()
      const conversationsButton = screen.getByText('Conversations').closest('button')
      expect(conversationsButton).toHaveFocus()
    })

    it('has proper focus management', async () => {
      const user = userEvent.setup()
      render(<Sidebar {...defaultProps} />)
      
      const dashboardButton = screen.getByText('Dashboard').closest('button')
      await user.click(dashboardButton)
      
      expect(dashboardButton).toHaveClass('focus:ring-2', 'focus:ring-sidebar-ring')
    })

    it('maintains focus visibility', () => {
      render(<Sidebar {...defaultProps} />)
      
      // Check navigation buttons specifically (skip toggle button)
      const dashboardButton = screen.getByText('Dashboard').closest('button')
      expect(dashboardButton).toHaveClass('focus:outline-none')
      expect(dashboardButton).toHaveClass('focus:ring-2')
    })
  })

  describe('Responsive Behavior', () => {
    it('applies transition classes for smooth animations', () => {
      render(<Sidebar {...defaultProps} />)
      
      const sidebars = screen.getAllByRole('navigation')
      const mainSidebar = sidebars.find(nav => nav.getAttribute('aria-label') === 'Main navigation')
      expect(mainSidebar).toHaveClass('transition-all', 'duration-300', 'ease-in-out')
    })

    it('handles state changes smoothly', async () => {
      const { rerender } = render(<Sidebar {...defaultProps} isOpen={true} />)
      
      let sidebars = screen.getAllByRole('navigation')
      let mainSidebar = sidebars.find(nav => nav.getAttribute('aria-label') === 'Main navigation')
      expect(mainSidebar).toHaveClass('w-64')
      
      rerender(<Sidebar {...defaultProps} isOpen={false} />)
      
      sidebars = screen.getAllByRole('navigation')
      mainSidebar = sidebars.find(nav => nav.getAttribute('aria-label') === 'Main navigation')
      expect(mainSidebar).toHaveClass('w-16')
    })
  })

  describe('Error Handling', () => {
    it('works without onNavigate callback', async () => {
      const user = userEvent.setup()
      render(<Sidebar {...defaultProps} onNavigate={undefined} />)
      
      const dashboardButton = screen.getByRole('button', { name: /dashboard/i })
      
      // Should not throw error
      await user.click(dashboardButton)
      expect(mockOnNavigate).not.toHaveBeenCalled()
    })

    it('works without onToggle callback', async () => {
      const user = userEvent.setup()
      render(<Sidebar {...defaultProps} onToggle={undefined} />)
      
      const toggleButton = screen.getByLabelText('Collapse sidebar')
      
      // Should not throw error
      await user.click(toggleButton)
      expect(mockOnToggle).not.toHaveBeenCalled()
    })
  })
})
