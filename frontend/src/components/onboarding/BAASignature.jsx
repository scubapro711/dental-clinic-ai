import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import API_CONFIG from '@/config/api';

/**
 * BAA (Business Associate Agreement) Signature Component
 * 
 * Displays HIPAA BAA agreement and collects electronic signature.
 * Integrates with backend API: /api/v1/baa/*
 * 
 * Props:
 * - organizationId: UUID of the organization
 * - onComplete: Callback when signature is successfully submitted
 * - onSkip: Optional callback to skip this step (not recommended)
 */
export default function BAASignature({ organizationId, onComplete, onSkip }) {
  // State
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  // BAA document data
  const [baaData, setBaaData] = useState(null);
  const [alreadySigned, setAlreadySigned] = useState(false);
  
  // Form data
  const [signatoryName, setSignatoryName] = useState('');
  const [signatoryTitle, setSignatoryTitle] = useState('');
  const [consentConfirmed, setConsentConfirmed] = useState(false);
  const [hasReadDocument, setHasReadDocument] = useState(false);
  
  // Scroll tracking
  const [hasScrolledToBottom, setHasScrolledToBottom] = useState(false);

  // Load BAA document on mount
  useEffect(() => {
    loadBAADocument();
  }, [organizationId]);

  const loadBAADocument = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch(API_CONFIG.endpoint('baa/document/${organizationId}'), {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to load BAA document');
      }
      
      const data = await response.json();
      setBaaData(data);
      setAlreadySigned(data.already_signed);
      
      // If already signed, show success and allow to continue
      if (data.already_signed) {
        setSuccess(true);
      }
    } catch (err) {
      setError(err.message || 'שגיאה בטעינת הסכם BAA');
    } finally {
      setLoading(false);
    }
  };

  const handleScroll = (e) => {
    const element = e.target;
    const isAtBottom = element.scrollHeight - element.scrollTop <= element.clientHeight + 50;
    
    if (isAtBottom && !hasScrolledToBottom) {
      setHasScrolledToBottom(true);
      setHasReadDocument(true);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!signatoryName.trim()) {
      setError('נא למלא שם מלא');
      return;
    }
    
    if (!signatoryTitle.trim()) {
      setError('נא למלא תפקיד');
      return;
    }
    
    if (!consentConfirmed) {
      setError('יש לאשר שקראת והבנת את ההסכם');
      return;
    }
    
    if (!hasReadDocument) {
      setError('נא לגלול ולקרוא את כל ההסכם');
      return;
    }
    
    try {
      setSubmitting(true);
      setError('');
      
      const response = await fetch(API_CONFIG.endpoint('baa/sign'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          organization_id: organizationId,
          signatory_name: signatoryName,
          signatory_title: signatoryTitle,
          consent_confirmed: consentConfirmed
        })
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to sign BAA');
      }
      
      const data = await response.json();
      setSuccess(true);
      
      // Wait 2 seconds to show success message, then call onComplete
      setTimeout(() => {
        onComplete(data);
      }, 2000);
      
    } catch (err) {
      setError(err.message || 'שגיאה בחתימה על ההסכם');
    } finally {
      setSubmitting(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <span className="mr-3 text-gray-600">טוען הסכם BAA...</span>
        </CardContent>
      </Card>
    );
  }

  // Success state (already signed or just signed)
  if (success || alreadySigned) {
    return (
      <Card className="w-full max-w-4xl mx-auto border-green-200 bg-green-50">
        <CardHeader>
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-8 h-8 text-green-600" />
            <div>
              <CardTitle className="text-green-900">הסכם BAA נחתם בהצלחה!</CardTitle>
              <CardDescription className="text-green-700">
                {alreadySigned 
                  ? `נחתם ב-${new Date(baaData.signature_date).toLocaleDateString('he-IL')}`
                  : 'החתימה נשמרה במערכת'
                }
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Alert className="bg-white border-green-300">
            <AlertDescription className="text-green-900">
              ההסכם נחתם אלקטרונית ונשמר במערכת. ניתן להמשיך בתהליך ההצטרפות.
            </AlertDescription>
          </Alert>
        </CardContent>
        <CardFooter>
          <Button 
            onClick={() => onComplete(baaData)} 
            className="w-full bg-green-600 hover:bg-green-700"
          >
            המשך
          </Button>
        </CardFooter>
      </Card>
    );
  }

  // Main form
  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex items-center gap-3">
          <FileText className="w-8 h-8 text-blue-600" />
          <div>
            <CardTitle>הסכם שותף עסקי (BAA)</CardTitle>
            <CardDescription>
              Business Associate Agreement - דרישה של HIPAA
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

          {/* Organization Info */}
          {baaData && (
            <Alert className="bg-blue-50 border-blue-200">
              <AlertDescription className="text-blue-900">
                <strong>מרפאה:</strong> {baaData.organization_name}
              </AlertDescription>
            </Alert>
          )}

          {/* BAA Document */}
          <div className="space-y-2">
            <Label className="text-base font-semibold">הסכם BAA</Label>
            <div 
              className="border rounded-lg p-6 bg-gray-50 max-h-96 overflow-y-auto prose prose-sm max-w-none"
              onScroll={handleScroll}
              dir="rtl"
            >
              {baaData && (
                <ReactMarkdown>{baaData.baa_text}</ReactMarkdown>
              )}
            </div>
            {!hasScrolledToBottom && (
              <p className="text-sm text-orange-600 flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                נא לגלול ולקרוא את כל ההסכם
              </p>
            )}
            {hasScrolledToBottom && (
              <p className="text-sm text-green-600 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                קראת את כל ההסכם
              </p>
            )}
          </div>

          {/* Signature Form */}
          <div className="space-y-4 pt-4 border-t">
            <h3 className="font-semibold text-lg">חתימה אלקטרונית</h3>
            
            {/* Signatory Name */}
            <div className="space-y-2">
              <Label htmlFor="signatory-name">
                שם מלא <span className="text-red-600">*</span>
              </Label>
              <Input
                id="signatory-name"
                type="text"
                placeholder="ד״ר יוסי כהן"
                value={signatoryName}
                onChange={(e) => setSignatoryName(e.target.value)}
                required
                disabled={submitting}
                className="text-right"
                dir="rtl"
              />
              <p className="text-xs text-gray-500">
                השם המלא של החותם על ההסכם
              </p>
            </div>

            {/* Signatory Title */}
            <div className="space-y-2">
              <Label htmlFor="signatory-title">
                תפקיד <span className="text-red-600">*</span>
              </Label>
              <Input
                id="signatory-title"
                type="text"
                placeholder="בעלים ורופא שיניים"
                value={signatoryTitle}
                onChange={(e) => setSignatoryTitle(e.target.value)}
                required
                disabled={submitting}
                className="text-right"
                dir="rtl"
              />
              <p className="text-xs text-gray-500">
                התפקיד במרפאה (בעלים, מנכ"ל, מנהל וכו')
              </p>
            </div>

            {/* Consent Checkbox */}
            <div className="space-y-3 pt-2">
              <div className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <Checkbox
                  id="consent"
                  checked={consentConfirmed}
                  onCheckedChange={setConsentConfirmed}
                  disabled={submitting || !hasReadDocument}
                  className="mt-1"
                />
                <div className="space-y-1">
                  <Label 
                    htmlFor="consent" 
                    className="text-sm font-medium cursor-pointer"
                  >
                    אני מאשר/ת שקראתי והבנתי את הסכם השותף העסקי (BAA) ומסכים/ה לתנאיו
                  </Label>
                  {baaData && (
                    <p className="text-xs text-gray-600" dir="rtl">
                      {baaData.consent_text}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Legal Notice */}
          <Alert className="bg-yellow-50 border-yellow-200">
            <AlertDescription className="text-yellow-900 text-sm" dir="rtl">
              <strong>הודעה משפטית:</strong> זהו הסכם משפטי מחייב. החתימה האלקטרונית שלך תישמר במערכת 
              ותהווה אישור לקריאה והבנה של ההסכם. מומלץ להתייעץ עם יועץ משפטי לפני החתימה.
            </AlertDescription>
          </Alert>
        </CardContent>

        <CardFooter className="flex gap-3">
          {onSkip && (
            <Button
              type="button"
              variant="outline"
              onClick={onSkip}
              disabled={submitting}
              className="flex-1"
            >
              דלג (לא מומלץ)
            </Button>
          )}
          <Button
            type="submit"
            disabled={submitting || !consentConfirmed || !hasReadDocument}
            className="flex-1 bg-blue-600 hover:bg-blue-700"
          >
            {submitting ? (
              <>
                <Loader2 className="ml-2 h-4 w-4 animate-spin" />
                חותם על ההסכם...
              </>
            ) : (
              <>
                <FileText className="ml-2 h-4 w-4" />
                חתום על ההסכם
              </>
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}

