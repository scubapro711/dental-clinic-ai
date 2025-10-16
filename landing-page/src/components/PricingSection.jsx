import { Check, Zap, TrendingUp, Crown, Star, Sparkles } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

/**
 * Pricing Section
 * 
 * Displays transparent pricing with:
 * - 3 pricing tiers (Basic, Professional, Enterprise)
 * - Early adopter discount (20% off for first 10 clinics)
 * - 30-day free trial
 * - Comparison to competitors
 * - All features included (4 AI agents, HIPAA, etc.)
 */
export default function PricingSection() {
  const plans = [
    {
      name: 'Basic',
      icon: Zap,
      color: 'blue',
      gradient: 'from-blue-500 to-blue-600',
      price: 799,
      description: 'למרפאות קטנות',
      features: [
        'עד 5 משתמשים',
        'עד 100 מטופלים',
        '4 סוכני AI (אלכס, שרה, מרקוס, סופיה)',
        'ציות HIPAA מלא',
        'Odoo ERP משולב',
        '500 הודעות SMS/חודש',
        'תמיכה באימייל',
        'ניסיון חינם 30 יום'
      ],
      popular: false
    },
    {
      name: 'Professional',
      icon: TrendingUp,
      color: 'purple',
      gradient: 'from-purple-500 to-purple-600',
      price: 1499,
      description: 'למרפאות בינוניות',
      features: [
        'עד 15 משתמשים',
        'עד 500 מטופלים',
        '4 סוכני AI (אלכס, שרה, מרקוס, סופיה)',
        'ציות HIPAA מלא',
        'Odoo ERP משולב',
        '1,500 הודעות SMS/חודש',
        'תמיכה עדיפות',
        'ניסיון חינם 30 יום',
        'דוחות מתקדמים',
        'אינטגרציות מותאמות אישית'
      ],
      popular: true
    },
    {
      name: 'Enterprise',
      icon: Crown,
      color: 'gradient',
      gradient: 'from-purple-500 to-pink-500',
      price: 2999,
      description: 'למרפאות גדולות',
      features: [
        'משתמשים ללא הגבלה',
        'מטופלים ללא הגבלה',
        '4 סוכני AI (אלכס, שרה, מרקוס, סופיה)',
        'ציות HIPAA מלא',
        'Odoo ERP משולב',
        'הודעות SMS ללא הגבלה',
        'תמיכה ייעודית 24/7',
        'ניסיון חינם 30 יום',
        'דוחות מתקדמים',
        'אינטגרציות מותאמות אישית',
        'מנהל חשבון ייעודי',
        'הדרכה מותאמת אישית'
      ],
      popular: false
    }
  ];

  const competitorComparison = [
    { name: 'CareStack', price: '₪499/ספק', features: 'PMS בסיסי, ללא AI' },
    { name: 'Dentrix Ascend', price: '₪399/ספק', features: 'מערכת ישנה, ללא AI' },
    { name: 'Open Dental', price: '₪300/ספק', features: 'ללא AI, הקמה מורכבת' },
    { name: 'DentaFlow', price: '₪799/מרפאה', features: '4 סוכני AI, HIPAA, ERP', highlight: true }
  ];

  const earlyAdopterSpotsLeft = 3;

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-gray-100" dir="rtl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-purple-100 text-purple-800 hover:bg-purple-100">
            תמחור שקוף
          </Badge>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            תמחור שהגיוני. ללא עלויות נסתרות.
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            כל התוכניות כוללות את כל 4 סוכני ה-AI, ציות HIPAA מלא, וניסיון חינם ל-30 יום.
          </p>
        </div>

        {/* Early Adopter Alert */}
        <div className="mb-12 bg-gradient-to-r from-purple-100 to-pink-100 border-2 border-purple-300 rounded-2xl p-6">
          <div className="flex items-center justify-center gap-4">
            <Sparkles className="h-8 w-8 text-purple-600" />
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-900 mb-1">
                🎉 הצעה מיוחדת למאמצים המוקדמים!
              </div>
              <div className="text-lg text-purple-700">
                20% הנחה לכל החיים • נותרו רק <span className="font-bold text-purple-900">{earlyAdopterSpotsLeft} מקומות</span>
              </div>
            </div>
            <Sparkles className="h-8 w-8 text-purple-600" />
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {plans.map((plan) => {
            const discountedPrice = Math.round(plan.price * 0.8);
            const Icon = plan.icon;

            return (
              <Card
                key={plan.name}
                className={`relative hover:shadow-2xl transition-all ${plan.popular ? 'border-purple-500 border-2 scale-105 z-10' : ''
                  }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-purple-600 hover:bg-purple-600 text-white text-base px-4 py-1">
                      <Star className="h-4 w-4 ml-1" />
                      הכי פופולרי
                    </Badge>
                  </div>
                )}

                <CardHeader className="text-center pb-8">
                  <div className={`w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center ${plan.color === 'blue' ? 'bg-blue-100' :
                      plan.color === 'purple' ? 'bg-purple-100' :
                        'bg-gradient-to-br from-purple-100 to-pink-100'
                    }`}>
                    <Icon className={`h-8 w-8 ${plan.color === 'blue' ? 'text-blue-600' :
                        plan.color === 'purple' ? 'text-purple-600' :
                          'text-purple-600'
                      }`} />
                  </div>
                  <CardTitle className="text-3xl mb-2">{plan.name}</CardTitle>
                  <CardDescription className="text-base">{plan.description}</CardDescription>
                </CardHeader>

                <CardContent className="space-y-6">
                  {/* Pricing */}
                  <div className="text-center pb-6 border-b">
                    <div className="text-sm text-gray-500 line-through mb-1">
                      ₪{plan.price.toLocaleString()}/חודש
                    </div>
                    <div className="text-5xl font-bold text-gray-900 mb-1">
                      ₪{discountedPrice.toLocaleString()}
                    </div>
                    <div className="text-gray-500">לחודש</div>
                    <Badge className="mt-2 bg-green-100 text-green-800 hover:bg-green-100">
                      חסוך 20% (₪{(plan.price - discountedPrice).toLocaleString()})
                    </Badge>
                  </div>

                  {/* Features */}
                  <ul className="space-y-3">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <Check className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>

                <CardFooter>
                  <Button
                    className={`w-full text-lg py-6 ${plan.popular
                        ? 'bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800'
                        : 'bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800'
                      } text-white`}
                  >
                    התחל ניסיון חינם
                  </Button>
                </CardFooter>
              </Card>
            );
          })}
        </div>

        {/* Competitor Comparison */}
        <div className="mb-16">
          <h3 className="text-2xl font-bold text-center text-gray-900 mb-8">
            השוואת מחירים למתחרים
          </h3>
          <Card className="overflow-hidden">
            <CardContent className="p-0">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-50 border-b-2 border-gray-200">
                    <th className="p-4 text-right font-bold text-gray-900">פלטפורמה</th>
                    <th className="p-4 text-center font-bold text-gray-900">מחיר חודשי</th>
                    <th className="p-4 text-center font-bold text-gray-900">מה כלול</th>
                  </tr>
                </thead>
                <tbody>
                  {competitorComparison.map((competitor, index) => (
                    <tr
                      key={index}
                      className={`border-b border-gray-100 ${competitor.highlight ? 'bg-gradient-to-r from-purple-50 to-pink-50' : 'hover:bg-gray-50'
                        }`}
                    >
                      <td className={`p-4 ${competitor.highlight ? 'font-bold text-purple-900' : 'text-gray-900'}`}>
                        {competitor.name}
                        {competitor.highlight && (
                          <Badge className="mr-2 bg-purple-600 text-white">זה אנחנו!</Badge>
                        )}
                      </td>
                      <td className={`p-4 text-center ${competitor.highlight ? 'font-bold text-purple-900' : 'text-gray-700'}`}>
                        {competitor.price}
                      </td>
                      <td className={`p-4 text-center ${competitor.highlight ? 'font-bold text-purple-900' : 'text-gray-600'}`}>
                        {competitor.features}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
          <p className="text-center text-gray-600 mt-4">
            💡 <strong>חסכו ₪3,600+/שנה</strong> לעומת תוכנות מסורתיות
          </p>
        </div>

        {/* Value Proposition */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-white text-center">
          <h3 className="text-3xl font-bold mb-4">
            קבלו 4 מומחי AI במחיר של רישיון תוכנה אחד
          </h3>
          <p className="text-xl mb-8 opacity-90">
            במקום לשלם ₪1,100+/חודש עבור מספר מערכות, קבלו הכל במקום אחד - החל מ-₪799/חודש
          </p>
          <div className="grid md:grid-cols-4 gap-6 max-w-4xl mx-auto mb-8">
            <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4">
              <div className="text-4xl font-bold mb-2">4</div>
              <div className="text-sm">סוכני AI</div>
            </div>
            <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4">
              <div className="text-4xl font-bold mb-2">100%</div>
              <div className="text-sm">ציות HIPAA</div>
            </div>
            <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4">
              <div className="text-4xl font-bold mb-2">1</div>
              <div className="text-sm">פלטפורמה</div>
            </div>
            <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4">
              <div className="text-4xl font-bold mb-2">₪0</div>
              <div className="text-sm">עלויות נסתרות</div>
            </div>
          </div>
          <Button
            size="lg"
            className="bg-white text-purple-600 hover:bg-gray-100 text-xl px-12 py-6 rounded-full font-bold shadow-2xl"
          >
            התחל ניסיון חינם ל-30 יום
          </Button>
          <p className="text-sm mt-4 opacity-75">
            ללא כרטיס אשראי • ביטול בכל עת • הכל כלול
          </p>
        </div>
      </div>
    </section>
  );
}

