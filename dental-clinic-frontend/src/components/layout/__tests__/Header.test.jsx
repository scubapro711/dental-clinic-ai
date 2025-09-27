import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Header } from '../Header'

// Mock console.log to avoid noise in tests
const mockConsoleLog = vi.spyOn(console, 'log').mockImplementation(() => {})

describe('Header Component', () => {
  const mockOnMenuToggle = vi.fn()
  
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders all essential elements', () => {
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      // Logo and title
      expect(screen.getByText('DC')).toBeInTheDocument()
      expect(screen.getByText('Dental Clinic AI')).toBeInTheDocument()
      
      // Search input (desktop)
      expect(screen.getByPlaceholderText('Search patients, appointments...')).toBeInTheDocument()
      
      // Action buttons
      expect(screen.getByLabelText('Notifications (3 unread)')).toBeInTheDocument()
      expect(screen.getByLabelText('Settings')).toBeInTheDocument()
      expect(screen.getByLabelText('User menu')).toBeInTheDocument()
      
      // User name
      expect(screen.getByText('Dr. Smith')).toBeInTheDocument()
    })

    it('renders mobile menu toggle button', () => {
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      const menuToggle = screen.getByLabelText('Toggle navigation menu')
      expect(menuToggle).toBeInTheDocument()
      expect(menuToggle).toHaveClass('lg:hidden')
    })

    it('renders notification badge with correct count', () => {
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      const badge = screen.getByText('3')
      expect(badge).toBeInTheDocument()
      expect(badge).toHaveClass('absolute', '-top-1', '-right-1')
    })

    it('applies custom className', () => {
      const customClass = 'custom-header-class'
      render(<Header onMenuToggle={mockOnMenuToggle} className={customClass} />)
      
      const header = screen.getByRole('banner')
      expect(header).toHaveClass(customClass)
    })
  })

  describe('Interactions', () => {
    it('calls onMenuToggle when menu button is clicked', async () => {
      const user = userEvent.setup()
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      const menuButton = screen.getByLabelText('Toggle navigation menu')
      await user.click(menuButton)
      
      expect(mockOnMenuToggle).toHaveBeenCalledTimes(1)
    })

    it('handles search form submission', async () => {
      const user = userEvent.setup()
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      const searchInput = screen.getByPlaceholderText('Search patients, appointments...')
      
      // Type in search input
      await user.type(searchInput, 'John Doe')
      expect(searchInput).toHaveValue('John Doe')
      
      // Submit form
      await user.keyboard('{Enter}')
      
      await waitFor(() => {
        expect(mockConsoleLog).toHaveBeenCalledWith('Searching for:', 'John Doe')
      })
    })

    it('does not search with empty query', async () => {
      const user = userEvent.setup()
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      const searchInput = screen.getByPlaceholderText('Search patients, appointments...')
      
      // Submit empty form
      await user.click(searchInput)
      await user.keyboard('{Enter}')
      
      expect(mockConsoleLog).not.toHaveBeenCalledWith('Searching for:', '')
    })

    it('handles notification button click', async () => {
      const user = userEvent.setup()
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      const notificationButton = screen.getByLabelText('Notifications (3 unread)')
      await user.click(notificationButton)
      
      expect(mockConsoleLog).toHaveBeenCalledWith('Opening notifications')
    })

    it('handles settings button click', async () => {
      const user = userEvent.setup()
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      const settingsButton = screen.getByLabelText('Settings')
      await user.click(settingsButton)
      
      expect(mockConsoleLog).toHaveBeenCalledWith('Profile action:', 'settings')
    })
  })

  describe('User Dropdown Menu', () => {
    it('opens dropdown menu when user button is clicked', async () => {
      const user = userEvent.setup()
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      const userButton = screen.getByLabelText('User menu')
      await user.click(userButton)
      
      // Check if dropdown items appear
      expect(screen.getByText('My Account')).toBeInTheDocument()
      expect(screen.getByText('Profile')).toBeInTheDocument()
      expect(screen.getByText('Settings')).toBeInTheDocument()
      expect(screen.getByText('Logout')).toBeInTheDocument()
    })

    it('handles profile menu item click', async () => {
      const user = userEvent.setup()
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      // Open dropdown
      const userButton = screen.getByLabelText('User menu')
      await user.click(userButton)
      
      // Click profile item
      const profileItem = screen.getByText('Profile')
      await user.click(profileItem)
      
      expect(mockConsoleLog).toHaveBeenCalledWith('Profile action:', 'profile')
    })

    it('handles logout menu item click', async () => {
      const user = userEvent.setup()
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      // Open dropdown
      const userButton = screen.getByLabelText('User menu')
      await user.click(userButton)
      
      // Click logout item
      const logoutItem = screen.getByText('Logout')
      await user.click(logoutItem)
      
      expect(mockConsoleLog).toHaveBeenCalledWith('Profile action:', 'logout')
    })

    it('applies destructive styling to logout item', async () => {
      const user = userEvent.setup()
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      // Open dropdown
      const userButton = screen.getByLabelText('User menu')
      await user.click(userButton)
      
      const logoutItem = screen.getByText('Logout')
      expect(logoutItem).toHaveClass('text-destructive')
    })
  })

  describe('Responsive Design', () => {
    it('hides desktop search on mobile', () => {
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      const searchContainer = screen.getByPlaceholderText('Search patients, appointments...').closest('div')
      expect(searchContainer).toHaveClass('hidden', 'md:block')
    })

    it('shows mobile search button', () => {
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      const mobileSearchButton = screen.getByLabelText('Search')
      expect(mobileSearchButton).toHaveClass('md:hidden')
    })

    it('hides user name on small screens', () => {
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      const userName = screen.getByText('Dr. Smith')
      expect(userName).toHaveClass('hidden', 'sm:inline')
    })

    it('hides title on small screens', () => {
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      const title = screen.getByText('Dental Clinic AI')
      expect(title).toHaveClass('hidden', 'sm:block')
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      expect(screen.getByLabelText('Toggle navigation menu')).toBeInTheDocument()
      expect(screen.getByLabelText('Global search')).toBeInTheDocument()
      expect(screen.getByLabelText('Notifications (3 unread)')).toBeInTheDocument()
      expect(screen.getByLabelText('Settings')).toBeInTheDocument()
      expect(screen.getByLabelText('User menu')).toBeInTheDocument()
    })

    it('has proper semantic structure', () => {
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      const header = screen.getByRole('banner')
      expect(header).toBeInTheDocument()
      
      const searchInput = screen.getByRole('searchbox')
      expect(searchInput).toBeInTheDocument()
    })

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup()
      render(<Header onMenuToggle={mockOnMenuToggle} />)
      
      // Tab through interactive elements
      await user.tab()
      expect(screen.getByLabelText('Toggle navigation menu')).toHaveFocus()
      
      await user.tab()
      expect(screen.getByLabelText('Global search')).toHaveFocus()
      
      await user.tab()
      expect(screen.getByLabelText('Search')).toHaveFocus()
    })
  })
})
