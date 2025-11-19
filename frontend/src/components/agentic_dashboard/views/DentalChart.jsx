import React from 'react';
import Tooth from '../shared/Tooth';

const DentalChart = ({ teeth }) => {
  // Simplified Odontogram Visualization (Can be 3D in Phase 2)
  // Renders 32 teeth in a grid
  const quadrants = [
     [18,17,16,15,14,13,12,11], // UR
     [21,22,23,24,25,26,27,28], // UL
     [48,47,46,45,44,43,42,41], // LR
     [31,32,33,34,35,36,37,38]  // LL
  ];

  const getToothStatus = (code) => {
    const tooth = teeth.find(t => t.code === String(code));
    if (!tooth) return { color: 'bg-white', border: 'border-slate-200' };
    
    switch(tooth.status) {
      case 'missing': return { color: 'bg-slate-100 opacity-50', border: 'border-slate-200', icon: <X size={12} className="text-slate-400"/> };
      case 'root_canal': return { color: 'bg-purple-100', border: 'border-purple-300', icon: <div className="w-1 h-3 bg-purple-500 rounded-full mx-auto"/> };
      case 'crown': return { color: 'bg-amber-100', border: 'border-amber-300', icon: <div className="w-full h-1 bg-amber-500 mt-1"/> };
      case 'filled': return { color: 'bg-blue-50', border: 'border-blue-300', icon: <div className="w-2 h-2 bg-blue-400 rounded-full mx-auto"/> };
      default: return { color: 'bg-white', border: 'border-slate-200' };
    }
  };

  return (
    <div className="bg-slate-50 p-6 rounded-xl border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700">
      <h4 className="text-sm font-bold text-slate-700 mb-4 dark:text-slate-300">מפת שיניים (Odontogram)</h4>
      <div className="grid grid-cols-2 gap-8 max-w-2xl mx-auto">
        {/* Upper Jaw */}
        <div className="flex justify-end gap-1">{quadrants[0].map(t => (
           <Tooth key={t} code={t} {...getToothStatus(t)} />
        ))}</div>
        <div className="flex justify-start gap-1">{quadrants[1].map(t => (
           <Tooth key={t} code={t} {...getToothStatus(t)} />
        ))}</div>
        {/* Lower Jaw */}
        <div className="flex justify-end gap-1">{quadrants[2].map(t => (
           <Tooth key={t} code={t} {...getToothStatus(t)} />
        ))}</div>
        <div className="flex justify-start gap-1">{quadrants[3].map(t => (
           <Tooth key={t} code={t} {...getToothStatus(t)} />
        ))}</div>
      </div>
      <div className="flex gap-4 justify-center mt-6 text-xs text-slate-500">
         <span className="flex items-center gap-1"><div className="w-3 h-3 bg-white border border-slate-300 rounded"/> בריא</span>
         <span className="flex items-center gap-1"><div className="w-3 h-3 bg-blue-50 border border-blue-300 rounded"/> סתימה</span>
         <span className="flex items-center gap-1"><div className="w-3 h-3 bg-purple-100 border border-purple-300 rounded"/> שורש</span>
         <span className="flex items-center gap-1"><div className="w-3 h-3 bg-amber-100 border border-amber-300 rounded"/> כתר</span>
         <span className="flex items-center gap-1"><div className="w-3 h-3 bg-slate-100 border border-slate-200 rounded"/> חסרה</span>
      </div>
    </div>
  );
};

export default DentalChart;
