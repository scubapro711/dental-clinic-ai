import { Shield, Lock, FileCheck, Bell, CheckCircle, X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';

/**
 * HIPAA Compliance Section
 * 
 * Emphasizes DentaFlow's built-in HIPAA compliance as a competitive advantage:
 * - Comparison table showing what's included vs competitors
 * - Trust signals (encryption, audit trails, BAA)
 * - Sophia AI monitoring
 */
export default function HIPAASection() {
  const complianceFeatures = [
    {
      feature: 'הצפנת נתונים',
      traditional: { included: false, cost: 'עלות נוספת' },
      dentaflow: { included: true, detail: 'AES-256 מובנה' }
    },
    {
      feature: 'Audit Trails',
      traditional: { included: false, cost: 'ידני' },
      dentaflow: { included: true, detail: 'אוטומטי' }
    },
    {
      feature: 'הסכם BAA',
      traditional: { included: false, cost: '₪500/שנה' },
      dentaflow: { included: true, detail: 'חינם' }
    },
    {
      feature: 'ניטור ציות',
      traditional: { included: false, cost: 'אחריותך' },
      dentaflow: { included: true, detail: 'סופיה AI 24/7' }
    },
    {
      feature: 'התראות אבטחה',
      traditional: { included: false, cost: 'אין' },
      dentaflow: { included: true, detail: 'בזמן אמת' }
    },
    {
      feature: 'דוחות ביקורת',
      traditional: { included: false, cost: 'ידני' },
      dentaflow: { included: true, detail: 'נוצרים אוטומטית' }
    }
  ];

  const trustSignals = [
    {
      icon: Lock,
      title: 'הצפנה מקצה לקצה',
      description: 'כל הנתונים מוצפנים ב-AES-256, אותו תקן שבנקים משתמשים בו'
    },
    {
      icon: FileCheck,
      title: 'Audit Logs אוטומטיים',
      description: 'כל פעולה נרשמת אוטומטית למעקב ושקיפות מלאה'
    },
    {
      icon: Shield,
      title: 'מרכזי נתונים תואמי HIPAA',
      description: 'כל הנתונים מאוחסנים במרכזי נתונים מאושרים HIPAA ב-GCP'
    },
    {
      icon: Bell,
      title: 'ניטור 24/7 על ידי סופיה',
      description: 'סופיה AI מנטרת ציות באופן רציף ומתריעה על בעיות מיד'
    }
  ];

  return (
    <section className="py-20 bg-white" dir="rtl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-green-100 text-green-800 hover:bg-green-100">
            <Shield className="h-3 w-3 ml-1" />
            ציות HIPAA
          </Badge>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            ציות HIPAA כלול - לא תוספת יקרה
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            רוב תוכנות הדנטליות גובות ₪500-1,000 לחודש נוסף עבור ציות HIPAA. 
            אנחנו כוללים את זה בחינם.
          </p>
        </div>

        {/* Problem Statement */}
        <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-8 mb-12">
          <div className="flex items-start gap-4">
            <div className="bg-red-500 rounded-full p-3 flex-shrink-0">
              <X className="h-8 w-8 text-white" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-red-900 mb-2">
                הבעיה עם תוכנות דנטליות אחרות
              </h3>
              <p className="text-lg text-red-800 mb-4">
                הפרות HIPAA עולות בממוצע <strong>$50,000 לאירוע</strong>. 
                רוב התוכנות גובות אלפי שקלים נוספים עבור ציות בסיסי, 
                והאחריות עדיין עליך.
              </p>
              <div className="bg-white rounded-lg p-4">
                <div className="font-bold text-gray-900 mb-2">עלויות טיפוסיות:</div>
                <ul className="space-y-1 text-gray-700">
                  <li>• הצפנת נתונים: ₪200/חודש</li>
                  <li>• BAA (Business Associate Agreement): ₪500/שנה</li>
                  <li>• ניטור ציות: ₪300/חודש</li>
                  <li>• דוחות ביקורת: ₪150/חודש</li>
                  <li className="font-bold text-red-600 pt-2 border-t">סה"כ: ₪650+/חודש נוסף</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Comparison Table */}
        <Card className="mb-12 overflow-hidden shadow-xl">
          <CardHeader className="bg-gradient-to-r from-green-50 to-blue-50">
            <CardTitle className="text-center text-2xl">מה כלול ב-DentaFlow</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b-2 border-gray-200">
                    <th className="p-4 text-right font-bold text-gray-900 bg-gray-50">תכונה</th>
                    <th className="p-4 text-center font-bold text-gray-700 bg-gray-50">
                      תוכנה מסורתית
                    </th>
                    <th className="p-4 text-center font-bold text-gray-900 bg-gradient-to-r from-green-50 to-blue-50">
                      <div className="flex items-center justify-center gap-2">
                        <span>DentaFlow</span>
                        <Badge className="bg-green-600 text-white">כלול</Badge>
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {complianceFeatures.map((item, index) => (
                    <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                      <td className="p-4 font-semibold text-gray-900">{item.feature}</td>
                      <td className="p-4 text-center bg-red-50">
                        <div className="flex flex-col items-center gap-2">
                          <X className="h-5 w-5 text-red-600" />
                          <span className="text-sm text-red-600 font-semibold">{item.traditional.cost}</span>
                        </div>
                      </td>
                      <td className="p-4 text-center bg-green-50">
                        <div className="flex flex-col items-center gap-2">
                          <CheckCircle className="h-5 w-5 text-green-600" />
                          <span className="text-sm font-semibold text-green-900">{item.dentaflow.detail}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Trust Signals Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {trustSignals.map((signal, index) => (
            <Card key={index} className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="bg-gradient-to-br from-green-100 to-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <signal.icon className="h-8 w-8 text-green-600" />
                </div>
                <h4 className="font-bold text-gray-900 mb-2">{signal.title}</h4>
                <p className="text-sm text-gray-600">{signal.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Sophia AI Highlight */}
        <div className="bg-gradient-to-r from-orange-100 to-red-100 rounded-2xl p-8 border-2 border-orange-200">
          <div className="grid lg:grid-cols-2 gap-8 items-center">
            <div>
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-full flex items-center justify-center text-white text-3xl font-bold shadow-lg">
                  S
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">סופיה - קצינת הציות שלך</h3>
                  <p className="text-gray-700">מנטרת HIPAA 24/7 אוטומטית</p>
                </div>
              </div>
              <p className="text-lg text-gray-800 mb-4">
                סופיה AI מנטרת את כל המערכות שלך באופן רציף, מזהה בעיות פוטנציאליות, 
                ומתריעה עליהן לפני שהן הופכות לבעיות אמיתיות.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">בדיקות אבטחה אוטומטיות כל שעה</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">התראות מיידיות על חריגות</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">דוחות ביקורת מוכנים תמיד</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">עדכונים אוטומטיים לתקנות חדשות</span>
                </li>
              </ul>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-lg">
              <div className="text-sm text-gray-500 mb-2">דוגמה לדו"ח סופיה</div>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="font-semibold text-gray-900">הצפנת נתונים</span>
                  <Badge className="bg-green-600 text-white">✓ פעיל</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="font-semibold text-gray-900">גיבויים</span>
                  <Badge className="bg-green-600 text-white">✓ יומי</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="font-semibold text-gray-900">Audit Logs</span>
                  <Badge className="bg-green-600 text-white">✓ פעיל</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="font-semibold text-gray-900">הרשאות גישה</span>
                  <Badge className="bg-green-600 text-white">✓ מוגדר</Badge>
                </div>
                <div className="mt-4 p-4 bg-gradient-to-r from-green-500 to-green-600 rounded-lg text-white text-center">
                  <div className="text-3xl font-bold mb-1">100%</div>
                  <div className="text-sm">ציות HIPAA</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="mt-12 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            מוכן להיות בציות מלא - בחינם?
          </h3>
          <p className="text-lg text-gray-600 mb-6">
            התחל ניסיון חינם ל-30 יום וקבל ציות HIPAA מלא מיום אחד
          </p>
          <button className="bg-gradient-to-r from-green-500 to-green-600 text-white px-8 py-4 rounded-full font-bold text-lg hover:from-green-600 hover:to-green-700 transition-colors shadow-xl">
            התחל ניסיון חינם
          </button>
          <p className="text-sm text-gray-500 mt-4">
            ללא כרטיס אשראי • ציות HIPAA מיום אחד • ביטול בכל עת
          </p>
        </div>
      </div>
    </section>
  );
}

