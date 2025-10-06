import React from 'react';
import { cn } from '@/lib/utils';

/**
 * Tooth Component
 * 
 * Represents a single tooth in the odontogram
 * Displays tooth number, status, and allows selection
 */
export default function Tooth({ 
  tooth, 
  isSelected, 
  onSelect, 
  onDoubleClick 
}) {
  const { id, status, conditions = [], treatments = [] } = tooth;

  // Status color mapping
  const statusColors = {
    healthy: 'bg-green-100 border-green-500 hover:bg-green-200',
    watch: 'bg-yellow-100 border-yellow-500 hover:bg-yellow-200',
    needs_treatment: 'bg-orange-100 border-orange-500 hover:bg-orange-200',
    urgent: 'bg-red-100 border-red-500 hover:bg-red-200',
    missing: 'bg-gray-300 border-gray-500 hover:bg-gray-400',
    treated: 'bg-blue-100 border-blue-500 hover:bg-blue-200',
  };

  const statusLabels = {
    healthy: 'בריא',
    watch: 'מעקב',
    needs_treatment: 'דרוש טיפול',
    urgent: 'דחוף',
    missing: 'חסר',
    treated: 'טופל',
  };

  const statusCode = status?.code || 'healthy';
  const colorClass = statusColors[statusCode] || statusColors.healthy;

  // Count active conditions and completed treatments
  const activeConditions = conditions.length;
  const completedTreatments = treatments.filter(t => t.status === 'completed').length;

  const handleClick = (e) => {
    e.preventDefault();
    if (onSelect) {
      onSelect(tooth, e.ctrlKey || e.metaKey);
    }
  };

  const handleDoubleClick = (e) => {
    e.preventDefault();
    if (onDoubleClick) {
      onDoubleClick(tooth);
    }
  };

  return (
    <div
      className={cn(
        "relative flex flex-col items-center justify-center",
        "w-12 h-16 rounded-lg border-2 cursor-pointer transition-all",
        "hover:shadow-lg hover:scale-105",
        colorClass,
        isSelected && "ring-4 ring-blue-500 ring-offset-2 scale-110"
      )}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      title={`שן ${id} - ${statusLabels[statusCode]}`}
    >
      {/* Tooth Number */}
      <div className="text-xs font-bold text-gray-700">
        {id}
      </div>

      {/* Tooth Visual (Simple SVG) */}
      <svg 
        width="24" 
        height="32" 
        viewBox="0 0 24 32" 
        className="my-1"
      >
        {/* Simple tooth shape */}
        <path
          d="M12 2 C8 2, 4 6, 4 12 L4 20 C4 26, 8 30, 12 30 C16 30, 20 26, 20 20 L20 12 C20 6, 16 2, 12 2 Z"
          fill="white"
          stroke="currentColor"
          strokeWidth="1"
          className="text-gray-600"
        />
        {/* Root */}
        <path
          d="M10 28 L10 30 M14 28 L14 30"
          stroke="currentColor"
          strokeWidth="1.5"
          className="text-gray-600"
        />
      </svg>

      {/* Indicators */}
      <div className="absolute top-0 right-0 flex gap-0.5">
        {activeConditions > 0 && (
          <div 
            className="w-3 h-3 rounded-full bg-red-500 text-white text-[8px] flex items-center justify-center font-bold"
            title={`${activeConditions} מצבים פעילים`}
          >
            {activeConditions}
          </div>
        )}
        {completedTreatments > 0 && (
          <div 
            className="w-3 h-3 rounded-full bg-blue-500 text-white text-[8px] flex items-center justify-center font-bold"
            title={`${completedTreatments} טיפולים הושלמו`}
          >
            ✓
          </div>
        )}
      </div>

      {/* Missing tooth indicator */}
      {statusCode === 'missing' && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl text-gray-500">✕</span>
        </div>
      )}
    </div>
  );
}
