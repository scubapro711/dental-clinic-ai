/**
 * DashboardSidebar - Fixed Right Sidebar
 * 
 * Features:
 * - Widget Library (drag to add widgets)
 * - Navigation menu
 * - Collapse/expand functionality
 * - Search widgets
 * - Filter by category
 * - RTL support
 */

import { useState } from 'react'
import { 
  ChevronLeft, 
  ChevronRight, 
  Search, 
  Users, 
  DollarSign, 
  CheckCircle, 
  AlertCircle, 
  Activity, 
  Settings, 
  BarChart3,
  Eye,
  Home,
  Calendar,
  UserCircle,
  LogOut
} from 'lucide-react'
import { useDashboard } from '../../contexts/DashboardContext'
import { getUserInfo, canViewWidget } from '../../utils/rbac'

// Widget definitions
export const WIDGET_LIBRARY = [
  {
    id: 'todays-patients',
    title: "Today's Patients",
    icon: Users,
    category: 'operations',
    description: 'View and manage today\'s patient appointments',
    defaultSize: { w: 4, h: 2 },
    color: 'blue'
  },
  {
    id: 'revenue',
    title: 'Revenue',
    icon: DollarSign,
    category: 'analytics',
    description: 'Track revenue and financial metrics',
    defaultSize: { w: 4, h: 2 },
    color: 'cyan'
  },
  {
    id: 'compliance',
    title: 'Compliance',
    icon: CheckCircle,
    category: 'admin',
    description: 'Monitor compliance and regulatory status',
    defaultSize: { w: 4, h: 2 },
    color: 'orange'
  },
  {
    id: 'decision-queue',
    title: 'Decision Queue',
    icon: AlertCircle,
    category: 'operations',
    description: 'Review pending decisions and approvals',
    defaultSize: { w: 4, h: 2 },
    color: 'green'
  },
  {
    id: 'clinical',
    title: 'Clinical Insights',
    icon: Activity,
    category: 'clinical',
    description: 'Clinical data and patient insights',
    defaultSize: { w: 4, h: 2 },
    color: 'purple'
  },
  {
    id: 'fine-tuning',
    title: 'Fine-Tuning',
    icon: Settings,
    category: 'admin',
    description: 'AI model fine-tuning and optimization',
    defaultSize: { w: 4, h: 2 },
    color: 'orange'
  },
  {
    id: 'agent-activity',
    title: 'Agent Activity',
    icon: BarChart3,
    category: 'analytics',
    description: 'Monitor AI agent performance and activity',
    defaultSize: { w: 4, h: 2 },
    color: 'cyan'
  },
  {
    id: 'transparency',
    title: 'Transparency',
    icon: Eye,
    category: 'admin',
    description: 'View AI decision-making transparency logs',
    defaultSize: { w: 4, h: 2 },
    color: 'purple'
  }
]

const CATEGORIES = [
  { id: 'all', label: 'All Widgets' },
  { id: 'operations', label: 'Operations' },
  { id: 'analytics', label: 'Analytics' },
  { id: 'clinical', label: 'Clinical' },
  { id: 'admin', label: 'Admin' }
]

const NAVIGATION_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: Home, path: '/clinic/dashboard' },
  { id: 'schedule', label: 'Schedule', icon: Calendar, path: '/clinic/schedule' },
  { id: 'patients', label: 'Patients', icon: Users, path: '/clinic/patients' },
  { id: 'profile', label: 'Profile', icon: UserCircle, path: '/clinic/profile' },
  { id: 'logout', label: 'Logout', icon: LogOut, path: '/logout' }
]

export function DashboardSidebar() {
  const { activeWidgets, isSidebarOpen, toggleSidebar } = useDashboard()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const userInfo = getUserInfo()
  
  // Filter widgets
  const filteredWidgets = WIDGET_LIBRARY.filter(widget => {
    // Check permissions
    if (!canViewWidget(widget.id)) return false
    
    // Check category
    if (selectedCategory !== 'all' && widget.category !== selectedCategory) return false
    
    // Check search
    if (searchQuery && !widget.title.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false
    }
    
    return true
  })
  
  // Icon color map
  const iconColorMap = {
    blue: { background: 'oklch(0.95 0.05 240)', color: 'var(--primary)' },
    purple: { background: 'oklch(0.95 0.05 300)', color: 'var(--accent)' },
    cyan: { background: 'oklch(0.95 0.05 200)', color: 'var(--secondary)' },
    green: { background: 'oklch(0.95 0.05 145)', color: 'var(--success)' },
    orange: { background: 'oklch(0.95 0.05 60)', color: 'var(--warning)' }
  }
  
  // Handle drag start
  const handleDragStart = (e: React.DragEvent, widget: typeof WIDGET_LIBRARY[0]) => {
    e.dataTransfer.setData('application/json', JSON.stringify(widget))
    e.dataTransfer.effectAllowed = 'copy'
  }
  
  return (
    <div
      className="dashboard-sidebar"
      data-collapsed={!isSidebarOpen}
      style={{
        position: 'fixed',
        right: '0',
        top: '0',
        height: '100vh',
        width: isSidebarOpen ? '320px' : '0px',
        background: 'var(--background)',
        borderLeft: '1px solid var(--border)',
        boxShadow: 'var(--shadow-lg)',
        transition: 'width var(--transition-base)',
        zIndex: 'var(--z-fixed)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}
    >
      {/* Toggle Button */}
      <button
        onClick={toggleSidebar}
        className="sidebar-toggle"
        aria-label={isSidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        style={{
          position: 'absolute',
          left: '-16px',
          top: '50%',
          transform: 'translateY(-50%)',
          width: '32px',
          height: '32px',
          borderRadius: 'var(--radius-full)',
          background: 'var(--primary)',
          color: 'var(--primary-foreground)',
          border: 'none',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: 'var(--shadow-md)',
          transition: 'all var(--transition-base)',
          zIndex: '1'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-50%) scale(1.1)'
          e.currentTarget.style.boxShadow = 'var(--shadow-lg)'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(-50%) scale(1)'
          e.currentTarget.style.boxShadow = 'var(--shadow-md)'
        }}
      >
        {isSidebarOpen ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
      </button>
      
      {/* Sidebar Content (only visible when open) */}
      {isSidebarOpen && (
        <div
          className="sidebar-content"
          style={{
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            padding: 'var(--spacing-lg)',
            gap: 'var(--spacing-lg)',
            overflow: 'hidden'
          }}
        >
          {/* Header */}
          <div className="sidebar-header">
            <h2
              style={{
                fontSize: 'var(--font-size-xl)',
                fontWeight: 'var(--font-weight-bold)',
                color: 'var(--foreground)',
                margin: '0 0 var(--spacing-xs) 0'
              }}
            >
              Customize Dashboard
            </h2>
            <p
              style={{
                fontSize: 'var(--font-size-sm)',
                color: 'var(--foreground-tertiary)',
                margin: '0'
              }}
            >
              Drag widgets to add them to your dashboard
            </p>
          </div>
          
          {/* Search */}
          <div
            className="sidebar-search"
            style={{
              position: 'relative'
            }}
          >
            <Search
              size={18}
              style={{
                position: 'absolute',
                left: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--foreground-tertiary)',
                pointerEvents: 'none'
              }}
            />
            <input
              type="text"
              placeholder="Search widgets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px 10px 40px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border)',
                background: 'var(--background-secondary)',
                color: 'var(--foreground)',
                fontSize: 'var(--font-size-sm)',
                transition: 'all var(--transition-base)'
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = 'var(--primary)'
                e.currentTarget.style.boxShadow = '0 0 0 2px var(--ring)'
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = 'var(--border)'
                e.currentTarget.style.boxShadow = 'none'
              }}
            />
          </div>
          
          {/* Category Filter */}
          <div
            className="sidebar-categories"
            style={{
              display: 'flex',
              gap: 'var(--spacing-xs)',
              flexWrap: 'wrap'
            }}
          >
            {CATEGORIES.map(category => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                style={{
                  padding: '6px 12px',
                  borderRadius: 'var(--radius-md)',
                  border: 'none',
                  background: selectedCategory === category.id ? 'var(--primary)' : 'var(--muted)',
                  color: selectedCategory === category.id ? 'var(--primary-foreground)' : 'var(--foreground)',
                  fontSize: 'var(--font-size-xs)',
                  fontWeight: 'var(--font-weight-medium)',
                  cursor: 'pointer',
                  transition: 'all var(--transition-base)'
                }}
                onMouseEnter={(e) => {
                  if (selectedCategory !== category.id) {
                    e.currentTarget.style.background = 'var(--muted-foreground)'
                    e.currentTarget.style.color = 'var(--background)'
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedCategory !== category.id) {
                    e.currentTarget.style.background = 'var(--muted)'
                    e.currentTarget.style.color = 'var(--foreground)'
                  }
                }}
              >
                {category.label}
              </button>
            ))}
          </div>
          
          {/* Widget Library */}
          <div
            className="sidebar-widgets"
            style={{
              flex: '1',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--spacing-sm)'
            }}
          >
            <h3
              style={{
                fontSize: 'var(--font-size-sm)',
                fontWeight: 'var(--font-weight-semibold)',
                color: 'var(--foreground-secondary)',
                margin: '0',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}
            >
              Available Widgets
            </h3>
            
            {filteredWidgets.map(widget => {
              const Icon = widget.icon
              const isActive = activeWidgets?.includes(widget.id)
              
              return (
                <div
                  key={widget.id}
                  draggable={!isActive}
                  onDragStart={(e) => handleDragStart(e, widget)}
                  className="widget-library-item"
                  style={{
                    padding: 'var(--spacing-md)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border)',
                    background: isActive ? 'var(--muted)' : 'var(--background)',
                    cursor: isActive ? 'not-allowed' : 'grab',
                    transition: 'all var(--transition-base)',
                    opacity: isActive ? 0.5 : 1
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.borderColor = 'var(--primary)'
                      e.currentTarget.style.boxShadow = 'var(--shadow-md)'
                      e.currentTarget.style.transform = 'translateY(-2px)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.borderColor = 'var(--border)'
                      e.currentTarget.style.boxShadow = 'none'
                      e.currentTarget.style.transform = 'translateY(0)'
                    }
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 'var(--spacing-sm)'
                    }}
                  >
                    <div
                      style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: 'var(--radius-md)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: '0',
                        ...iconColorMap[widget.color as keyof typeof iconColorMap]
                      }}
                    >
                      <Icon size={20} />
                    </div>
                    
                    <div style={{ flex: '1', minWidth: '0' }}>
                      <h4
                        style={{
                          fontSize: 'var(--font-size-sm)',
                          fontWeight: 'var(--font-weight-semibold)',
                          color: 'var(--foreground)',
                          margin: '0 0 4px 0',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {widget.title}
                      </h4>
                      <p
                        style={{
                          fontSize: 'var(--font-size-xs)',
                          color: 'var(--foreground-tertiary)',
                          margin: '0',
                          lineHeight: '1.4'
                        }}
                      >
                        {widget.description}
                      </p>
                      {isActive && (
                        <span
                          style={{
                            fontSize: 'var(--font-size-xs)',
                            color: 'var(--primary)',
                            fontWeight: 'var(--font-weight-medium)',
                            marginTop: '4px',
                            display: 'block'
                          }}
                        >
                          Already added
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
            
            {filteredWidgets.length === 0 && (
              <div
                style={{
                  padding: 'var(--spacing-xl)',
                  textAlign: 'center',
                  color: 'var(--foreground-tertiary)',
                  fontSize: 'var(--font-size-sm)'
                }}
              >
                No widgets found
              </div>
            )}
          </div>
          
          {/* AI Agents Section */}
          <div
            className="sidebar-agents"
            style={{
              borderTop: '1px solid var(--border)',
              paddingTop: 'var(--spacing-md)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--spacing-xs)'
            }}
          >
            <h3
              style={{
                fontSize: 'var(--font-size-sm)',
                fontWeight: 'var(--font-weight-semibold)',
                color: 'var(--foreground-secondary)',
                margin: '0 0 var(--spacing-xs) 0',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}
            >
              AI Agents
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {[
                { id: 'alex', name: 'Alex', role: 'Patient Experience', value: '247' },
                { id: 'sarah', name: 'Sarah', role: 'Clinical Support', value: '98%' },
                { id: 'marcus', name: 'Marcus', role: 'Financial', value: '₪45,230' },
                { id: 'sophia', name: 'Sophia', role: 'Scheduling', value: '8' },
                { id: 'harper', name: 'Harper', role: 'Compliance', value: '96%' }
              ].map(agent => (
                <div
                  key={agent.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--muted)',
                    fontSize: 'var(--font-size-xs)',
                    transition: 'all var(--transition-base)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'var(--primary)'
                    e.currentTarget.style.color = 'var(--primary-foreground)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'var(--muted)'
                    e.currentTarget.style.color = 'var(--foreground)'
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 'var(--font-weight-semibold)' }}>{agent.name}</div>
                    <div style={{ fontSize: '10px', opacity: 0.7 }}>{agent.role}</div>
                  </div>
                  <div style={{ fontWeight: 'var(--font-weight-bold)' }}>{agent.value}</div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Navigation */}
          <div
            className="sidebar-navigation"
            style={{
              borderTop: '1px solid var(--border)',
              paddingTop: 'var(--spacing-md)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--spacing-xs)'
            }}
          >
            <h3
              style={{
                fontSize: 'var(--font-size-sm)',
                fontWeight: 'var(--font-weight-semibold)',
                color: 'var(--foreground-secondary)',
                margin: '0 0 var(--spacing-xs) 0',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}
            >
              Navigation
            </h3>
            
            {NAVIGATION_ITEMS.map(item => {
              const Icon = item.icon
              const isActive = window.location.pathname === item.path
              
              return (
                <a
                  key={item.id}
                  href={item.path}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--spacing-sm)',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-md)',
                    background: isActive ? 'var(--primary)' : 'transparent',
                    color: isActive ? 'var(--primary-foreground)' : 'var(--foreground)',
                    textDecoration: 'none',
                    fontSize: 'var(--font-size-sm)',
                    fontWeight: 'var(--font-weight-medium)',
                    transition: 'all var(--transition-base)'
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = 'var(--muted)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = 'transparent'
                    }
                  }}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </a>
              )
            })}
          </div>
          
          {/* User Info and Logout */}
          <div
            className="sidebar-user"
            style={{
              borderTop: '1px solid var(--border)',
              paddingTop: 'var(--spacing-md)',
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--spacing-sm)'
            }}
          >
            {/* User Info */}
            <div
              style={{
                padding: '12px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--muted)',
                fontSize: 'var(--font-size-xs)'
              }}
            >
              <div style={{ fontWeight: 'var(--font-weight-semibold)', marginBottom: '4px' }}>
                {userInfo?.name || 'User'}
              </div>
              <div style={{ opacity: 0.7 }}>
                {userInfo?.email || 'user@dentaflow.ai'}
              </div>
              <div style={{ opacity: 0.7, marginTop: '4px' }}>
                {userInfo?.role || 'User'}
              </div>
            </div>
            
            {/* Security Link */}
            <a
              href="/clinic/security"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-sm)',
                padding: '10px 12px',
                borderRadius: 'var(--radius-md)',
                background: 'transparent',
                color: 'var(--foreground)',
                textDecoration: 'none',
                fontSize: 'var(--font-size-sm)',
                fontWeight: 'var(--font-weight-medium)',
                transition: 'all var(--transition-base)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--muted)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent'
              }}
            >
              <span>🔒</span>
              <span>Security</span>
            </a>
            
            {/* Logout Button */}
            <button
              onClick={() => {
                localStorage.removeItem('auth_token')
                localStorage.removeItem('user_profile')
                localStorage.removeItem('token')
                localStorage.removeItem('access_token')
                localStorage.removeItem('mockUser')
                window.location.href = '/login'
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-sm)',
                padding: '10px 12px',
                borderRadius: 'var(--radius-md)',
                background: 'transparent',
                color: 'var(--destructive)',
                border: 'none',
                fontSize: 'var(--font-size-sm)',
                fontWeight: 'var(--font-weight-medium)',
                cursor: 'pointer',
                transition: 'all var(--transition-base)',
                width: '100%',
                textAlign: 'left'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--destructive)'
                e.currentTarget.style.color = 'var(--destructive-foreground)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent'
                e.currentTarget.style.color = 'var(--destructive)'
              }}
            >
              <span>🚪</span>
              <span>Logout</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

