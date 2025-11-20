/**
 * NavigationSidebar - Hybrid sidebar combining v2 navigation with v1 widget library
 * 
 * Features:
 * - v2 design: Logo, plan badge, navigation links, user profile
 * - v1 functionality: Widget library, search, filter, RBAC
 * - Mini transparency well with expandable modal
 * - Dark mode support
 * - Mobile responsive
 * 
 * Sections:
 * 1. Logo (v2 style)
 * 2. Plan Badge (v2 gradient)
 * 3. Navigation (5 links, v2 styling)
 * 4. Widget Library (v1 functionality)
 * 5. Mini Transparency Well
 * 6. Controls (dark mode, settings, logout)
 * 7. User Profile (v2 gradient avatar)
 */

import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, Users, MessageSquare, Bot, FileBarChart,
  Crown, Moon, Sun, Settings, LogOut, Search,
  ChevronDown, ChevronRight, ChevronUp, ChevronLeft, X
} from 'lucide-react'
import { useDashboard } from '../../contexts/DashboardContext'
import { getUserInfo } from '../../utils/rbac'
import { WIDGET_LIBRARY } from './DashboardSidebar'
import { MiniTransparencyWell } from './MiniTransparencyWell'
import { TransparencyModal } from './TransparencyModal'

// Navigation menu items (v2 design)
const MENU_ITEMS = [
  { id: 'dashboard', label: 'דשבורד', icon: LayoutDashboard, path: '/clinic/dashboard' },
  { id: 'patients', label: 'מטופלים', icon: Users, path: '/clinic/patients' },
  { id: 'communications', label: 'תקשורת', icon: MessageSquare, path: '/clinic/communications' },
  { id: 'agents', label: 'סוכני AI', icon: Bot, path: '/clinic/agents' },
  { id: 'reports', label: 'דוחות', icon: FileBarChart, path: '/clinic/analytics' }
]

// Widget categories
const CATEGORIES = [
  { id: 'all', label: 'All' },
  { id: 'operations', label: 'Operations' },
  { id: 'analytics', label: 'Analytics' },
  { id: 'clinical', label: 'Clinical' },
  { id: 'admin', label: 'Admin' }
]

interface NavigationSidebarProps {
  darkMode: boolean
  onToggleDarkMode: () => void
  onLogout: () => void
}

export function NavigationSidebar({ darkMode, onToggleDarkMode, onLogout }: NavigationSidebarProps) {
  const location = useLocation()
  const { activeWidgets, addWidget, removeWidget, isSidebarOpen, toggleSidebar } = useDashboard()
  
  // Widget library state
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [widgetSectionCollapsed, setWidgetSectionCollapsed] = useState(false)
  const [availableCollapsed, setAvailableCollapsed] = useState(false)
  const [activeCollapsed, setActiveCollapsed] = useState(true)
  
  // Transparency well state
  const [wellExpanded, setWellExpanded] = useState(false)
  
  const userInfo = getUserInfo()
  
  // Filter widgets
  const filteredWidgets = WIDGET_LIBRARY.filter(widget => {
    if (selectedCategory !== 'all' && widget.category !== selectedCategory) return false
    if (searchQuery && !widget.title.toLowerCase().includes(searchQuery.toLowerCase())) return false
    return true
  })
  
  const availableWidgets = filteredWidgets.filter(w => !activeWidgets?.includes(w.id))
  const activeWidgetsList = filteredWidgets.filter(w => activeWidgets?.includes(w.id))
  
  if (!isSidebarOpen) {
    return (
      <button
        onClick={toggleSidebar}
        className="fixed right-0 top-1/2 -translate-y-1/2 w-8 h-12 bg-blue-600 text-white rounded-l-lg shadow-lg hover:bg-blue-700 transition flex items-center justify-center z-40"
        aria-label="Open sidebar"
      >
        <ChevronLeft size={18}/>
      </button>
    )
  }
  
  return (
    <>
      <aside className="fixed right-0 top-0 h-screen w-80 bg-white dark:bg-slate-800 border-l border-slate-200 dark:border-slate-700 shadow-2xl z-50 flex flex-col overflow-hidden">
        
        {/* Section 1: Logo */}
        <div className="p-4 flex items-center gap-3">
          <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center text-white font-bold shadow-lg shadow-blue-200 dark:shadow-blue-900/50 text-xl">
            D
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-800 dark:text-white tracking-tight leading-none">
              DentaFlow
            </h1>
            <span className="text-[10px] text-slate-400 font-medium tracking-widest uppercase">
              סביבת עבודה
            </span>
          </div>
        </div>
        
        {/* Section 2: Plan Badge */}
        <div className="px-4 mb-3">
          <div className="p-2 rounded-lg flex items-center gap-2 text-white text-xs font-bold bg-gradient-to-r from-blue-500 to-blue-600 shadow-md">
            <Crown size={14}/>
            <span>Professional Plan</span>
          </div>
        </div>
        
        {/* Section 3: Navigation */}
        <div className="px-4 mb-3">
          <h3 className="px-2 mb-2 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Navigation
          </h3>
          <nav className="space-y-1">
            {MENU_ITEMS.map(item => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              
              return (
                <Link
                  key={item.id}
                  to={item.path}
                  className={`
                    w-full flex items-center gap-3 px-4 py-3 
                    rounded-xl transition text-sm font-medium
                    ${isActive
                      ? 'bg-blue-50 text-blue-700 shadow-sm dark:bg-blue-900/30 dark:text-blue-300'
                      : 'text-slate-500 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-700'
                    }
                  `}
                >
                  <Icon size={20} strokeWidth={2}/> 
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </div>
        
        {/* Section 4: Widget Library */}
        <div className="flex-1 overflow-hidden flex flex-col px-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Customize Dashboard
            </h3>
            <button 
              onClick={() => setWidgetSectionCollapsed(!widgetSectionCollapsed)}
              className="p-1 hover:bg-slate-100 dark:hover:bg-slate-700 rounded transition"
              aria-label={widgetSectionCollapsed ? 'Expand widget section' : 'Collapse widget section'}
            >
              {widgetSectionCollapsed ? <ChevronDown size={14}/> : <ChevronUp size={14}/>}
            </button>
          </div>
          
          {!widgetSectionCollapsed && (
            <>
              {/* Search */}
              <div className="mb-2">
                <div className="relative">
                  <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none"/>
                  <input
                    type="text"
                    placeholder="Search widgets..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              
              {/* Categories */}
              <div className="mb-2 flex gap-1 flex-wrap">
                {CATEGORIES.map(cat => (
                  <button
                    key={cat.id}
                    onClick={() => setSelectedCategory(cat.id)}
                    className={`px-2 py-1 text-[10px] font-medium rounded-md transition ${
                      selectedCategory === cat.id
                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600'
                    }`}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>
              
              {/* Widget Lists */}
              <div className="flex-1 overflow-y-auto space-y-2">
                {/* Available Widgets */}
                <div>
                  <button
                    onClick={() => setAvailableCollapsed(!availableCollapsed)}
                    className="w-full flex items-center justify-between px-2 py-1 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 rounded transition"
                  >
                    <span>Available ({availableWidgets.length})</span>
                    {availableCollapsed ? <ChevronRight size={12}/> : <ChevronDown size={12}/>}
                  </button>
                  
                  {!availableCollapsed && availableWidgets.length > 0 && (
                    <div className="mt-1 space-y-1">
                      {availableWidgets.map(widget => {
                        const Icon = widget.icon
                        return (
                          <div
                            key={widget.id}
                            onClick={() => addWidget(widget.id, {
                              i: widget.id,
                              x: 0,
                              y: 0,
                              w: widget.defaultSize.w,
                              h: widget.defaultSize.h
                            })}
                            className="flex items-center gap-2 p-2 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 cursor-pointer transition"
                          >
                            <div className="w-7 h-7 rounded-lg flex items-center justify-center bg-blue-50 dark:bg-blue-900/30">
                              <Icon size={14} className="text-blue-600 dark:text-blue-400"/>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="text-xs font-medium text-slate-700 dark:text-slate-200 truncate">
                                {widget.title}
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
                
                {/* Active Widgets */}
                <div>
                  <button
                    onClick={() => setActiveCollapsed(!activeCollapsed)}
                    className="w-full flex items-center justify-between px-2 py-1 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 rounded transition"
                  >
                    <span>Active ({activeWidgetsList.length})</span>
                    {activeCollapsed ? <ChevronRight size={12}/> : <ChevronDown size={12}/>}
                  </button>
                  
                  {!activeCollapsed && activeWidgetsList.length > 0 && (
                    <div className="mt-1 space-y-1">
                      {activeWidgetsList.map(widget => {
                        const Icon = widget.icon
                        return (
                          <div
                            key={widget.id}
                            className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600"
                          >
                            <div className="w-7 h-7 rounded-lg flex items-center justify-center bg-blue-50 dark:bg-blue-900/30">
                              <Icon size={14} className="text-blue-600 dark:text-blue-400"/>
                            </div>
                            <div className="flex-1 min-w-0 text-xs font-medium text-slate-700 dark:text-slate-200 truncate">
                              {widget.title}
                            </div>
                            <button
                              onClick={() => removeWidget(widget.id)}
                              className="p-1 hover:bg-red-100 dark:hover:bg-red-900/30 rounded transition"
                              aria-label={`Remove ${widget.title}`}
                            >
                              <X size={10} className="text-slate-400 hover:text-red-600"/>
                            </button>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
        
        {/* Section 5: Mini "Well" */}
        <div className="px-4 mb-3">
          <MiniTransparencyWell onExpand={() => setWellExpanded(true)} />
        </div>
        
        {/* Section 6: Controls */}
        <div className="px-4 pt-3 border-t border-slate-200 dark:border-slate-700">
          <div className="flex justify-between items-center mb-3">
            <button 
              onClick={onToggleDarkMode}
              className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition"
              title={darkMode ? 'Light Mode' : 'Dark Mode'}
              aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {darkMode ? (
                <Sun size={16} className="text-amber-400"/>
              ) : (
                <Moon size={16} className="text-slate-400"/>
              )}
            </button>
            <div className="flex gap-1">
              <button 
                className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                title="Settings"
                aria-label="Settings"
              >
                <Settings size={16}/>
              </button>
              <button 
                onClick={onLogout}
                className="p-2 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20 transition text-slate-400 hover:text-red-600"
                title="Logout"
                aria-label="Logout"
              >
                <LogOut size={16}/>
              </button>
            </div>
          </div>
        </div>
        
        {/* Section 7: User Profile */}
        <div className="px-4 pb-4">
          <div className="bg-slate-50 dark:bg-slate-700/50 p-3 rounded-xl flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center text-white text-sm font-bold shadow-md">
              {userInfo?.full_name?.split(' ').map((n: string) => n[0]).join('') || 'RC'}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-semibold text-slate-800 dark:text-white truncate">
                {userInfo?.full_name || 'Dr. Ron Cohen'}
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400 truncate">
                {userInfo?.role || 'מנהל מערכת'}
              </div>
            </div>
          </div>
        </div>
        
        {/* Toggle Button */}
        <button
          onClick={toggleSidebar}
          className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-full w-8 h-12 bg-blue-600 text-white rounded-l-lg shadow-lg hover:bg-blue-700 transition flex items-center justify-center"
          aria-label="Close sidebar"
        >
          <ChevronRight size={18}/>
        </button>
      </aside>
      
      {/* Transparency Modal */}
      <TransparencyModal 
        isOpen={wellExpanded}
        onClose={() => setWellExpanded(false)}
      />
    </>
  )
}
