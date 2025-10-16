import { Phone, Stethoscope, TrendingUp, Shield, MessageCircle, Clock, Brain, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

/**
 * AI Team Section
 * 
 * Showcases all 4 AI agents with:
 * - Individual agent cards with avatars
 * - Sample conversations
 * - Competitive advantages for each agent
 * - Interactive tabs to explore each agent
 */
export default function AITeamSection() {
  const agents = [
    {
      id: 'alex',
      name: 'אלכס',
      title: 'קבלת קהל AI',
      icon: Phone,
      color: 'blue',
      gradient: 'from-blue-500 to-blue-600',
      bgGradient: 'from-blue-50 to-blue-100',
      tagline: 'לעולם לא תפספסו תור שוב',
      features: [
        'קביעת תורים 24/7 (אפילו ב-2 בלילה)',
        'שליחת תזכורות אוטומטיות',
        'מענה מיידי לשאלות מטופלים',
        'הפחתת 40% בביטולי תורים'
      ],
      advantage: 'בניגוד לצ\'אטבוטים בסיסיים, אלכס מבין טרמינולוגיה דנטלית ומשתלב עם היומן בזמן אמת.',
      conversation: [
        { role: 'patient', text: 'אני צריך תור דחוף למחר', time: '23:00' },
        { role: 'alex', text: 'יש לי פנוי מחר ב-9:00 עם ד"ר כהן. לקבוע?', time: '23:00' },
        { role: 'patient', text: 'כן בבקשה', time: '23:01' },
        { role: 'alex', text: 'מצוין! התור נקבע. תקבל SMS אישור בקרוב. נתראה מחר ב-9:00 🦷', time: '23:01' }
      ]
    },
    {
      id: 'sarah',
      name: 'שרה',
      title: 'עוזרת דנטלית AI',
      icon: Stethoscope,
      color: 'green',
      gradient: 'from-green-500 to-green-600',
      bgGradient: 'from-green-50 to-green-100',
      tagline: 'חינוך מטופלים מומחה, 24/7',
      features: [
        'מענה על שאלות טיפול',
        'הוראות לאחר טיפול',
        'הסברים על הליכים',
        'הפחתת 30% בעומס על הצוות'
      ],
      advantage: 'לשרה יש ידע על 1,000+ הליכים דנטליים. אף פלטפורמה אחרת לא מציעה רמה כזו של אוטומציה בחינוך מטופלים.',
      conversation: [
        { role: 'patient', text: 'האם אני יכול לאכול אחרי טיפול שורש?', time: '14:30' },
        { role: 'sarah', text: 'המתן 2-3 שעות עד שההרדמה תעבור. הימנע ממזון קשה ל-24 שעות. קח משככי כאבים לפי המרשם. התקשר אם הכאב נמשך מעבר ל-48 שעות.', time: '14:30' },
        { role: 'patient', text: 'תודה! זה ממש עוזר', time: '14:31' },
        { role: 'sarah', text: 'תמיד לשירותך! החלמה מהירה 💚', time: '14:31' }
      ]
    },
    {
      id: 'marcus',
      name: 'מרקוס',
      title: 'CFO AI',
      icon: TrendingUp,
      color: 'purple',
      gradient: 'from-purple-500 to-purple-600',
      bgGradient: 'from-purple-50 to-purple-100',
      tagline: 'היועץ הפיננסי שלך, תמיד פעיל',
      features: [
        'מעקב הכנסות בזמן אמת',
        'תחזית תזרים מזומנים',
        'דוחות פיננסיים אוטומטיים',
        'זיהוי הזדמנויות לחיסכון'
      ],
      advantage: 'אף פלטפורמה דנטלית אחרת אין לה CFO AI ייעודי. מרקוס נותן לך תובנות עסקיות ששוות ₪10,000+/חודש מיועץ.',
      conversation: [
        { role: 'owner', text: 'מה ההכנסה שלנו החודש?', time: '10:15' },
        { role: 'marcus', text: 'MRR: ₪45,000, עלייה של 12% מהחודש שעבר. חשבוניות ממתינות: ₪8,500. המלצה: עקוב אחרי 3 תשלומים באיחור לשיפור תזרים המזומנים.', time: '10:15' },
        { role: 'owner', text: 'איזה טיפולים הכי רווחיים?', time: '10:16' },
        { role: 'marcus', text: 'שתלים: ₪18,000 (40% מההכנסה), שיקום: ₪12,000 (27%). המלצה: הגדל שיווק לשתלים - ROI הכי גבוה.', time: '10:16' }
      ],
      isUnique: true
    },
    {
      id: 'sophia',
      name: 'סופיה',
      title: 'קצינת ציות AI',
      icon: Shield,
      color: 'orange',
      gradient: 'from-orange-500 to-orange-600',
      bgGradient: 'from-orange-50 to-orange-100',
      tagline: 'הישארו בציות, הישארו מאובטחים',
      features: [
        'ניטור HIPAA 24/7',
        'דוחות ביקורת אוטומטיים',
        'התראות על בעיות אבטחה',
        'מוכנות תמידית לביקורת'
      ],
      advantage: 'הפרות HIPAA עולות $50,000+ לאירוע. סופיה מוודאת שאתם תמיד בציות - אוטומטית.',
      conversation: [
        { role: 'admin', text: 'האם אנחנו מוכנים לביקורת HIPAA?', time: '09:00' },
        { role: 'sophia', text: 'כן. ביקורת אחרונה: 10/10/2025. כל המערכות בציות. ביקורת הבאה: 10/01/2026. אזכיר לך 30 יום מראש.', time: '09:00' },
        { role: 'admin', text: 'מה עם גיבויים?', time: '09:01' },
        { role: 'sophia', text: 'גיבוי אוטומטי יומי ב-2:00 AM. גיבוי אחרון: היום 2:00 AM. כל הנתונים מוצפנים AES-256. בדיקת שחזור אחרונה: 05/10/2025 - הצלחה.', time: '09:01' }
      ],
      isUnique: true
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-gray-100" dir="rtl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-blue-100 text-blue-800 hover:bg-blue-100">
            הצוות שלך
          </Badge>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            4 מומחי AI. פלטפורמה אחת. אפשרויות אינסופיות.
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            הכירו את צוות ה-AI המתמחה שלכם - כל אחד מומחה בתחום שלו, 
            כולם עובדים 24/7 כדי להפוך את המרפאה שלכם ליעילה יותר.
          </p>
        </div>

        {/* Agent Tabs */}
        <Tabs defaultValue="alex" className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-8 bg-white p-2 rounded-xl shadow-lg">
            {agents.map((agent) => (
              <TabsTrigger
                key={agent.id}
                value={agent.id}
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:text-white relative"
                style={{
                  backgroundImage: `linear-gradient(to right, var(--tw-gradient-stops))`,
                  '--tw-gradient-from': agent.color === 'blue' ? '#3B82F6' :
                    agent.color === 'green' ? '#10B981' :
                      agent.color === 'purple' ? '#9333EA' : '#F97316',
                  '--tw-gradient-to': agent.color === 'blue' ? '#2563EB' :
                    agent.color === 'green' ? '#059669' :
                      agent.color === 'purple' ? '#7C3AED' : '#EA580C'
                }}
              >
                <div className="flex flex-col items-center gap-2 py-2">
                  <agent.icon className="h-5 w-5" />
                  <span className="font-semibold">{agent.name}</span>
                  {agent.isUnique && (
                    <Badge className="absolute -top-2 -right-2 bg-yellow-400 text-yellow-900 text-xs px-1 py-0">
                      ייחודי
                    </Badge>
                  )}
                </div>
              </TabsTrigger>
            ))}
          </TabsList>

          {agents.map((agent) => (
            <TabsContent key={agent.id} value={agent.id}>
              <div className="grid lg:grid-cols-2 gap-8">
                {/* Agent Info Card */}
                <Card className={`bg-gradient-to-br ${agent.bgGradient} border-2 border-${agent.color}-200`}>
                  <CardHeader>
                    <div className="flex items-center gap-4 mb-4">
                      <div className={`w-16 h-16 bg-gradient-to-br ${agent.gradient} rounded-full flex items-center justify-center text-white text-3xl font-bold shadow-lg`}>
                        {agent.name[0]}
                      </div>
                      <div>
                        <CardTitle className="text-2xl">{agent.name}</CardTitle>
                        <CardDescription className="text-lg font-semibold text-gray-700">
                          {agent.title}
                        </CardDescription>
                      </div>
                      {agent.isUnique && (
                        <Badge className="bg-yellow-100 text-yellow-800 border-2 border-yellow-300">
                          ⭐ ייחודי ל-DentaFlow
                        </Badge>
                      )}
                    </div>
                    <p className="text-xl font-bold text-gray-900">{agent.tagline}</p>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Features */}
                    <div>
                      <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                        <Brain className="h-5 w-5" />
                        מה {agent.name} עושה:
                      </h4>
                      <ul className="space-y-2">
                        {agent.features.map((feature, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-700">{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Competitive Advantage */}
                    <div className="bg-white/60 backdrop-blur-sm rounded-lg p-4 border-2 border-white">
                      <h4 className="font-bold text-gray-900 mb-2 flex items-center gap-2">
                        <TrendingUp className="h-5 w-5" />
                        היתרון התחרותי:
                      </h4>
                      <p className="text-gray-700 italic">"{agent.advantage}"</p>
                    </div>
                  </CardContent>
                </Card>

                {/* Sample Conversation */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MessageCircle className="h-5 w-5" />
                      דוגמה לשיחה
                    </CardTitle>
                    <CardDescription>
                      ראה איך {agent.name} מתקשר עם משתמשים בזמן אמת
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {agent.conversation.map((message, index) => (
                        <div
                          key={index}
                          className={`flex ${message.role === 'patient' || message.role === 'owner' || message.role === 'admin' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-[80%] rounded-2xl px-4 py-3 ${message.role === 'patient' || message.role === 'owner' || message.role === 'admin'
                                ? 'bg-blue-500 text-white rounded-br-none'
                                : `bg-gradient-to-br ${agent.gradient} text-white rounded-bl-none`
                              }`}
                          >
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs opacity-75">
                                {message.role === 'patient' ? 'מטופל' :
                                  message.role === 'owner' ? 'בעלים' :
                                    message.role === 'admin' ? 'מנהל' :
                                      agent.name}
                              </span>
                              <Clock className="h-3 w-3 opacity-75" />
                              <span className="text-xs opacity-75">{message.time}</span>
                            </div>
                            <p className="text-sm leading-relaxed">{message.text}</p>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Typing Indicator */}
                    <div className="flex items-center gap-2 mt-4 text-gray-500">
                      <div className={`w-8 h-8 bg-gradient-to-br ${agent.gradient} rounded-full flex items-center justify-center text-white text-sm font-bold`}>
                        {agent.name[0]}
                      </div>
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          ))}
        </Tabs>

        {/* Bottom CTA */}
        <div className="mt-16 text-center bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-white">
          <h3 className="text-3xl font-bold mb-4">
            מוכן להכיר את הצוות שלך?
          </h3>
          <p className="text-xl mb-8 opacity-90">
            התחל ניסיון חינם ל-30 יום וגלה איך 4 מומחי AI יכולים לשנות את המרפאה שלך
          </p>
          <button className="bg-white text-purple-600 px-8 py-4 rounded-full font-bold text-lg hover:bg-gray-100 transition-colors shadow-xl">
            התחל ניסיון חינם
          </button>
        </div>
      </div>
    </section>
  );
}

