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

export { ToastProvider, useToast, SubscriptionProvider, useSubscription, AuthProvider, useAuth };
