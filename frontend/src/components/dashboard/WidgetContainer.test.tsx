import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { WidgetContainer } from './WidgetContainer'
import { DashboardProvider } from '../../contexts/DashboardContext'

// Mock useDashboard
const mockUseDashboard = {
  isCollapsed: vi.fn(() => false),
  toggleCollapse: vi.fn(),
  isEditMode: false,
  canViewWidget: vi.fn(() => true)
}

vi.mock('../../contexts/DashboardContext', () => ({
  useDashboard: () => mockUseDashboard,
  DashboardProvider: ({ children }: any) => <div>{children}</div>
}))

describe('WidgetContainer', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUseDashboard.isCollapsed = vi.fn(() => false)
    mockUseDashboard.canViewWidget = vi.fn(() => true)
    mockUseDashboard.isEditMode = false
  })
  
  it('renders widget with title', () => {
    render(
      <WidgetContainer widgetId="test-widget" title="Test Widget">
        <div>Widget Content</div>
      </WidgetContainer>
    )
    
    expect(screen.getByText('Test Widget')).toBeInTheDocument()
    expect(screen.getByText('Widget Content')).toBeInTheDocument()
  })
  
  it('shows collapse button', () => {
    render(
      <WidgetContainer widgetId="test-widget" title="Test Widget">
        <div>Content</div>
      </WidgetContainer>
    )
    
    const collapseBtn = screen.getByTestId('collapse-test-widget')
    expect(collapseBtn).toBeInTheDocument()
  })
  
  it('calls toggleCollapse when button clicked', () => {
    render(
      <WidgetContainer widgetId="test-widget" title="Test Widget">
        <div>Content</div>
      </WidgetContainer>
    )
    
    const collapseBtn = screen.getByTestId('collapse-test-widget')
    fireEvent.click(collapseBtn)
    
    expect(mockUseDashboard.toggleCollapse).toHaveBeenCalledWith('test-widget')
  })
  
  it('does not render if no permission', () => {
    mockUseDashboard.canViewWidget = vi.fn(() => false)
    
    const { container } = render(
      <WidgetContainer widgetId="test-widget" title="Test Widget">
        <div>Content</div>
      </WidgetContainer>
    )
    
    expect(container.firstChild).toBeNull()
  })
  
  it('shows more button in edit mode', () => {
    mockUseDashboard.isEditMode = true
    
    render(
      <WidgetContainer widgetId="test-widget" title="Test Widget">
        <div>Content</div>
      </WidgetContainer>
    )
    
    expect(screen.getByTestId('more-test-widget')).toBeInTheDocument()
  })
  
  it('hides more button when not in edit mode', () => {
    mockUseDashboard.isEditMode = false
    
    render(
      <WidgetContainer widgetId="test-widget" title="Test Widget">
        <div>Content</div>
      </WidgetContainer>
    )
    
    expect(screen.queryByTestId('more-test-widget')).not.toBeInTheDocument()
  })
  
  it('applies collapsed class when collapsed', () => {
    mockUseDashboard.isCollapsed = vi.fn(() => true)
    
    render(
      <WidgetContainer widgetId="test-widget" title="Test Widget">
        <div>Content</div>
      </WidgetContainer>
    )
    
    const content = screen.getByTestId('test-widget-content')
    expect(content).toHaveStyle({ display: 'none' })
  })
  
  it('renders icon when provided', () => {
    render(
      <WidgetContainer widgetId="test-widget" title="Test Widget" icon={<span>📊</span>}>
        <div>Content</div>
      </WidgetContainer>
    )
    
    expect(screen.getByText('📊')).toBeInTheDocument()
  })
})
