import { useState } from 'react'
import { Bell, Settings, User, Menu, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Badge } from '@/components/ui/badge'

/**
 * Header Component - Top navigation bar with logo, search, and user controls
 * 
 * Features:
 * - Responsive design with mobile menu toggle
 * - Global search functionality
 * - Notifications with badge count
 * - User profile dropdown
 * - Settings access
 */
export function Header({ onMenuToggle, className = '' }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [notificationCount] = useState(3) // Mock notification count

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      // TODO: Implement global search
      console.log('Searching for:', searchQuery)
    }
  }

  const handleNotificationClick = () => {
    // TODO: Open notifications panel
    console.log('Opening notifications')
  }

  const handleProfileClick = (action) => {
    // TODO: Implement profile actions
    console.log('Profile action:', action)
  }

  return (
    <header 
      className={`bg-background border-b border-border px-4 py-3 flex items-center justify-between ${className}`}
      role="banner"
    >
      {/* Left Section - Logo and Menu Toggle */}
      <div className="flex items-center gap-4">
        {/* Mobile Menu Toggle */}
        <Button
          variant="ghost"
          size="sm"
          onClick={onMenuToggle}
          className="lg:hidden"
          aria-label="Toggle navigation menu"
        >
          <Menu className="h-5 w-5" />
        </Button>

        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-sm">DC</span>
          </div>
          <h1 className="font-semibold text-lg hidden sm:block">
            Dental Clinic AI
          </h1>
        </div>
      </div>

      {/* Center Section - Search */}
      <div className="flex-1 max-w-md mx-4 hidden md:block">
        <form onSubmit={handleSearch} className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search patients, appointments..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 pr-4"
            aria-label="Global search"
          />
        </form>
      </div>

      {/* Right Section - Actions and User */}
      <div className="flex items-center gap-2">
        {/* Mobile Search Button */}
        <Button
          variant="ghost"
          size="sm"
          className="md:hidden"
          aria-label="Search"
        >
          <Search className="h-5 w-5" />
        </Button>

        {/* Notifications */}
        <Button
          variant="ghost"
          size="sm"
          onClick={handleNotificationClick}
          className="relative"
          aria-label={`Notifications ${notificationCount > 0 ? `(${notificationCount} unread)` : ''}`}
        >
          <Bell className="h-5 w-5" />
          {notificationCount > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
            >
              {notificationCount > 9 ? '9+' : notificationCount}
            </Badge>
          )}
        </Button>

        {/* Settings */}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => handleProfileClick('settings')}
          aria-label="Settings"
        >
          <Settings className="h-5 w-5" />
        </Button>

        {/* User Profile Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button 
              variant="ghost" 
              size="sm"
              className="flex items-center gap-2"
              aria-label="User menu"
            >
              <User className="h-5 w-5" />
              <span className="hidden sm:inline">Dr. Smith</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => handleProfileClick('profile')}>
              <User className="mr-2 h-4 w-4" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleProfileClick('settings')}>
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem 
              onClick={() => handleProfileClick('logout')}
              className="text-destructive"
            >
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
