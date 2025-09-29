import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { 
  Bot,
  Shield,
  Eye,
  Users,
  MessageSquare,
  Calendar,
  BarChart3,
  Brain,
  Zap,
  CheckCircle,
  ArrowRight,
  Play,
  Pause,
  Settings,
  Phone,
  MessageCircle,
  Clock,
  TrendingUp,
  Activity,
  Cpu,
  Database,
  Wifi,
  Target,
  Command,
  Monitor,
  Headphones,
  Star,
  Award,
  Globe,
  Lock,
  RefreshCw,
  AlertTriangle,
  Heart,
  Sparkles
} from 'lucide-react';

/**
 * AgenticLandingPage Component
 * 
 * Revolutionary landing page design based on the Agentic UX master plan.
 * Transforms the traditional "dental software" presentation into an 
 * "autonomous AI agent" experience that embodies Mission Control principles.
 * 
 * Key Design Principles:
 * - Agentic UX: Focus on the AI agent, not software features
 * - Mission Control: User delegates goals, agent executes autonomously
 * - Transparency & Trust: Clear explanations and human control
 * - Human Handoff: Seamless transition to human oversight
 * 
 * Colors: #001529 (primary dark), #220 (primary medium), #f5f5f5 (background)
 */
const AgenticLandingPage = () => {
  const [agentStatus, setAgentStatus] = useState('active');
  const [currentDemo, setCurrentDemo] = useState(0);
  const [isAnimating, setIsAnimating] = useState(true);

  // Agent activity simulation
  const [agentActivities, setAgentActivities] = useState([
    { id: 1, action: 'מזמן תור למטופל חדש', status: 'active', time: '14:32' },
    { id: 2, action: 'מעדכן יומן רופא', status: 'completed', time: '14:30' },
    { id: 3, action: 'שולח תזכורת SMS', status: 'completed', time: '14:28' },
    { id: 4, action: 'מנתח נתוני ביצועים', status: 'active', time: '14:25' }
  ]);

  // System scenarios
  const systemScenarios = [
    {
      title: 'זימון תורים אוטומטי',
      description: 'הסוכן מטפל ב-89% מהפניות ללא התערבות',
      visual: 'whatsapp-booking'
    },
    {
      title: 'ניהול יומן חכם',
      description: 'מזהה חורים ביומן ומציע פתרונות',
      visual: 'calendar-optimization'
    },
    {
      title: 'תקשורת מקצועית',
      description: 'מנהל שיחות מורכבות עם מטופלים',
      visual: 'professional-communication'
    }
  ];

  // Animate agent activities
  useEffect(() => {
    const interval = setInterval(() => {
      if (isAnimating) {
        setAgentActivities(prev => {
          const newActivities = [...prev];
          const randomIndex = Math.floor(Math.random() * newActivities.length);
          newActivities[randomIndex] = {
            ...newActivities[randomIndex],
            status: newActivities[randomIndex].status === 'active' ? 'completed' : 'active',
            time: new Date().toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' })
          };
          return newActivities;
        });
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [isAnimating]);

  // Cycle through system scenarios
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentDemo(prev => (prev + 1) % systemScenarios.length);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#f5f5f5]" dir="rtl">
      {/* Hero Section - The Agent Introduction */}
      <section className="relative overflow-hidden bg-gradient-to-br from-[#001529] via-[#220] to-[#001529] text-white">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.05%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%222%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
        
        <div className="relative max-w-7xl mx-auto px-6 py-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Message */}
            <div className="space-y-8">
              <div className="space-y-4">
                <Badge className="bg-white/10 text-white border-white/20 text-lg px-4 py-2">
                  <Sparkles className="w-5 h-5 ml-2" />
                  מהפכה בניהול מרפאות
                </Badge>
                
                <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
                  הכירו את הסוכן
                  <br />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
                    האוטונומי שלכם
                  </span>
                </h1>
                
                <p className="text-xl lg:text-2xl text-blue-100 leading-relaxed">
                  הסוכן החכם שמנהל את המרפאה שלכם 24/7
                  <br />
                  <strong>אתם קובעים את המטרות - הוא דואג לביצוע</strong>
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <Button size="lg" className="bg-white text-[#001529] hover:bg-blue-50 text-lg px-8 py-4">
                  <Play className="w-5 h-5 ml-2" />
                  צפו במערכת חיה
                </Button>
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10 text-lg px-8 py-4">
                  <Shield className="w-5 h-5 ml-2" />
                  מרכז השליטה והבקרה
                </Button>
              </div>

              {/* Trust Indicators */}
              <div className="flex items-center gap-6 pt-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span className="text-blue-100">שקיפות מלאה</span>
                </div>
                <div className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-blue-400" />
                  <span className="text-blue-100">שליטה אנושית</span>
                </div>
                <div className="flex items-center gap-2">
                  <Eye className="w-5 h-5 text-cyan-400" />
                  <span className="text-blue-100">מעקב בזמן אמת</span>
                </div>
              </div>
            </div>

            {/* Right Column - Agent Visualization */}
            <div className="relative">
              <div className="relative bg-white/10 backdrop-blur-sm rounded-3xl p-8 border border-white/20">
                {/* Central Agent */}
                <div className="flex flex-col items-center space-y-6">
                  <div className="relative">
                    <div className="w-24 h-24 bg-gradient-to-br from-blue-400 to-cyan-400 rounded-full flex items-center justify-center shadow-2xl">
                      <Bot className="w-12 h-12 text-white" />
                    </div>
                    <div className="absolute -top-2 -right-2">
                      <div className={cn(
                        "w-6 h-6 rounded-full flex items-center justify-center",
                        agentStatus === 'active' ? "bg-green-500 animate-pulse" : "bg-yellow-500"
                      )}>
                        <div className="w-2 h-2 bg-white rounded-full" />
                      </div>
                    </div>
                  </div>

                  <div className="text-center">
                    <h3 className="text-xl font-bold text-white">הסוכן הדיגיטלי שלכם</h3>
                    <p className="text-blue-200">פעיל ומנהל את המרפאה כרגע</p>
                  </div>

                  {/* Activity Lines */}
                  <div className="grid grid-cols-2 gap-4 w-full">
                    {agentActivities.map((activity, index) => (
                      <div 
                        key={activity.id}
                        className="bg-white/5 backdrop-blur-sm rounded-lg p-3 border border-white/10"
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <div className={cn(
                            "w-2 h-2 rounded-full",
                            activity.status === 'active' ? "bg-green-400 animate-pulse" : "bg-blue-400"
                          )} />
                          <span className="text-xs text-blue-200">{activity.time}</span>
                        </div>
                        <p className="text-sm text-white font-medium">{activity.action}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Floating Mission Control Preview */}
              <div className="absolute -bottom-4 -left-4 bg-white rounded-xl p-4 shadow-2xl border border-gray-200 max-w-xs">
                <div className="flex items-center gap-2 mb-2">
                  <Monitor className="w-4 h-4 text-[#001529]" />
                  <span className="text-sm font-medium text-[#001529]">מרכז השליטה</span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-600">תורים היום</span>
                    <span className="font-medium text-[#001529]">23</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-600">שיחות פעילות</span>
                    <span className="font-medium text-green-600">5</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1">
                    <div className="bg-green-500 h-1 rounded-full w-3/4"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works - 3 Steps */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-[#001529] mb-4">
              איך זה עובד? תהליך פשוט בשלושה שלבים
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              מעבר מניהול ידני למערכת אוטונומית מלאה תחת השליטה שלכם
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Step 1: Delegate */}
            <Card className="relative overflow-hidden border-2 border-blue-100 hover:border-blue-300 transition-all duration-300 hover:shadow-xl">
              <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-bl-3xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">1</span>
              </div>
              <CardHeader className="pt-20">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                  <Target className="w-8 h-8 text-blue-600" />
                </div>
                <CardTitle className="text-2xl text-[#001529]">הגדירו מטרות</CardTitle>
                <p className="text-gray-600">אתם קובעים את המטרות</p>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-6">
                  הגדירו מטרות-על פשוטות: "ודא שאין חורים ביומן", "שמור על שביעות רצון מטופלים גבוהה"
                </p>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-sm">מטרה: מלא יומן ב-95%</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-sm">מטרה: זמן תגובה &lt; 30 שניות</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-sm">מטרה: שביעות רצון &gt; 90%</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Step 2: Execute */}
            <Card className="relative overflow-hidden border-2 border-green-100 hover:border-green-300 transition-all duration-300 hover:shadow-xl">
              <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-bl-3xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">2</span>
              </div>
              <CardHeader className="pt-20">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                  <Zap className="w-8 h-8 text-green-600" />
                </div>
                <CardTitle className="text-2xl text-[#001529]">הסוכן פועל</CardTitle>
                <p className="text-gray-600">ביצוע אוטונומי של משימות</p>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-6">
                  הסוכן מבצע מאות משימות יומיות: מתקשר עם מטופלים, מזמן תורים, מנהל את היומן, מכין דיווחים
                </p>
                <div className="space-y-3">
                  {[
                    { icon: MessageCircle, text: 'מנהל 50+ שיחות יומיות', color: 'text-green-600' },
                    { icon: Calendar, text: 'מזמן ומעדכן תורים', color: 'text-blue-600' },
                    { icon: BarChart3, text: 'מכין דיווחי ביצועים', color: 'text-purple-600' }
                  ].map((item, index) => (
                    <div key={index} className="flex items-center gap-3">
                      <item.icon className={cn("w-5 h-5", item.color)} />
                      <span className="text-sm text-gray-700">{item.text}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Step 3: Control */}
            <Card className="relative overflow-hidden border-2 border-purple-100 hover:border-purple-300 transition-all duration-300 hover:shadow-xl">
              <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-bl-3xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">3</span>
              </div>
              <CardHeader className="pt-20">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                  <Command className="w-8 h-8 text-purple-600" />
                </div>
                <CardTitle className="text-2xl text-[#001529]">אתם בשליטה</CardTitle>
                <p className="text-gray-600">מרכז השליטה והבקרה</p>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-6">
                  עקבו אחר כל פעולה, קבלו הסברים, התערבו בכל רגע, קחו שליטה מלאה כשצריך
                </p>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">סטטוס הסוכן</span>
                    <Badge className="bg-green-100 text-green-800">פעיל</Badge>
                  </div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">משימות פעילות</span>
                    <span className="text-sm font-medium">3</span>
                  </div>
                  <Button size="sm" className="w-full bg-[#001529] hover:bg-[#220]">
                    <Shield className="w-4 h-4 ml-2" />
                    קח שליטה
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Agent Capabilities - Not Features */}
      <section className="py-20 bg-[#f5f5f5]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-[#001529] mb-4">
              מה הסוכן עושה עבורכם?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              במקום לנהל תוכנה, הסוכן מנהל את המרפאה עבורכם
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Autonomous Appointment Management */}
            <Card className="p-8 hover:shadow-xl transition-all duration-300 border-r-4 border-r-blue-500">
              <div className="flex items-start gap-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <Calendar className="w-8 h-8 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-[#001529] mb-3">
                    🤖 ניהול תורים אוטונומי
                  </h3>
                  <p className="text-gray-700 mb-4 text-lg">
                    הסוכן מזמן, מאשר ומזכיר על תורים באופן אוטונומי. מטפל בביטולים ושינויים ללא התערבותכם.
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-gray-600">זימון תורים חכם לפי זמינות</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-gray-600">תזכורות אוטומטיות ב-SMS ו-WhatsApp</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-gray-600">ניהול רשימת המתנה ואופטימיזציה</span>
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Smart Patient Communication */}
            <Card className="p-8 hover:shadow-xl transition-all duration-300 border-r-4 border-r-green-500">
              <div className="flex items-start gap-6">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <MessageSquare className="w-8 h-8 text-green-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-[#001529] mb-3">
                    💬 תקשורת חכמה עם מטופלים
                  </h3>
                  <p className="text-gray-700 mb-4 text-lg">
                    מנהל שיחות WhatsApp וטלפון מקצועיות. עונה על שאלות נפוצות ומעביר מקרים מורכבים אליכם.
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-gray-600">מענה מיידי 24/7 לפניות מטופלים</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-gray-600">טיפול בשאלות נפוצות באופן אוטונומי</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-gray-600">העברה חלקה למטפל אנושי בעת הצורך</span>
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Analytics & Reporting */}
            <Card className="p-8 hover:shadow-xl transition-all duration-300 border-r-4 border-r-purple-500">
              <div className="flex items-start gap-6">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <BarChart3 className="w-8 h-8 text-purple-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-[#001529] mb-3">
                    📊 אנליטיקה ודיווחים
                  </h3>
                  <p className="text-gray-700 mb-4 text-lg">
                    מכין דיווחי ביצועים מפורטים, מזהה מגמות ומציע שיפורים לאופטימיזציה של המרפאה.
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-gray-600">דיווחים יומיים, שבועיים וחודשיים</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-gray-600">זיהוי מגמות והזדמנויות לשיפור</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-gray-600">המלצות מותאמות אישית</span>
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Smart Knowledge Management */}
            <Card className="p-8 hover:shadow-xl transition-all duration-300 border-r-4 border-r-orange-500">
              <div className="flex items-start gap-6">
                <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <Brain className="w-8 h-8 text-orange-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-[#001529] mb-3">
                    🔧 ניהול ידע חכם
                  </h3>
                  <p className="text-gray-700 mb-4 text-lg">
                    לומד מהתנהגות המרפאה ומשתפר כל הזמן. מנהל בסיס ידע מתעדכן של שאלות ותשובות.
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-gray-600">למידה מתמשכת מאינטראקציות</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-gray-600">עדכון אוטומטי של בסיס הידע</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-gray-600">התאמה לסגנון המרפאה</span>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Trust & Transparency */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-[#001529] mb-4">
              שקיפות מלאה - אתם תמיד יודעים מה קורה
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              בניית אמון דרך שקיפות מלאה ושליטה אנושית מתמשכת
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Trust Principles */}
            <div className="space-y-8">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <Eye className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-[#001529] mb-2">הסברים לכל פעולה</h3>
                  <p className="text-gray-700">
                    הסוכן מסביר למה הוא עושה כל פעולה. תמיד תדעו מה הרציונל מאחורי כל החלטה.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <Shield className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-[#001529] mb-2">שליטה מלאה</h3>
                  <p className="text-gray-700">
                    אפשרות לעצור, לשנות או לקחת שליטה בכל רגע. הסוכן עובד עבורכם, לא במקומכם.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <Activity className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-[#001529] mb-2">מעקב בזמן אמת</h3>
                  <p className="text-gray-700">
                    רואים בדיוק מה הסוכן עושה כרגע, איזה משימות הוא מבצע ומה התוצאות.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <Headphones className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-[#001529] mb-2">Human Handoff</h3>
                  <p className="text-gray-700">
                    מעבר חלק לטיפול אנושי כשצריך. הסוכן יודע מתי להעביר אליכם את השליטה.
                  </p>
                </div>
              </div>
            </div>

            {/* Mission Control Preview */}
            <div className="relative">
              <Card className="p-6 shadow-2xl border-2 border-[#001529]/10">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-bold text-[#001529]">מרכז השליטה והבקרה</h3>
                  <Badge className="bg-green-100 text-green-800">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse ml-2" />
                    פעיל
                  </Badge>
                </div>

                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm font-medium">סטטוס הסוכן</span>
                    <span className="text-sm text-green-600">מבצע משימות</span>
                  </div>
                  
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm font-medium">משימות פעילות</span>
                    <span className="text-sm font-bold">3</span>
                  </div>
                  
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm font-medium">שיחות מנוהלות היום</span>
                    <span className="text-sm font-bold">47</span>
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm font-medium">פעילות אחרונה:</div>
                    <div className="text-xs text-gray-600 bg-blue-50 p-2 rounded">
                      14:32 - זימון תור למטופל חדש דרך WhatsApp
                    </div>
                    <div className="text-xs text-gray-600 bg-green-50 p-2 rounded">
                      14:30 - עדכון יומן רופא - תור בוטל
                    </div>
                  </div>

                  <div className="flex gap-2 pt-4">
                    <Button size="sm" className="flex-1 bg-[#001529] hover:bg-[#220]">
                      <Shield className="w-4 h-4 ml-2" />
                      קח שליטה
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1">
                      <Pause className="w-4 h-4 ml-2" />
                      השהה
                    </Button>
                  </div>
                </div>
              </Card>

              {/* Floating explanation */}
              <div className="absolute -top-4 -left-4 bg-yellow-100 border border-yellow-300 rounded-lg p-3 max-w-xs">
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle className="w-4 h-4 text-yellow-600" />
                  <span className="text-sm font-medium text-yellow-800">הסבר אוטומטי</span>
                </div>
                <p className="text-xs text-yellow-700">
                  הסוכן מזמן תור כי זיהה פנייה חדשה ומצא זמינות מתאימה ביומן
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission Control Dashboard Preview */}
      <section className="py-20 bg-gradient-to-br from-[#f5f5f5] to-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-[#001529] mb-4">
              מרכז השליטה והבקרה שלכם
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              תצוגה מקדימה של הדשבורד שמאפשר לכם לנהל ולפקח על הסוכן
            </p>
          </div>

          <div className="relative">
            <Card className="p-8 shadow-2xl border border-gray-200 bg-white">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Real-time Statistics */}
                <div className="lg:col-span-2 space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card className="p-4 border-r-4 border-r-green-500">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">תורים היום</p>
                          <p className="text-2xl font-bold text-[#001529]">23</p>
                        </div>
                        <Calendar className="w-8 h-8 text-green-500" />
                      </div>
                      <div className="flex items-center gap-1 mt-2">
                        <TrendingUp className="w-4 h-4 text-green-500" />
                        <span className="text-xs text-green-600">+12% מאתמול</span>
                      </div>
                    </Card>

                    <Card className="p-4 border-r-4 border-r-blue-500">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">שיחות פעילות</p>
                          <p className="text-2xl font-bold text-[#001529]">5</p>
                        </div>
                        <MessageSquare className="w-8 h-8 text-blue-500" />
                      </div>
                      <div className="flex items-center gap-1 mt-2">
                        <Activity className="w-4 h-4 text-blue-500" />
                        <span className="text-xs text-blue-600">בזמן אמת</span>
                      </div>
                    </Card>

                    <Card className="p-4 border-r-4 border-r-purple-500">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">שביעות רצון</p>
                          <p className="text-2xl font-bold text-[#001529]">94%</p>
                        </div>
                        <Heart className="w-8 h-8 text-purple-500" />
                      </div>
                      <div className="flex items-center gap-1 mt-2">
                        <TrendingUp className="w-4 h-4 text-purple-500" />
                        <span className="text-xs text-purple-600">+2% השבוע</span>
                      </div>
                    </Card>
                  </div>

                  <Card className="p-6">
                    <h3 className="text-lg font-bold text-[#001529] mb-4">פעילות הסוכן בזמן אמת</h3>
                    <div className="space-y-3">
                      {agentActivities.map((activity) => (
                        <div key={activity.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center gap-3">
                            <div className={cn(
                              "w-3 h-3 rounded-full",
                              activity.status === 'active' ? "bg-green-500 animate-pulse" : "bg-blue-500"
                            )} />
                            <span className="text-sm font-medium">{activity.action}</span>
                          </div>
                          <span className="text-xs text-gray-500">{activity.time}</span>
                        </div>
                      ))}
                    </div>
                  </Card>
                </div>

                {/* Control Panel */}
                <div className="space-y-6">
                  <Card className="p-6 border-r-4 border-r-[#001529]">
                    <h3 className="text-lg font-bold text-[#001529] mb-4">בקרת הסוכן</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">סטטוס</span>
                        <Badge className="bg-green-100 text-green-800">פעיל</Badge>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">מצב עבודה</span>
                        <span className="text-sm text-gray-600">אוטונומי</span>
                      </div>

                      <div className="space-y-2">
                        <Button className="w-full bg-[#001529] hover:bg-[#220]">
                          <Shield className="w-4 h-4 ml-2" />
                          קח שליטה מלאה
                        </Button>
                        <Button variant="outline" className="w-full">
                          <Pause className="w-4 h-4 ml-2" />
                          השהה פעילות
                        </Button>
                        <Button variant="outline" className="w-full">
                          <Settings className="w-4 h-4 ml-2" />
                          הגדרות מתקדמות
                        </Button>
                      </div>
                    </div>
                  </Card>

                  <Card className="p-6">
                    <h3 className="text-lg font-bold text-[#001529] mb-4">התראות</h3>
                    <div className="space-y-3">
                      <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <div className="flex items-center gap-2 mb-1">
                          <AlertTriangle className="w-4 h-4 text-yellow-600" />
                          <span className="text-sm font-medium text-yellow-800">דרושה התערבות</span>
                        </div>
                        <p className="text-xs text-yellow-700">מטופל מבקש שינוי מורכב בתור</p>
                        <Button size="sm" className="mt-2 bg-yellow-600 hover:bg-yellow-700 text-white">
                          טפל עכשיו
                        </Button>
                      </div>
                    </div>
                  </Card>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-[#001529] to-[#220] text-white">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-4xl lg:text-5xl font-bold mb-6">
            מוכנים להכיר את הסוכן שלכם?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            הצטרפו למהפכה של ניהול מרפאות אוטונומי. 
            התחילו עם מערכת חיה ותראו איך הסוכן יכול לשנות את המרפאה שלכם.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-white text-[#001529] hover:bg-blue-50 text-lg px-8 py-4">
              <Play className="w-5 h-5 ml-2" />
              התחל מערכת חיה
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10 text-lg px-8 py-4">
              <Calendar className="w-5 h-5 ml-2" />
              קבע פגישת ייעוץ
            </Button>
          </div>

          <div className="flex items-center justify-center gap-8 mt-12 text-blue-200">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              <span>ללא התחייבות</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              <span>מערכת מלאה</span>
            </div>
            <div className="flex items-center gap-2">
              <Headphones className="w-5 h-5" />
              <span>תמיכה מלאה</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#001529] text-white py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            <div className="lg:col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                  <Bot className="w-6 h-6 text-[#001529]" />
                </div>
                <span className="text-2xl font-bold">DentalAI</span>
              </div>
              <p className="text-blue-200 mb-4 max-w-md">
                הסוכן האוטונומי המתקדם לניהול מרפאות שיניים. 
                מהפכה בחוויית המטופל וביעילות המרפאה.
              </p>
              <div className="flex items-center gap-4">
                <Badge className="bg-white/10 text-white">
                  <Shield className="w-4 h-4 ml-2" />
                  מאובטח ומוגן
                </Badge>
                <Badge className="bg-white/10 text-white">
                  <Globe className="w-4 h-4 ml-2" />
                  תמיכה בעברית
                </Badge>
              </div>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">המוצר</h4>
              <div className="space-y-2 text-blue-200">
                <div>מרכז השליטה והבקרה</div>
                <div>ניהול תורים אוטונומי</div>
                <div>תקשורת חכמה</div>
                <div>אנליטיקה מתקדמת</div>
              </div>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">תמיכה</h4>
              <div className="space-y-2 text-blue-200">
                <div>מרכז עזרה</div>
                <div>הדרכות וידאו</div>
                <div>תמיכה טכנית</div>
                <div>קהילת משתמשים</div>
              </div>
            </div>
          </div>
          
          <div className="border-t border-[#220] mt-8 pt-8 text-center text-blue-200">
            <p>&copy; 2025 DentalAI. כל הזכויות שמורות. מופעל על ידי Manus AI.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default AgenticLandingPage;
