/**
 * DecisionQueueWidget Component
 * 
 * Displays pending decisions that require human approval.
 * Integrated with real backend API.
 */

import React from 'react';
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { useDecisions } from '../../../hooks/dashboard/useDecisions';
import { PRIORITY_COLORS, AGENT_COLORS } from '../constants';

export const DecisionQueueWidget = () => {
  const { decisions, isLoading, error, approveDecision, rejectDecision } = useDecisions();

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-900 dark:text-red-200">שגיאה בטעינת החלטות</p>
            <p className="text-xs text-red-700 dark:text-red-300 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (decisions.length === 0) {
    return (
      <div className="p-6 text-center">
        <CheckCircle className="w-12 h-12 mx-auto mb-3 text-emerald-500" />
        <p className="text-sm text-slate-600 dark:text-slate-400">אין החלטות ממתינות</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-slate-100 dark:divide-slate-700">
      {decisions.map((decision) => (
        <div key={decision.id} className="p-4 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition">
          {/* Agent Badge */}
          <div className="flex items-center gap-2 mb-2">
            <div className={`w-2 h-2 rounded-full ${AGENT_COLORS[decision.agent_id]}`}></div>
            <span className="text-xs font-medium text-slate-600 dark:text-slate-400">
              {decision.agent_name}
            </span>
          </div>

          {/* Title */}
          <h4 className="font-bold text-sm mb-1 text-slate-900 dark:text-white">
            {decision.title}
          </h4>

          {/* Description */}
          <p className="text-xs text-slate-600 dark:text-slate-400 mb-3">
            {decision.description}
          </p>

          {/* Priority & Confidence */}
          <div className="flex items-center gap-2 mb-3">
            <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${PRIORITY_COLORS[decision.priority]}`}>
              {decision.priority === 'high' ? 'גבוה' : decision.priority === 'medium' ? 'בינוני' : 'נמוך'}
            </span>
            <span className="text-xs text-slate-500 dark:text-slate-400">
              ביטחון: {decision.confidence}%
            </span>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <button
              onClick={() => approveDecision(decision.id)}
              className="flex-1 px-3 py-1.5 bg-emerald-600 text-white rounded-lg text-xs font-bold hover:bg-emerald-700 transition flex items-center justify-center gap-1"
            >
              <CheckCircle size={14} />
              אשר
            </button>
            <button
              onClick={() => rejectDecision(decision.id)}
              className="flex-1 px-3 py-1.5 bg-red-600 text-white rounded-lg text-xs font-bold hover:bg-red-700 transition flex items-center justify-center gap-1"
            >
              <XCircle size={14} />
              דחה
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
