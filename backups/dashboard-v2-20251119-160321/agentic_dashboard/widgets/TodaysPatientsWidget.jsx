/**
 * TodaysPatientsWidget Component
 * 
 * Displays today's appointments.
 * Integrated with real backend API.
 */

import React, { useState, useEffect } from 'react';
import { Calendar, Clock, User, AlertTriangle } from 'lucide-react';
import { dashboardApiClient } from '../../../utils/dashboardApiClient';

const STATUS_COLORS = {
  scheduled: 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400',
  confirmed: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400',
  in_progress: 'bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-400',
  completed: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400',
  cancelled: 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400',
  no_show: 'bg-orange-100 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400'
};

const STATUS_LABELS = {
  scheduled: 'מתוכנן',
  confirmed: 'מאושר',
  in_progress: 'בטיפול',
  completed: 'הושלם',
  cancelled: 'בוטל',
  no_show: 'לא הגיע'
};

export const TodaysPatientsWidget = () => {
  const [appointments, setAppointments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const data = await dashboardApiClient.get('/appointments/today');
        setAppointments(data.appointments || []);
      } catch (err) {
        console.error('Failed to fetch appointments:', err);
        setError(err.response?.data?.detail || 'שגיאה בטעינת תורים');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAppointments();
  }, []);

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-900 dark:text-red-200">שגיאה בטעינת תורים</p>
            <p className="text-xs text-red-700 dark:text-red-300 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (appointments.length === 0) {
    return (
      <div className="p-6 text-center">
        <Calendar className="w-12 h-12 mx-auto mb-3 text-slate-300 dark:text-slate-600" />
        <p className="text-sm text-slate-600 dark:text-slate-400">אין תורים להיום</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-slate-100 dark:divide-slate-700">
      {appointments.map((apt) => (
        <div key={apt.id} className="p-4 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition">
          {/* Time */}
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-slate-400" />
            <span className="text-sm font-bold text-slate-900 dark:text-white">
              {apt.time}
            </span>
          </div>

          {/* Patient */}
          <div className="flex items-center gap-2 mb-2">
            <User className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-700 dark:text-slate-300">
              {apt.patient_name}
            </span>
          </div>

          {/* Type & Status */}
          <div className="flex items-center gap-2">
            <span className="text-xs px-2 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 rounded-full">
              {apt.type === 'checkup' ? 'בדיקה' : 
               apt.type === 'cleaning' ? 'ניקוי' :
               apt.type === 'treatment' ? 'טיפול' :
               apt.type === 'emergency' ? 'חירום' : 'מעקב'}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${STATUS_COLORS[apt.status]}`}>
              {STATUS_LABELS[apt.status]}
            </span>
          </div>

          {/* Doctor */}
          {apt.doctor && (
            <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
              רופא: {apt.doctor}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
