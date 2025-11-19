import React, { useState, useEffect } from 'react';
import { BrainCircuit, CheckCircle } from 'lucide-react';
import { useToast } from '../../../contexts/ToastContext';
import { useAuth } from '../../../contexts/AgenticAuthContext';
import { api } from '../../../api/client';

const DecisionQueueWidget = () => {
  const { organization } = useAuth();
  const [items, setItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const { addToast } = useToast();
  
  useEffect(() => {
    if (organization) {
      loadDecisions();
    }
  }, [organization]);
  
  const loadDecisions = async () => {
    try {
      setIsLoading(true);
      const response = await api.decisionQueue.list({ status: 'pending' });
      setItems(response.data.suggestions || []);
    } catch (error) {
      console.error('Failed to load decisions:', error);
      addToast('שגיאה בטעינת החלטות', 'error');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleApprove = async (id) => {
    try {
      await api.decisionQueue.approve(id);
      setItems(prev => prev.filter(x => x.id !== id));
      addToast('פעולה אושרה בהצלחה', 'success');
    } catch (error) {
      console.error('Failed to approve decision:', error);
      addToast('שגיאה באישור פעולה', 'error');
    }
  };
  
  const handleReject = async (id) => {
    try {
      await api.decisionQueue.reject(id);
      setItems(prev => prev.filter(x => x.id !== id));
      addToast('פעולה נדחתה');
    } catch (error) {
      console.error('Failed to reject decision:', error);
      addToast('שגיאה בדחיית פעולה', 'error');
    }
  };
  
  return (
    <div className="p-5 h-full flex flex-col">
      <h3 className="text-slate-700 font-bold flex gap-2 text-sm mb-4 dark:text-slate-200">
        <BrainCircuit size={18} className="text-purple-600 dark:text-purple-400"/> אישורים
      </h3>
      <div className="space-y-3 overflow-y-auto custom-scrollbar pr-1 flex-grow">
        {isLoading ? (
          <div className="flex items-center justify-center h-full text-slate-400 text-xs">טוען...</div>
        ) : items.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 text-xs">
            <CheckCircle size={32} className="mb-2 opacity-20"/>
            הסוכנים מסתדרים לבד 🎉
          </div>
        ) : (
          items.map(i => (
            <div key={i.id} className="p-3 bg-slate-50 rounded-xl border border-slate-100 hover:border-purple-200 transition-colors dark:bg-slate-700/50 dark:border-slate-600 dark:hover:border-purple-500/50">
              <div className="flex justify-between mb-1">
                <span className="font-bold text-sm dark:text-slate-200">{i.title}</span>
                <span className="text-[10px] font-mono text-slate-500 bg-white px-1 rounded border border-slate-200 dark:bg-slate-600 dark:border-slate-500 dark:text-slate-300">
                  {i.confidence || 95}% AI
                </span>
              </div>
              <p className="text-xs text-slate-500 mb-2 line-clamp-2 dark:text-slate-400">{i.description}</p>
              <div className="flex items-center gap-1 mb-3">
                <div className={`w-4 h-4 rounded-full flex items-center justify-center text-[8px] font-bold text-white ${
                  i.agent_name?.includes('Marcus') ? 'bg-emerald-500' : 'bg-purple-500'
                }`}>
                  {i.agent_name?.[0] || 'A'}
                </div>
                <span className="text-[10px] text-slate-400 font-medium dark:text-slate-300">{i.agent_name || 'AI Agent'}</span>
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={() => handleReject(i.id)} 
                  className="flex-1 py-1 rounded border border-slate-200 text-xs hover:bg-slate-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-600"
                >
                  דחה
                </button>
                <button 
                  onClick={() => handleApprove(i.id)} 
                  className="flex-1 py-1 rounded bg-purple-600 text-white text-xs hover:bg-purple-700"
                >
                  אשר
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default DecisionQueueWidget;
