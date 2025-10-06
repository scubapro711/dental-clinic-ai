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
 * Connected to real OdooClient API
 */
export default function TodaysPatientsWidget({ onChatWithPatient }) {
  const [patients, setPatients] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTodaysPatients();
  }, []);

  const fetchTodaysPatients = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/v1/dashboard/widgets/patients/today', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || 'demo_token'}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Transform API data to widget format
      const transformedData = data.map(appt => ({
        id: appt.id,
        name: appt.name,
        time: new Date(appt.time).toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' }),
        treatment: appt.treatment,
        status: appt.status === 'confirmed' ? 'confirmed' : 'unconfirmed',
        isFirstVisit: appt.isFirstVisit,
        phone: appt.phone
      }));
      
      setPatients(transformedData);
    } catch (error) {
      console.error('Error fetching patients:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      confirmed: { variant: 'default', text: 'אושר', icon: CheckCircle2, color: 'text-green-600' },
      unconfirmed: { variant: 'secondary', text: 'ממתין', icon: Clock, color: 'text-yellow-600' },
    };
    const config = variants[status] || variants.unconfirmed;
    const Icon = config.icon;
    
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className={cn("w-3 h-3", config.color)} />
        <span>{config.text}</span>
      </Badge>
    );
  };

  const handleChat = (patient) => {
    if (onChatWithPatient) {
      onChatWithPatient(`תספר לי על התור של ${patient.name} היום`);
    }
  };

  const handleCall = (patient) => {
    if (patient.phone) {
      window.open(`tel:${patient.phone}`);
    }
  };

  const handleConfirm = (patient) => {
    if (onChatWithPatient) {
      onChatWithPatient(`אשר את התור של ${patient.name}`);
    }
  };

  const handleViewAll = () => {
    if (onChatWithPatient) {
      onChatWithPatient('הצג את כל התורים להיום');
    }
  };

  if (error) {
    return (
      <BaseWidget
        title="מטופלים היום"
        subtitle={`שגיאה בטעינת נתונים`}
        agent="alex"
        icon={Calendar}
      >
        <div className="text-center py-4">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-2" />
          <p className="text-sm text-gray-600">{error}</p>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchTodaysPatients}
            className="mt-2"
          >
            נסה שוב
          </Button>
        </div>
      </BaseWidget>
    );
  }

  return (
    <BaseWidget
      title="מטופלים היום"
      subtitle={`${patients.length} תורים`}
      agent="alex"
      icon={Calendar}
      isLoading={isLoading}
    >
      <div className="space-y-3">
        {patients.map((patient) => (
          <div
            key={patient.id}
            className={cn(
              "p-3 rounded-lg border transition-all",
              patient.isFirstVisit ? "bg-blue-50 border-blue-200" : "bg-white border-gray-200",
              "hover:shadow-md"
            )}
          >
            {/* Patient Header */}
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-gray-900">{patient.name}</h4>
                  {patient.isFirstVisit && (
                    <Badge variant="outline" className="text-xs">ביקור ראשון</Badge>
                  )}
                </div>
                <div className="flex items-center gap-3 mt-1 text-sm text-gray-600">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {patient.time}
                  </span>
                  <span>•</span>
                  <span>{patient.treatment}</span>
                </div>
              </div>
              {getStatusBadge(patient.status)}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 mt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleChat(patient)}
                className="flex-1 flex items-center justify-center gap-1"
              >
                <MessageSquare className="w-3 h-3" />
                שיחה
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleCall(patient)}
                className="flex-1 flex items-center justify-center gap-1"
              >
                <Phone className="w-3 h-3" />
                התקשר
              </Button>
              {patient.status === 'unconfirmed' && (
                <Button
                  variant="default"
                  size="sm"
                  onClick={() => handleConfirm(patient)}
                  className="flex-1 flex items-center justify-center gap-1"
                >
                  <CheckCircle2 className="w-3 h-3" />
                  אשר
                </Button>
              )}
            </div>
          </div>
        ))}

        {patients.length === 0 && !isLoading && (
          <div className="text-center py-8 text-gray-500">
            <Calendar className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>אין תורים היום</p>
          </div>
        )}

        {/* View All Button */}
        {patients.length > 0 && (
          <Button
            variant="outline"
            className="w-full"
            onClick={handleViewAll}
          >
            הצג את כל התורים להיום
          </Button>
        )}
      </div>
    </BaseWidget>
  );
}
