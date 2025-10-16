import { useState } from 'react';
import { ArrowLeft, Shield, Star, Users, TrendingUp } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

/**
 * Hero Section Component
 * 
 * The main landing section that emphasizes DentaFlow's unique value proposition:
 * - 4 specialized AI agents (unique competitive advantage)
 * - HIPAA compliance included
 * - 30-day free trial
 * - Early adopter discount
 */
export default function HeroSection() {
  const [videoPlaying, setVideoPlaying] = useState(false);

  const handleStartTrial = () => {
    // Navigate to signup
    window.location.href = '/signup';
  };

  const handleWatchDemo = () => {
    setVideoPlaying(true);
    // Open video modal
  };

  return (
    <section className="relative min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      {/* Content Container */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          
          {/* Left Column - Text Content */}
          <div className="text-right" dir="rtl">
            {/* Trust Badges */}
            <div className="flex flex-wrap gap-2 justify-end mb-6">
              <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
                <Shield className="h-3 w-3 ml-1" />
                תואם HIPAA
              </Badge>
              <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100">
                <Star className="h-3 w-3 ml-1" />
                דירוג 4.9/5
              </Badge>
              <Badge className="bg-purple-100 text-purple-800 hover:bg-purple-100">
                <Users className="h-3 w-3 ml-1" />
                50+ מרפאות
              </Badge>
            </div>

            {/* Main Headline */}
            <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              הפלטפורמה הדנטלית היחידה עם{' '}
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                4 מומחי AI
              </span>
              {' '}שעובדים 24/7
            </h1>

            {/* Subheadline */}
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              הכירו את <strong>אלכס, שרה, מרקוס וסופיה</strong> - צוות ה-AI שלכם לקבלת קהל, 
              טיפול במטופלים, ניהול כספים וציות רגולטורי. הכל תואם HIPAA, הכל כלול.
            </p>

            {/* Key Benefits */}
            <div className="grid grid-cols-2 gap-4 mb-8">
              <div className="flex items-center gap-2 bg-white/60 backdrop-blur-sm rounded-lg p-4">
                <div className="bg-blue-100 rounded-full p-2">
                  <TrendingUp className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">10+</div>
                  <div className="text-sm text-gray-600">שעות חיסכון בשבוע</div>
                </div>
              </div>
              
              <div className="flex items-center gap-2 bg-white/60 backdrop-blur-sm rounded-lg p-4">
                <div className="bg-green-100 rounded-full p-2">
                  <Shield className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">95%</div>
                  <div className="text-sm text-gray-600">שביעות רצון מטופלים</div>
                </div>
              </div>
            </div>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-4 justify-end">
              <Button 
                size="lg" 
                className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white text-lg px-8 py-6"
                onClick={handleStartTrial}
              >
                התחל ניסיון חינם ל-30 יום
                <ArrowLeft className="mr-2 h-5 w-5" />
              </Button>
              
              <Button 
                size="lg" 
                variant="outline" 
                className="border-2 border-purple-600 text-purple-600 hover:bg-purple-50 text-lg px-8 py-6"
                onClick={handleWatchDemo}
              >
                צפה בהדגמה
              </Button>
            </div>

            {/* Subtext */}
            <p className="text-sm text-gray-500 mt-4">
              ללא כרטיס אשראי • ביטול בכל עת • תואם HIPAA מיום אחד
            </p>

            {/* Early Adopter Alert */}
            <div className="mt-8 bg-gradient-to-r from-purple-100 to-pink-100 border border-purple-200 rounded-lg p-4">
              <div className="flex items-center gap-2 justify-end">
                <div className="text-right">
                  <div className="font-bold text-purple-900">🎉 הצעה מיוחדת למאמצים המוקדמים!</div>
                  <div className="text-sm text-purple-700">
                    20% הנחה לכל החיים • נותרו רק 3 מקומות
                  </div>
                </div>
                <div className="bg-purple-600 text-white rounded-full px-3 py-1 text-sm font-bold">
                  חדש
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Visual */}
          <div className="relative">
            {/* Main Visual - AI Agents Illustration */}
            <div className="relative bg-white rounded-2xl shadow-2xl p-8">
              {/* Agent Cards */}
              <div className="grid grid-cols-2 gap-4">
                {/* Alex */}
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 border-2 border-blue-200">
                  <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-2">
                    A
                  </div>
                  <div className="font-bold text-gray-900">אלכס</div>
                  <div className="text-xs text-gray-600">קבלת קהל AI</div>
                  <div className="mt-2 text-xs text-gray-500">
                    ✓ קביעת תורים 24/7<br/>
                    ✓ תזכורות אוטומטיות
                  </div>
                </div>

                {/* Sarah */}
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 border-2 border-green-200">
                  <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-2">
                    S
                  </div>
                  <div className="font-bold text-gray-900">שרה</div>
                  <div className="text-xs text-gray-600">עוזרת דנטלית AI</div>
                  <div className="mt-2 text-xs text-gray-500">
                    ✓ מענה על שאלות<br/>
                    ✓ הדרכת מטופלים
                  </div>
                </div>

                {/* Marcus */}
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 border-2 border-purple-200">
                  <div className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-2">
                    M
                  </div>
                  <div className="font-bold text-gray-900">מרקוס</div>
                  <div className="text-xs text-gray-600">CFO AI</div>
                  <div className="mt-2 text-xs text-gray-500">
                    ✓ מעקב הכנסות<br/>
                    ✓ דוחות פיננסיים
                  </div>
                  <Badge className="mt-2 bg-yellow-100 text-yellow-800 text-xs">
                    ייחודי!
                  </Badge>
                </div>

                {/* Sophia */}
                <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4 border-2 border-orange-200">
                  <div className="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-2">
                    S
                  </div>
                  <div className="font-bold text-gray-900">סופיה</div>
                  <div className="text-xs text-gray-600">קצינת ציות AI</div>
                  <div className="mt-2 text-xs text-gray-500">
                    ✓ ניטור HIPAA<br/>
                    ✓ דוחות ביקורת
                  </div>
                  <Badge className="mt-2 bg-yellow-100 text-yellow-800 text-xs">
                    ייחודי!
                  </Badge>
                </div>
              </div>

              {/* Activity Indicator */}
              <div className="mt-6 bg-gray-50 rounded-lg p-3">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <div className="flex -space-x-2">
                    <div className="w-6 h-6 bg-blue-500 rounded-full border-2 border-white"></div>
                    <div className="w-6 h-6 bg-green-500 rounded-full border-2 border-white"></div>
                    <div className="w-6 h-6 bg-purple-500 rounded-full border-2 border-white"></div>
                    <div className="w-6 h-6 bg-orange-500 rounded-full border-2 border-white"></div>
                  </div>
                  <div className="flex-1 text-right">
                    <div className="font-semibold text-gray-900">4 סוכנים פעילים</div>
                    <div className="text-xs text-gray-500">עובדים עבורך עכשיו</div>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-xs text-green-600 font-semibold">פעיל</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Floating Stats */}
            <div className="absolute -bottom-4 -left-4 bg-white rounded-xl shadow-lg p-4 border border-gray-200">
              <div className="flex items-center gap-3">
                <div className="bg-green-100 rounded-full p-2">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">40%</div>
                  <div className="text-xs text-gray-600">הפחתת עלויות אדמין</div>
                </div>
              </div>
            </div>

            <div className="absolute -top-4 -right-4 bg-white rounded-xl shadow-lg p-4 border border-gray-200">
              <div className="flex items-center gap-3">
                <div className="bg-blue-100 rounded-full p-2">
                  <Shield className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">100%</div>
                  <div className="text-xs text-gray-600">ציות HIPAA</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="text-gray-400 text-sm">גלול למטה</div>
        <div className="w-6 h-10 border-2 border-gray-300 rounded-full mx-auto mt-2">
          <div className="w-2 h-2 bg-gray-400 rounded-full mx-auto mt-2 animate-pulse"></div>
        </div>
      </div>
    </section>
  );
}

