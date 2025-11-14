import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
import API_CONFIG from '@/config/api';
  CheckCircle2, 
  Circle, 
  Building2, 
  User, 
  FileText, 
  Mail, 
  Users, 
  UserPlus,
  Loader2,
  ArrowRight,
  Sparkles
} from 'lucide-react';

/**
 * Onboarding Dashboard
 * 
 * Shows onboarding progress and guides new clinics through setup:
 * 1. ✅ Clinic details (completed during registration)
 * 2. ✅ Owner details (completed during registration)
 * 3. ⚠️ BAA signature
 * 4. ⚠️ Email verification
 * 5. ⚠️ Invite team members
 * 6. ⚠️ Add first patient
 * 
 * Fetches progress from backend and provides quick actions.
 */
export default function OnboardingDashboard() {
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState({
    clinic_details: true,
    owner_details: true,
    baa_signed: false,
    email_verified: false,
    team_invited: false,
    first_patient: false
  });
  
  const [organizationId, setOrganizationId] = useState(null);
  const [userEmail, setUserEmail] = useState(null);

  useEffect(() => {
    loadOnboardingProgress();
  }, []);

  const loadOnboardingProgress = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('access_token');
      if (!token) {
        navigate('/login');
        return;
      }
      
      // Get current user info
      const userResponse = await fetch(API_CONFIG.endpoint('auth/me'), {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!userResponse.ok) {
        throw new Error('Failed to load user info');
      }
      
      const userData = await userResponse.json();
      setUserEmail(userData.email);
      setOrganizationId(userData.organization_id);
      
      // Check BAA status
      if (userData.organization_id) {
        const baaResponse = await fetch(API_CONFIG.endpoint('baa/status/${userData.organization_id}'), {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (baaResponse.ok) {
          const baaData = await baaResponse.json();
          setProgress(prev => ({
            ...prev,
            baa_signed: baaData.signed
          }));
        }
      }
      
      // Check email verification status
      const verificationResponse = await fetch(API_CONFIG.endpoint('auth/verification-status'), {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (verificationResponse.ok) {
        const verificationData = await verificationResponse.json();
        setProgress(prev => ({
          ...prev,
          email_verified: verificationData.is_verified
        }));
      }
      
      // TODO: Check team members and patients
      // For now, these remain false
      
    } catch (err) {
      console.error('Failed to load onboarding progress:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateProgress = () => {
    const total = Object.keys(progress).length;
    const completed = Object.values(progress).filter(v => v).length;
    return Math.round((completed / total) * 100);
  };

  const getNextStep = () => {
    if (!progress.baa_signed) return 'baa';
    if (!progress.email_verified) return 'email';
    if (!progress.team_invited) return 'team';
    if (!progress.first_patient) return 'patient';
    return null;
  };

  const handleAction = (action) => {
    switch (action) {
      case 'baa':
        navigate(`/onboarding/baa?org=${organizationId}`);
        break;
      case 'email':
        navigate('/onboarding/verify-email');
        break;
      case 'team':
        navigate('/clinic/settings/team');
        break;
      case 'patient':
        navigate('/clinic/patients/new');
        break;
      default:
        break;
    }
  };

  const handleSkipOnboarding = () => {
    navigate('/clinic');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <Loader2 className="w-12 h-12 animate-spin text-blue-600" />
      </div>
    );
  }

  const progressPercentage = calculateProgress();
  const nextStep = getNextStep();
  const isComplete = progressPercentage === 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
      <div className="max-w-4xl mx-auto py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-full mb-4">
            <Sparkles className="w-5 h-5" />
            <span className="font-semibold">ברוכים הבאים ל-DentaFlow!</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            בואו נגדיר את המרפאה שלכם
          </h1>
          <p className="text-gray-600 text-lg">
            {isComplete 
              ? 'כל הכבוד! סיימתם את תהליך ההגדרה 🎉'
              : 'עוד כמה שלבים קטנים ותהיו מוכנים להתחיל'
            }
          </p>
        </div>

        {/* Progress Card */}
        <Card className="mb-8 border-2 border-blue-200 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>התקדמות ההגדרה</span>
              <span className="text-3xl font-bold text-blue-600">{progressPercentage}%</span>
            </CardTitle>
            <CardDescription>
              השלמתם {Object.values(progress).filter(v => v).length} מתוך {Object.keys(progress).length} שלבים
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
              <div 
                className="bg-gradient-to-r from-blue-600 to-purple-600 h-4 rounded-full transition-all duration-500"
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Checklist */}
        <div className="space-y-4 mb-8">
          {/* Clinic Details */}
          <ChecklistItem
            icon={Building2}
            title="פרטי מרפאה"
            description="שם, כתובת וטלפון המרפאה"
            completed={progress.clinic_details}
            disabled
          />

          {/* Owner Details */}
          <ChecklistItem
            icon={User}
            title="פרטי בעלים"
            description="פרטי המנהל הראשי של המרפאה"
            completed={progress.owner_details}
            disabled
          />

          {/* BAA Signature */}
          <ChecklistItem
            icon={FileText}
            title="חתימה על הסכם BAA"
            description="הסכם שותף עסקי (דרישה של HIPAA)"
            completed={progress.baa_signed}
            action={() => handleAction('baa')}
            actionLabel="חתום עכשיו"
            important={!progress.baa_signed}
          />

          {/* Email Verification */}
          <ChecklistItem
            icon={Mail}
            title="אימות אימייל"
            description="אימות כתובת האימייל שלך"
            completed={progress.email_verified}
            action={() => handleAction('email')}
            actionLabel="אמת עכשיו"
          />

          {/* Team Invitation */}
          <ChecklistItem
            icon={Users}
            title="הזמנת צוות"
            description="הזמן רופאים ועובדים נוספים"
            completed={progress.team_invited}
            action={() => handleAction('team')}
            actionLabel="הזמן צוות"
            optional
          />

          {/* First Patient */}
          <ChecklistItem
            icon={UserPlus}
            title="מטופל ראשון"
            description="הוסף את המטופל הראשון שלך"
            completed={progress.first_patient}
            action={() => handleAction('patient')}
            actionLabel="הוסף מטופל"
            optional
          />
        </div>

        {/* Next Step Alert */}
        {!isComplete && nextStep && (
          <Alert className="mb-6 bg-blue-50 border-blue-200">
            <AlertDescription className="flex items-center justify-between" dir="rtl">
              <span className="text-blue-900 font-medium">
                השלב הבא: {getNextStepLabel(nextStep)}
              </span>
              <Button 
                onClick={() => handleAction(nextStep)}
                className="bg-blue-600 hover:bg-blue-700"
                size="sm"
              >
                התחל
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Complete Alert */}
        {isComplete && (
          <Alert className="mb-6 bg-green-50 border-green-200">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            <AlertDescription className="text-green-900 font-medium" dir="rtl">
              מעולה! סיימתם את תהליך ההגדרה. אתם מוכנים להתחיל להשתמש במערכת! 🎉
            </AlertDescription>
          </Alert>
        )}

        {/* Actions */}
        <div className="flex gap-4">
          <Button
            onClick={handleSkipOnboarding}
            variant="outline"
            className="flex-1"
          >
            {isComplete ? 'עבור לדשבורד' : 'דלג לעכשיו'}
          </Button>
          {!isComplete && nextStep && (
            <Button
              onClick={() => handleAction(nextStep)}
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              המשך הגדרה
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

// Checklist Item Component
function ChecklistItem({ 
  icon: Icon, 
  title, 
  description, 
  completed, 
  action, 
  actionLabel = 'התחל',
  disabled = false,
  optional = false,
  important = false
}) {
  return (
    <Card className={`transition-all ${
      completed 
        ? 'border-green-200 bg-green-50' 
        : important
        ? 'border-orange-200 bg-orange-50'
        : 'border-gray-200 hover:border-blue-200'
    }`}>
      <CardContent className="flex items-center gap-4 p-4">
        {/* Icon */}
        <div className={`p-3 rounded-lg ${
          completed 
            ? 'bg-green-100' 
            : important
            ? 'bg-orange-100'
            : 'bg-blue-100'
        }`}>
          {completed ? (
            <CheckCircle2 className="w-6 h-6 text-green-600" />
          ) : (
            <Icon className={`w-6 h-6 ${
              important ? 'text-orange-600' : 'text-blue-600'
            }`} />
          )}
        </div>

        {/* Content */}
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            {title}
            {optional && (
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                אופציונלי
              </span>
            )}
            {important && (
              <span className="text-xs bg-orange-100 text-orange-600 px-2 py-0.5 rounded">
                חשוב
              </span>
            )}
          </h3>
          <p className="text-sm text-gray-600">{description}</p>
        </div>

        {/* Status/Action */}
        <div>
          {completed ? (
            <span className="text-green-600 font-medium text-sm">✓ הושלם</span>
          ) : disabled ? (
            <Circle className="w-6 h-6 text-gray-300" />
          ) : action ? (
            <Button
              onClick={action}
              size="sm"
              variant={important ? "default" : "outline"}
              className={important ? "bg-orange-600 hover:bg-orange-700" : ""}
            >
              {actionLabel}
            </Button>
          ) : (
            <Circle className="w-6 h-6 text-gray-400" />
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// Helper function to get next step label
function getNextStepLabel(step) {
  const labels = {
    baa: 'חתימה על הסכם BAA',
    email: 'אימות אימייל',
    team: 'הזמנת צוות',
    patient: 'הוספת מטופל ראשון'
  };
  return labels[step] || '';
}

