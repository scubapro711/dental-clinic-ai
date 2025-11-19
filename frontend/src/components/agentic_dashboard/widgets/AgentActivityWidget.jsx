/**
 * AgentActivityWidget Component
 * 
 * Displays real-time agent activity feed
 */
import React from 'react';
import { Bot } from 'lucide-react';

export const AgentActivityWidget = ({ activities = [] }) => (
  <div className="p-5 h-full flex flex-col">
    <h3 className="text-slate-700 font-bold flex gap-2 text-sm mb-4 dark:text-slate-200">
      <Bot size={18} className="text-blue-500"/> פיד סוכנים
    </h3>
    <div className="flex-grow overflow-y-auto custom-scrollbar space-y-3 pr-1">
      {activities.length === 0 ? (
        <div className="text-center text-slate-400 text-sm py-8">
          אין פעילות אחרונה
        </div>
      ) : (
        activities.map(l => (
          <div key={l.id} className="flex gap-3 items-start text-xs animate-in slide-in-from-bottom-2">
            <div className={`mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0 ${
              l.status==='error' ? 'bg-red-500' : 
              l.status==='warning' ? 'bg-amber-500' : 
              l.status==='success' ? 'bg-emerald-500' : 
              'bg-blue-400'
            }`} />
            <div className="flex-1">
              <div className="flex justify-between">
                <span className="font-bold text-slate-700 dark:text-slate-300">{l.agent}</span>
                <span className="text-[10px] text-slate-400 font-mono">{l.time}</span>
              </div>
              <p className="text-slate-500 dark:text-slate-400">{l.msg}</p>
            </div>
          </div>
        ))
      )}
    </div>
  </div>
);
