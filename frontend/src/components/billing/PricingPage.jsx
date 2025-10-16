import React, { useState, useEffect } from 'react';
import { 
  Check, X, Sparkles, Users, FileText, Zap, 
  Shield, TrendingUp, Crown, Star, ArrowLeft
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { API_BASE_URL } from '@/config';

/**
 * Pricing Page Component
 * 
 * Displays available subscription plans for clinics to choose from.
 * Features:
 * - Three pricing tiers (Basic, Professional, Enterprise)
 * - 30-day free trial
 * - Early adopter discount (20% off for first 10 clinics)
 * - Feature comparison
 * - Integration with Stripe for payment
 */
export default function PricingPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [plans, setPlans] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [earlyAdopterAvailable, setEarlyAdopterAvailable] = useState(false);
  const [processingSubscription, setProcessingSubscription] = useState(false);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/plans`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPlans(data.plans || []);
        setEarlyAdopterAvailable(data.early_adopter_available || false);
      } else {
        console.error('Failed to fetch plans');
      }
    } catch (error) {
      console.error('Error fetching plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlan = async (plan) => {
    if (processingSubscription) return;

    setProcessingSubscription(true);
    setSelectedPlan(plan);

    try {
      // Create subscription with trial
      const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          plan_id: plan.id,
          apply_early_adopter_discount: earlyAdopterAvailable
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Redirect to Stripe Checkout
        if (data.checkout_url) {
          window.location.href = data.checkout_url;
        } else {
          // Subscription created successfully without payment (trial)
          navigate('/clinic/subscription');
        }
      } else {
        const error = await response.json();
        alert(`Failed to create subscription: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error creating subscription:', error);
      alert('Failed to create subscription. Please try again.');
    } finally {
      setProcessingSubscription(false);
    }
  };

  const getPlanIcon = (planName) => {
    const name = planName?.toLowerCase() || '';
    if (name.includes('basic')) return <Zap className="h-6 w-6" />;
    if (name.includes('professional')) return <TrendingUp className="h-6 w-6" />;
    if (name.includes('enterprise')) return <Crown className="h-6 w-6" />;
    return <Star className="h-6 w-6" />;
  };

  const getPlanColor = (planName) => {
    const name = planName?.toLowerCase() || '';
    if (name.includes('basic')) return 'blue';
    if (name.includes('professional')) return 'purple';
    if (name.includes('enterprise')) return 'gradient';
    return 'gray';
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('he-IL', {
      style: 'currency',
      currency: 'ILS',
      minimumFractionDigits: 0
    }).format(price);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">טוען תוכניות...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50" dir="rtl">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">בחר תוכנית מנוי</h1>
                <p className="text-sm text-gray-500">התחל עם ניסיון חינם ל-30 יום</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Early Adopter Alert */}
        {earlyAdopterAvailable && (
          <Alert className="mb-8 border-purple-200 bg-gradient-to-r from-purple-50 to-pink-50">
            <Sparkles className="h-5 w-5 text-purple-600" />
            <AlertDescription className="text-purple-900">
              <strong>הצעה מיוחדת למאמצים המוקדמים!</strong> קבל 20% הנחה לכל החיים. 
              מוגבל ל-10 המרפאות הראשונות בלבד! 🎉
            </AlertDescription>
          </Alert>
        )}

        {/* Trial Info */}
        <div className="text-center mb-12">
          <Badge className="mb-4 bg-green-100 text-green-800 hover:bg-green-100">
            <Shield className="h-3 w-3 ml-1" />
            ניסיון חינם ל-30 יום
          </Badge>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            התחל עם DentaFlow היום
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            כל התוכניות כוללות ניסיון חינם ל-30 יום. לא נדרש כרטיס אשראי להתחלה.
            החיוב יתחיל רק לאחר תום תקופת הניסיון.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {plans.map((plan) => {
            const color = getPlanColor(plan.name);
            const isPopular = plan.name?.toLowerCase().includes('professional');
            const discountedPrice = earlyAdopterAvailable 
              ? plan.monthly_price * 0.8 
              : plan.monthly_price;

            return (
              <Card 
                key={plan.id}
                className={`relative hover:shadow-xl transition-all ${
                  isPopular ? 'border-purple-500 border-2 scale-105' : ''
                }`}
              >
                {isPopular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-purple-600 hover:bg-purple-600 text-white">
                      <Star className="h-3 w-3 ml-1" />
                      הכי פופולרי
                    </Badge>
                  </div>
                )}

                <CardHeader className="text-center">
                  <div className={`w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center ${
                    color === 'blue' ? 'bg-blue-100 text-blue-600' :
                    color === 'purple' ? 'bg-purple-100 text-purple-600' :
                    color === 'gradient' ? 'bg-gradient-to-br from-purple-500 to-pink-500 text-white' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {getPlanIcon(plan.name)}
                  </div>
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>

                <CardContent className="space-y-6">
                  {/* Pricing */}
                  <div className="text-center">
                    {earlyAdopterAvailable && (
                      <div className="text-sm text-gray-500 line-through mb-1">
                        {formatPrice(plan.monthly_price)}/חודש
                      </div>
                    )}
                    <div className="text-4xl font-bold text-gray-900">
                      {formatPrice(discountedPrice)}
                    </div>
                    <div className="text-sm text-gray-500">לחודש</div>
                    {earlyAdopterAvailable && (
                      <Badge className="mt-2 bg-green-100 text-green-800 hover:bg-green-100">
                        חסוך 20%
                      </Badge>
                    )}
                  </div>

                  {/* Features */}
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-gray-500" />
                      <span className="text-sm">עד {plan.max_users} משתמשים</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-gray-500" />
                      <span className="text-sm">עד {plan.max_patients} מטופלים</span>
                    </div>
                    {plan.features && Object.entries(plan.features).map(([key, value]) => (
                      <div key={key} className="flex items-center gap-2">
                        {value ? (
                          <Check className="h-4 w-4 text-green-600" />
                        ) : (
                          <X className="h-4 w-4 text-gray-300" />
                        )}
                        <span className="text-sm">{key}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>

                <CardFooter>
                  <Button
                    className={`w-full ${
                      isPopular 
                        ? 'bg-purple-600 hover:bg-purple-700' 
                        : 'bg-gray-900 hover:bg-gray-800'
                    }`}
                    onClick={() => handleSelectPlan(plan)}
                    disabled={processingSubscription}
                  >
                    {processingSubscription && selectedPlan?.id === plan.id ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white ml-2"></div>
                        מעבד...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4 ml-2" />
                        התחל ניסיון חינם
                      </>
                    )}
                  </Button>
                </CardFooter>
              </Card>
            );
          })}
        </div>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">שאלות נפוצות</h3>
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">מה קורה אחרי תקופת הניסיון?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  אחרי 30 יום, נשלח לך התראה בדוא"ל ונחייב את כרטיס האשראי שלך אוטומטית.
                  תוכל לבטל בכל עת לפני תום תקופת הניסיון ללא חיוב.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">האם אוכל לשדרג או להוריד דרגה?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  כן! תוכל לשנות את התוכנית שלך בכל עת. השינוי ייכנס לתוקף מיד והחיוב יותאם באופן יחסי.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">מה כלול בהנחה למאמצים המוקדמים?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  10 המרפאות הראשונות יקבלו 20% הנחה לכל החיים! ההנחה תישאר גם אם תשדרג את התוכנית שלך.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}

