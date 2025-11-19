/**
 * ClinicalSystemWidget Component
 * 
 * Displays clinical system integration status (Sophia agent)
 */
import React from 'react';
import { Server, RefreshCw } from 'lucide-react';

export const ClinicalSystemWidget = () => {
  const systems = [
    { name: 'Odoo Sync', st: 'ok', label: 'מחובר' }, 
    { name: 'PACS Imaging', st: 'ok', label: 'מחובר' }, 
    { name: 'Insurance GW', st: 'warn', label: 'איטי' }
  ];
  
  return (
    <div className="p-5 h-full flex flex-col">
      <h3 className="text-slate-700 font-bold flex gap-2 text-sm mb-4 dark:text-slate-200">
        <Server size={18} className="text-slate-500"/> תשתיות (Sophia)
      </h3>
      <div className="space-y-3 flex-grow">
        {systems.map((s,i) => (
          <div key={i} className="flex items-center justify-between text-xs p-1.5 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700/50">
            <div className="flex items-center gap-2 text-slate-600 font-medium dark:text-slate-400">
              <div className={`w-2 h-2 rounded-full ${
                s.st==='ok' ? 'bg-emerald-500 shadow-[0_0_5px_rgba(16,185,129,0.4)]' : 'bg-amber-500'
              }`}></div>
              {s.name}
            </div>
            <div className="font-bold text-slate-400 dark:text-slate-500">{s.label}</div>
          </div>
        ))}
      </div>
      <button className="w-full mt-auto flex items-center justify-center gap-1 text-[10px] text-blue-500 hover:underline">
        <RefreshCw size={10}/> רענן חיבורים
      </button>
    </div>
  );
};
