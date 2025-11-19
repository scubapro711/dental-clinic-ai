import React, { useState, useEffect } from 'react';
import { Bell, Bot, ChevronDown, Crown, FileBarChart, LayoutDashboard, LogOut, Menu, MessageSquare, Moon, Settings, Sun, Users } from 'lucide-react';
import DashboardView from './views/DashboardView';
import FloatingChatWidget from './shared/FloatingChatWidget';
import FullPatientFile from './views/FullPatientFile';
import LandingPage from './LandingPage';
import PatientModal from './modals/PatientModal';
import PatientsManagementView from './views/PatientsManagementView';
import SystemPulseHeader from './shared/SystemPulseHeader';
import TransparencyPanelWidget from './widgets/TransparencyPanelWidget';
import { useSubscription } from '../../contexts/SubscriptionContext';
import { useAuth } from '../../contexts/AgenticAuthContext';
import { SUBSCRIPTION_PLANS } from '../../constants/agenticDashboard';

const MainAppContent = () => {
  const { organization, user, isLoading, login, logout } = useAuth();
  const { plan } = useSubscription(); // Get current plan
  const isWsConnected = !!organization; 
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [fullFilePatientId, setFullFilePatientId] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
     if (darkMode) {
       document.documentElement.classList.add('dark');
     } else {
       document.documentElement.classList.remove('dark');
     }
  }, [darkMode]);

  if (isLoading) return <div className="h-screen flex items-center justify-center bg-slate-50 text-slate-400 text-sm">טוען מערכת...</div>;

  // Show Landing Page if not logged in
  if (!user) {
     return <LandingPage onLogin={login} />;
  }

  let content;
  if (currentView === 'patient_file_full') {
    content = <FullPatientFile patientId={fullFilePatientId} onBack={() => setCurrentView('dashboard')} />;
  } else if (currentView === 'dashboard') {
    content = <DashboardView onPatientSelect={setSelectedPatient} />;
  } else if (currentView === 'patients') {
    content = <PatientsManagementView onOpenFullFile={(pid) => { setFullFilePatientId(pid); setCurrentView('patient_file_full'); }} />;
  } else {
    content = <div className="flex-1 flex items-center justify-center text-slate-400">מודול זה בפיתוח</div>;
  }

  return (
    <div className={`flex h-screen bg-slate-50/50 text-right font-sans text-slate-800 overflow-hidden transition-colors duration-200 ${darkMode ? 'dark bg-slate-900 text-slate-100' : ''}`} dir="rtl">
      <aside className={`fixed md:static inset-y-0 right-0 w-64 bg-white border-l border-slate-200 z-30 transform transition-transform duration-300 md:transform-none flex flex-col p-4 shadow-2xl md:shadow-none dark:bg-slate-800 dark:border-slate-700 ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        <div className="mb-8 flex items-center gap-3 px-2 mt-2"><div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center text-white font-bold shadow-lg shadow-blue-200 text-xl">D</div><div><h1 className="text-lg font-bold text-slate-800 tracking-tight leading-none dark:text-white">DentaFlow</h1><span className="text-[10px] text-slate-400 font-medium tracking-widest uppercase">סביבת עבודה</span></div></div>
        
        {/* PLAN BADGE */}
        <div className={`mb-6 mx-2 p-2 rounded-lg flex items-center gap-2 text-white text-xs font-bold ${SUBSCRIPTION_PLANS[organization.plan || 'starter'].color}`}>
           <Crown size={14}/>
           <span>{SUBSCRIPTION_PLANS[organization.plan || 'starter'].name} Plan</span>
        </div>

        <nav className="space-y-1">
          {[{id:'dashboard',l:'דשבורד',i:LayoutDashboard},{id:'patients',l:'מטופלים',i:Users},{id:'comm',l:'תקשורת',i:MessageSquare},{id:'agents',l:'סוכני AI',i:Bot},{id:'reports',l:'דוחות',i:FileBarChart}].map(item=>(<button key={item.id} onClick={()=>{setCurrentView(item.id);if(window.innerWidth<768)setSidebarOpen(false);}} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition text-sm font-medium ${currentView===item.id?'bg-blue-50 text-blue-700 shadow-sm dark:bg-blue-900/30 dark:text-blue-300':'text-slate-500 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-700'}`}><item.i size={20} strokeWidth={2}/> {item.l}</button>))}
        </nav>
        
        <div className="mt-auto">
           <div className="mt-4 mb-4 flex-1 min-h-0 overflow-hidden rounded-2xl shadow-inner border border-slate-100 hidden md:block dark:border-slate-700"><TransparencyPanelWidget /></div>
           <div className="pt-4 border-t border-slate-100 dark:border-slate-700">
              <div className="flex justify-between items-center px-2 mb-2">
                 <button onClick={() => setDarkMode(!darkMode)} className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition">
                    {darkMode ? <Sun size={16} className="text-amber-400"/> : <Moon size={16} className="text-slate-400"/>}
                 </button>
                 <div className="flex gap-1">
                    <button className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"><Settings size={16}/></button>
                    <button onClick={logout} className="p-2 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20 transition text-slate-400 hover:text-red-600"><LogOut size={16}/></button>
                 </div>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl flex items-center gap-3 dark:bg-slate-700/50"><div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold">RC</div><div className="flex-1 min-w-0"><div className="text-xs font-bold text-slate-800 truncate dark:text-white">ד"ר רון כהן</div><div className="text-[10px] text-slate-500 dark:text-slate-400">מנהל מערכת</div></div></div>
           </div>
        </div>
      </aside>
      <main className="flex-1 flex flex-col h-screen relative overflow-hidden dark:bg-slate-900">
        {currentView !== 'patient_file_full' && (
          <header className="h-16 px-6 flex items-center justify-between bg-white/80 backdrop-blur-md border-b border-slate-200/60 sticky top-0 z-10 dark:bg-slate-800/80 dark:border-slate-700">
            <div className="flex items-center gap-4">
              <button className="md:hidden p-2 -mr-2 text-slate-500" onClick={() => setSidebarOpen(true)}><Menu/></button>
              <div className="relative group hidden sm:block"><button className="flex items-center gap-2 text-xs font-bold text-slate-600 bg-white border border-slate-200 px-3 py-1.5 rounded-lg shadow-sm hover:border-blue-300 hover:text-blue-600 transition active:scale-95 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-200">{organization?.name} <ChevronDown size={14} className="opacity-50"/></button></div>
              <SystemPulseHeader isWsConnected={isWsConnected} />
            </div>
            <div className="flex items-center gap-3"><button className="w-8 h-8 rounded-full bg-white border border-slate-200 flex items-center justify-center text-slate-500 hover:text-blue-600 hover:border-blue-200 transition shadow-sm relative dark:bg-slate-700 dark:border-slate-600 dark:text-slate-300"><Bell size={16}/><span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-slate-700"></span></button></div>
          </header>
        )}
        {content}
      </main>
      <PatientModal p={selectedPatient} close={() => setSelectedPatient(null)} onOpenFullFile={(pid) => {setFullFilePatientId(pid); setCurrentView('patient_file_full');}} />
      <FloatingChatWidget />
    </div>
  );
};

export default MainAppContent;
