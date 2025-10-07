/**
 * Mission Control Layout - Main dashboard layout structure
 * 
 * Features:
 * - Fixed header with search, alerts, user menu
 * - Collapsible left sidebar with navigation
 * - Main dashboard area with draggable widgets
 * - Optional right panel for details
 * - Fixed bottom status bar
 */

import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Home,
  MessageSquare,
  BarChart3,
  Settings,
  FileText,
  Users,
  Calendar,
  Menu,
  Search,
  Bell,
  User,
  LogOut,
  Sparkles,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useDashboardStore } from '@/stores/dashboardStore'
import { useWebSocket } from '@/hooks/useWebSocket'

const navigation = [
  { name: 'Home', href: '#top', icon: Home, scrollTo: 'top' },
  { name: 'Conversations', href: '#conversations', icon: MessageSquare, scrollTo: 'conversations' },
  { name: 'Analytics', href: '#analytics', icon: BarChart3, scrollTo: 'analytics' },
  { name: 'Configuration', href: '#configuration', icon: Settings, scrollTo: 'configuration' },
  { name: 'Logs', href: '#logs', icon: FileText, scrollTo: 'logs' },
  { name: 'Patients', href: '#patients', icon: Users, scrollTo: 'patients' },
  { name: 'Appointments', href: '#appointments', icon: Calendar, scrollTo: 'appointments' },
]

export function MissionControlLayout({ children, user, onLogout }) {
  const location = useLocation()
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  
  const {
    sidebarCollapsed,
    toggleSidebar,
    rightPanelOpen,
    closeRightPanel,
    unreadAlertCount,
    wsConnected,
    wsLastUpdate,
    metrics,
    agentStatus,
  } = useDashboardStore()

  // Initialize WebSocket connection
  const { connected: wsActive } = useWebSocket()

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/dashboard/search?q=${encodeURIComponent(searchQuery)}`)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'online':
        return 'bg-green-500'
      case 'offline':
        return 'bg-gray-500'
      case 'error':
        return 'bg-red-500'
      case 'paused':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-500'
    }
  }

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="h-16 border-b bg-card flex items-center px-4 gap-4 flex-shrink-0">
        {/* Logo & Org Name */}
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-xl">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold">DentalDesk AI</h1>
            <p className="text-xs text-muted-foreground">Mission Control</p>
          </div>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search conversations, patients..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
        </form>

        {/* Right Side */}
        <div className="flex items-center gap-2">
          {/* Alerts */}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-5 w-5" />
            {unreadAlertCount > 0 && (
              <Badge
                variant="destructive"
                className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
              >
                {unreadAlertCount}
              </Badge>
            )}
          </Button>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center gap-2">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
                    {user?.full_name?.charAt(0) || 'U'}
                  </AvatarFallback>
                </Avatar>
                <span className="text-sm font-medium hidden md:inline">
                  {user?.full_name || 'User'}
                </span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="mr-2 h-4 w-4" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <aside
          className={cn(
            'border-r bg-card transition-all duration-300 flex-shrink-0',
            sidebarCollapsed ? 'w-16' : 'w-60'
          )}
        >
          <nav className="p-2 space-y-1">
            {navigation.map((item) => {
              const isActive = location.hash === item.href || (item.scrollTo === 'top' && !location.hash)
              const Icon = item.icon
              
              const handleClick = (e) => {
                e.preventDefault()
                if (item.scrollTo === 'top') {
                  window.scrollTo({ top: 0, behavior: 'smooth' })
                } else {
                  const element = document.getElementById(item.scrollTo)
                  if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
                  }
                }
                window.location.hash = item.href
              }
              
              return (
                <a
                  key={item.name}
                  href={item.href}
                  onClick={handleClick}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors cursor-pointer',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-accent hover:text-accent-foreground'
                  )}
                  title={sidebarCollapsed ? item.name : undefined}
                >
                  <Icon className="h-5 w-5 flex-shrink-0" />
                  {!sidebarCollapsed && (
                    <span className="text-sm font-medium">{item.name}</span>
                  )}
                  {!sidebarCollapsed && item.badge && (
                    <Badge variant="secondary" className="ml-auto">
                      {item.badge}
                    </Badge>
                  )}
                </a>
              )
            })}
          </nav>

          {/* Collapse Toggle */}
          <div className="absolute bottom-4 left-2 right-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleSidebar}
              className="w-full justify-center"
            >
              {sidebarCollapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <>
                  <ChevronLeft className="h-4 w-4 mr-2" />
                  <span className="text-xs">Collapse</span>
                </>
              )}
            </Button>
          </div>
        </aside>

        {/* Main Dashboard Area */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>

        {/* Right Panel (Optional) */}
        {rightPanelOpen && (
          <aside className="w-80 border-l bg-card flex-shrink-0 overflow-auto">
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Details</h3>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={closeRightPanel}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
              {/* Right panel content goes here */}
            </div>
          </aside>
        )}
      </div>

      {/* Bottom Status Bar */}
      <footer className="h-10 border-t bg-card flex items-center px-4 gap-4 text-xs flex-shrink-0">
        {/* Agent Status */}
        <div className="flex items-center gap-2">
          <div className={cn('w-2 h-2 rounded-full', getStatusColor(agentStatus.status))} />
          <span className="font-medium">
            Alex: {agentStatus.status.charAt(0).toUpperCase() + agentStatus.status.slice(1)}
          </span>
        </div>

        <div className="h-4 w-px bg-border" />

        {/* Active Conversations */}
        <div className="flex items-center gap-2">
          <MessageSquare className="h-3 w-3" />
          <span>Conversations: {metrics.activeConversations}</span>
        </div>

        <div className="h-4 w-px bg-border" />

        {/* WebSocket Status */}
        <div className="flex items-center gap-2">
          <div className={cn('w-2 h-2 rounded-full', wsActive ? 'bg-green-500' : 'bg-red-500')} />
          <span>
            {wsActive ? 'Connected' : 'Disconnected'}
            {wsLastUpdate && ` • ${Math.round((Date.now() - wsLastUpdate) / 1000)}s ago`}
          </span>
        </div>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Version */}
        <span className="text-muted-foreground">v1.0.0</span>
      </footer>
    </div>
  )
}

export default MissionControlLayout
