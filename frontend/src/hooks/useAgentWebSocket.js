import { useState, useEffect } from 'react';
import { AGENTS_ROSTER } from '../constants/agenticDashboard';

export const useAgentWebSocket = (enabled, orgId) => {
  const [activities, setActivities] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  
  useEffect(() => {
    if (!enabled || !orgId) return;
    setIsConnected(true);
    const interval = setInterval(() => {
      const msgs = [
        { agent: AGENTS_ROSTER.MARCUS.name, role: AGENTS_ROSTER.MARCUS.role, msg: 'התקבל אישור מחברת הביטוח (הראל)', status: 'success' },
        { agent: AGENTS_ROSTER.ALEX.name, role: AGENTS_ROSTER.ALEX.role, msg: 'דני ביטל תור - שלחתי הצעה למטופל ממתין', status: 'warning' },
        { agent: AGENTS_ROSTER.SARAH.name, role: AGENTS_ROSTER.SARAH.role, msg: 'זיהיתי רגישות לפניצילין בתיק החדש', status: 'error' },
        { agent: AGENTS_ROSTER.HARPER.name, role: AGENTS_ROSTER.HARPER.role, msg: 'בוצעה בדיקת תאימות יומית - תקין', status: 'info' },
      ];
      const m = msgs[Math.floor(Math.random() * msgs.length)];
      setActivities(p => [{id: Date.now(), time: new Date().toLocaleTimeString('he-IL', {hour:'2-digit', minute:'2-digit'}), ...m}, ...p].slice(0, 6));
    }, 4000);

    return () => { clearInterval(interval); setIsConnected(false); };
  }, [enabled, orgId]);

  return { activities, isConnected };
};
