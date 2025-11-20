/**
 * AddTreatmentModal - Add treatment modal (Level 3)
 * 
 * Features:
 * - Treatment form
 * - Tooth selector
 * - Price input
 * - Notes textarea
 * - Save/cancel actions
 * - Validation
 * - v2 design styling
 */

import { useState, useEffect } from 'react'
import { X, Save, AlertCircle } from 'lucide-react'
import API_CONFIG from '../../config/api'

const TREATMENT_TYPES = [
  'ניקוי אבנית',
  'סתימה',
  'עקירה',
  'שורש',
  'כתר',
  'גשר',
  'השתלה',
  'הלבנה',
  'אחר'
]

export default function AddTreatmentModal({ patientId, onClose, onSave }) {
  const [formData, setFormData] = useState({
    type: '',
    tooth: '',
    price: '',
    notes: '',
    date: new Date().toISOString().split('T')[0]
  })
  
  const [errors, setErrors] = useState({})
  const [saving, setSaving] = useState(false)
  
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
  
  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }))
    }
  }
  
  const validate = () => {
    const newErrors = {}
    
    if (!formData.type) {
      newErrors.type = 'נא לבחור סוג טיפול'
    }
    
    if (!formData.price || formData.price <= 0) {
      newErrors.price = 'נא להזין מחיר תקין'
    }
    
    if (!formData.date) {
      newErrors.date = 'נא לבחור תאריך'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }
  
  const handleSave = async () => {
    if (!validate()) {
      return
    }
    
    try {
      setSaving(true)
      
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/patients/${patientId}/treatments`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })
      
      if (!response.ok) {
        throw new Error('Failed to save treatment')
      }
      
      const data = await response.json()
      onSave(data)
    } catch (err) {
      console.error('Error saving treatment:', err)
      setErrors({ submit: err.message })
    } finally {
      setSaving(false)
    }
  }
  
  return (
    <div 
      className="fixed inset-0 bg-black/50 z-[110] flex items-center justify-center p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="treatment-modal-title"
    >
      <div 
        className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden"
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
          
          <h3 
            id="treatment-modal-title"
            className="text-xl font-bold"
          >
            הוסף טיפול
          </h3>
          <p className="text-blue-100 text-sm mt-1">
            מטופל #{patientId}
          </p>
        </div>
        
        {/* Form */}
        <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
          {/* Treatment Type */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              סוג טיפול <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.type}
              onChange={(e) => handleChange('type', e.target.value)}
              className={`w-full px-4 py-3 rounded-xl border ${
                errors.type 
                  ? 'border-red-300 dark:border-red-700' 
                  : 'border-slate-200 dark:border-slate-700'
              } bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500`}
            >
              <option value="">בחר סוג טיפול...</option>
              {TREATMENT_TYPES.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
            {errors.type && (
              <p className="mt-1 text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
                <AlertCircle size={12}/>
                {errors.type}
              </p>
            )}
          </div>
          
          {/* Tooth Number */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              מספר שן
            </label>
            <input
              type="text"
              value={formData.tooth}
              onChange={(e) => handleChange('tooth', e.target.value)}
              placeholder="לדוגמה: 16"
              className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          {/* Price */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              מחיר <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type="number"
                value={formData.price}
                onChange={(e) => handleChange('price', e.target.value)}
                placeholder="0"
                className={`w-full px-4 py-3 rounded-xl border ${
                  errors.price 
                    ? 'border-red-300 dark:border-red-700' 
                    : 'border-slate-200 dark:border-slate-700'
                } bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500`}
              />
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
                ₪
              </span>
            </div>
            {errors.price && (
              <p className="mt-1 text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
                <AlertCircle size={12}/>
                {errors.price}
              </p>
            )}
          </div>
          
          {/* Date */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              תאריך <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) => handleChange('date', e.target.value)}
              className={`w-full px-4 py-3 rounded-xl border ${
                errors.date 
                  ? 'border-red-300 dark:border-red-700' 
                    : 'border-slate-200 dark:border-slate-700'
              } bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500`}
            />
            {errors.date && (
              <p className="mt-1 text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
                <AlertCircle size={12}/>
                {errors.date}
              </p>
            )}
          </div>
          
          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              הערות
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              placeholder="הערות נוספות..."
              rows={3}
              className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>
          
          {/* Submit Error */}
          {errors.submit && (
            <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
              <p className="text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
                <AlertCircle size={16}/>
                {errors.submit}
              </p>
            </div>
          )}
        </div>
        
        {/* Actions */}
        <div className="p-6 pt-0 flex gap-3">
          <button
            onClick={onClose}
            disabled={saving}
            className="flex-1 px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ביטול
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex-1 px-4 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white transition font-medium flex items-center justify-center gap-2 shadow-lg shadow-blue-200 dark:shadow-blue-900/50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"/>
                שומר...
              </>
            ) : (
              <>
                <Save size={16}/>
                שמור
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
