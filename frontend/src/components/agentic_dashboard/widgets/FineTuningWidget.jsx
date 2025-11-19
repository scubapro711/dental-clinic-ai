import React from 'react';
import { GitBranch } from 'lucide-react';
import FeatureGuard from '../shared/FeatureGuard';
import { SUBSCRIPTION_PLANS, AGENTS_ROSTER, MOCK_PATIENTS_DB } from '../../../constants/agenticDashboard';

const FineTuningWidget = () => (
    <FeatureGuard feature="advanced_ai">
      <div className="p-5 h-full flex flex-col">
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-slate-700 font-bold flex gap-2 text-sm dark:text-slate-200"><GitBranch size={18} className="text-indigo-600 dark:text-indigo-400"/> בקרת סוכנים</h3>
          <span className="text-[10px] bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded border border-indigo-100 dark:bg-indigo-900/30 dark:text-indigo-300 dark:border-indigo-800">LangGraph</span>
        </div>
        <div className="flex-grow flex flex-col justify-center">
          <div className="text-xs text-slate-500 mb-2 dark:text-slate-400">נדרש משוב עבור הסוכן <strong>{AGENTS_ROSTER.SARAH.name}</strong>:</div>
          <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 mb-3 relative dark:bg-slate-700/50 dark:border-slate-600">
             <p className="text-xs text-slate-700 italic dark:text-slate-300">"המטופל דיווח על נפיחות. סווג כ-'חירום' ונקבע תור להיום."</p>
          </div>
          <div className="flex gap-2 mt-auto">
             <button className="flex-1 border border-slate-200 hover:bg-slate-50 text-slate-600 py-1.5 rounded-lg text-xs transition font-medium dark:border-slate-600 dark:text-slate-400 dark:hover:bg-slate-700">שגוי</button>
             <button className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-1.5 rounded-lg text-xs transition font-medium shadow-sm shadow-indigo-200">מדויק ✅</button>
          </div>
        </div>
      </div>
    </FeatureGuard>
);

export default FineTuningWidget;
