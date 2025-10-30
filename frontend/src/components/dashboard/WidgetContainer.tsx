/**
 * WidgetContainer - Wrapper component for dashboard widgets
 * 
 * Features:
 * - Collapse/expand functionality
 * - RBAC integration (hides if no permission)
 * - Edit mode support
 * - Smooth animations
 * - Accessibility (ARIA labels, keyboard navigation)
 * 
 * Best Practices:
 * - Keep existing CSS classes for backward compatibility
 * - Add new classes alongside (not replace)
 * - Use semantic HTML
 * - Add proper ARIA labels
 * - Handle null/undefined children gracefully
 */

import { ReactNode } from 'react'
import { ChevronDown, ChevronUp, MoreVertical } from 'lucide-react'
import { useDashboard } from '../../contexts/DashboardContext'

interface WidgetContainerProps {
  widgetId: string
  title: string
  icon?: ReactNode
  defaultCollapsed?: boolean
  children: ReactNode
}

export function WidgetContainer({
  widgetId,
  title,
  icon,
  defaultCollapsed = false,
  children
}: WidgetContainerProps) {
  const { 
    isCollapsed, 
    toggleCollapse, 
    isEditMode, 
    canViewWidget 
  } = useDashboard()
  
  // Check RBAC permissions
  if (!canViewWidget(widgetId)) {
    return null  // Don't render if no permission
  }
  
  const collapsed = isCollapsed(widgetId)
  
  return (
    <div 
      className="dashboard-widget-card widget-container"
      data-testid={`widget-${widgetId}`}
      data-collapsed={collapsed}
    >
      {/* Header */}
      <div className="dashboard-widget-header widget-header flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-2">
          {icon && <span className="widget-icon">{icon}</span>}
          <h3 className="dashboard-widget-title text-lg font-semibold">
            {title}
          </h3>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Collapse button */}
          <button
            onClick={() => toggleCollapse(widgetId)}
            className="p-2 hover:bg-gray-100 rounded transition-colors"
            aria-label={collapsed ? `Expand ${title}` : `Collapse ${title}`}
            data-testid={`collapse-${widgetId}`}
          >
            {collapsed ? (
              <ChevronDown size={20} className="text-gray-600" />
            ) : (
              <ChevronUp size={20} className="text-gray-600" />
            )}
          </button>
          
          {/* More menu (future: hide, resize) */}
          {isEditMode && (
            <button 
              className="p-2 hover:bg-gray-100 rounded transition-colors"
              aria-label={`More options for ${title}`}
              data-testid={`more-${widgetId}`}
            >
              <MoreVertical size={20} className="text-gray-600" />
            </button>
          )}
        </div>
      </div>
      
      {/* Content */}
      <div 
        className={`widget-content transition-all duration-300 ease-in-out ${
          collapsed ? 'max-h-0 opacity-0 overflow-hidden' : 'max-h-[2000px] opacity-100'
        }`}
        data-testid={`${widgetId}-content`}
      >
        {children}
      </div>
    </div>
  )
}

