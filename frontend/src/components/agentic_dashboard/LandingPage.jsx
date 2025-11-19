import React, { useState } from 'react';
import { Bot, BrainCircuit, Check, Shield } from 'lucide-react';
import { SUBSCRIPTION_PLANS, AGENTS_ROSTER, MOCK_PATIENTS_DB } from '../../constants/agenticDashboard';

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

export default LandingPage;
