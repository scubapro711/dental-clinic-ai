import React, { createContext, useContext, useState, useCallback } from 'react';

const ToastContext = createContext(null);

export const useToast = () => useContext(ToastContext);

export const ToastProvider = ({ children }) => {
   const [toasts, setToasts] = useState([]);
   const addToast = useCallback((message, type = 'info') => {
      const id = Date.now();
      setToasts(prev => [...prev, { id, message, type }]);
      setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3000);
   }, []);
   return (
      <ToastContext.Provider value={{ addToast }}>
         {children}
         <div className="fixed bottom-4 right-4 z-50 space-y-2 pointer-events-none">
            {toasts.map(t => (
               <div key={t.id} className={`p-4 rounded-lg shadow-lg text-white text-sm animate-in slide-in-from-right pointer-events-auto ${t.type === 'error' ? 'bg-red-600' : 'bg-blue-600'}`}>
                  {t.message}
               </div>
            ))}
         </div>
      </ToastContext.Provider>
   );
};
