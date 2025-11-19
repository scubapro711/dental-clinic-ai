/**
 * SystemPulseHeader Component
 * 
 * Displays system status and key metrics at the top of the dashboard.
 */

import React from 'react';
import { Activity, Users, Calendar, DollarSign, AlertCircle } from 'lucide-react';
import { useDashboardMetrics } from '../../hooks/dashboard/useDashboardMetrics';

export const SystemPulseHeader = () => {
  const { stats, isLoading, error } = useDashboardMetrics();

  if (isLoading) {
    return (
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-2xl shadow-lg">
        <div className="flex items-center gap-3">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
          <span className="text-sm">טוען נתונים...</span>
        </div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="bg-red-600 text-white p-6 rounded-2xl shadow-lg">
        <div className="flex items-center gap-3">
          <AlertCircle className="w-6 h-6" />
          <div>
            <div className="font-bold">שגיאה בטעינת נתונים</div>
            <div className="text-sm opacity-90">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  const metrics = [
    {
      icon: Users,
      label: 'מטופלים',
      value: stats.total_patients,
      color: 'from-blue-500 to-blue-600'
    },
    {
      icon: Calendar,
      label: 'תורים היום',
      value: stats.appointments_today,
      color: 'from-purple-500 to-purple-600'
    },
    {
      icon: DollarSign,
      label: 'הכנסות החודש',
      value: `₪${(stats.revenue_this_month / 1000).toFixed(0)}K`,
      color: 'from-emerald-500 to-emerald-600'
    },
    {
      icon: AlertCircle,
      label: 'החלטות ממתינות',
      value: stats.pending_decisions,
      color: 'from-orange-500 to-orange-600'
    }
  ];

  return (
    <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-2xl shadow-lg">
      {/* System Status */}
      <div className="flex items-center gap-3 mb-6">
        <div className="relative">
          <Activity className="w-6 h-6" />
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></div>
        </div>
        <div>
          <div className="font-bold text-lg">מערכת פעילה</div>
          <div className="text-sm opacity-90">כל הסוכנים מקוונים</div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {metrics.map((metric, i) => {
          const IconComponent = metric.icon;
          return (
            <div key={i} className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${metric.color} flex items-center justify-center mb-3`}>
                <IconComponent className="w-5 h-5 text-white" />
              </div>
              <div className="text-2xl font-bold mb-1">{metric.value}</div>
              <div className="text-sm opacity-90">{metric.label}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
