import { useState, useEffect } from 'react'
import { Header } from './Header'
import { Sidebar } from './Sidebar'
import { cn } from '@/lib/utils'

/**
 * Layout Container Component - Main application layout structure
 * 
 * Features:
 * - Responsive layout with header and sidebar
 * - Mobile-first design with collapsible sidebar
 * - Persistent sidebar state in localStorage
 * - Smooth transitions and animations
 * - Proper content area management
 */

export function Layout({ 
  children, 
  className = '',
  defaultSidebarOpen = true,
  activeNavItem = 'dashboard'
}) {
  const [sidebarOpen, setSidebarOpen] = useState(defaultSidebarOpen)
  const [isMobile, setIsMobile] = useState(false)

  // Check if we're on mobile and handle responsive behavior
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 1024 // lg breakpoint
      setIsMobile(mobile)
      
      // Auto-close sidebar on mobile only on initial load
      if (mobile && sidebarOpen && !localStorage.getItem('dental-clinic-sidebar-mobile-override')) {
        setSidebarOpen(false)
      }
    }

    // Check on mount
    checkMobile()

    // Listen for resize events
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Load sidebar state from localStorage on mount
  useEffect(() => {
    const savedState = localStorage.getItem('dental-clinic-sidebar-open')
    if (savedState !== null) {
      setSidebarOpen(JSON.parse(savedState))
    }
  }, [])

  // Save sidebar state to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('dental-clinic-sidebar-open', JSON.stringify(sidebarOpen))
  }, [sidebarOpen])

  const handleSidebarToggle = () => {
    setSidebarOpen(prev => !prev)
  }

  const handleNavigation = (itemId, href) => {
    // TODO: Implement navigation logic
    console.log('Navigating to:', itemId, href)
    
    // Close sidebar on mobile after navigation
    if (isMobile) {
      setSidebarOpen(false)
    }
  }

  const handleMobileOverlayClick = () => {
    if (isMobile && sidebarOpen) {
      setSidebarOpen(false)
    }
  }

  return (
    <div 
      className={cn('min-h-screen bg-background flex flex-col', className)}
      data-testid="layout-container"
    >
      {/* Header */}
      <Header 
        onMenuToggle={handleSidebarToggle}
        className="sticky top-0 z-40"
      />

      {/* Main Content Area */}
      <div className="flex flex-1 relative">
        {/* Mobile Overlay */}
        {isMobile && sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-30 lg:hidden"
            onClick={handleMobileOverlayClick}
            aria-label="Close sidebar"
            data-testid="mobile-overlay"
          />
        )}

        {/* Sidebar */}
        <div
          className={cn(
            'fixed lg:static inset-y-0 left-0 z-40 lg:z-auto',
            'transition-transform duration-300 ease-in-out lg:transition-none',
            isMobile && !sidebarOpen && '-translate-x-full lg:translate-x-0'
          )}
        >
          <Sidebar
            isOpen={sidebarOpen}
            onToggle={handleSidebarToggle}
            activeItem={activeNavItem}
            onNavigate={handleNavigation}
            className="h-full"
          />
        </div>

        {/* Main Content */}
        <main
          className={cn(
            'flex-1 flex flex-col min-w-0',
            'transition-all duration-300 ease-in-out',
            // Add left margin on desktop when sidebar is open
            !isMobile && sidebarOpen && 'lg:ml-0',
            // Ensure content is not hidden behind sidebar on mobile
            isMobile && 'ml-0'
          )}
          role="main"
          aria-label="Main content"
        >
          {/* Content Container */}
          <div className="flex-1 p-4 lg:p-6 overflow-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

/**
 * Layout Context Hook - For accessing layout state in child components
 */
export function useLayout() {
  // This would typically use React Context
  // For now, return a simple object
  return {
    // TODO: Implement layout context
    isMobile: window.innerWidth < 1024,
    sidebarOpen: true
  }
}
