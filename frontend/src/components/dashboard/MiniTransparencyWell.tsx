/**
 * MiniTransparencyWell - Compact transparency panel for sidebar
 * 
 * Features:
 * - Shows current agent activity
 * - Click to expand full transparency modal
 * - Compact design (60px height)
 * - v2 design: rounded-2xl, shadow-inner
 */

import { Bot, Activity } from 'lucide-react'
import useAgentActivity from '../../hooks/useAgentActivity'

interface MiniTransparencyWellProps {
  onExpand: () => void
}

export function MiniTransparencyWell({ onExpand }: MiniTransparencyWellProps) {
  const { activity, toolCalls } = useAgentActivity()
  
  // Extract agent name and task
  const activeAgent = activity?.agent || null
  const currentTask = activity?.task || null
  const progress = activity?.progress || 0
  
  return (
    <div 
      onClick={onExpand}
      className="p-3 rounded-2xl shadow-inner border border-slate-100 dark:border-slate-700 cursor-pointer hover:border-blue-300 hover:shadow-md transition-all bg-white dark:bg-slate-800"
      role="button"
      aria-label="View agent activity details"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onExpand()
        }
      }}
    >
      {activeAgent ? (
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
            <Bot size={14} className="text-blue-600 dark:text-blue-400 animate-pulse"/>
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-semibold text-slate-700 dark:text-slate-200 truncate">
              {activeAgent}
            </div>
            <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">
              {currentTask || 'Working...'}
            </div>
          </div>
          <div className="flex flex-col items-end flex-shrink-0">
            <div className="text-xs font-bold text-blue-600 dark:text-blue-400">
              {Math.round(progress)}%
            </div>
            <div className="text-[9px] text-slate-400">
              ▲ Click
            </div>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center gap-2 text-slate-400">
          <Activity size={14}/>
          <span className="text-xs">No active agents</span>
        </div>
      )}
    </div>
  )
}
