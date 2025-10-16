import { useState } from 'react';
import { Check, FileSignature, Shield, Building2, Users, CreditCard } from 'lucide-react';
import DigitalSignature from './DigitalSignature';

/**
 * Clinic Onboarding Component
 * 
 * Multi-step onboarding process for new clinics:
 * 1. Welcome & Overview
 * 2. Sign BAA (Business Associate Agreement) - REQUIRED for HIPAA
 * 3. Sign DPA (Data Processing Agreement) - REQUIRED for GDPR
 * 4. Clinic Setup (users, settings)
 * 5. Choose Plan & Payment
 */
export default function ClinicOnboarding() {
  const [currentStep, setCurrentStep] = useState(1);
  const [signatures, setSignatures] = useState({
    baa: null,
    dpa: null
  });

  const steps = [
    { id: 1, name: 'ברוכים הבאים', icon: Building2 },
    { id: 2, name: 'חתימה על BAA', icon: FileSignature },
    { id: 3, name: 'חתימה על DPA', icon: Shield },
    { id: 4, name: 'הגדרת מרפאה', icon: Users },
    { id: 5, name: 'בחירת תוכנית', icon: CreditCard }
  ];

  const handleBAASign = (signatureData) => {
    setSignatures({ ...signatures, baa: signatureData });
    setCurrentStep(3);
  };

  const handleDPASign = (signatureData) => {
    setSignatures({ ...signatures, dpa: signatureData });
    setCurrentStep(4);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Progress Bar */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <nav aria-label="Progress">
            <ol className="flex items-center justify-between">
              {steps.map((step, stepIdx) => (
                <li key={step.id} className="relative flex-1">
                  {stepIdx !== 0 && (
                    <div
                      className={`absolute top-5 left-0 -ml-px h-0.5 w-full ${
                        step.id <= currentStep ? 'bg-blue-600' : 'bg-gray-200'
                      }`}
                      style={{ right: '50%' }}
                    />
                  )}
                  <div className="group relative flex flex-col items-center">
                    <span
                      className={`flex h-10 w-10 items-center justify-center rounded-full border-2 transition-colors ${
                        step.id < currentStep
                          ? 'border-blue-600 bg-blue-600'
                          : step.id === currentStep
                          ? 'border-blue-600 bg-white'
                          : 'border-gray-300 bg-white'
                      }`}
                    >
                      {step.id < currentStep ? (
                        <Check className="h-5 w-5 text-white" />
                      ) : (
                        <step.icon
                          className={`h-5 w-5 ${
                            step.id === currentStep ? 'text-blue-600' : 'text-gray-400'
                          }`}
                        />
                      )}
                    </span>
                    <span
                      className={`mt-2 text-xs font-medium ${
                        step.id <= currentStep ? 'text-blue-600' : 'text-gray-500'
                      }`}
                    >
                      {step.name}
                    </span>
                  </div>
                </li>
              ))}
            </ol>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Step 1: Welcome */}
        {currentStep === 1 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8" dir="rtl">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              ברוכים הבאים ל-DentaFlow! 🎉
            </h1>
            <p className="text-lg text-gray-600 mb-6">
              אנחנו שמחים שבחרת להצטרף לפלטפורמה המתקדמת ביותר לניהול מרפאות שיניים.
            </p>

            <div className="bg-blue-50 border-r-4 border-blue-600 p-6 rounded mb-8">
              <h3 className="font-bold text-blue-900 mb-2">לפני שנתחיל</h3>
              <p className="text-blue-800">
                כדי לעמוד בדרישות HIPAA ו-GDPR, נצטרך ממך לחתום על 2 מסמכים משפטיים:
              </p>
              <ul className="mt-3 space-y-2 text-blue-800">
                <li className="flex items-center gap-2">
                  <FileSignature className="h-5 w-5" />
                  <span><strong>BAA</strong> (Business Associate Agreement) - הסכם שותף עסקי ל-HIPAA</span>
                </li>
                <li className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  <span><strong>DPA</strong> (Data Processing Agreement) - הסכם עיבוד נתונים ל-GDPR</span>
                </li>
              </ul>
            </div>

            <div className="space-y-4 mb-8">
              <h3 className="font-bold text-gray-900">מה יקרה בתהליך ההצטרפות?</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">📝 חתימה על מסמכים</h4>
                  <p className="text-sm text-gray-600">חתימה דיגיטלית על BAA ו-DPA (2-3 דקות)</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">⚙️ הגדרת מרפאה</h4>
                  <p className="text-sm text-gray-600">הוספת משתמשים והגדרות בסיסיות (5 דקות)</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">💳 בחירת תוכנית</h4>
                  <p className="text-sm text-gray-600">בחירת תוכנית והזנת פרטי תשלום (2 דקות)</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">🚀 התחלת שימוש</h4>
                  <p className="text-sm text-gray-600">30 יום ניסיון חינם, ללא כרטיס אשראי!</p>
                </div>
              </div>
            </div>

            <button
              onClick={() => setCurrentStep(2)}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition-colors"
            >
              בואו נתחיל →
            </button>
          </div>
        )}

        {/* Step 2: Sign BAA */}
        {currentStep === 2 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8" dir="rtl">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              חתימה על BAA (Business Associate Agreement)
            </h2>
            <p className="text-gray-600 mb-6">
              ה-BAA הוא הסכם משפטי הנדרש על פי HIPAA. הוא מגדיר את האחריות שלנו בהגנה על מידע רפואי מוגן (PHI).
            </p>

            <div className="bg-yellow-50 border-r-4 border-yellow-600 p-6 rounded mb-6">
              <p className="text-sm text-yellow-900">
                <strong>חשוב:</strong> חתימה על מסמך זה היא חובה חוקית לפי HIPAA. ללא חתימה, לא נוכל לספק לך את השירות.
              </p>
            </div>

            <DigitalSignature
              documentType="BAA"
              documentTitle="Business Associate Agreement (BAA)"
              documentUrl="/legal/baa"
              onSign={handleBAASign}
            />
          </div>
        )}

        {/* Step 3: Sign DPA */}
        {currentStep === 3 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8" dir="rtl">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              חתימה על DPA (Data Processing Agreement)
            </h2>
            <p className="text-gray-600 mb-6">
              ה-DPA הוא הסכם הנדרש על פי GDPR (התקנה האירופית להגנת מידע). הוא מגדיר איך אנחנו מעבדים ומגנים על נתונים אישיים.
            </p>

            <div className="bg-blue-50 border-r-4 border-blue-600 p-6 rounded mb-6">
              <p className="text-sm text-blue-900">
                <strong>למה DPA?</strong> גם אם אין לך לקוחות באירופה כרגע, זה מבטיח שאנחנו עומדים בסטנדרטים הגבוהים ביותר של הגנת מידע.
              </p>
            </div>

            <DigitalSignature
              documentType="DPA"
              documentTitle="Data Processing Agreement (DPA)"
              documentUrl="/legal/dpa"
              onSign={handleDPASign}
            />
          </div>
        )}

        {/* Step 4: Clinic Setup */}
        {currentStep === 4 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8" dir="rtl">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              הגדרת המרפאה שלך
            </h2>
            <p className="text-gray-600 mb-6">
              בואו נגדיר את המרפאה שלך. תוכל לשנות את ההגדרות האלה בכל עת.
            </p>

            {/* Clinic setup form will go here */}
            <div className="text-center py-12 text-gray-500">
              <p>Clinic setup form - Coming soon</p>
              <button
                onClick={() => setCurrentStep(5)}
                className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
              >
                המשך →
              </button>
            </div>
          </div>
        )}

        {/* Step 5: Choose Plan */}
        {currentStep === 5 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8" dir="rtl">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              בחירת תוכנית
            </h2>
            <p className="text-gray-600 mb-6">
              בחר את התוכנית המתאימה למרפאה שלך. תוכל לשנות בכל עת.
            </p>

            {/* Pricing plans will go here */}
            <div className="text-center py-12 text-gray-500">
              <p>Pricing plans - Coming soon</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

