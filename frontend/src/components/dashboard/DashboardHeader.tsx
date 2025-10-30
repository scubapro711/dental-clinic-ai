/**
 * DashboardHeader - Header with Edit Mode toggle and Reset button
 * 
 * Features:
 * - Edit Mode toggle
 * - Reset to defaults button (only in edit mode)
 * - User greeting
 * - Responsive design
 * 
 * Best Practices:
 * - Clear visual feedback for edit mode
 * - Confirm before reset (prevent accidental data loss)
 * - Responsive (hide text on mobile)
 * - Accessible (ARIA labels, keyboard navigation)
 */

import { Settings, RotateCcw } from 'lucide-react'
import { useDashboard } from '../../contexts/DashboardContext'
import { getUserInfo } from '../../utils/rbac'

export function DashboardHeader() {
  const { isEditMode, toggleEditMode, resetToDefaults } = useDashboard()
  const userInfo = getUserInfo()
  
  const handleReset = () => {
    if (confirm('Reset dashboard to default layout? This cannot be undone.')) {
      resetToDefaults()
    }
  }
  
  return (
    <div className="dashboard-header-customization flex items-center justify-between mb-6 p-4 bg-white rounded-lg shadow-sm">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-600 hidden sm:block">
          Welcome back, {userInfo?.name || 'User'}
        </p>
      </div>
      
      <div className="flex items-center gap-2">
        {/* Edit Mode Toggle */}
        <button
          onClick={toggleEditMode}
          className={`
            px-4 py-2 rounded-lg flex items-center gap-2 transition-all
            ${isEditMode
              ? 'bg-blue-600 text-white shadow-md'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }
          `}
          aria-label={isEditMode ? 'Exit edit mode' : 'Enter edit mode'}
          data-testid="edit-mode-toggle"
        >
          <Settings size={16} />
          <span className="hidden sm:inline">
            {isEditMode ? 'Done' : 'Customize'}
          </span>
        </button>
        
        {/* Reset Button (only in edit mode) */}
        {isEditMode && (
          <button
            onClick={handleReset}
            className="px-4 py-2 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 flex items-center gap-2 transition-colors"
            aria-label="Reset to default layout"
            data-testid="reset-button"
          >
            <RotateCcw size={16} />
            <span className="hidden sm:inline">Reset</span>
          </button>
        )}
      </div>
    </div>
  )
}
