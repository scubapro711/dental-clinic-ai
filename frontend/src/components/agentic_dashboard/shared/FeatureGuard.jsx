import React from 'react';
import { Lock } from 'lucide-react';
import { useSubscription } from '../../../contexts/SubscriptionContext';

const FeatureGuard = ({ feature, children, fallback }) => {
  const { hasFeature } = useSubscription();
  if (hasFeature(feature)) return children;
  
  return fallback || (
    <div className="h-full w-full flex flex-col items-center justify-center bg-slate-50 p-4 text-center border border-dashed border-slate-200 rounded-xl dark:bg-slate-800/50 dark:border-slate-700">
       <Lock className="text-slate-400 mb-2" size={24}/>
       <h4 className="font-bold text-slate-600 text-sm dark:text-slate-300">פיצ'ר נעול</h4>
       <p className="text-xs text-slate-500 mt-1 mb-3 dark:text-slate-400">שדרג לתוכנית מתקדמת כדי לגשת לכלי זה.</p>
       <button className="px-3 py-1.5 bg-blue-600 text-white text-xs font-bold rounded-lg shadow-sm hover:bg-blue-700 transition">שדרג עכשיו</button>
    </div>
  );
};

export default FeatureGuard;
