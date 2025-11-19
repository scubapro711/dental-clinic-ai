import React from 'react';

const SystemPulseHeader = ({ isWsConnected }) => (
  <div className="hidden md:flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-200 dark:bg-slate-800 dark:border-slate-700">
    <div className="relative flex h-2.5 w-2.5">
      <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isWsConnected ? 'bg-emerald-400' : 'bg-red-400'}`}></span>
      <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${isWsConnected ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
    </div>
    <span className="text-xs font-medium text-slate-600 dark:text-slate-300">
       סטטוס מערכת: <span className={isWsConnected ? 'text-emerald-600 font-bold dark:text-emerald-400' : 'text-red-600 font-bold dark:text-red-400'}>{isWsConnected ? 'מחובר' : 'מנותק'}</span>
    </span>
  </div>
);

export default SystemPulseHeader;
