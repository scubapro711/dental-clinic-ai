import React, { useState } from 'react';
import { Activity, AlertTriangle, ArrowRight, BrainCircuit, Calendar, CheckCircle, FileText, HeartPulse, ImageIcon, Pill, Plus, Users } from 'lucide-react';
import AddTreatmentModal from '../modals/AddTreatmentModal';
import DentalChart from './DentalChart';
import { SUBSCRIPTION_PLANS, AGENTS_ROSTER, MOCK_PATIENTS_DB } from '../../../constants/agenticDashboard';

const FullPatientFile = ({ patientId, onBack }) => {
  // In real app, fetch patient details using ID
  // For now, find in mock DB (which we enhanced)
  const patientData = MOCK_PATIENTS_DB.find(p => p.id === Number(patientId)) || MOCK_PATIENTS_DB[0];
  const age = new Date().getFullYear() - new Date(patientData.birth_date).getFullYear();

  const [activeTab, setActiveTab] = useState('overview'); // overview, clinical, treatments, financial, docs
  
  // Local state for treatments to allow adding new ones
  const [treatments, setTreatments] = useState(patientData.treatments || []);
  const [isTreatmentModalOpen, setIsTreatmentModalOpen] = useState(false);

  const handleAddTreatment = (newTreatment) => {
    setTreatments(prev => [newTreatment, ...prev]);
  };

  const renderContent = () => {
    switch(activeTab) {
      case 'overview':
        return (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-2">
            {/* Medical Alerts */}
            <div className="lg:col-span-2 space-y-6">
               <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 dark:bg-slate-800 dark:border-slate-700">
                  <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2 dark:text-white"><HeartPulse className="text-red-500"/> התראות רפואיות</h3>
                  <div className="flex flex-wrap gap-3">
                     {patientData.medical_history?.allergies.map(a => (
                        <span key={a} className="px-3 py-1 bg-red-50 text-red-700 border border-red-100 rounded-full text-sm font-bold flex items-center gap-2"><AlertTriangle size={14}/> רגישות: {a}</span>
                     ))}
                     {patientData.medical_history?.conditions.map(c => (
                        <span key={c} className="px-3 py-1 bg-amber-50 text-amber-700 border border-amber-100 rounded-full text-sm font-bold flex items-center gap-2"><Activity size={14}/> {c}</span>
                     ))}
                  </div>
                  <div className="mt-6 pt-6 border-t border-slate-100 dark:border-slate-700">
                     <h4 className="text-sm font-bold text-slate-700 mb-3 dark:text-slate-300">תרופות קבועות</h4>
                     <div className="space-y-2">
                        {patientData.medical_history?.medications.map(m => (
                           <div key={m} className="flex items-center gap-2 text-slate-600 text-sm dark:text-slate-400"><Pill size={14}/> {m}</div>
                        ))}
                     </div>
                  </div>
               </div>
            </div>
            {/* Contact Info */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 h-fit dark:bg-slate-800 dark:border-slate-700">
               <h3 className="text-lg font-bold text-slate-800 mb-4 dark:text-white">פרטים אישיים</h3>
               <div className="space-y-4 text-sm">
                  <div><label className="text-slate-400 text-xs">טלפון</label><div className="text-slate-700 font-medium dark:text-slate-300">{patientData.phone}</div></div>
                  <div><label className="text-slate-400 text-xs">כתובת</label><div className="text-slate-700 font-medium dark:text-slate-300">{patientData.address}</div></div>
                  <div><label className="text-slate-400 text-xs">ביטוח</label><div className="text-slate-700 font-medium dark:text-slate-300">{patientData.insurance_provider}</div></div>
                  <div className="pt-4 border-t border-slate-100 dark:border-slate-700">
                     <button className="w-full py-2 bg-slate-100 text-slate-600 rounded-lg font-bold hover:bg-slate-200 transition dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600">עריכת פרטים</button>
                  </div>
               </div>
            </div>
          </div>
        );
      case 'clinical':
        return (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2">
             <DentalChart teeth={patientData.dental_chart || []} />
             <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 dark:bg-slate-800 dark:border-slate-700">
                <h3 className="text-lg font-bold text-slate-800 mb-4 dark:text-white">אבחנות אחרונות (AI)</h3>
                <div className="p-4 bg-purple-50 border border-purple-100 rounded-xl flex gap-4 items-start dark:bg-purple-900/20 dark:border-purple-800">
                   <div className="p-2 bg-purple-100 rounded-lg text-purple-600 dark:bg-purple-800 dark:text-purple-200"><BrainCircuit size={20}/></div>
                   <div>
                      <h4 className="font-bold text-purple-900 text-sm dark:text-purple-300">ניתוח רנטגן אוטומטי (Sarah)</h4>
                      <p className="text-sm text-purple-800/80 mt-1 dark:text-purple-300/80">בצילום מתאריך 15/11 זוהתה עששת התחלתית בשן 24 (Mesial). מומלץ מעקב בעוד 3 חודשים.</p>
                   </div>
                </div>
             </div>
          </div>
        );
      case 'treatments':
        return (
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden animate-in fade-in slide-in-from-bottom-2 dark:bg-slate-800 dark:border-slate-700">
             <table className="w-full text-right text-sm">
               <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 dark:bg-slate-900/50 dark:border-slate-700 dark:text-slate-400">
                 <tr><th className="px-6 py-4">תאריך</th><th className="px-6 py-4">שן</th><th className="px-6 py-4">טיפול</th><th className="px-6 py-4">רופא</th><th className="px-6 py-4">סטטוס</th></tr>
               </thead>
               <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                 {treatments.map(t => (
                   <tr key={t.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/30">
                     <td className="px-6 py-4 text-slate-600 font-mono dark:text-slate-400">{t.date}</td>
                     <td className="px-6 py-4 font-bold text-slate-700 dark:text-slate-300">{t.tooth || '-'}</td>
                     <td className="px-6 py-4 text-slate-800 font-medium dark:text-slate-200">{t.desc}</td>
                     <td className="px-6 py-4 text-slate-500 dark:text-slate-400">{t.doctor}</td>
                     <td className="px-6 py-4"><span className="px-2 py-1 bg-emerald-50 text-emerald-700 rounded-full text-xs font-bold border border-emerald-100 dark:bg-emerald-900/20 dark:text-emerald-400 dark:border-emerald-800">בוצע</span></td>
                   </tr>
                 ))}
               </tbody>
             </table>
             <div className="p-4 border-t border-slate-100 dark:border-slate-700">
                <button onClick={() => setIsTreatmentModalOpen(true)} className="flex items-center gap-2 text-blue-600 font-bold text-sm hover:bg-blue-50 px-4 py-2 rounded-lg transition dark:hover:bg-blue-900/20 dark:text-blue-400"><Plus size={16}/> הוסף טיפול חדש</button>
             </div>
             <AddTreatmentModal isOpen={isTreatmentModalOpen} onClose={() => setIsTreatmentModalOpen(false)} onAdd={handleAddTreatment} doctorName={MOCK_USER.full_name} />
          </div>
        );
      case 'documents':
        return (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 animate-in fade-in slide-in-from-bottom-2">
             {patientData.documents?.map(d => (
               <div key={d.id} className="group relative bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-md transition dark:bg-slate-800 dark:border-slate-700">
                  <div className="aspect-square bg-slate-100 flex items-center justify-center dark:bg-slate-900">
                     {d.type === 'xray' ? <ImageIcon size={32} className="text-slate-400"/> : <FileText size={32} className="text-slate-400"/>}
                  </div>
                  <div className="p-3">
                     <div className="text-sm font-bold text-slate-800 truncate dark:text-white">{d.name}</div>
                     <div className="text-xs text-slate-500 dark:text-slate-400">{d.date}</div>
                  </div>
               </div>
             ))}
             <button className="border-2 border-dashed border-slate-300 rounded-2xl flex flex-col items-center justify-center text-slate-400 gap-2 hover:border-blue-400 hover:text-blue-500 transition min-h-[150px] dark:border-slate-600 dark:hover:border-blue-500">
                <Plus size={32}/>
                <span className="text-sm font-medium">העלאת קובץ</span>
             </button>
          </div>
        );
      default: return null;
    }
  };

  return (
    <div className="flex-1 bg-slate-50 overflow-y-auto dark:bg-slate-900/50">
      {/* Sticky Header */}
      <div className="bg-white border-b border-slate-200 p-6 sticky top-0 z-10 shadow-sm dark:bg-slate-800 dark:border-slate-700">
        <button onClick={onBack} className="text-slate-500 flex items-center gap-2 text-sm hover:text-slate-800 mb-4 font-medium transition dark:text-slate-400 dark:hover:text-white"><ArrowRight size={16}/> חזרה לרשימה</button>
        
        <div className="flex justify-between items-start">
          <div className="flex gap-4">
            <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center font-bold text-3xl shadow-inner dark:bg-blue-900 dark:text-blue-200">
              {patientData.name[0]}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{patientData.name}</h1>
              <div className="text-slate-500 text-sm mt-1 flex gap-3 dark:text-slate-400">
                <span className="flex items-center gap-1"><Users size={14}/> {patientData.id}</span>
                <span className="flex items-center gap-1"><Calendar size={14}/> {age}</span>
                <span className="flex items-center gap-1 text-emerald-600 font-bold dark:text-emerald-400"><CheckCircle size={14}/> מנוי פעיל</span>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
             <button className="bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-bold hover:bg-slate-50 transition dark:bg-slate-700 dark:border-slate-600 dark:text-slate-200 dark:hover:bg-slate-600">צור קשר</button>
             <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-bold shadow-sm hover:bg-blue-700 transition">תור חדש</button>
          </div>
        </div>

        {/* Tabs Navigation */}
        <div className="flex gap-1 mt-8 border-b border-slate-100 dark:border-slate-700 overflow-x-auto">
          {[
            {id:'overview', label:'סקירה', icon:LayoutDashboard},
            {id:'clinical', label:'תיק קליני', icon:Stethoscope},
            {id:'treatments', label:'טיפולים', icon:Syringe},
            {id:'appointments', label:'תורים', icon:Calendar},
            {id:'financial', label:'כספים', icon:CreditCard},
            {id:'documents', label:'מסמכים', icon:FileImage}
          ].map(t => (
            <button 
              key={t.id} 
              onClick={() => setActiveTab(t.id)} 
              className={`pb-3 px-4 text-sm font-bold flex items-center gap-2 border-b-2 transition whitespace-nowrap ${activeTab===t.id ? 'text-blue-600 border-blue-600 dark:text-blue-400 dark:border-blue-400' : 'text-slate-500 border-transparent hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'}`}
            >
              <t.icon size={16}/> {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content Area */}
      <div className="p-6 max-w-6xl mx-auto min-h-[500px]">
         {renderContent()}
      </div>
    </div>
  );
};

// --- DASHBOARD VIEW ---

export default FullPatientFile;
