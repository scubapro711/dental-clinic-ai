import React, { useState } from 'react';
import { Plus } from 'lucide-react';
import AgentActivityWidget from '../widgets/AgentActivityWidget';
import TodaysPatientsWidget from '../widgets/TodaysPatientsWidget';
import DecisionQueueWidget from '../widgets/DecisionQueueWidget';
import RevenueWidget from '../widgets/RevenueWidget';
import ComplianceAlertsWidget from '../widgets/ComplianceAlertsWidget';
import ClinicalSystemWidget from '../widgets/ClinicalSystemWidget';
import FineTuningWidget from '../widgets/FineTuningWidget';
import WidgetWrapper from '../shared/WidgetWrapper';
import { useAuth } from '../../../contexts/AgenticAuthContext';
import { useAgentWebSocket } from '../../../hooks/useAgentWebSocket';

const DashboardView = ({ onPatientSelect }) => {
  const [availableWidgets, setAvailableWidgets] = useState(['patients', 'decisions', 'revenue', 'compliance', 'activity', 'systems', 'tuning']);
  const removeWidget = (id) => setAvailableWidgets(prev => prev.filter(w => w !== id));
  const addWidget = (id) => !availableWidgets.includes(id) && setAvailableWidgets(prev => [...prev, id]);
  const { organization } = useAuth();
  const { activities } = useAgentWebSocket(true, organization?.id);

  const allWidgetsDef = [
    { id: 'patients', label: 'יומן מטופלים', component: <TodaysPatientsWidget onSelect={onPatientSelect}/> },
    { id: 'decisions', label: 'תור החלטות', component: <DecisionQueueWidget/> },
    { id: 'revenue', label: 'הכנסות', component: <RevenueWidget/>, isWide: true },
    { id: 'compliance', label: 'רגולציה', component: <ComplianceAlertsWidget/> },
    { id: 'activity', label: 'פיד סוכנים', component: <AgentActivityWidget activities={activities}/> },
    { id: 'systems', label: 'תשתיות', component: <ClinicalSystemWidget/> },
    { id: 'tuning', label: 'בקרת סוכנים', component: <FineTuningWidget/> },
  ];

  const hiddenWidgets = allWidgetsDef.filter(w => !availableWidgets.includes(w.id));

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-slate-50/50 relative dark:bg-slate-900/50">
      <div className="px-6 pt-6 pb-4 flex justify-between items-center shrink-0">
        <div><h2 className="text-2xl font-bold text-slate-900 tracking-tight dark:text-white">מרכז שליטה</h2><p className="text-slate-500 text-sm mt-1 dark:text-slate-400">מותאם אישית</p></div>
        {hiddenWidgets.length > 0 && <div className="flex gap-2 flex-wrap justify-end">{hiddenWidgets.map(w => (<button key={w.id} onClick={()=>addWidget(w.id)} className="flex items-center gap-1 bg-white border border-dashed border-slate-300 text-slate-500 text-xs px-3 py-1.5 rounded-lg hover:border-blue-400 hover:text-blue-600 transition dark:bg-slate-800 dark:border-slate-600 dark:text-slate-400"><Plus size={14}/> {w.label}</button>))}</div>}
      </div>
      <div className="flex-1 overflow-y-auto p-6 pt-2 custom-scrollbar">
         <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 auto-rows-[minmax(300px,auto)]">
            {availableWidgets.map(widgetId => {
               const def = allWidgetsDef.find(w => w.id === widgetId);
               if (!def) return null;
               return <WidgetWrapper key={def.id} title={def.label} onClose={()=>removeWidget(def.id)} isWide={def.isWide}>{def.component}</WidgetWrapper>;
            })}
         </div>
      </div>
    </div>
  );
};

export default DashboardView;
