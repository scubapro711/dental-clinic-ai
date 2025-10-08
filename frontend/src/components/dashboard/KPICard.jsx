import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

/**
 * KPI Card Component - כרטיס מדד ביצועים
 * 
 * Props:
 * - title: כותרת (string)
 * - value: ערך ראשי (string | number) - פונט 30px
 * - subtitle: טקסט משני (string) - פונט קטן יותר
 * - trend: מגמה ('up' | 'down')
 * - icon: אייקון (string emoji)
 * - color: צבע ('blue' | 'green' | 'purple' | 'red')
 * 
 * Design:
 * - Large value (30px font)
 * - Subtitle below value (14px font)
 * - Trend indicator (up/down arrow)
 * - Icon in top-right corner
 * - Color-coded border
 */
export default function KPICard({
  title,
  value,
  subtitle,
  trend = 'neutral',
  icon = '📊',
  color = 'blue'
}) {
  const colorClasses = {
    blue: {
      border: 'border-blue-500',
      bg: 'bg-blue-50',
      text: 'text-blue-600',
      icon: 'text-blue-500'
    },
    green: {
      border: 'border-green-500',
      bg: 'bg-green-50',
      text: 'text-green-600',
      icon: 'text-green-500'
    },
    purple: {
      border: 'border-purple-500',
      bg: 'bg-purple-50',
      text: 'text-purple-600',
      icon: 'text-purple-500'
    },
    red: {
      border: 'border-red-500',
      bg: 'bg-red-50',
      text: 'text-red-600',
      icon: 'text-red-500'
    }
  };
  
  const colors = colorClasses[color] || colorClasses.blue;
  
  return (
    <div
      className={`bg-white rounded-lg shadow-md border-r-4 ${colors.border} p-6 hover:shadow-lg transition-shadow`}
    >
      {/* Header - Title and Icon */}
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        <span className="text-3xl">{icon}</span>
      </div>
      
      {/* Main Value - Large Font (30px) */}
      <div className="mb-2">
        <div className={`text-4xl font-bold ${colors.text}`}>
          {value}
        </div>
      </div>
      
      {/* Subtitle and Trend */}
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-500">{subtitle}</span>
        
        {trend !== 'neutral' && (
          <div className={`flex items-center gap-1 ${
            trend === 'up' ? 'text-green-600' : 'text-red-600'
          }`}>
            {trend === 'up' ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
