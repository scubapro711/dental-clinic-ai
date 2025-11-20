/**
 * TransparencyModal - Full transparency panel in modal
 * 
 * Features:
 * - Full-screen modal overlay
 * - Shows complete agent activity details
 * - Click outside to close
 * - ESC key to close
 */

import { useEffect } from 'react'
import { X, Bot } from 'lucide-react'
import EnhancedTransparencyPanel from '../transparency/EnhancedTransparencyPanel'

interface TransparencyModalProps {
  isOpen: boolean
  onClose: () => void
}

export function TransparencyModal({ isOpen, onClose }: TransparencyModalProps) {
  // Handle ESC key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }
    
    if (isOpen) {
      document.addEventListener('keydown', handleEsc)
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden'
    }
    
    return () => {
      document.removeEventListener('keydown', handleEsc)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])
  
  if (!isOpen) return null
  
  return (
    <div 
      className="fixed inset-0 bg-black/50 z-[100] flex items-center justify-center p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="transparency-modal-title"
    >
      <div 
        className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <Bot size={20} className="text-blue-600 dark:text-blue-400"/>
            </div>
            <div>
              <h3 
                id="transparency-modal-title"
                className="text-lg font-bold text-slate-800 dark:text-white"
              >
                Agent Activity
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Real-time transparency
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition"
            aria-label="Close modal"
          >
            <X size={20} className="text-slate-400"/>
          </button>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <EnhancedTransparencyPanel />
        </div>
      </div>
    </div>
  )
}
