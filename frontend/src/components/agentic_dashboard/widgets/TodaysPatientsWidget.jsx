import React from 'react';
import { Users } from 'lucide-react';

const TodaysPatientsWidget = ({ onSelect }) => {
  const pts = [
    {id:1, time:'09:00', name:'ישראל ישראלי', status:'confirmed', type:'בדיקה'},
    {id:2, time:'10:30', name:'רבקה מיכאלי', status:'in_progress', type:'עקירה'},
    {id:3, time:'11:15', name:'יוסי כהן', status:'scheduled', type:'שיננית'},
  ];
  const getStatusLabel = (s) => ({ 'confirmed': 'מאושר', 'in_progress': 'בטיפול', 'scheduled': 'מתוכנן', 'no_show': 'לא הגיע' }[s] || s);

  return (
    <div className="p-5 h-full flex flex-col">
      <h3 className="text-slate-700 font-bold flex gap-2 text-sm mb-4 dark:text-slate-200"><Users size={18} className="text-indigo-500"/> יומן היום</h3>
      <div className="space-y-2 flex-grow overflow-y-auto">
        {pts.map(p => (
          <div key={p.id} onClick={()=>onSelect(p)} className="flex items-center justify-between p-2.5 rounded-xl hover:bg-indigo-50 cursor-pointer border border-transparent hover:border-indigo-100 dark:hover:bg-slate-700/50 dark:hover:border-slate-600">
            <div className="flex items-center gap-3"><div className="bg-slate-100 text-slate-600 text-xs font-bold px-2 py-1 rounded dark:bg-slate-700 dark:text-slate-300">{p.time}</div><div className="text-sm font-bold text-slate-800 dark:text-slate-200">{p.name}</div></div>
            <div className={`text-[10px] px-2 py-0.5 rounded-full ${p.status==='in_progress'?'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300':'bg-slate-100 dark:bg-slate-700 dark:text-slate-400'}`}>{getStatusLabel(p.status)}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TodaysPatientsWidget;
