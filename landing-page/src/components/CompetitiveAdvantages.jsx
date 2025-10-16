import { Check, X, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';

/**
 * Competitive Advantages Section
 * 
 * Highlights DentaFlow's unique competitive advantages through comparison tables:
 * - Traditional Software vs Other AI Solutions vs DentaFlow
 * - Feature comparison with checkmarks and X marks
 * - Emphasis on unique features (Marcus CFO AI, Sophia Compliance AI)
 */
export default function CompetitiveAdvantages() {
  const comparisons = [
    {
      category: 'תקשורת עם מטופלים',
      traditional: { text: 'ידני, שעות פעילות מוגבלות', status: 'bad' },
      otherAI: { text: 'צ\'אטבוט בסיסי', status: 'partial' },
      dentaflow: { text: 'אלכס AI - קבלת קהל 24/7', status: 'good' }
    },
    {
      category: 'ניהול פיננסי',
      traditional: { text: 'דוחות ידניים, ללא תחזיות', status: 'bad' },
      otherAI: { text: 'לא זמין', status: 'bad' },
      dentaflow: { text: 'מרקוס CFO AI - ניתוח פיננסי מתקדם', status: 'unique' }
    },
    {
      category: 'ציות רגולטורי',
      traditional: { text: 'אחריות המרפאה, עלות נוספת', status: 'bad' },
      otherAI: { text: 'לא זמין', status: 'bad' },
      dentaflow: { text: 'סופיה AI - ניטור HIPAA 24/7', status: 'unique' }
    },
    {
      category: 'חינוך מטופלים',
      traditional: { text: 'תלוי בזמינות הצוות', status: 'partial' },
      otherAI: { text: 'תשובות בסיסיות', status: 'partial' },
      dentaflow: { text: 'שרה AI - מומחית ל-1,000+ טיפולים', status: 'good' }
    },
    {
      category: 'מערכות משולבות',
      traditional: { text: '5-7 מערכות נפרדות', status: 'bad' },
      otherAI: { text: 'אינטגרציה חלקית', status: 'partial' },
      dentaflow: { text: 'פלטפורמה אחת משולבת (Odoo ERP)', status: 'good' }
    },
    {
      category: 'עלות חודשית',
      traditional: { text: '₪1,100+ (מספר מערכות)', status: 'bad' },
      otherAI: { text: '₪800-1,500', status: 'partial' },
      dentaflow: { text: 'החל מ-₪799 (הכל כלול)', status: 'good' }
    }
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'good':
        return <Check className="h-5 w-5 text-green-600" />;
      case 'unique':
        return <Badge className="bg-yellow-100 text-yellow-800 text-xs">ייחודי!</Badge>;
      case 'partial':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'bad':
        return <X className="h-5 w-5 text-red-600" />;
      default:
        return null;
    }
  };

  const getStatusBg = (status) => {
    switch (status) {
      case 'good':
      case 'unique':
        return 'bg-green-50';
      case 'partial':
        return 'bg-yellow-50';
      case 'bad':
        return 'bg-red-50';
      default:
        return 'bg-gray-50';
    }
  };

  return (
    <section className="py-20 bg-white" dir="rtl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-purple-100 text-purple-800 hover:bg-purple-100">
            השוואה תחרותית
          </Badge>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            מה הופך את DentaFlow לשונה?
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            הפסיקו לשלם עבור מספר מערכות. DentaFlow היא הפלטפורמה המשולבת היחידה 
            עם AI שבאמת עובד עבורכם.
          </p>
        </div>

        {/* Comparison Table */}
        <Card className="overflow-hidden shadow-xl">
          <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50">
            <CardTitle className="text-center text-2xl">השוואת פתרונות</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b-2 border-gray-200">
                    <th className="p-4 text-right font-bold text-gray-900 bg-gray-50">קטגוריה</th>
                    <th className="p-4 text-center font-bold text-gray-700 bg-gray-50">
                      תוכנה מסורתית
                    </th>
                    <th className="p-4 text-center font-bold text-gray-700 bg-gray-50">
                      פתרונות AI אחרים
                    </th>
                    <th className="p-4 text-center font-bold text-gray-900 bg-gradient-to-r from-blue-50 to-purple-50">
                      <div className="flex items-center justify-center gap-2">
                        <span className="text-2xl">DentaFlow</span>
                        <Badge className="bg-purple-600 text-white">מומלץ</Badge>
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {comparisons.map((item, index) => (
                    <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                      <td className="p-4 font-semibold text-gray-900">{item.category}</td>
                      <td className={`p-4 text-center ${getStatusBg(item.traditional.status)}`}>
                        <div className="flex flex-col items-center gap-2">
                          {getStatusIcon(item.traditional.status)}
                          <span className="text-sm text-gray-600">{item.traditional.text}</span>
                        </div>
                      </td>
                      <td className={`p-4 text-center ${getStatusBg(item.otherAI.status)}`}>
                        <div className="flex flex-col items-center gap-2">
                          {getStatusIcon(item.otherAI.status)}
                          <span className="text-sm text-gray-600">{item.otherAI.text}</span>
                        </div>
                      </td>
                      <td className={`p-4 text-center ${getStatusBg(item.dentaflow.status)}`}>
                        <div className="flex flex-col items-center gap-2">
                          {getStatusIcon(item.dentaflow.status)}
                          <span className="text-sm font-semibold text-gray-900">{item.dentaflow.text}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Key Takeaway */}
        <div className="mt-12 bg-gradient-to-r from-purple-100 to-pink-100 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            💡 המסקנה: חסכו ₪3,600+ בשנה ועבדו חכם יותר
          </h3>
          <p className="text-lg text-gray-700 mb-6">
            במקום לשלם עבור 5-7 מערכות נפרדות, קבלו פלטפורמה אחת משולבת עם 4 מומחי AI 
            שעובדים 24/7 עבור המרפאה שלכם.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <div className="bg-white rounded-lg px-6 py-3 shadow-md">
              <div className="text-3xl font-bold text-purple-600">4</div>
              <div className="text-sm text-gray-600">סוכני AI</div>
            </div>
            <div className="bg-white rounded-lg px-6 py-3 shadow-md">
              <div className="text-3xl font-bold text-green-600">1</div>
              <div className="text-sm text-gray-600">פלטפורמה</div>
            </div>
            <div className="bg-white rounded-lg px-6 py-3 shadow-md">
              <div className="text-3xl font-bold text-blue-600">∞</div>
              <div className="text-sm text-gray-600">אפשרויות</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

