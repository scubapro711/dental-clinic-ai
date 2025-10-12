import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Step1ClinicDetails from '@/components/onboarding/Step1ClinicDetails';
import Step2OwnerDetails from '@/components/onboarding/Step2OwnerDetails';
import BAASignature from '@/components/onboarding/BAASignature';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

/**
 * Clinic Onboarding Wizard
 * 
 * Multi-step registration flow for new dental clinics:
 * 1. Clinic Details
 * 2. Owner Details
 * 3. BAA Signature
 * 4. Complete & Login
 * 
 * Integrates with backend API: POST /organizations/register
 */
export default function ClinicOnboardingWizard() {
  const navigate = useNavigate();
  
  // Current step (1-4)
  const [currentStep, setCurrentStep] = useState(1);
  
  // Form data from all steps
  const [formData, setFormData] = useState({});
  
  // Registration state
  const [registering, setRegistering] = useState(false);
  const [error, setError] = useState('');
  const [organizationId, setOrganizationId] = useState(null);
  const [accessToken, setAccessToken] = useState(null);

  // Step 1: Clinic Details
  const handleStep1Next = (data) => {
    setFormData(prev => ({ ...prev, ...data }));
    setCurrentStep(2);
  };

  // Step 2: Owner Details
  const handleStep2Next = async (data) => {
    setFormData(prev => ({ ...prev, ...data }));
    
    // Combine all data and register organization
    const registrationData = {
      ...formData,
      ...data
    };
    
    await registerOrganization(registrationData);
  };

  const handleStep2Back = () => {
    setCurrentStep(1);
  };

  // Register organization with backend
  const registerOrganization = async (data) => {
    try {
      setRegistering(true);
      setError('');
      
      const response = await fetch('/api/v1/organizations/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }
      
      const result = await response.json();
      
      // Save organization ID and access token
      setOrganizationId(result.organization_id);
      setAccessToken(result.access_token);
      
      // Store access token in localStorage
      localStorage.setItem('access_token', result.access_token);
      
      // Move to BAA signature step
      setCurrentStep(3);
      
    } catch (err) {
      setError(err.message || 'שגיאה ברישום המרפאה');
      console.error('Registration error:', err);
    } finally {
      setRegistering(false);
    }
  };

  // Step 3: BAA Signature
  const handleBAAComplete = () => {
    // BAA signed successfully, move to completion
    setCurrentStep(4);
    
    // Wait 2 seconds then redirect to dashboard
    setTimeout(() => {
      navigate('/clinic');
    }, 2000);
  };

  const handleBAASkip = () => {
    // Not recommended, but allow skipping
    setCurrentStep(4);
    
    // Redirect to dashboard with warning
    setTimeout(() => {
      navigate('/clinic?baa_pending=true');
    }, 2000);
  };

  // Progress indicator
  const getProgressPercentage = () => {
    return (currentStep / 4) * 100;
  };

  const getStepLabel = (step) => {
    const labels = {
      1: 'פרטי מרפאה',
      2: 'פרטי בעלים',
      3: 'חתימה על BAA',
      4: 'השלמה'
    };
    return labels[step] || '';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
      <div className="max-w-5xl mx-auto py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            ברוכים הבאים ל-DentaFlow
          </h1>
          <p className="text-gray-600 text-lg">
            בואו נגדיר את המרפאה שלכם בכמה שלבים פשוטים
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-600">
              שלב {currentStep} מתוך 4
            </span>
            <span className="text-sm font-medium text-gray-600">
              {getStepLabel(currentStep)}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-gradient-to-r from-blue-600 to-purple-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${getProgressPercentage()}%` }}
            />
          </div>
          
          {/* Step indicators */}
          <div className="flex justify-between mt-4">
            {[1, 2, 3, 4].map((step) => (
              <div 
                key={step}
                className={`flex flex-col items-center ${
                  step <= currentStep ? 'text-blue-600' : 'text-gray-400'
                }`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold ${
                  step < currentStep 
                    ? 'bg-green-100 text-green-600' 
                    : step === currentStep
                    ? 'bg-blue-100 text-blue-600'
                    : 'bg-gray-100 text-gray-400'
                }`}>
                  {step < currentStep ? <CheckCircle2 className="w-5 h-5" /> : step}
                </div>
                <span className="text-xs mt-1 hidden sm:block">{getStepLabel(step)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Registering State */}
        {registering && (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-12 h-12 animate-spin text-blue-600 mb-4" />
            <p className="text-lg font-medium text-gray-700">יוצר את המרפאה שלך...</p>
            <p className="text-sm text-gray-500">זה ייקח רק כמה שניות</p>
          </div>
        )}

        {/* Step Components */}
        {!registering && (
          <>
            {currentStep === 1 && (
              <Step1ClinicDetails
                initialData={formData}
                onNext={handleStep1Next}
              />
            )}

            {currentStep === 2 && (
              <Step2OwnerDetails
                initialData={formData}
                onNext={handleStep2Next}
                onBack={handleStep2Back}
              />
            )}

            {currentStep === 3 && organizationId && (
              <BAASignature
                organizationId={organizationId}
                onComplete={handleBAAComplete}
                onSkip={handleBAASkip}
              />
            )}

            {currentStep === 4 && (
              <div className="flex flex-col items-center justify-center py-12">
                <div className="bg-green-100 p-6 rounded-full mb-6">
                  <CheckCircle2 className="w-16 h-16 text-green-600" />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  ההרשמה הושלמה בהצלחה! 🎉
                </h2>
                <p className="text-lg text-gray-600 mb-6">
                  מעביר אותך לדשבורד...
                </p>
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              </div>
            )}
          </>
        )}

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-gray-500">
          <p>
            כבר יש לך חשבון?{' '}
            <a href="/login" className="text-blue-600 hover:underline font-medium">
              התחבר כאן
            </a>
          </p>
          <p className="mt-2">
            צריך עזרה?{' '}
            <a href="mailto:support@dentaflow.co.il" className="text-blue-600 hover:underline">
              צור קשר עם התמיכה
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

