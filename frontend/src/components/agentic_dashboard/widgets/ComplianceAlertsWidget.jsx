import React from 'react';
import { AlertTriangle, ShieldAlert } from 'lucide-react';

const ComplianceAlertsWidget = () => (
    <div className="p-5 h-full flex flex-col relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-1.5 h-full bg-red-500 transition-all group-hover:w-2"/>
      <h3 className="text-slate-700 font-bold flex gap-2 text-sm mb-3 dark:text-slate-200"><ShieldAlert size={18} className="text-red-500"/> התראות Harper</h3>
      <div className="space-y-2 flex-grow">
        <div className="flex gap-2 items-start p-2 bg-red-50 rounded-lg border border-red-100 dark:bg-red-900/20 dark:border-red-800/50"><AlertTriangle size={14} className="text-red-500 mt-0.5 flex-shrink-0"/><span className="text-xs text-red-800 font-medium leading-tight dark:text-red-300">חסר טופס סודיות (תיק 302)</span></div>
        <div className="flex gap-2 items-start p-2 bg-red-50 rounded-lg border border-red-100 dark:bg-red-900/20 dark:border-red-800/50"><AlertTriangle size={14} className="text-red-500 mt-0.5 flex-shrink-0"/><span className="text-xs text-red-800 font-medium leading-tight dark:text-red-300">אישור הורים פג תוקף</span></div>
      </div>
      <button className="w-full mt-2 text-xs text-red-600 font-bold hover:bg-red-50 py-2 rounded-lg transition dark:hover:bg-red-900/20">טפל בזה</button>
    </div>
);

export default ComplianceAlertsWidget;
