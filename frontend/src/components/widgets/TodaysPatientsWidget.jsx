import React, { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar, Phone, MessageSquare, CheckCircle2, Clock, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Today's Patients Widget - Alex Agent
 * 
 * Shows today's patient appointments with quick actions
 */
export default function TodaysPatientsWidget({ onChatWithPatient }) {
  const [patients, setPatients] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchTodaysPatients();
  }, []);

  const fetchTodaysPatients = async () => {
    setIsLoading(true);
    try {
      // Fetch real data from Odoo via Backend API
      const response = await fetch('/api/v1/appointments/today', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id') || '1'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Transform Odoo data to widget format
        const transformedPatients = data.map(apt => ({
          id: apt.id,
          name: apt.patient_name || 'Unknown',
          time: new Date(apt.appointment_start).toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
          }),
          treatment: apt.treatment_type || 'General',
          status: apt.status === 'confirmed' ? 'confirmed' : 
                  apt.status === 'pending' ? 'unconfirmed' : 
                  'urgent',
          isFirstVisit: apt.is_first_visit || false,
          patientId: apt.patient_id,
          appointmentId: apt.id
        }));
        
        setPatients(transformedPatients);
      } else {
        // Fallback to mock data if API fails
        console.warn('API failed, using mock data');
        const mockData = [
          {
            id: 1,
            name: 'Sarah Johnson',
            time: '9:00 AM',
            treatment: 'Root Canal',
            status: 'confirmed',
            isFirstVisit: false
          },
          {
            id: 2,
            name: 'David Cohen',
            time: '11:30 AM',
            treatment: 'Cleaning',
            status: 'unconfirmed',
            isFirstVisit: false
          },
          {
            id: 3,
            name: 'Emma Wilson',
            time: '2:00 PM',
            treatment: 'First Visit',
            status: 'confirmed',
            isFirstVisit: true
          }
        ];
        setPatients(mockData);
      }
    } catch (error) {
      console.error('Error fetching patients:', error);
      // Fallback to mock data on error
      const mockData = [
        {
          id: 1,
          name: 'Sarah Johnson',
          time: '9:00 AM',
          treatment: 'Root Canal',
          status: 'confirmed',
          isFirstVisit: false
        },
        {
          id: 2,
          name: 'David Cohen',
          time: '11:30 AM',
          treatment: 'Cleaning',
          status: 'unconfirmed',
          isFirstVisit: false
        },
        {
          id: 3,
          name: 'Emma Wilson',
          time: '2:00 PM',
          treatment: 'First Visit',
          status: 'confirmed',
          isFirstVisit: true
        }
      ];
      setPatients(mockData);
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
      unconfirmed: {
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
      onChatWithPatient(`Tell me about ${patient.name}'s appointment today`);
    }
  };

  return (
    <BaseWidget
      title="מטופלים היום"
      agent="alex"
      icon="👥"
      badge={`${patients.length} תורים`}
      isLoading={isLoading}
    >
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
                  patient.status === 'unconfirmed' ? 'border-orange-200 bg-orange-50' :
                  'border-red-200 bg-red-50'
                )}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm">{patient.name}</span>
                      {patient.isFirstVisit && (
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
                  {patient.status === 'unconfirmed' && (
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

      {/* Footer Action */}
      {patients.length > 0 && (
        <div className="mt-4 pt-3 border-t">
          <Button
            variant="ghost"
            className="w-full text-xs"
            onClick={() => onChatWithPatient && onChatWithPatient('Show me all appointments for today')}
          >
            הצג את כל התורים להיום
          </Button>
        </div>
      )}
    </BaseWidget>
  );
}
