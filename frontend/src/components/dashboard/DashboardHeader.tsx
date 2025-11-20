/**
 * DashboardHeader v8.0 - Clean v2 Design
 * 
 * Features:
 * - Frosted glass effect (v2 signature look)
 * - Clean, minimal design
 * - No agent cards (moved to AI Agents page via sidebar)
 * - Organization selector
 * - Dark mode toggle
 * - Responsive design
 */

import { getUserInfo } from '../../utils/rbac'
import { OrganizationSelector } from '../OrganizationSelector'
import { Moon, Sun, Building2 } from 'lucide-react'

interface DashboardHeaderProps {
  darkMode?: boolean
  onToggleDarkMode?: () => void
}

export function DashboardHeader({ darkMode, onToggleDarkMode }: DashboardHeaderProps = {}) {
  const userInfo = getUserInfo()
  
  return (
    <header 
      className="h-16 px-6 flex items-center justify-between bg-white/80 dark:bg-slate-800/80 backdrop-blur-md border-b border-slate-200/60 dark:border-slate-700/60 sticky top-0 z-10"
    >
      {/* Left: Logo + Title */}
      <div className="flex items-center gap-4">
        <div className="w-9 h-9 bg-gradient-to-tr from-blue-500 to-blue-600 rounded-xl shadow-lg shadow-blue-200 dark:shadow-blue-900/50 flex items-center justify-center text-white font-bold text-lg">
          D
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-800 dark:text-white">
            Dashboard
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Welcome back, <span className="font-medium text-slate-700 dark:text-slate-300">
              {userInfo?.name || 'User'}
            </span>
          </p>
        </div>
      </div>
      
      {/* Right: Organization + Dark Mode */}
      <div className="flex items-center gap-3">
        {/* Organization Selector */}
        <div className="hidden md:block">
          <OrganizationSelector />
        </div>
        
        {/* Dark Mode Toggle */}
        {onToggleDarkMode && (
          <button
            onClick={onToggleDarkMode}
            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            className="p-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 transition-all duration-200 flex items-center justify-center"
          >
            {darkMode ? (
              <Sun size={18} className="text-amber-500" />
            ) : (
              <Moon size={18} className="text-slate-600" />
            )}
          </button>
        )}
      </div>
    </header>
  )
}
