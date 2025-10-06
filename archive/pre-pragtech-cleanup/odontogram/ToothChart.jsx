import React from 'react';
import Tooth from './Tooth';
import { cn } from '@/lib/utils';

/**
 * ToothChart Component
 * 
 * Displays all 32 teeth in proper dental chart layout
 * Organized by quadrants (Upper Right, Upper Left, Lower Left, Lower Right)
 */
export default function ToothChart({ 
  teeth = [], 
  selectedTeeth = [], 
  onToothSelect, 
  onToothDoubleClick 
}) {
  // Organize teeth by quadrants
  const quadrants = {
    1: teeth.filter(t => Math.floor(t.id / 10) === 1).sort((a, b) => b.id - a.id), // Upper Right (18-11)
    2: teeth.filter(t => Math.floor(t.id / 10) === 2).sort((a, b) => a.id - b.id), // Upper Left (21-28)
    3: teeth.filter(t => Math.floor(t.id / 10) === 3).sort((a, b) => a.id - b.id), // Lower Left (31-38)
    4: teeth.filter(t => Math.floor(t.id / 10) === 4).sort((a, b) => b.id - a.id), // Lower Right (48-41)
  };

  const isToothSelected = (toothId) => {
    return selectedTeeth.some(t => t.id === toothId);
  };

  const QuadrantLabel = ({ number, label, position }) => (
    <div className={cn(
      "text-xs font-semibold text-gray-600 px-2 py-1",
      position === 'top' ? 'mb-2' : 'mt-2'
    )}>
      <div className="flex items-center gap-2">
        <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold">
          {number}
        </span>
        <span>{label}</span>
      </div>
    </div>
  );

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* Title */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">מפת שיניים (Odontogram)</h2>
        <p className="text-sm text-gray-600 mt-1">לחץ לבחירה | Ctrl+לחיצה לבחירה מרובה | לחיצה כפולה לפרטים</p>
      </div>

      {/* Upper Jaw */}
      <div className="mb-8">
        <div className="text-center text-sm font-semibold text-gray-500 mb-2">
          לסת עליונה (Upper Jaw)
        </div>
        
        <div className="flex justify-center items-start gap-8">
          {/* Quadrant 1: Upper Right */}
          <div className="flex flex-col items-end">
            <QuadrantLabel number="1" label="ימין עליון" position="top" />
            <div className="flex gap-2 flex-row-reverse">
              {quadrants[1].map(tooth => (
                <Tooth
                  key={tooth.id}
                  tooth={tooth}
                  isSelected={isToothSelected(tooth.id)}
                  onSelect={onToothSelect}
                  onDoubleClick={onToothDoubleClick}
                />
              ))}
            </div>
          </div>

          {/* Center Line */}
          <div className="w-px h-20 bg-gray-400 self-center"></div>

          {/* Quadrant 2: Upper Left */}
          <div className="flex flex-col items-start">
            <QuadrantLabel number="2" label="שמאל עליון" position="top" />
            <div className="flex gap-2">
              {quadrants[2].map(tooth => (
                <Tooth
                  key={tooth.id}
                  tooth={tooth}
                  isSelected={isToothSelected(tooth.id)}
                  onSelect={onToothSelect}
                  onDoubleClick={onToothDoubleClick}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Horizontal Divider */}
      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t-2 border-gray-300"></div>
        </div>
        <div className="relative flex justify-center">
          <span className="px-4 bg-white text-sm text-gray-500 font-semibold">
            קו חיתוך (Bite Line)
          </span>
        </div>
      </div>

      {/* Lower Jaw */}
      <div>
        <div className="text-center text-sm font-semibold text-gray-500 mb-2">
          לסת תחתונה (Lower Jaw)
        </div>
        
        <div className="flex justify-center items-start gap-8">
          {/* Quadrant 4: Lower Right */}
          <div className="flex flex-col items-end">
            <div className="flex gap-2 flex-row-reverse">
              {quadrants[4].map(tooth => (
                <Tooth
                  key={tooth.id}
                  tooth={tooth}
                  isSelected={isToothSelected(tooth.id)}
                  onSelect={onToothSelect}
                  onDoubleClick={onToothDoubleClick}
                />
              ))}
            </div>
            <QuadrantLabel number="4" label="ימין תחתון" position="bottom" />
          </div>

          {/* Center Line */}
          <div className="w-px h-20 bg-gray-400 self-center"></div>

          {/* Quadrant 3: Lower Left */}
          <div className="flex flex-col items-start">
            <div className="flex gap-2">
              {quadrants[3].map(tooth => (
                <Tooth
                  key={tooth.id}
                  tooth={tooth}
                  isSelected={isToothSelected(tooth.id)}
                  onSelect={onToothSelect}
                  onDoubleClick={onToothDoubleClick}
                />
              ))}
            </div>
            <QuadrantLabel number="3" label="שמאל תחתון" position="bottom" />
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <div className="text-sm font-semibold text-gray-700 mb-3">מקרא:</div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-100 border-2 border-green-500"></div>
            <span className="text-xs text-gray-600">בריא</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-yellow-100 border-2 border-yellow-500"></div>
            <span className="text-xs text-gray-600">מעקב</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-orange-100 border-2 border-orange-500"></div>
            <span className="text-xs text-gray-600">דרוש טיפול</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-red-100 border-2 border-red-500"></div>
            <span className="text-xs text-gray-600">דחוף</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-gray-300 border-2 border-gray-500"></div>
            <span className="text-xs text-gray-600">חסר</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-blue-100 border-2 border-blue-500"></div>
            <span className="text-xs text-gray-600">טופל</span>
          </div>
        </div>
      </div>

      {/* Selection Info */}
      {selectedTeeth.length > 0 && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="text-sm text-blue-900">
            <span className="font-semibold">נבחרו:</span> {selectedTeeth.length} שיניים
            {' '}({selectedTeeth.map(t => t.id).join(', ')})
          </div>
        </div>
      )}
    </div>
  );
}
