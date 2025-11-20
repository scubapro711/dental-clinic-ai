/**
 * PatientModal - Quick view patient modal (Level 1)
 * 
 * Features:
 * - Overlay modal with patient summary
 * - Click to open full patient file
 * - Close on backdrop click
 * - ESC key support
 * - v2 design styling
 */

import { useEffect } from 'react'
import { X, User, Phone, Mail, Calendar, DollarSign, FileText } from 'lucide-react'

export default function PatientModal({ patient, onClose, onOpenFullFile }) {
  // Handle ESC key
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }
    
    document.addEventListener('keydown', handleEsc)
    document.body.style.overflow = 'hidden'
    
    return () => {
      document.removeEventListener('keydown', handleEsc)
      document.body.style.overflow = 'unset'
    }
  }, [onClose])
  
  if (!patient) return null
  
  return (
    <div 
      className="fixed inset-0 bg-black/50 z-[100] flex items-center justify-center p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="patient-modal-title"
    >
      <div 
        className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 text-white relative">
          <button 
            onClick={onClose}
            className="absolute left-4 top-4 p-2 hover:bg-white/20 rounded-lg transition"
            aria-label="Close modal"
          >
            <X size={20}/>
          </button>
          
          <div className="flex items-center gap-4 mt-8">
            <div className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-2xl font-bold">
              {patient.name?.split(' ').map(n => n[0]).join('') || 'P'}
            </div>
            <div>
              <h3 
                id="patient-modal-title"
                className="text-xl font-bold"
              >
                {patient.name || 'Unknown Patient'}
              </h3>
              <p className="text-blue-100 text-sm">
                ID: {patient.id}
              </p>
            </div>
          </div>
        </div>
        
        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Contact Info */}
          <div className="space-y-3">
            <div className="flex items-center gap-3 text-sm">
              <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center">
                <Phone size={14} className="text-blue-600 dark:text-blue-400"/>
              </div>
              <div>
                <div className="text-xs text-slate-500 dark:text-slate-400">טלפון</div>
                <div className="font-medium text-slate-700 dark:text-slate-200">
                  {patient.phone || 'לא זמין'}
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-3 text-sm">
              <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center">
                <Mail size={14} className="text-blue-600 dark:text-blue-400"/>
              </div>
              <div>
                <div className="text-xs text-slate-500 dark:text-slate-400">אימייל</div>
                <div className="font-medium text-slate-700 dark:text-slate-200">
                  {patient.email || 'לא זמין'}
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-3 text-sm">
              <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center">
                <Calendar size={14} className="text-blue-600 dark:text-blue-400"/>
              </div>
              <div>
                <div className="text-xs text-slate-500 dark:text-slate-400">ביקור אחרון</div>
                <div className="font-medium text-slate-700 dark:text-slate-200">
                  {patient.last_visit || 'אין מידע'}
                </div>
              </div>
            </div>
          </div>
          
          {/* Financial Summary */}
          <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <DollarSign size={16} className="text-slate-400"/>
                <span className="text-sm font-medium text-slate-600 dark:text-slate-300">
                  יתרה
                </span>
              </div>
              <div className={`text-lg font-bold ${
                (patient.balance || 0) < 0 
                  ? 'text-red-600 dark:text-red-400' 
                  : 'text-green-600 dark:text-green-400'
              }`}>
                ₪{Math.abs(patient.balance || 0).toLocaleString()}
                {(patient.balance || 0) < 0 && ' חוב'}
              </div>
            </div>
          </div>
          
          {/* Status Badge */}
          {patient.status && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-500 dark:text-slate-400">סטטוס:</span>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                patient.status === 'active' 
                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                  : patient.status === 'debt'
                  ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300'
                  : 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'
              }`}>
                {patient.status === 'active' ? 'פעיל' : patient.status === 'debt' ? 'חוב' : patient.status}
              </span>
            </div>
          )}
        </div>
        
        {/* Actions */}
        <div className="p-6 pt-0 flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition font-medium"
          >
            סגור
          </button>
          <button
            onClick={() => {
              onOpenFullFile(patient.id)
              onClose()
            }}
            className="flex-1 px-4 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white transition font-medium flex items-center justify-center gap-2 shadow-lg shadow-blue-200 dark:shadow-blue-900/50"
          >
            <FileText size={16}/>
            פתח תיק מלא
          </button>
        </div>
      </div>
    </div>
  )
}
