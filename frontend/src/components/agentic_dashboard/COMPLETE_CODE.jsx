import React, { useState, useEffect, useContext, createContext, useRef, useMemo, useCallback } from 'react';
import { 
  LayoutDashboard, 
  Users, 
  Activity, 
  MessageSquare, 
  Bell, 
  Settings, 
  LogOut, 
  ChevronDown, 
  CheckCircle, 
  XCircle, 
  Bot, 
  TrendingUp,
  ShieldAlert,
  BrainCircuit,
  FileText,
  Stethoscope,
  AlertTriangle,
  CreditCard,
  X,
  Server,
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
  Eye,
  GitBranch,
  Database,
  Wifi,
  Menu,
  Search,
  ArrowRight,
  Calendar,
  FileBarChart, 
  Image as ImageIcon,
  Pill,
  HeartPulse,
  UserPlus,
  Filter,
  MoreHorizontal,
  Phone,
  Sparkles,
  Lightbulb,
  Plus,
  LayoutGrid,
  Maximize2,
  Moon,
  Sun,
  History,
  FileImage,
  Syringe,
  ClipboardList,
  Save,
  Send, 
  Minimize2, 
  MessageCircle,
  Mail,
  Smartphone,
  Check,
  Lock,
  Rocket,
  Crown,
  Shield
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// ==========================================
// FILE 1: CONSTANTS & MOCKS (src/data/mocks.js)
// ==========================================

// משתמשי דמו מתוך מסמך האימות (Flow 2)
const MOCK_USERS = {
    'rachel@dentaflow.ai': {
        id: 'usr_demo_admin',
        email: 'rachel@dentaflow.ai',
        full_name: 'Dr. Rachel Cohen',
        role: 'CLINIC_ADMIN',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Rachel'
    },
    'sarah@example.com': {
        id: 'usr_demo_patient',
        email: 'sarah@example.com',
        full_name: 'Sarah Johnson',
        role: 'PATIENT',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah'
    }
};

const MOCK_ORG = {
  id: 'org_denta_flow_01',
  name: 'מרפאת שניידר - תל אביב',
  plan: 'professional'
};

const SUBSCRIPTION_PLANS = {
  starter: { name: 'Starter', price: 1633, features: ['basic_ai', 'patient_portal'], color: 'bg-slate-500' },
  professional: { name: 'Professional', price: 3070, features: ['basic_ai', 'patient_portal', 'advanced_ai', 'sms', 'analytics'], color: 'bg-blue-600' },
  enterprise: { name: 'Enterprise', price: 6141, features: ['all'], color: 'bg-amber-500' }
};

const AGENTS_ROSTER = {
  ALEX: { id: 'alex', name: 'Alex', role: 'Patient Coordinator', color: 'blue' },
  SARAH: { id: 'sarah', name: 'Sarah', role: 'Clinical Operations', color: 'purple' },
  MARCUS: { id: 'marcus', name: 'Marcus', role: 'CFO', color: 'emerald' },
  SOPHIA: { id: 'sophia', name: 'Sophia', role: 'Practice Admin', color: 'orange' },
  HARPER: { id: 'harper', name: 'Harper', role: 'HIPAA Specialist', color: 'red' }
};

const MOCK_PATIENTS_DB = [
  { 
    id: 1, 
    name: 'ישראל ישראלי', 
    email: 'israel@example.com', 
    phone: '050-1234567', 
    birth_date: '1980-01-01', 
    last_visit: '2025-11-19', 
    total_visits: 12, 
    outstanding_balance: 0.00, 
    insurance_provider: 'הראל', 
    status: 'active',
    address: 'רחוב הרצל 10, תל אביב',
    medical_history: {
      allergies: ['פניצילין', 'אגוזים'],
      conditions: ['סוכרת סוג 2'],
      medications: ['מטפורמין 500mg']
    },
    dental_chart: [
      { code: '18', status: 'missing' },
      { code: '16', status: 'filled', material: 'composite', date: '2023-05-10' },
      { code: '24', status: 'healthy' },
      { code: '36', status: 'root_canal', condition: 'good', date: '2024-01-15' },
      { code: '46', status: 'crown', material: 'zirconia' }
    ],
    treatments: [
      { id: 2001, date: '2025-11-19', type: 'root_canal', tooth: '36', desc: 'טיפול שורש - תעלה אחת', doctor: 'ד"ר רון כהן', cost: 1500, status: 'completed' },
      { id: 1998, date: '2025-06-10', type: 'cleaning', tooth: '', desc: 'הסרת אבנית', doctor: 'מיכל לוי (שיננית)', cost: 250, status: 'completed' }
    ],
    documents: [
       { id: 8001, name: 'צילום רנטגן - שן 36', type: 'xray', date: '2025-11-15', url: 'https://placehold.co/150x150/000000/FFF?text=XRAY-36' },
       { id: 8002, name: 'טופס הסכמה לטיפול', type: 'form', date: '2025-11-19', url: '#' }
    ]
  },
  { id: 2, name: 'רבקה מיכאלי', email: 'rivka@example.com', phone: '052-9876543', birth_date: '1992-05-15', last_visit: '2025-10-10', total_visits: 5, outstanding_balance: 450.00, insurance_provider: 'הפניקס', status: 'debt' },
  { id: 3, name: 'דנה רון', email: 'dana@example.com', phone: '054-3334444', birth_date: '1995-11-20', last_visit: '2025-11-01', total_visits: 2, outstanding_balance: 0.00, insurance_provider: 'מכבי שלי', status: 'active' }
];

// ==========================================
// FILE 2: API CLIENT (src/api/client.js)
// ==========================================

const mockApiClient = {
  // Flow 1 & 2: Login Logic
  login: async (email, password) => {
      await new Promise(r => setTimeout(r, 800)); // Simulate network delay
      
      const user = MOCK_USERS[email];
      // Check demo credentials (demo123)
      if (user && password === 'demo123') {
          return {
              access_token: 'mock_access_token_' + Date.now(),
              refresh_token: 'mock_refresh_token_' + Date.now(),
              user: user,
              organization: MOCK_ORG
          };
      }
      throw new Error('AUTHENTICATION_FAILED');
  },

  get: async (endpoint, orgId) => {
    // Flow 3: Security Check
    if (!orgId && !endpoint.includes('/auth')) {
      console.error(`[CRITICAL] 🛑 API Call Blocked! Missing X-Organization-ID header.`);
      throw new Error("Security Violation: Missing Organization Context");
    }
    console.log(`[API] ✅ GET ${endpoint}`);
    
    await new Promise(r => setTimeout(r, 300));

    if (endpoint === '/decisions/pending') {
      return {
        decisions: [
          { 
            id: 'dec-001', 
            agent_id: AGENTS_ROSTER.MARCUS.id,
            agent_name: `${AGENTS_ROSTER.MARCUS.name} (${AGENTS_ROSTER.MARCUS.role})`,
            category: 'billing_approval',
            title: 'אישור הנחה חריגה (15%)', 
            description: 'מטופל וותיק, ביקש הנחה עקב המצב הכלכלי.',
            priority: 'high', 
            confidence: 88 
          },
          { 
            id: 'dec-002', 
            agent_id: AGENTS_ROSTER.SARAH.id,
            agent_name: `${AGENTS_ROSTER.SARAH.name} (${AGENTS_ROSTER.SARAH.role})`,
            category: 'treatment_plan',
            title: 'שינוי תוכנית טיפול', 
            description: 'זוהתה עששת עמוקה יותר מהצפוי בשן 36 בצילום החדש.',
            priority: 'medium', 
            confidence: 92 
          }
        ]
      };
    }
    
    if (endpoint === '/auth/me') {
       // Simulate fetching user from token
       // In real app, decoding JWT happens here or on server
       return { ...MOCK_USERS['rachel@dentaflow.ai'], permissions: ['view_dashboard', 'view_patients', 'view_financials', 'edit_clinical_records'] };
    }

    return { success: true };
  }
};

// ==========================================
// FILE 3: CONTEXTS (src/contexts/...)
// ==========================================

const ToastContext = createContext(null);
const useToast = () => useContext(ToastContext);

const ToastProvider = ({ children }) => {
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

const SubscriptionContext = createContext(null);
const useSubscription = () => {
  const context = useContext(SubscriptionContext);
  if (!context) {
    return { 
      plan: SUBSCRIPTION_PLANS['starter'], 
      hasFeature: () => false 
    };
  }
  return context;
};

const SubscriptionProvider = ({ children, organization }) => {
  const planKey = organization?.plan || 'starter';
  const plan = SUBSCRIPTION_PLANS[planKey];

  const hasFeature = (featureKey) => {
    if (planKey === 'enterprise') return true;
    return plan.features.includes(featureKey);
  };

  return (
    <SubscriptionContext.Provider value={{ plan, hasFeature }}>
      {children}
    </SubscriptionContext.Provider>
  );
};

const AuthContext = createContext(null);
const useAuth = () => useContext(AuthContext);

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [organization, setOrganization] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const { addToast } = useToast();

  useEffect(() => {
    const initAuth = async () => {
      try {
          // Migration Logic (Spec Phase 1)
          const oldKey = localStorage.getItem('organization_id');
          if (oldKey && !localStorage.getItem('current_organization_id')) {
            localStorage.setItem('current_organization_id', oldKey);
          }
          
          const token = localStorage.getItem('access_token');
          if (token) {
             const userData = await mockApiClient.get('/auth/me'); 
             setUser(userData);
             const orgId = localStorage.getItem('current_organization_id') || MOCK_ORG.id;
             setOrganization({ ...MOCK_ORG, id: orgId });
          }
      } catch (error) {
          // Silent fail if not logged in
      } finally {
          setIsLoading(false);
      }
    };
    initAuth();
  }, [addToast]);

  const login = async (email, password) => {
    try {
        const response = await mockApiClient.login(email, password);
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
        localStorage.setItem('current_organization_id', response.organization.id);
        
        setUser(response.user);
        setOrganization(response.organization);
        return true;
    } catch (err) {
        addToast('שגיאה בהתחברות: שם משתמש או סיסמה שגויים', 'error');
        return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_organization_id');
    setUser(null);
    setOrganization(null);
  };

  const value = useMemo(() => ({ user, organization, isLoading, login, logout }), [user, organization, isLoading]);

  return (
    <AuthContext.Provider value={value}>
      {organization ? (
         <SubscriptionProvider organization={organization}>
            {children}
         </SubscriptionProvider>
      ) : (
         children
      )}
    </AuthContext.Provider>
  );
};

// ==========================================
// FILE 4: HOOKS (src/hooks/...)
// ==========================================

const useAgentWebSocket = (enabled, orgId) => {
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

const useDraggable = (initialPosition) => {
  const [position, setPosition] = useState(initialPosition);
  const [isDragging, setIsDragging] = useState(false);
  const ref = useRef(null);
  const dragStartPos = useRef({ x: 0, y: 0 });

  const onMouseDown = (e) => {
    if (e.target.closest('.no-drag')) return;
    setIsDragging(true);
    dragStartPos.current = {
      x: e.clientX - position.x,
      y: e.clientY - position.y
    };
  };

  const onMouseMove = useCallback((e) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragStartPos.current.x,
        y: e.clientY - dragStartPos.current.y
      });
    }
  }, [isDragging]);

  const onMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);
    } else {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, [isDragging, onMouseMove, onMouseUp]);

  return { position, onMouseDown, ref, isDragging };
};


// ==========================================
// FILE 5: SHARED COMPONENTS (src/components/ui/...)
// ==========================================

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

const AddTreatmentModal = ({ isOpen, onClose, onAdd, doctorName }) => {
  if (!isOpen) return null;
  
  const [formData, setFormData] = useState({
    type: 'סתימה',
    tooth: '',
    desc: '',
    cost: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onAdd({
      ...formData,
      doctor: doctorName,
      date: new Date().toISOString().split('T')[0],
      status: 'completed',
      id: Date.now()
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-[60] p-4 animate-in fade-in duration-200" onClick={onClose}>
      <div className="bg-white w-full max-w-md rounded-2xl shadow-2xl p-6 dark:bg-slate-800 dark:border-slate-700" onClick={e=>e.stopPropagation()}>
        <h2 className="text-xl font-bold text-slate-800 mb-4 dark:text-white">הוספת טיפול חדש</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1 dark:text-slate-300">סוג טיפול</label>
            <select 
              className="w-full p-2 border border-slate-300 rounded-lg dark:bg-slate-700 dark:border-slate-600 dark:text-white"
              value={formData.type}
              onChange={e => setFormData({...formData, type: e.target.value})}
            >
              <option>סתימה</option>
              <option>טיפול שורש</option>
              <option>עקירה</option>
              <option>כתר</option>
              <option>הסרת אבנית</option>
              <option>בדיקה</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1 dark:text-slate-300">מספר שן (אופציונלי)</label>
            <input 
              type="text" 
              className="w-full p-2 border border-slate-300 rounded-lg dark:bg-slate-700 dark:border-slate-600 dark:text-white"
              value={formData.tooth}
              onChange={e => setFormData({...formData, tooth: e.target.value})}
              placeholder="לדוגמה: 36"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1 dark:text-slate-300">תיאור הטיפול</label>
            <textarea 
              className="w-full p-2 border border-slate-300 rounded-lg dark:bg-slate-700 dark:border-slate-600 dark:text-white"
              value={formData.desc}
              onChange={e => setFormData({...formData, desc: e.target.value})}
              placeholder="פירוט מה בוצע..."
              rows={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1 dark:text-slate-300">עלות (₪)</label>
            <input 
              type="number" 
              className="w-full p-2 border border-slate-300 rounded-lg dark:bg-slate-700 dark:border-slate-600 dark:text-white"
              value={formData.cost}
              onChange={e => setFormData({...formData, cost: e.target.value})}
            />
          </div>
          <div className="flex gap-2 mt-6">
            <button type="button" onClick={onClose} className="flex-1 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium dark:text-slate-300 dark:hover:bg-slate-700">ביטול</button>
            <button type="submit" className="flex-1 py-2 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 shadow-sm flex justify-center items-center gap-2"><Save size={18}/> שמור טיפול</button>
          </div>
        </form>
      </div>
    </div>
  );
};

const PatientModal = ({ p, close, onOpenFullFile }) => {
  if (!p) return null;
  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200" onClick={close}>
      <div className="bg-white w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] dark:bg-slate-800 dark:border-slate-700" onClick={e=>e.stopPropagation()}>
        <div className="bg-slate-50 p-4 border-b border-slate-100 flex justify-between items-center dark:bg-slate-900 dark:border-slate-700">
           <div className="flex gap-3 items-center">
             <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-lg dark:bg-blue-900 dark:text-blue-200">{p.name[0]}</div>
             <div>
               <h2 className="font-bold text-slate-800 dark:text-white">{p.name}</h2>
               <div className="text-xs text-slate-500 dark:text-slate-400">תיק מס' {p.id} • {p.type || 'כללי'}</div>
             </div>
           </div>
           <button onClick={close} className="p-1 hover:bg-slate-200 rounded-full transition dark:hover:bg-slate-700 dark:text-slate-400"><X size={20}/></button>
        </div>
        <div className="p-6 overflow-y-auto space-y-4">
          <div className="p-4 bg-purple-50 border border-purple-100 rounded-xl dark:bg-purple-900/20 dark:border-purple-800">
             <h4 className="text-purple-700 font-bold text-sm flex gap-2 mb-2 dark:text-purple-300"><BrainCircuit size={16}/> תובנות AI</h4>
             <p className="text-sm text-slate-700 leading-relaxed dark:text-slate-300">הסוכן זיהה דפוס של הימנעות מטיפולי שורש בעבר. הומלץ להציע הרגעה (גז צחוק) מראש.</p>
          </div>
        </div>
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end gap-2 dark:bg-slate-900 dark:border-slate-700">
           <button onClick={close} className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-white hover:shadow-sm rounded-lg transition dark:text-slate-300 dark:hover:bg-slate-800">סגור</button>
           <button 
             onClick={() => { close(); onOpenFullFile(p.id); }}
             className="px-4 py-2 text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm shadow-blue-200 transition"
           >
             פתח תיק מלא
           </button>
        </div>
      </div>
    </div>
  );
};

const SystemPulseHeader = ({ isWsConnected }) => (
  <div className="hidden md:flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-200 dark:bg-slate-800 dark:border-slate-700">
    <div className="relative flex h-2.5 w-2.5">
      <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isWsConnected ? 'bg-emerald-400' : 'bg-red-400'}`}></span>
      <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${isWsConnected ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
    </div>
    <span className="text-xs font-medium text-slate-600 dark:text-slate-300">
       סטטוס מערכת: <span className={isWsConnected ? 'text-emerald-600 font-bold dark:text-emerald-400' : 'text-red-600 font-bold dark:text-red-400'}>{isWsConnected ? 'מחובר' : 'מנותק'}</span>
    </span>
  </div>
);

const WidgetWrapper = ({ children, title, onClose, isWide }) => (
  <div className={`flex flex-col bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden relative group transition-all hover:shadow-md h-full dark:bg-slate-800 dark:border-slate-700 ${isWide ? 'md:col-span-2 xl:col-span-2' : 'col-span-1'}`}>
    <div className="absolute top-2 right-2 z-20 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
       <button onClick={onClose} title="הסר" className="p-1 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded dark:hover:bg-red-900/30"><X size={14}/></button>
    </div>
    <div className="h-full w-full">{children}</div>
  </div>
);

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

const RevenueWidget = () => (
  <div className="p-5 h-full flex flex-col">
    <div className="flex justify-between mb-4"><h3 className="text-slate-500 text-xs font-bold uppercase dark:text-slate-400">הכנסות (Marcus)</h3><div className="text-2xl font-bold text-slate-800 dark:text-white">₪24,500</div></div>
    <div className="flex-grow min-h-[100px]">
       <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={[{v:4000},{v:3000},{v:5000},{v:2780},{v:1890},{v:6390},{v:3490}]}>
             <defs><linearGradient id="cV" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#10b981" stopOpacity={0.1}/><stop offset="95%" stopColor="#10b981" stopOpacity={0}/></linearGradient></defs>
             <Area type="monotone" dataKey="v" stroke="#10b981" strokeWidth={2} fill="url(#cV)" />
          </AreaChart>
       </ResponsiveContainer>
    </div>
  </div>
);

const DecisionQueueWidget = () => {
  const { organization } = useAuth();
  const [items, setItems] = useState([]);
  const { addToast } = useToast();
  useEffect(() => {
    if (organization) mockApiClient.get('/decisions/pending', organization.id).then(res => setItems(res.decisions || []));
  }, [organization]);
  return (
    <div className="p-5 h-full flex flex-col">
      <h3 className="text-slate-700 font-bold flex gap-2 text-sm mb-4 dark:text-slate-200"><BrainCircuit size={18} className="text-purple-600 dark:text-purple-400"/> אישורים</h3>
      <div className="space-y-3 overflow-y-auto custom-scrollbar pr-1 flex-grow">
        {items.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 text-xs"><CheckCircle size={32} className="mb-2 opacity-20"/>הסוכנים מסתדרים לבד 🎉</div>
        ) : (
          items.map(i => (
            <div key={i.id} className="p-3 bg-slate-50 rounded-xl border border-slate-100 hover:border-purple-200 transition-colors dark:bg-slate-700/50 dark:border-slate-600 dark:hover:border-purple-500/50">
              <div className="flex justify-between mb-1"><span className="font-bold text-sm dark:text-slate-200">{i.title}</span><span className="text-[10px] font-mono text-slate-500 bg-white px-1 rounded border border-slate-200 dark:bg-slate-600 dark:border-slate-500 dark:text-slate-300">{i.confidence}% AI</span></div>
              <p className="text-xs text-slate-500 mb-2 line-clamp-2 dark:text-slate-400">{i.description}</p>
              <div className="flex items-center gap-1 mb-3">
                 <div className={`w-4 h-4 rounded-full flex items-center justify-center text-[8px] font-bold text-white ${i.agent_name.includes('Marcus') ? 'bg-emerald-500' : 'bg-purple-500'}`}>{i.agent_name[0]}</div>
                 <span className="text-[10px] text-slate-400 font-medium dark:text-slate-300">{i.agent_name}</span>
              </div>
              <div className="flex gap-2"><button onClick={() => {setItems(p=>p.filter(x=>x.id!==i.id)); addToast('פעולה נדחתה');}} className="flex-1 py-1 rounded border border-slate-200 text-xs hover:bg-slate-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-600">דחה</button><button onClick={() => {setItems(p=>p.filter(x=>x.id!==i.id)); addToast('פעולה אושרה בהצלחה', 'success');}} className="flex-1 py-1 rounded bg-purple-600 text-white text-xs hover:bg-purple-700">אשר</button></div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

const AgentActivityWidget = ({ activities }) => (
  <div className="p-5 h-full flex flex-col">
    <h3 className="text-slate-700 font-bold flex gap-2 text-sm mb-4 dark:text-slate-200"><Bot size={18} className="text-blue-500"/> פיד סוכנים</h3>
    <div className="flex-grow overflow-y-auto custom-scrollbar space-y-3 pr-1">
      {activities.map(l => (
        <div key={l.id} className="flex gap-3 items-start text-xs animate-in slide-in-from-bottom-2">
           <div className={`mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0 ${l.status==='error'?'bg-red-500':l.status==='warning'?'bg-amber-500':l.status==='success'?'bg-emerald-500':'bg-blue-400'}`} />
           <div className="flex-1"><div className="flex justify-between"><span className="font-bold text-slate-700 dark:text-slate-300">{l.agent}</span><span className="text-[10px] text-slate-400 font-mono">{l.time}</span></div><p className="text-slate-500 dark:text-slate-400">{l.msg}</p></div>
        </div>
      ))}
    </div>
  </div>
);

const TodaysPatientsWidget = ({ onSelect }) => {
  const pts = [
    {id:1, time:'09:00', name:'ישראל ישראלי', status:'confirmed', type:'בדיקה'},
    {id:2, time:'10:30', name:'רבקה מיכאלי', status:'in_progress', type:'עקירה'},
    {id:3, time:'11:15', name:'יוסי כהן', status:'scheduled', type:'שיננית'},
  ];
  const getStatusLabel = (s) => ({ 'confirmed': 'מאושר', 'in_progress': 'בטיפול', 'scheduled': 'מתוכנן', 'no_show': 'לא הגיע' }[s] || s);

  return (
    <div className="p-5 h-full flex flex-col">
      <h3 className="text-slate-700 font-bold flex gap-2 text-sm mb-4 dark:text-slate-200"><Users size={18} className="text-indigo-500"/> יומן היום</h3>
      <div className="space-y-2 flex-grow overflow-y-auto">
        {pts.map(p => (
          <div key={p.id} onClick={()=>onSelect(p)} className="flex items-center justify-between p-2.5 rounded-xl hover:bg-indigo-50 cursor-pointer border border-transparent hover:border-indigo-100 dark:hover:bg-slate-700/50 dark:hover:border-slate-600">
            <div className="flex items-center gap-3"><div className="bg-slate-100 text-slate-600 text-xs font-bold px-2 py-1 rounded dark:bg-slate-700 dark:text-slate-300">{p.time}</div><div className="text-sm font-bold text-slate-800 dark:text-slate-200">{p.name}</div></div>
            <div className={`text-[10px] px-2 py-0.5 rounded-full ${p.status==='in_progress'?'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300':'bg-slate-100 dark:bg-slate-700 dark:text-slate-400'}`}>{getStatusLabel(p.status)}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

const ComplianceAlertsWidget = () => (
    <div className="p-5 h-full flex flex-col relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-1.5 h-full bg-red-500 transition-all group-hover:w-2"/>
      <h3 className="text-slate-700 font-bold flex gap-2 text-sm mb-3 dark:text-slate-200"><ShieldAlert size={18} className="text-red-500"/> התראות Harper</h3>
      <div className="space-y-2 flex-grow">
        <div className="flex gap-2 items-start p-2 bg-red-50 rounded-lg border border-red-100 dark:bg-red-900/20 dark:border-red-800/50"><AlertTriangle size={14} className="text-red-500 mt-0.5 flex-shrink-0"/><span className="text-xs text-red-800 font-medium leading-tight dark:text-red-300">חסר טופס סודיות (תיק 302)</span></div>
        <div className="flex gap-2 items-start p-2 bg-red-50 rounded-lg border border-red-100 dark:bg-red-900/20 dark:border-red-800/50"><AlertTriangle size={14} className="text-red-500 mt-0.5 flex-shrink-0"/><span className="text-xs text-red-800 font-medium leading-tight dark:text-red-300">אישור הורים פג תוקף</span></div>
      </div>
      <button className="w-full mt-2 text-xs text-red-600 font-bold hover:bg-red-50 py-2 rounded-lg transition dark:hover:bg-red-900/20">טפל בזה</button>
    </div>
);

const ClinicalSystemWidget = () => {
  const systems = [{ name: 'Odoo Sync', st: 'ok', label: 'מחובר' }, { name: 'PACS Imaging', st: 'ok', label: 'מחובר' }, { name: 'Insurance GW', st: 'warn', label: 'איטי' }];
  return (
    <div className="p-5 h-full flex flex-col">
      <h3 className="text-slate-700 font-bold flex gap-2 text-sm mb-4 dark:text-slate-200"><Server size={18} className="text-slate-500"/> תשתיות (Sophia)</h3>
      <div className="space-y-3 flex-grow">
        {systems.map((s,i) => (
          <div key={i} className="flex items-center justify-between text-xs p-1.5 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700/50">
            <div className="flex items-center gap-2 text-slate-600 font-medium dark:text-slate-400"><div className={`w-2 h-2 rounded-full ${s.st==='ok'?'bg-emerald-500 shadow-[0_0_5px_rgba(16,185,129,0.4)]':'bg-amber-500'}`}></div>{s.name}</div>
            <div className="font-bold text-slate-400 dark:text-slate-500">{s.label}</div>
          </div>
        ))}
      </div>
      <button className="w-full mt-auto flex items-center justify-center gap-1 text-[10px] text-blue-500 hover:underline"><RefreshCw size={10}/> רענן חיבורים</button>
    </div>
  );
};

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

const TransparencyPanelWidget = () => (
    <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-200 h-full flex flex-col relative overflow-hidden dark:bg-slate-800 dark:border-slate-700">
      <div className="flex justify-between items-center mb-4 z-10">
        <h3 className="font-bold flex gap-2 text-slate-700 text-xs uppercase tracking-wider dark:text-slate-300"><Sparkles size={14} className="text-blue-500"/> העוזר החכם</h3>
        <div className="bg-green-50 text-green-600 text-[10px] px-2 py-0.5 rounded-full font-bold flex items-center gap-1 border border-green-100 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800"><span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span> פעיל</div>
      </div>
      <div className="flex-grow overflow-y-auto custom-scrollbar space-y-4 z-10">
         <div className="relative">
             <div className="flex items-center gap-2 mb-1.5"><div className="p-1 bg-blue-50 text-blue-600 rounded-md dark:bg-blue-900/30 dark:text-blue-300"><Stethoscope size={12}/></div><span className="text-xs font-bold text-slate-700 dark:text-slate-300">Sarah (Clinical)</span><span className="text-[10px] text-slate-400 mr-auto">10:42</span></div>
             <div className="bg-slate-50/80 p-2.5 rounded-xl border border-slate-100 text-xs text-slate-600 space-y-1.5 relative dark:bg-slate-700/50 dark:border-slate-600 dark:text-slate-300">
                <p>נבדק צילום רנטגן עבור מטופל 99281.</p>
                <div className="flex items-center gap-1.5 text-amber-700 bg-amber-50 w-fit px-2 py-1 rounded-md border border-amber-100 dark:bg-amber-900/20 dark:text-amber-400 dark:border-amber-800"><AlertTriangle size={10}/><span className="font-medium">חשד לעששת (רביע 3)</span></div>
             </div>
         </div>
         <div className="relative">
             <div className="flex items-center gap-2 mb-1.5"><div className="p-1 bg-purple-50 text-purple-600 rounded-md dark:bg-purple-900/30 dark:text-purple-300"><Calendar size={12}/></div><span className="text-xs font-bold text-slate-700 dark:text-slate-300">Alex (Coordinator)</span><span className="text-[10px] text-slate-400 mr-auto">10:45</span></div>
             <div className="bg-slate-50/80 p-2.5 rounded-xl border border-slate-100 text-xs text-slate-600 relative dark:bg-slate-700/50 dark:border-slate-600 dark:text-slate-300">
                <p>התור של דני בוטל. <span className="font-bold text-purple-600 dark:text-purple-400">סרקתי את היומן ומצאתי 2 חלונות פנויים</span> להקדמת תורים דחופים.</p>
             </div>
         </div>
      </div>
    </div>
);

// --- 6. FULL CLINICAL PATIENT FILE (The "Real Deal") ---

const DentalChart = ({ teeth }) => {
  // Simplified Odontogram Visualization (Can be 3D in Phase 2)
  // Renders 32 teeth in a grid
  const quadrants = [
     [18,17,16,15,14,13,12,11], // UR
     [21,22,23,24,25,26,27,28], // UL
     [48,47,46,45,44,43,42,41], // LR
     [31,32,33,34,35,36,37,38]  // LL
  ];

  const getToothStatus = (code) => {
    const tooth = teeth.find(t => t.code === String(code));
    if (!tooth) return { color: 'bg-white', border: 'border-slate-200' };
    
    switch(tooth.status) {
      case 'missing': return { color: 'bg-slate-100 opacity-50', border: 'border-slate-200', icon: <X size={12} className="text-slate-400"/> };
      case 'root_canal': return { color: 'bg-purple-100', border: 'border-purple-300', icon: <div className="w-1 h-3 bg-purple-500 rounded-full mx-auto"/> };
      case 'crown': return { color: 'bg-amber-100', border: 'border-amber-300', icon: <div className="w-full h-1 bg-amber-500 mt-1"/> };
      case 'filled': return { color: 'bg-blue-50', border: 'border-blue-300', icon: <div className="w-2 h-2 bg-blue-400 rounded-full mx-auto"/> };
      default: return { color: 'bg-white', border: 'border-slate-200' };
    }
  };

  return (
    <div className="bg-slate-50 p-6 rounded-xl border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700">
      <h4 className="text-sm font-bold text-slate-700 mb-4 dark:text-slate-300">מפת שיניים (Odontogram)</h4>
      <div className="grid grid-cols-2 gap-8 max-w-2xl mx-auto">
        {/* Upper Jaw */}
        <div className="flex justify-end gap-1">{quadrants[0].map(t => (
           <Tooth key={t} code={t} {...getToothStatus(t)} />
        ))}</div>
        <div className="flex justify-start gap-1">{quadrants[1].map(t => (
           <Tooth key={t} code={t} {...getToothStatus(t)} />
        ))}</div>
        {/* Lower Jaw */}
        <div className="flex justify-end gap-1">{quadrants[2].map(t => (
           <Tooth key={t} code={t} {...getToothStatus(t)} />
        ))}</div>
        <div className="flex justify-start gap-1">{quadrants[3].map(t => (
           <Tooth key={t} code={t} {...getToothStatus(t)} />
        ))}</div>
      </div>
      <div className="flex gap-4 justify-center mt-6 text-xs text-slate-500">
         <span className="flex items-center gap-1"><div className="w-3 h-3 bg-white border border-slate-300 rounded"/> בריא</span>
         <span className="flex items-center gap-1"><div className="w-3 h-3 bg-blue-50 border border-blue-300 rounded"/> סתימה</span>
         <span className="flex items-center gap-1"><div className="w-3 h-3 bg-purple-100 border border-purple-300 rounded"/> שורש</span>
         <span className="flex items-center gap-1"><div className="w-3 h-3 bg-amber-100 border border-amber-300 rounded"/> כתר</span>
         <span className="flex items-center gap-1"><div className="w-3 h-3 bg-slate-100 border border-slate-200 rounded"/> חסרה</span>
      </div>
    </div>
  );
};

const Tooth = ({ code, color, border, icon }) => (
  <div className={`w-8 h-10 ${color} border ${border} rounded-md flex flex-col items-center justify-center relative transition-all hover:scale-110 cursor-pointer`}>
     <span className="text-[8px] text-slate-400 absolute top-0.5">{code}</span>
     <div className="mt-2">{icon}</div>
  </div>
);

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

// --- LANDING PAGE (New!) ---
// דף נחיתה ומסך לוגין משולב (Flow 1 & 2)
const LandingPage = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoginView, setIsLoginView] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const success = await onLogin(email, password);
    if (!success) {
        setError('שגיאת התחברות: בדוק את הפרטים ונסה שוב.');
    }
  };

  const demoLogin = (role) => {
    if(role === 'admin') {
        setEmail('rachel@dentaflow.ai');
        setPassword('demo123');
    } else {
        setEmail('sarah@example.com');
        setPassword('demo123');
    }
    setIsLoginView(true);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white overflow-y-auto relative">
        {/* Login Overlay */}
        {isLoginView && (
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 max-w-md w-full shadow-2xl relative">
                    <button onClick={() => setIsLoginView(false)} className="absolute top-4 right-4 text-slate-400 hover:text-white"><X/></button>
                    <div className="flex flex-col items-center mb-6">
                        <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center mb-4"><Bot size={24}/></div>
                        <h2 className="text-2xl font-bold">התחברות למערכת</h2>
                        <p className="text-slate-400 text-sm">הזן פרטי כניסה או השתמש במשתמשי דמו</p>
                    </div>

                    {error && <div className="bg-red-500/10 border border-red-500 text-red-400 px-4 py-2 rounded-lg text-sm mb-4">{error}</div>}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm text-slate-300 mb-1">אימייל</label>
                            <input 
                                type="email" 
                                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="user@example.com"
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-slate-300 mb-1">סיסמה</label>
                            <input 
                                type="password" 
                                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                            />
                        </div>
                        <button type="submit" className="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-xl font-bold transition shadow-lg shadow-blue-900/50">התחבר</button>
                    </form>

                    <div className="mt-6 pt-6 border-t border-slate-700">
                        <p className="text-center text-xs text-slate-500 mb-3">כניסה מהירה לדמו (Flow 2):</p>
                        <div className="grid grid-cols-2 gap-3">
                            <button type="button" onClick={() => demoLogin('admin')} className="px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-xs font-medium transition">Admin (Rachel)</button>
                            <button type="button" onClick={() => demoLogin('patient')} className="px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-xs font-medium transition">Patient (Sarah)</button>
                        </div>
                    </div>
                </div>
            </div>
        )}

        {/* Landing Content */}
        <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-16">
            <div className="flex items-center gap-2"><div className="w-8 h-8 bg-blue-600 rounded-lg"></div><span className="font-bold text-xl">DentaFlow</span></div>
            <button onClick={() => setIsLoginView(true)} className="text-sm font-bold text-slate-300 hover:text-white">התחבר</button>
        </div>
        
        <div className="text-center mb-24">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">ניהול מרפאה חכם.<br/>באוטומציה מלאה.</h1>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-8">המערכת הראשונה שמשלבת סוכני AI לניהול תורים, כספים ורגולציה - הכל במקום אחד.</p>
            <button onClick={() => setIsLoginView(true)} className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-full text-lg shadow-lg shadow-blue-900/50 transition transform hover:scale-105 flex items-center gap-2 mx-auto"><Rocket/> התחל</button>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-24">
            <div className="p-8 bg-slate-800/50 border border-slate-700 rounded-3xl hover:border-blue-500/50 transition">
                <Bot className="text-blue-400 mb-4" size={32}/>
                <h3 className="text-xl font-bold mb-2">צוות AI 24/7</h3>
                <p className="text-slate-400">5 סוכנים חכמים שעובדים בשבילך: מתיאום תורים ועד בדיקת ביטוחים.</p>
            </div>
            <div className="p-8 bg-slate-800/50 border border-slate-700 rounded-3xl hover:border-purple-500/50 transition">
                <BrainCircuit className="text-purple-400 mb-4" size={32}/>
                <h3 className="text-xl font-bold mb-2">קבלת החלטות</h3>
                <p className="text-slate-400">המערכת מנתחת נתונים וממליצה על פעולות בזמן אמת.</p>
            </div>
            <div className="p-8 bg-slate-800/50 border border-slate-700 rounded-3xl hover:border-emerald-500/50 transition">
                <Shield className="text-emerald-400 mb-4" size={32}/>
                <h3 className="text-xl font-bold mb-2">בטוח ותואם</h3>
                <p className="text-slate-400">תאימות מלאה ל-HIPAA ורגולציה מקומית. המידע שלך מוגן.</p>
            </div>
        </div>

        <div className="mb-24">
            <h2 className="text-3xl font-bold text-center mb-12">תוכניות ומחירים</h2>
            <div className="grid md:grid-cols-3 gap-6">
                {Object.entries(SUBSCRIPTION_PLANS).map(([key, plan]) => (
                    <div key={key} className={`p-6 rounded-3xl border flex flex-col ${key === 'professional' ? 'bg-slate-800 border-blue-500 relative' : 'bg-slate-800/50 border-slate-700'}`}>
                    {key === 'professional' && <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full">מומלץ</div>}
                    <h3 className="text-lg font-bold mb-2">{plan.name}</h3>
                    <div className="text-3xl font-bold mb-6">₪{plan.price}<span className="text-sm text-slate-500 font-normal">/חודש</span></div>
                    <ul className="space-y-3 mb-8 flex-1">
                        {plan.features.includes('all') ? (
                            <li className="flex items-center gap-2 text-sm text-slate-300"><Check size={16} className="text-emerald-400"/> הכל כלול</li>
                        ) : (
                            <>
                            <li className="flex items-center gap-2 text-sm text-slate-300"><Check size={16} className="text-emerald-400"/> ניהול מטופלים</li>
                            {plan.features.includes('advanced_ai') && <li className="flex items-center gap-2 text-sm text-slate-300"><Check size={16} className="text-emerald-400"/> סוכני AI מתקדמים</li>}
                            {plan.features.includes('analytics') && <li className="flex items-center gap-2 text-sm text-slate-300"><Check size={16} className="text-emerald-400"/> דוחות וניתוחים</li>}
                            </>
                        )}
                    </ul>
                    <button onClick={() => setIsLoginView(true)} className={`w-full py-3 rounded-xl font-bold transition ${key === 'professional' ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'bg-slate-700 hover:bg-slate-600 text-white'}`}>בחר תוכנית</button>
                    </div>
                ))}
            </div>
        </div>
        </div>
    </div>
  );
};

// --- VIEWS (Patients List) ---

const PatientsManagementView = ({ onOpenFullFile }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const filteredPatients = MOCK_PATIENTS_DB.filter(p => p.name.includes(searchTerm));

  return (
    <div className="flex-1 overflow-y-auto p-6 bg-slate-50/50 dark:bg-slate-900/50">
       <div className="max-w-5xl mx-auto">
         <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
            <div><h2 className="text-2xl font-bold text-slate-900 tracking-tight dark:text-white">ניהול מטופלים</h2><p className="text-slate-500 text-sm mt-1 dark:text-slate-400">מאגר מטופלים מרכזי (מסונכרן עם Odoo)</p></div>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-bold shadow-sm hover:bg-blue-700 transition flex items-center gap-2"><UserPlus size={18}/> מטופל חדש</button>
         </div>
         <div className="bg-white p-2 rounded-2xl shadow-sm border border-slate-200 mb-6 flex gap-2 items-center dark:bg-slate-800 dark:border-slate-700">
            <div className="relative flex-1"><Search size={18} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400"/><input type="text" placeholder="חיפוש..." className="w-full pl-4 pr-10 py-2.5 bg-transparent border-none focus:ring-0 text-sm dark:text-white" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}/></div>
            <div className="w-px h-8 bg-slate-100 mx-1 dark:bg-slate-700"></div><button className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded-lg transition dark:hover:bg-slate-700 dark:hover:text-slate-300"><Filter size={18}/></button>
         </div>
         <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden dark:bg-slate-800 dark:border-slate-700">
            <table className="w-full text-right text-sm">
               <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 font-medium dark:bg-slate-900/50 dark:border-slate-700 dark:text-slate-400"><tr><th className="px-6 py-4">שם</th><th className="px-6 py-4">סטטוס</th><th className="px-6 py-4">ביטוח</th><th className="px-6 py-4">יתרה</th><th className="px-6 py-4"></th></tr></thead>
               <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                  {filteredPatients.map((p) => (
                     <tr key={p.id} className="group hover:bg-slate-50/80 transition dark:hover:bg-slate-700/50">
                        <td className="px-6 py-4 font-bold text-slate-800 dark:text-white">{p.name}</td>
                        <td className="px-6 py-4"><span className={`px-2 py-0.5 rounded-full text-xs font-bold ${p.status==='active'?'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400':p.status==='debt'?'bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400':'bg-slate-100 dark:bg-slate-700'}`}>{p.status==='active'?'פעיל':p.status==='debt'?'חוב':'לא פעיל'}</span></td>
                        <td className="px-6 py-4 text-slate-600 dark:text-slate-400">{p.insurance_provider}</td>
                        <td className="px-6 py-4 font-mono font-bold dark:text-slate-300">{p.outstanding_balance > 0 ? <span className="text-red-500 dark:text-red-400">₪{p.outstanding_balance}</span> : '—'}</td>
                        <td className="px-6 py-4"><button onClick={() => onOpenFullFile(p.id)} className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition dark:hover:bg-blue-900/30"><Eye size={16}/></button></td>
                     </tr>
                  ))}
               </tbody>
            </table>
         </div>
       </div>
    </div>
  );
};

// --- APP SHELL ---

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

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <MainAppContent />
      </AuthProvider>
    </ToastProvider>
  );
}