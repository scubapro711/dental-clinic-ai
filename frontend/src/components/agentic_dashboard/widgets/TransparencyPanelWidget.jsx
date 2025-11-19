/**
 * TransparencyPanelWidget Component
 * 
 * Displays AI assistant activity and reasoning transparency
 */
import React from 'react';
import { Sparkles, Stethoscope, Calendar, AlertTriangle } from 'lucide-react';

export const TransparencyPanelWidget = () => (
  <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-200 h-full flex flex-col relative overflow-hidden dark:bg-slate-800 dark:border-slate-700">
    <div className="flex justify-between items-center mb-4 z-10">
      <h3 className="font-bold flex gap-2 text-slate-700 text-xs uppercase tracking-wider dark:text-slate-300">
        <Sparkles size={14} className="text-blue-500"/> העוזר החכם
      </h3>
      <div className="bg-green-50 text-green-600 text-[10px] px-2 py-0.5 rounded-full font-bold flex items-center gap-1 border border-green-100 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800">
        <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span> פעיל
      </div>
    </div>
    <div className="flex-grow overflow-y-auto custom-scrollbar space-y-4 z-10">
      <div className="relative">
        <div className="flex items-center gap-2 mb-1.5">
          <div className="p-1 bg-blue-50 text-blue-600 rounded-md dark:bg-blue-900/30 dark:text-blue-300">
            <Stethoscope size={12}/>
          </div>
          <span className="text-xs font-bold text-slate-700 dark:text-slate-300">Sarah (Clinical)</span>
          <span className="text-[10px] text-slate-400 mr-auto">10:42</span>
        </div>
        <div className="bg-slate-50/80 p-2.5 rounded-xl border border-slate-100 text-xs text-slate-600 space-y-1.5 relative dark:bg-slate-700/50 dark:border-slate-600 dark:text-slate-300">
          <p>נבדק צילום רנטגן עבור מטופל 99281.</p>
          <div className="flex items-center gap-1.5 text-amber-700 bg-amber-50 w-fit px-2 py-1 rounded-md border border-amber-100 dark:bg-amber-900/20 dark:text-amber-400 dark:border-amber-800">
            <AlertTriangle size={10}/>
            <span className="font-medium">חשד לעששת (רביע 3)</span>
          </div>
        </div>
      </div>
      <div className="relative">
        <div className="flex items-center gap-2 mb-1.5">
          <div className="p-1 bg-purple-50 text-purple-600 rounded-md dark:bg-purple-900/30 dark:text-purple-300">
            <Calendar size={12}/>
          </div>
          <span className="text-xs font-bold text-slate-700 dark:text-slate-300">Alex (Coordinator)</span>
          <span className="text-[10px] text-slate-400 mr-auto">10:45</span>
        </div>
        <div className="bg-slate-50/80 p-2.5 rounded-xl border border-slate-100 text-xs text-slate-600 relative dark:bg-slate-700/50 dark:border-slate-600 dark:text-slate-300">
          <p>התור של דני בוטל. <span className="font-bold text-purple-600 dark:text-purple-400">סרקתי את היומן ומצאתי 2 חלונות פנויים</span> להקדמת תורים דחופים.</p>
        </div>
      </div>
    </div>
  </div>
);
