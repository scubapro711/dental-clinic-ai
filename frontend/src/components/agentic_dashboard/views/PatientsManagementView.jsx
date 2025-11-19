import React, { useState } from 'react';
import { Eye, Filter, Search, UserPlus } from 'lucide-react';
import { SUBSCRIPTION_PLANS, AGENTS_ROSTER, MOCK_PATIENTS_DB } from '../../../constants/agenticDashboard';

const PatientsManagementView = ({ onOpenFullFile }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const filteredPatients = MOCK_PATIENTS_DB.filter(p => p.name.includes(searchTerm));

  return (
    <div className="flex-1 overflow-y-auto p-6 bg-slate-50/50 dark:bg-slate-900/50">
       <div className="max-w-5xl mx-auto">
         <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
            <div><h2 className="text-2xl font-bold text-slate-900 tracking-tight dark:text-white">ניהול מטופלים</h2><p className="text-slate-500 text-sm mt-1 dark:text-slate-400">מאגר מטופלים מרכזי (מסונכרן עם Odoo)</p></div>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-bold shadow-sm hover:bg-blue-700 transition flex items-center gap-2"><UserPlus size={18}/> מטופל חדש</button>
         </div>
         <div className="bg-white p-2 rounded-2xl shadow-sm border border-slate-200 mb-6 flex gap-2 items-center dark:bg-slate-800 dark:border-slate-700">
            <div className="relative flex-1"><Search size={18} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400"/><input type="text" placeholder="חיפוש..." className="w-full pl-4 pr-10 py-2.5 bg-transparent border-none focus:ring-0 text-sm dark:text-white" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}/></div>
            <div className="w-px h-8 bg-slate-100 mx-1 dark:bg-slate-700"></div><button className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded-lg transition dark:hover:bg-slate-700 dark:hover:text-slate-300"><Filter size={18}/></button>
         </div>
         <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden dark:bg-slate-800 dark:border-slate-700">
            <table className="w-full text-right text-sm">
               <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 font-medium dark:bg-slate-900/50 dark:border-slate-700 dark:text-slate-400"><tr><th className="px-6 py-4">שם</th><th className="px-6 py-4">סטטוס</th><th className="px-6 py-4">ביטוח</th><th className="px-6 py-4">יתרה</th><th className="px-6 py-4"></th></tr></thead>
               <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                  {filteredPatients.map((p) => (
                     <tr key={p.id} className="group hover:bg-slate-50/80 transition dark:hover:bg-slate-700/50">
                        <td className="px-6 py-4 font-bold text-slate-800 dark:text-white">{p.name}</td>
                        <td className="px-6 py-4"><span className={`px-2 py-0.5 rounded-full text-xs font-bold ${p.status==='active'?'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400':p.status==='debt'?'bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400':'bg-slate-100 dark:bg-slate-700'}`}>{p.status==='active'?'פעיל':p.status==='debt'?'חוב':'לא פעיל'}</span></td>
                        <td className="px-6 py-4 text-slate-600 dark:text-slate-400">{p.insurance_provider}</td>
                        <td className="px-6 py-4 font-mono font-bold dark:text-slate-300">{p.outstanding_balance > 0 ? <span className="text-red-500 dark:text-red-400">₪{p.outstanding_balance}</span> : '—'}</td>
                        <td className="px-6 py-4"><button onClick={() => onOpenFullFile(p.id)} className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition dark:hover:bg-blue-900/30"><Eye size={16}/></button></td>
                     </tr>
                  ))}
               </tbody>
            </table>
         </div>
       </div>
    </div>
  );
};

// --- APP SHELL ---

export default PatientsManagementView;
