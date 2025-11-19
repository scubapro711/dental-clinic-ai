import React, { useState } from 'react';
import { Bot, MessageSquare, Send } from 'lucide-react';
import { useSubscription } from '../../../contexts/SubscriptionContext';
import { useDraggable } from '../../../hooks/useDraggable';

const FloatingChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { position, onMouseDown, ref, isDragging } = useDraggable({ x: 20, y: 20 }); 

  const style = {
    position: 'fixed',
    bottom: `${position.y}px`, 
    left: `${position.x}px`,
    zIndex: 9999,
    touchAction: 'none'
  };

  const [messages, setMessages] = useState([
     { id: 1, role: 'assistant', text: 'היי ד"ר כהן, אני אלכס. איך אפשר לעזור היום?', time: '09:00' }
  ]);
  const [input, setInput] = useState('');

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const newMsg = { id: Date.now(), role: 'user', text: input, time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) };
    setMessages(prev => [...prev, newMsg]);
    setInput('');
    
    setTimeout(() => {
       setMessages(prev => [...prev, { id: Date.now()+1, role: 'assistant', text: 'קיבלתי, אני בודק את זה מיד...', time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }]);
    }, 1000);
  };

  // Feature Guard for Chat (Only Pro and above)
  const { hasFeature } = useSubscription();
  if (!hasFeature('advanced_ai')) return null; 

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 left-6 w-14 h-14 bg-blue-600 text-white rounded-full shadow-xl hover:bg-blue-700 transition-all flex items-center justify-center hover:scale-110 z-50"
      >
        <MessageSquare size={28} />
      </button>
    );
  }

  return (
    <div 
      ref={ref}
      style={style}
      className={`bg-white w-80 h-[500px] rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden dark:bg-slate-800 dark:border-slate-700 ${isDragging ? 'cursor-grabbing' : ''}`}
    >
      <div 
        onMouseDown={onMouseDown}
        className="bg-blue-600 p-4 flex justify-between items-center cursor-grab active:cursor-grabbing text-white"
      >
        <div className="flex items-center gap-2">
           <Bot size={20} />
           <div className="font-bold">Alex (Agent)</div>
        </div>
        <div className="flex gap-2">
           <button onClick={() => setIsOpen(false)} className="hover:bg-blue-700 p-1 rounded no-drag"><Minimize2 size={18}/></button>
           <button onClick={() => setIsOpen(false)} className="hover:bg-blue-700 p-1 rounded no-drag"><X size={18}/></button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 dark:bg-slate-900 no-drag custom-scrollbar">
         {messages.map(m => (
            <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
               <div className={`max-w-[80%] p-3 rounded-2xl text-sm ${m.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none dark:bg-slate-700 dark:border-slate-600 dark:text-white'}`}>
                  <div>{m.text}</div>
                  <div className={`text-[10px] mt-1 text-right ${m.role === 'user' ? 'text-blue-100' : 'text-slate-400'}`}>{m.time}</div>
               </div>
            </div>
         ))}
      </div>

      <form onSubmit={handleSend} className="p-3 border-t border-slate-200 bg-white dark:bg-slate-800 dark:border-slate-700 no-drag flex gap-2">
         <input 
           type="text" 
           value={input}
           onChange={e => setInput(e.target.value)}
           placeholder="הקלד הודעה..."
           className="flex-1 bg-slate-100 border-none rounded-full px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-white"
         />
         <button type="submit" className="p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition shadow-sm">
            <Send size={18} />
         </button>
      </form>
    </div>
  );
};

// --- 5. WIDGETS (Dashboard) ---

export default FloatingChatWidget;
