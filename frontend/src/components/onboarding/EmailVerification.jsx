import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Mail, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';

/**
 * Email Verification Component
 * 
 * Displays 6-digit code input for email verification.
 * Integrates with backend API: /api/v1/auth/verify-email
 * 
 * Props:
 * - email: Email address to verify
 * - onComplete: Callback when verification is successful
 * - onSkip: Optional callback to skip verification
 */
export default function EmailVerification({ email, onComplete, onSkip }) {
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  
  // Refs for input fields
  const inputRefs = useRef([]);

  // Countdown timer for resend cooldown
  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => {
        setResendCooldown(resendCooldown - 1);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCooldown]);

  // Auto-send verification email on mount
  useEffect(() => {
    if (email) {
      sendVerificationEmail();
    }
  }, [email]);

  const sendVerificationEmail = async () => {
    try {
      setResending(true);
      setError('');
      
      const response = await fetch('/api/v1/auth/resend-verification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email })
      });
      
      if (!response.ok) {
        throw new Error('Failed to send verification email');
      }
      
      // Set cooldown for 60 seconds
      setResendCooldown(60);
      
    } catch (err) {
      setError('שגיאה בשליחת קוד אימות');
      console.error('Send verification error:', err);
    } finally {
      setResending(false);
    }
  };

  const handleCodeChange = (index, value) => {
    // Only allow digits
    if (value && !/^\d$/.test(value)) {
      return;
    }
    
    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);
    
    // Clear error
    setError('');
    
    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
    
    // Auto-submit when all 6 digits entered
    if (newCode.every(digit => digit !== '') && index === 5) {
      verifyCode(newCode.join(''));
    }
  };

  const handleKeyDown = (index, e) => {
    // Handle backspace
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    
    // Handle arrow keys
    if (e.key === 'ArrowLeft' && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
    if (e.key === 'ArrowRight' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').trim();
    
    // Only accept 6 digits
    if (/^\d{6}$/.test(pastedData)) {
      const newCode = pastedData.split('');
      setCode(newCode);
      
      // Focus last input
      inputRefs.current[5]?.focus();
      
      // Auto-verify
      verifyCode(pastedData);
    }
  };

  const verifyCode = async (codeString) => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('/api/v1/auth/verify-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          token: codeString // Backend expects "token" field
        })
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Verification failed');
      }
      
      const data = await response.json();
      setSuccess(true);
      
      // Wait 2 seconds then call onComplete
      setTimeout(() => {
        onComplete(data);
      }, 2000);
      
    } catch (err) {
      setError(err.message || 'קוד אימות שגוי או פג תוקף');
      // Clear code on error
      setCode(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const codeString = code.join('');
    
    if (codeString.length !== 6) {
      setError('נא למלא את כל 6 הספרות');
      return;
    }
    
    verifyCode(codeString);
  };

  const handleResend = async () => {
    if (resendCooldown > 0) return;
    
    // Clear code
    setCode(['', '', '', '', '', '']);
    inputRefs.current[0]?.focus();
    
    await sendVerificationEmail();
  };

  // Success state
  if (success) {
    return (
      <Card className="w-full max-w-md mx-auto border-green-200 bg-green-50">
        <CardHeader>
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-8 h-8 text-green-600" />
            <div>
              <CardTitle className="text-green-900">האימייל אומת בהצלחה!</CardTitle>
              <CardDescription className="text-green-700">
                החשבון שלך מופעל ומוכן לשימוש
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Alert className="bg-white border-green-300">
            <AlertDescription className="text-green-900">
              מעביר אותך להמשך...
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="bg-blue-100 p-3 rounded-lg">
            <Mail className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <CardTitle>אימות אימייל</CardTitle>
            <CardDescription>
              שלחנו קוד בן 6 ספרות ל-{email}
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Code Input */}
          <div className="space-y-2">
            <div className="flex gap-2 justify-center" dir="ltr">
              {code.map((digit, index) => (
                <Input
                  key={index}
                  ref={el => inputRefs.current[index] = el}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleCodeChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  onPaste={handlePaste}
                  disabled={loading || resending}
                  className="w-12 h-14 text-center text-2xl font-bold"
                  autoFocus={index === 0}
                />
              ))}
            </div>
            <p className="text-sm text-gray-500 text-center">
              הזן את קוד האימות בן 6 הספרות
            </p>
          </div>

          {/* Resend Button */}
          <div className="text-center">
            <Button
              type="button"
              variant="link"
              onClick={handleResend}
              disabled={resendCooldown > 0 || resending}
              className="text-blue-600"
            >
              {resending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  שולח קוד חדש...
                </>
              ) : resendCooldown > 0 ? (
                `שלח קוד מחדש (${resendCooldown}s)`
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  שלח קוד מחדש
                </>
              )}
            </Button>
          </div>

          {/* Info Alert */}
          <Alert className="bg-blue-50 border-blue-200">
            <AlertDescription className="text-blue-900 text-sm" dir="rtl">
              <strong>לא קיבלת את הקוד?</strong>
              <br />
              בדוק את תיקיית הספאם או לחץ על "שלח קוד מחדש"
            </AlertDescription>
          </Alert>
        </CardContent>

        <CardFooter className="flex gap-3">
          {onSkip && (
            <Button
              type="button"
              variant="outline"
              onClick={onSkip}
              disabled={loading}
              className="flex-1"
            >
              דלג (לא מומלץ)
            </Button>
          )}
          <Button
            type="submit"
            disabled={loading || code.some(d => d === '')}
            className="flex-1 bg-blue-600 hover:bg-blue-700"
          >
            {loading ? (
              <>
                <Loader2 className="ml-2 h-4 w-4 animate-spin" />
                מאמת...
              </>
            ) : (
              'אמת קוד'
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}

