import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';

/**
 * FAQ Section
 * 
 * Answers common questions about DentaFlow:
 * - Competitive advantages
 * - Security and compliance
 * - Pricing and trial
 * - Setup and migration
 * - Expandable accordion interface
 */
export default function FAQSection() {
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      question: 'איך DentaFlow שונה מתוכנות דנטליות אחרות?',
      answer: 'אנחנו הפלטפורמה היחידה עם 4 סוכני AI מתמחים (קבלת קהל, עוזרת דנטלית, CFO, קצינת ציות). בנוסף, ציות HIPAA כלול בחינם - לא תוספת יקרה. רוב המתחרים גובים ₪500-1,000/חודש נוסף עבור ציות, ואף אחד לא מציע CFO AI או Compliance Officer AI.'
    },
    {
      question: 'האם הנתונים של המטופלים שלי מאובטחים?',
      answer: 'בהחלט. כל הנתונים מוצפנים ב-AES-256 (אותו תקן שבנקים משתמשים בו), מאוחסנים במרכזי נתונים תואמי HIPAA ב-GCP, ומנוטרים 24/7 על ידי סופיה, קצינת הציות AI שלנו. אנחנו מבצעים גיבויים אוטומטיים יומיים, ושומרים audit logs מלאים של כל פעולה.'
    },
    {
      question: 'האם אני צריך כרטיס אשראי לניסיון החינם?',
      answer: 'לא. התחל את הניסיון ל-30 יום רק עם כתובת אימייל. לא נבקש כרטיס אשראי עד שתחליט להמשיך לאחר תקופת הניסיון. אתה יכול לבטל בכל עת ללא עלות.'
    },
    {
      question: 'האם אני יכול לבטל בכל עת?',
      answer: 'כן. אין חוזים, אין התחייבויות. בטל בלחיצה אחת מתוך הגדרות החשבון. אם תבטל, תוכל לייצא את כל הנתונים שלך (מטופלים, תורים, חשבוניות) לפני הביטול. נמחק את הנתונים שלך תוך 30 יום לפי דרישות HIPAA.'
    },
    {
      question: 'מה קורה לנתונים שלי אם אבטל?',
      answer: 'אתה יכול לייצא את כל הנתונים שלך (מטופלים, תורים, חשבוניות, דוחות) לפני הביטול. אנחנו נותנים לך 30 יום לייצא הכל. לאחר מכן, נמחק את הנתונים שלך לצמיתות לפי דרישות HIPAA. אין עלויות נסתרות או דמי ביטול.'
    },
    {
      question: 'כמה זמן לוקח להקים את המערכת?',
      answer: 'רוב המרפאות מוכנות לעבודה תוך פחות מ-10 דקות. התהליך כולל: (1) הרשמה (2 דקות), (2) ייבוא נתוני מטופלים (5 דקות), (3) חיבור יומן (2 דקות). צוות ההטמעה שלנו כאן לעזור אם צריך. אנחנו גם מציעים הדרכה מותאמת אישית לתוכנית Enterprise.'
    },
    {
      question: 'האם אני יכול לייבא את נתוני המטופלים הקיימים שלי?',
      answer: 'כן. אנחנו תומכים בייבוא CSV ויכולים לעזור לך להעביר נתונים מרוב תוכנות הדנטליות (Dentrix, Open Dental, CareStack, וכו\'). אם יש לך פורמט מיוחד, צוות התמיכה שלנו יעזור לך עם ההעברה.'
    },
    {
      question: 'מה קורה אם ה-AI לא יכול לענות על שאלה?',
      answer: 'ה-AI יעביר את השאלה לצוות שלך וילמד מהאינטראקציה. עם הזמן, הוא נהיה חכם יותר. בנוסף, אתה יכול להוסיף תשובות מותאמות אישית למקרים ספציפיים. כל סוכן AI משתפר כל הזמן מהשימוש שלך.'
    },
    {
      question: 'האם ההנחה למאמצים המוקדמים תקפה לכל החיים?',
      answer: 'כן! אם אתה אחת מ-10 המרפאות הראשונות, תקבל 20% הנחה לכל החיים - גם אם תשדרג תוכנית או תוסיף משתמשים. ההנחה נשארת איתך לתמיד. נותרו רק 3 מקומות!'
    },
    {
      question: 'איך אני יכול לדעת שהמערכת תעבוד למרפאה שלי?',
      answer: 'לכן אנחנו מציעים ניסיון חינם ל-30 יום ללא כרטיס אשראי. תוכל לנסות את כל 4 סוכני ה-AI, לייבא מטופלים אמיתיים, ולראות בדיוק איך המערכת עובדת במרפאה שלך. אם זה לא מתאים - פשוט תבטל. אין סיכון.'
    }
  ];

  const toggleFAQ = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-gray-100" dir="rtl">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-gray-100 text-gray-800 hover:bg-gray-100">
            שאלות נפוצות
          </Badge>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            שאלות שאנשים שואלים
          </h2>
          <p className="text-xl text-gray-600">
            מצא תשובות לשאלות הנפוצות ביותר על DentaFlow
          </p>
        </div>

        {/* FAQ Accordion */}
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <Card
              key={index}
              className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => toggleFAQ(index)}
            >
              <CardContent className="p-0">
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-bold text-gray-900 flex-1">
                      {faq.question}
                    </h3>
                    <div className="flex-shrink-0 mr-4">
                      {openIndex === index ? (
                        <ChevronUp className="h-5 w-5 text-gray-600" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-gray-600" />
                      )}
                    </div>
                  </div>

                  {openIndex === index && (
                    <div className="mt-4 text-gray-700 leading-relaxed border-t pt-4">
                      {faq.answer}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Still Have Questions CTA */}
        <div className="mt-16 text-center bg-white rounded-2xl p-8 shadow-lg">
          <h3 className="text-2xl font-bold text-gray-900 mb-3">
            עדיין יש לך שאלות?
          </h3>
          <p className="text-gray-600 mb-6">
            צוות התמיכה שלנו כאן לעזור. דבר איתנו או התחל ניסיון חינם ותראה בעצמך.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-8 py-3 rounded-full font-bold hover:from-blue-600 hover:to-blue-700 transition-colors">
              דבר עם המכירות
            </button>
            <button className="bg-gradient-to-r from-green-500 to-green-600 text-white px-8 py-3 rounded-full font-bold hover:from-green-600 hover:to-green-700 transition-colors">
              התחל ניסיון חינם
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

