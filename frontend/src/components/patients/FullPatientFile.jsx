/**
 * FullPatientFile - Complete patient file view (Level 2)
 * 
 * Features:
 * - Full patient profile
 * - Personal information
 * - Dental chart
 * - Treatment history
 * - Financial summary
 * - Add treatment button
 * - Back to dashboard button
 * - v2 design styling
 */

import { useState, useEffect } from 'react'
import { 
  ArrowRight, User, Phone, Mail, MapPin, Calendar, 
  DollarSign, Plus, FileText, Activity, AlertCircle
} from 'lucide-react'
import API_CONFIG from '../../config/api'

export default function FullPatientFile({ patientId, onBack, onAddTreatment }) {
  const [patient, setPatient] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Fetch patient data
  useEffect(() => {
    if (!patientId) {
      setError('No patient ID provided')
      setLoading(false)
      return
    }
    
    fetchPatientData()
  }, [patientId])
  
  const fetchPatientData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/patients/${patientId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch patient data')
      }
      
      const data = await response.json()
      setPatient(data)
    } catch (err) {
      console.error('Error fetching patient:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }
  
  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4"/>
          <p className="text-slate-600 dark:text-slate-400">טוען נתוני מטופל...</p>
        </div>
      </div>
    )
  }
  
  if (error || !patient) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4"/>
          <p className="text-slate-600 dark:text-slate-400 mb-4">
            {error || 'Patient not found'}
          </p>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            חזרה לדשבורד
          </button>
        </div>
      </div>
    )
  }
  
  return (
    <div className="flex-1 flex flex-col bg-slate-50 dark:bg-slate-900 overflow-hidden">
      {/* Custom Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="flex items-center gap-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 text-sm font-medium transition"
            >
              <ArrowRight size={16}/>
              חזרה לדשבורד
            </button>
            
            <div className="w-px h-6 bg-slate-200 dark:bg-slate-700"/>
            
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center text-white text-sm font-bold shadow-md">
                {patient.name?.split(' ').map(n => n[0]).join('') || 'P'}
              </div>
              <div>
                <h1 className="text-lg font-bold text-slate-800 dark:text-white">
                  {patient.name || 'Unknown Patient'}
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  ID: {patient.id}
                </p>
              </div>
            </div>
          </div>
          
          <button
            onClick={onAddTreatment}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition font-medium shadow-lg shadow-blue-200 dark:shadow-blue-900/50"
          >
            <Plus size={16}/>
            הוסף טיפול
          </button>
        </div>
      </header>
      
      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-6xl mx-auto space-y-6">
          
          {/* Personal Information */}
          <section className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
            <h2 className="text-lg font-bold text-slate-800 dark:text-white mb-4 flex items-center gap-2">
              <User size={20} className="text-blue-600"/>
              מידע אישי
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
                  <Phone size={16} className="text-blue-600 dark:text-blue-400"/>
                </div>
                <div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">טלפון</div>
                  <div className="font-medium text-slate-700 dark:text-slate-200">
                    {patient.phone || 'לא זמין'}
                  </div>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
                  <Mail size={16} className="text-blue-600 dark:text-blue-400"/>
                </div>
                <div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">אימייל</div>
                  <div className="font-medium text-slate-700 dark:text-slate-200">
                    {patient.email || 'לא זמין'}
                  </div>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
                  <MapPin size={16} className="text-blue-600 dark:text-blue-400"/>
                </div>
                <div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">כתובת</div>
                  <div className="font-medium text-slate-700 dark:text-slate-200">
                    {patient.address || 'לא זמין'}
                  </div>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
                  <Calendar size={16} className="text-blue-600 dark:text-blue-400"/>
                </div>
                <div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">תאריך לידה</div>
                  <div className="font-medium text-slate-700 dark:text-slate-200">
                    {patient.date_of_birth || 'לא זמין'}
                  </div>
                </div>
              </div>
            </div>
          </section>
          
          {/* Financial Summary */}
          <section className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
            <h2 className="text-lg font-bold text-slate-800 dark:text-white mb-4 flex items-center gap-2">
              <DollarSign size={20} className="text-blue-600"/>
              סיכום פיננסי
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-700/50">
                <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">יתרה נוכחית</div>
                <div className={`text-2xl font-bold ${
                  (patient.balance || 0) < 0 
                    ? 'text-red-600 dark:text-red-400' 
                    : 'text-green-600 dark:text-green-400'
                }`}>
                  ₪{Math.abs(patient.balance || 0).toLocaleString()}
                  {(patient.balance || 0) < 0 && ' חוב'}
                </div>
              </div>
              
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-700/50">
                <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">סה"כ טיפולים</div>
                <div className="text-2xl font-bold text-slate-700 dark:text-slate-200">
                  {patient.total_treatments || 0}
                </div>
              </div>
              
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-700/50">
                <div className="text-xs text-slate-500 dark:text-slate-400 mb-1">ביקור אחרון</div>
                <div className="text-sm font-medium text-slate-700 dark:text-slate-200">
                  {patient.last_visit || 'אין מידע'}
                </div>
              </div>
            </div>
          </section>
          
          {/* Treatment History */}
          <section className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
            <h2 className="text-lg font-bold text-slate-800 dark:text-white mb-4 flex items-center gap-2">
              <FileText size={20} className="text-blue-600"/>
              היסטוריית טיפולים
            </h2>
            
            {patient.treatments && patient.treatments.length > 0 ? (
              <div className="space-y-3">
                {patient.treatments.map((treatment, index) => (
                  <div 
                    key={index}
                    className="p-4 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-600 transition"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="font-medium text-slate-700 dark:text-slate-200">
                          {treatment.type || 'טיפול'}
                        </div>
                        <div className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                          {treatment.date || 'תאריך לא ידוע'}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-slate-700 dark:text-slate-200">
                          ₪{(treatment.price || 0).toLocaleString()}
                        </div>
                        {treatment.tooth && (
                          <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                            שן {treatment.tooth}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-400">
                <FileText size={48} className="mx-auto mb-2 opacity-20"/>
                <p>אין טיפולים רשומים</p>
              </div>
            )}
          </section>
          
          {/* Dental Chart Placeholder */}
          <section className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
            <h2 className="text-lg font-bold text-slate-800 dark:text-white mb-4 flex items-center gap-2">
              <Activity size={20} className="text-blue-600"/>
              מפת שיניים
            </h2>
            
            <div className="text-center py-12 text-slate-400">
              <Activity size={48} className="mx-auto mb-2 opacity-20"/>
              <p>מפת שיניים תוצג כאן</p>
              <p className="text-sm mt-1">בפיתוח...</p>
            </div>
          </section>
          
        </div>
      </div>
    </div>
  )
}
