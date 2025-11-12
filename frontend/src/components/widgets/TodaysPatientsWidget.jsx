import React, { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar, Phone, MessageSquare, CheckCircle2, Clock, AlertCircle, TrendingUp, Users } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Today's Patients Widget - Alex Agent
 * 
 * Shows today's patient appointments with enriched statistics
 * Now uses ALL available backend data for maximum value
 */
export default function TodaysPatientsWidget({ onChatWithPatient }) {
  const [patients, setPatients] = useState([]);
  const [summary, setSummary] = useState(null);
  const [upcoming, setUpcoming] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchTodaysPatients();
  }, []);

  const fetchTodaysPatients = async () => {
    setIsLoading(true);
    try {
      // Fetch enriched data from Backend API
      const response = await fetch('/api/v1/appointments/today-enriched', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id') || '1'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Set appointments
        setPatients(data.appointments || []);
        
        // Set summary statistics
        setSummary(data.summary || {
          total: 0,
          confirmed: 0,
          pending: 0,
          cancelled: 0,
          first_visits: 0,
          upcoming_week: 0,
          new_patients_this_month: 0
        });
        
        // Set upcoming appointments
        setUpcoming(data.upcoming || []);
      } else {
        // Empty state if API fails
        console.warn('API failed, showing empty state');
        setPatients([]);
        setSummary({
          total: 0,
          confirmed: 0,
          pending: 0,
          cancelled: 0,
          first_visits: 0,
          upcoming_week: 0,
          new_patients_this_month: 0
        });
        setUpcoming([]);
      }
    } catch (error) {
      console.error('Error fetching patients:', error);
      // Empty state on error
      setPatients([]);
      setSummary({
        total: 0,
        confirmed: 0,
        pending: 0,
        cancelled: 0,
        first_visits: 0,
        upcoming_week: 0,
        new_patients_this_month: 0
      });
      setUpcoming([]);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusConfig = (status) => {
    const configs = {
      confirmed: {
        icon: <CheckCircle2 className="w-4 h-4" />,
        color: 'text-green-600 bg-green-100',
        label: 'אושר'
      },
      pending: {
        icon: <Clock className="w-4 h-4" />,
        color: 'text-orange-600 bg-orange-100',
        label: 'ממתין'
      },
      urgent: {
        icon: <AlertCircle className="w-4 h-4" />,
        color: 'text-red-600 bg-red-100',
        label: 'דחוף'
      }
    };
    return configs[status] || configs.confirmed;
  };

  const handleChatClick = (patient) => {
    if (onChatWithPatient) {
      onChatWithPatient(`Tell me about ${patient.patient_name}'s appointment today`);
    }
  };

  return (
    <BaseWidget
      title="מטופלים היום"
      agent="alex"
      icon="👥"
      badge={`${summary?.total || 0} תורים`}
      isLoading={isLoading}
    >
      <div className="space-y-4">
        {/* Summary Statistics - NEW! */}
        {summary && summary.total > 0 && (
          <div className="grid grid-cols-2 gap-2 p-3 bg-blue-50 rounded-lg border-2 border-blue-200">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-600" />
              <div>
                <div className="text-xs text-gray-600">מאושרים</div>
                <div className="text-sm font-semibold">{summary.confirmed}</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-orange-600" />
              <div>
                <div className="text-xs text-gray-600">ממתינים</div>
                <div className="text-sm font-semibold">{summary.pending}</div>
              </div>
            </div>
            {summary.first_visits > 0 && (
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-blue-600" />
                <div>
                  <div className="text-xs text-gray-600">ביקורים ראשונים</div>
                  <div className="text-sm font-semibold">{summary.first_visits}</div>
                </div>
              </div>
            )}
            {summary.upcoming_week > 0 && (
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-purple-600" />
                <div>
                  <div className="text-xs text-gray-600">השבוע הבא</div>
                  <div className="text-sm font-semibold">{summary.upcoming_week}</div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* New Patients This Month - NEW! */}
        {summary && summary.new_patients_this_month > 0 && (
          <div className="p-3 bg-green-50 rounded-lg border-2 border-green-200">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <div className="flex-1">
                <div className="text-xs font-semibold text-green-900">
                  {summary.new_patients_this_month} מטופלים חדשים החודש
                </div>
                <div className="text-xs text-green-700 mt-1">
                  צמיחה מצוינת! 🎉
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Today's Appointments List */}
        <div className="space-y-3">
          {patients.length === 0 ? (
            <div className="text-center text-sm text-gray-500 py-4">
              אין תורים להיום
            </div>
          ) : (
            patients.map((patient) => {
              const statusConfig = getStatusConfig(patient.status);
              
              return (
                <div
                  key={patient.id}
                  className={cn(
                    'rounded-lg border-2 p-3 transition-all duration-200',
                    'hover:shadow-md cursor-pointer',
                    patient.status === 'confirmed' ? 'border-green-200 bg-green-50' :
                    patient.status === 'pending' ? 'border-orange-200 bg-orange-50' :
                    'border-red-200 bg-red-50'
                  )}
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm">{patient.patient_name}</span>
                        {patient.is_first_visit && (
                          <Badge variant="secondary" className="text-xs">
                            ביקור ראשון
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-1 text-xs text-gray-600 mt-1">
                        <Calendar className="w-3 h-3" />
                        <span>{patient.time}</span>
                        <span className="mx-1">•</span>
                        <span>{patient.treatment}</span>
                      </div>
                    </div>
                    <Badge className={cn('text-xs flex items-center gap-1', statusConfig.color)}>
                      {statusConfig.icon}
                      {statusConfig.label}
                    </Badge>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 mt-3">
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1 text-xs h-7"
                      onClick={() => handleChatClick(patient)}
                    >
                      <MessageSquare className="w-3 h-3 mr-1" />
                      שיחה
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1 text-xs h-7"
                    >
                      <Phone className="w-3 h-3 mr-1" />
                      התקשר
                    </Button>
                    {patient.status === 'pending' && (
                      <Button
                        size="sm"
                        className="flex-1 text-xs h-7 bg-green-600 hover:bg-green-700"
                      >
                        <CheckCircle2 className="w-3 h-3 mr-1" />
                        אשר
                      </Button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Upcoming Appointments Preview - NEW! */}
        {upcoming.length > 0 && (
          <div className="pt-3 border-t">
            <div className="text-xs font-semibold text-gray-700 mb-2">
              תורים קרובים:
            </div>
            <div className="space-y-1">
              {upcoming.slice(0, 3).map((apt) => (
                <div key={apt.id} className="flex items-center justify-between text-xs p-2 bg-gray-50 rounded">
                  <span className="text-gray-700">{apt.patient_name}</span>
                  <span className="text-gray-500">{apt.time}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer Actions */}
      {patients.length > 0 && (
        <div className="mt-4 pt-3 border-t space-y-2">
          <Button
            variant="ghost"
            className="w-full text-xs"
            onClick={() => onChatWithPatient && onChatWithPatient('Show me all appointments for today')}
          >
            הצג את כל התורים להיום
          </Button>
          {summary && summary.upcoming_week > 0 && (
            <Button
              variant="ghost"
              className="w-full text-xs"
              onClick={() => onChatWithPatient && onChatWithPatient('Show me appointments for next week')}
            >
              📅 הצג {summary.upcoming_week} תורים השבוע הבא
            </Button>
          )}
        </div>
      )}
    </BaseWidget>
  );
}
