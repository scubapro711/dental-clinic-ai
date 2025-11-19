import React from 'react';
import { BrainCircuit } from 'lucide-react';

const PatientModal = ({ p, close, onOpenFullFile }) => {
  if (!p) return null;
  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200" onClick={close}>
      <div className="bg-white w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] dark:bg-slate-800 dark:border-slate-700" onClick={e=>e.stopPropagation()}>
        <div className="bg-slate-50 p-4 border-b border-slate-100 flex justify-between items-center dark:bg-slate-900 dark:border-slate-700">
           <div className="flex gap-3 items-center">
             <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-lg dark:bg-blue-900 dark:text-blue-200">{p.name[0]}</div>
             <div>
               <h2 className="font-bold text-slate-800 dark:text-white">{p.name}</h2>
               <div className="text-xs text-slate-500 dark:text-slate-400">תיק מס' {p.id} • {p.type || 'כללי'}</div>
             </div>
           </div>
           <button onClick={close} className="p-1 hover:bg-slate-200 rounded-full transition dark:hover:bg-slate-700 dark:text-slate-400"><X size={20}/></button>
        </div>
        <div className="p-6 overflow-y-auto space-y-4">
          <div className="p-4 bg-purple-50 border border-purple-100 rounded-xl dark:bg-purple-900/20 dark:border-purple-800">
             <h4 className="text-purple-700 font-bold text-sm flex gap-2 mb-2 dark:text-purple-300"><BrainCircuit size={16}/> תובנות AI</h4>
             <p className="text-sm text-slate-700 leading-relaxed dark:text-slate-300">הסוכן זיהה דפוס של הימנעות מטיפולי שורש בעבר. הומלץ להציע הרגעה (גז צחוק) מראש.</p>
          </div>
        </div>
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end gap-2 dark:bg-slate-900 dark:border-slate-700">
           <button onClick={close} className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-white hover:shadow-sm rounded-lg transition dark:text-slate-300 dark:hover:bg-slate-800">סגור</button>
           <button 
             onClick={() => { close(); onOpenFullFile(p.id); }}
             className="px-4 py-2 text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm shadow-blue-200 transition"
           >
             פתח תיק מלא
           </button>
        </div>
      </div>
    </div>
  );
};

export default PatientModal;
