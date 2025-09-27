import { useState } from 'react'
import { 
  LayoutDashboard, 
  MessageSquare, 
  Calendar, 
  Users, 
  BarChart3, 
  BookOpen, 
  Settings,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

/**
 * Sidebar Navigation Component - Collapsible navigation menu
 * 
 * Features:
 * - Collapsible sidebar with smooth animations
 * - Active state management
 * - Keyboard navigation support
 * - Responsive behavior
 * - Icon-only mode when collapsed
 */

const navigationItems = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    href: '/dashboard',
    description: 'Overview and metrics'
  },
  {
    id: 'conversations',
    label: 'Conversations',
    icon: MessageSquare,
    href: '/conversations',
    description: 'Chat history and management'
  },
  {
    id: 'appointments',
    label: 'Appointments',
    icon: Calendar,
    href: '/appointments',
    description: 'Schedule and bookings'
  },
  {
    id: 'patients',
    label: 'Patients',
    icon: Users,
    href: '/patients',
    description: 'Patient management'
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: BarChart3,
    href: '/analytics',
    description: 'Reports and insights'
  },
  {
    id: 'knowledge',
    label: 'Knowledge Base',
    icon: BookOpen,
    href: '/knowledge',
    description: 'AI knowledge management'
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
    href: '/settings',
    description: 'System configuration'
  }
]

export function Sidebar({ 
  isOpen = true, 
  onToggle, 
  activeItem = 'dashboard',
  onNavigate,
  className = '' 
}) {
  const [hoveredItem, setHoveredItem] = useState(null)

  const handleItemClick = (item) => {
    if (onNavigate) {
      onNavigate(item.id, item.href)
    }
  }

  const handleKeyDown = (event, item) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      handleItemClick(item)
    }
  }

  return (
    <aside 
      className={cn(
        'bg-sidebar border-r border-sidebar-border transition-all duration-300 ease-in-out flex flex-col',
        isOpen ? 'w-64' : 'w-16',
        className
      )}
      role="navigation"
      aria-label="Main navigation"
    >
      {/* Sidebar Header */}
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center justify-between">
          {isOpen && (
            <h2 className="font-semibold text-sidebar-foreground">
              Navigation
            </h2>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="text-sidebar-foreground hover:bg-sidebar-accent"
            aria-label={isOpen ? 'Collapse sidebar' : 'Expand sidebar'}
          >
            {isOpen ? (
              <ChevronLeft className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 p-2">
        <ul className="space-y-1" role="list">
          {navigationItems.map((item) => {
            const Icon = item.icon
            const isActive = activeItem === item.id
            const isHovered = hoveredItem === item.id

            return (
              <li key={item.id} role="listitem">
                <button
                  onClick={() => handleItemClick(item)}
                  onKeyDown={(e) => handleKeyDown(e, item)}
                  onMouseEnter={() => setHoveredItem(item.id)}
                  onMouseLeave={() => setHoveredItem(null)}
                  className={cn(
                    'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-all duration-200',
                    'focus:outline-none focus:ring-2 focus:ring-sidebar-ring',
                    isActive
                      ? 'bg-sidebar-primary text-sidebar-primary-foreground'
                      : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
                    !isOpen && 'justify-center'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                  aria-label={isOpen ? undefined : item.label}
                  title={!isOpen ? item.description : undefined}
                >
                  <Icon 
                    className={cn(
                      'h-5 w-5 flex-shrink-0',
                      isActive && 'text-sidebar-primary-foreground'
                    )} 
                  />
                  
                  {isOpen && (
                    <div className="flex-1 min-w-0">
                      <span className="font-medium truncate block">
                        {item.label}
                      </span>
                      {(isHovered || isActive) && (
                        <span className="text-xs opacity-75 truncate block">
                          {item.description}
                        </span>
                      )}
                    </div>
                  )}
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Sidebar Footer */}
      <div className="p-4 border-t border-sidebar-border">
        {isOpen ? (
          <div className="text-xs text-sidebar-foreground/60">
            <p>Dental Clinic AI</p>
            <p>Version 2.4.0</p>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="w-2 h-2 bg-sidebar-primary rounded-full" />
          </div>
        )}
      </div>
    </aside>
  )
}
