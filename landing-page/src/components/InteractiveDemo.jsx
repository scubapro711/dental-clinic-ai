import { useState } from 'react';
import { MessageCircle, Send, Sparkles } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

/**
 * Interactive Demo Section
 * 
 * Allows visitors to try Alex AI right on the landing page:
 * - Pre-populated quick questions
 * - Real-time chat interface
 * - Simulated Alex responses
 * - CTA to start free trial after demo
 */
export default function InteractiveDemo() {
  const [messages, setMessages] = useState([
    {
      role: 'alex',
      text: 'שלום! אני אלכס, קבלת הקהל AI של DentaFlow. איך אני יכול לעזור לך היום?',
      time: new Date().toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const quickQuestions = [
    'לקבוע תור לשבוע הבא',
    'מה שעות הפעילות?',
    'האם אתם מקבלים ביטוח?',
    'אני צריך לשנות תור'
  ];

  const alexResponses = {
    'לקבוע תור לשבוע הבא': 'בהחלט! יש לי פנוי ביום רביעי הבא ב-10:00 או ב-14:30 עם ד"ר כהן. איזה זמן מתאים לך?',
    'מה שעות הפעילות?': 'אנחנו פתוחים ימים א\'-ה\' בין 8:00-18:00, ויום ו\' בין 8:00-13:00. האם תרצה לקבוע תור?',
    'האם אתם מקבלים ביטוח?': 'כן, אנחנו עובדים עם כל קופות החולים וחברות הביטוח המובילות. תצטרך להביא אישור מראש מקופת החולים.',
    'אני צריך לשנות תור': 'אין בעיה! מה התאריך והשעה של התור הנוכחי שלך? אעזור לך למצוא זמן חדש.',
    'default': 'זו שאלה מעניינת! במערכת המלאה, הייתי יכול לעזור לך עם זה. האם תרצה להתחיל ניסיון חינם ל-30 יום כדי לחוות את כל היכולות שלי?'
  };

  const handleSendMessage = (text) => {
    if (!text.trim()) return;

    // Add user message
    const userMessage = {
      role: 'user',
      text: text,
      time: new Date().toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    // Simulate Alex typing
    setIsTyping(true);

    // Get Alex's response
    setTimeout(() => {
      const response = alexResponses[text] || alexResponses['default'];
      const alexMessage = {
        role: 'alex',
        text: response,
        time: new Date().toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, alexMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const handleQuickQuestion = (question) => {
    handleSendMessage(question);
  };

  return (
    <section className="py-20 bg-white" dir="rtl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-blue-100 text-blue-800 hover:bg-blue-100">
            <Sparkles className="h-3 w-3 ml-1" />
            נסה עכשיו
          </Badge>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            נסה את אלכס עכשיו - ללא הרשמה
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            חווה את הכוח של AI לקבלת קהל בזמן אמת. לחץ על אחת השאלות או כתוב משלך.
          </p>
        </div>

        {/* Demo Container */}
        <div className="max-w-4xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Chat Interface */}
            <Card className="shadow-2xl">
              <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-blue-600 text-2xl font-bold">
                    A
                  </div>
                  <div>
                    <CardTitle>אלכס - קבלת קהל AI</CardTitle>
                    <CardDescription className="text-blue-100">
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                        <span>פעיל עכשיו</span>
                      </div>
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="p-0">
                {/* Messages */}
                <div className="h-96 overflow-y-auto p-4 space-y-4 bg-gray-50">
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-2xl px-4 py-3 ${message.role === 'user'
                            ? 'bg-blue-500 text-white rounded-br-none'
                            : 'bg-white text-gray-900 rounded-bl-none shadow-md'
                          }`}
                      >
                        <div className="text-xs opacity-75 mb-1">
                          {message.role === 'user' ? 'אתה' : 'אלכס'} • {message.time}
                        </div>
                        <p className="text-sm leading-relaxed">{message.text}</p>
                      </div>
                    </div>
                  ))}

                  {/* Typing Indicator */}
                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="bg-white rounded-2xl rounded-bl-none px-4 py-3 shadow-md">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Input */}
                <div className="p-4 border-t bg-white">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(inputValue)}
                      placeholder="כתוב הודעה..."
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                      dir="rtl"
                    />
                    <Button
                      onClick={() => handleSendMessage(inputValue)}
                      className="bg-blue-500 hover:bg-blue-600 rounded-full px-6"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Questions & Info */}
            <div className="space-y-6">
              {/* Quick Questions */}
              <Card>
                <CardHeader>
                  <CardTitle>שאלות מהירות</CardTitle>
                  <CardDescription>לחץ על אחת השאלות כדי לראות איך אלכס עונה</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {quickQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleQuickQuestion(question)}
                      className="w-full text-right p-4 bg-gradient-to-r from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 rounded-lg transition-colors border border-blue-200"
                    >
                      <div className="flex items-center gap-2">
                        <MessageCircle className="h-4 w-4 text-blue-600 flex-shrink-0" />
                        <span className="text-gray-900">{question}</span>
                      </div>
                    </button>
                  ))}
                </CardContent>
              </Card>

              {/* Demo Info */}
              <Card className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200">
                <CardContent className="pt-6">
                  <h4 className="font-bold text-gray-900 mb-3">💡 זה רק טעימה!</h4>
                  <p className="text-gray-700 mb-4">
                    במערכת המלאה, אלכס יכול:
                  </p>
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>לקבוע ולשנות תורים בזמן אמת</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>לשלוח תזכורות SMS אוטומטיות</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>לעבוד 24/7 - אפילו בשבת!</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>להשתלב עם Odoo ERP שלך</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>

              {/* CTA */}
              <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
                <CardContent className="pt-6 text-center">
                  <h4 className="text-2xl font-bold mb-3">מתרשם?</h4>
                  <p className="mb-6 opacity-90">
                    התחל ניסיון חינם ל-30 יום וקבל את אלכס + 3 סוכני AI נוספים
                  </p>
                  <Button
                    size="lg"
                    className="w-full bg-white text-purple-600 hover:bg-gray-100 text-lg py-6"
                  >
                    התחל ניסיון חינם
                  </Button>
                  <p className="text-xs mt-3 opacity-75">
                    ללא כרטיס אשראי • ביטול בכל עת
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>

        {/* Bottom Stats */}
        <div className="mt-16 grid md:grid-cols-4 gap-6 max-w-4xl mx-auto">
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600 mb-2">24/7</div>
            <div className="text-sm text-gray-600">זמינות</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-green-600 mb-2">95%</div>
            <div className="text-sm text-gray-600">שביעות רצון</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-purple-600 mb-2">40%</div>
            <div className="text-sm text-gray-600">פחות ביטולים</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-orange-600 mb-2">0</div>
            <div className="text-sm text-gray-600">שיחות שהוחמצו</div>
          </div>
        </div>
      </div>
    </section>
  );
}

