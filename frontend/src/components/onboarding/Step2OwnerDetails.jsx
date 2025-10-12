import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { User, Mail, Phone, Lock, ArrowRight, ArrowLeft, AlertCircle, Eye, EyeOff } from 'lucide-react';

/**
 * Step 2: Owner Details
 * 
 * Collects owner/administrator information:
 * - Full name
 * - Email
 * - Phone
 * - Password
 * 
 * Props:
 * - initialData: Object with initial form values
 * - onNext: Callback with form data when user proceeds
 * - onBack: Callback to go back to previous step
 */
export default function Step2OwnerDetails({ initialData = {}, onNext, onBack }) {
  const [formData, setFormData] = useState({
    owner_full_name: initialData.owner_full_name || '',
    owner_email: initialData.owner_email || '',
    owner_phone: initialData.owner_phone || '',
    owner_password: initialData.owner_password || '',
    owner_password_confirm: initialData.owner_password_confirm || ''
  });

  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validate = () => {
    const newErrors = {};

    // Full name
    if (!formData.owner_full_name.trim()) {
      newErrors.owner_full_name = 'שם מלא הוא שדה חובה';
    } else if (formData.owner_full_name.trim().length < 2) {
      newErrors.owner_full_name = 'שם מלא חייב להכיל לפחות 2 תווים';
    }

    // Email
    if (!formData.owner_email.trim()) {
      newErrors.owner_email = 'אימייל הוא שדה חובה';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.owner_email)) {
      newErrors.owner_email = 'אימייל לא תקין';
    }

    // Phone (Israeli format)
    if (formData.owner_phone && !/^0\d{1,2}-?\d{7}$/.test(formData.owner_phone.replace(/\s/g, ''))) {
      newErrors.owner_phone = 'מספר טלפון לא תקין (לדוגמה: 050-1234567)';
    }

    // Password
    if (!formData.owner_password) {
      newErrors.owner_password = 'סיסמה היא שדה חובה';
    } else if (formData.owner_password.length < 8) {
      newErrors.owner_password = 'סיסמה חייבת להכיל לפחות 8 תווים';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.owner_password)) {
      newErrors.owner_password = 'סיסמה חייבת להכיל אותיות גדולות, קטנות ומספרים';
    }

    // Password confirmation
    if (!formData.owner_password_confirm) {
      newErrors.owner_password_confirm = 'אימות סיסמה הוא שדה חובה';
    } else if (formData.owner_password !== formData.owner_password_confirm) {
      newErrors.owner_password_confirm = 'הסיסמאות אינן תואמות';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validate()) {
      onNext(formData);
    }
  };

  const getPasswordStrength = (password) => {
    if (!password) return { strength: 0, label: '', color: '' };
    
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z\d]/.test(password)) strength++;
    
    if (strength <= 2) return { strength, label: 'חלשה', color: 'bg-red-500' };
    if (strength <= 4) return { strength, label: 'בינונית', color: 'bg-yellow-500' };
    return { strength, label: 'חזקה', color: 'bg-green-500' };
  };

  const passwordStrength = getPasswordStrength(formData.owner_password);

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="bg-purple-100 p-3 rounded-lg">
            <User className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <CardTitle>פרטי הבעלים</CardTitle>
            <CardDescription>
              שלב 2 מתוך 4 - פרטי המנהל/בעלים של המרפאה
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          {/* Full Name */}
          <div className="space-y-2">
            <Label htmlFor="owner_full_name">
              שם מלא <span className="text-red-600">*</span>
            </Label>
            <div className="relative">
              <User className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                id="owner_full_name"
                name="owner_full_name"
                type="text"
                placeholder="ד״ר יוסי כהן"
                value={formData.owner_full_name}
                onChange={handleChange}
                className={`pr-10 text-right ${errors.owner_full_name ? 'border-red-500' : ''}`}
                dir="rtl"
              />
            </div>
            {errors.owner_full_name && (
              <p className="text-sm text-red-600 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.owner_full_name}
              </p>
            )}
          </div>

          {/* Email */}
          <div className="space-y-2">
            <Label htmlFor="owner_email">
              אימייל <span className="text-red-600">*</span>
            </Label>
            <div className="relative">
              <Mail className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                id="owner_email"
                name="owner_email"
                type="email"
                placeholder="yossi@example.com"
                value={formData.owner_email}
                onChange={handleChange}
                className={`pr-10 text-right ${errors.owner_email ? 'border-red-500' : ''}`}
                dir="rtl"
              />
            </div>
            {errors.owner_email && (
              <p className="text-sm text-red-600 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.owner_email}
              </p>
            )}
            <p className="text-xs text-gray-500">
              האימייל האישי שלך (ישמש להתחברות למערכת)
            </p>
          </div>

          {/* Phone */}
          <div className="space-y-2">
            <Label htmlFor="owner_phone">
              טלפון נייד (אופציונלי)
            </Label>
            <div className="relative">
              <Phone className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                id="owner_phone"
                name="owner_phone"
                type="tel"
                placeholder="050-1234567"
                value={formData.owner_phone}
                onChange={handleChange}
                className={`pr-10 text-right ${errors.owner_phone ? 'border-red-500' : ''}`}
                dir="rtl"
              />
            </div>
            {errors.owner_phone && (
              <p className="text-sm text-red-600 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.owner_phone}
              </p>
            )}
          </div>

          {/* Password */}
          <div className="space-y-2">
            <Label htmlFor="owner_password">
              סיסמה <span className="text-red-600">*</span>
            </Label>
            <div className="relative">
              <Lock className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                id="owner_password"
                name="owner_password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={formData.owner_password}
                onChange={handleChange}
                className={`pr-10 pl-10 text-right ${errors.owner_password ? 'border-red-500' : ''}`}
                dir="rtl"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute left-3 top-3 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {errors.owner_password && (
              <p className="text-sm text-red-600 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.owner_password}
              </p>
            )}
            {formData.owner_password && (
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all ${passwordStrength.color}`}
                      style={{ width: `${(passwordStrength.strength / 6) * 100}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium">{passwordStrength.label}</span>
                </div>
                <p className="text-xs text-gray-500">
                  לפחות 8 תווים, כולל אותיות גדולות, קטנות ומספרים
                </p>
              </div>
            )}
          </div>

          {/* Password Confirmation */}
          <div className="space-y-2">
            <Label htmlFor="owner_password_confirm">
              אימות סיסמה <span className="text-red-600">*</span>
            </Label>
            <div className="relative">
              <Lock className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                id="owner_password_confirm"
                name="owner_password_confirm"
                type={showPasswordConfirm ? 'text' : 'password'}
                placeholder="••••••••"
                value={formData.owner_password_confirm}
                onChange={handleChange}
                className={`pr-10 pl-10 text-right ${errors.owner_password_confirm ? 'border-red-500' : ''}`}
                dir="rtl"
              />
              <button
                type="button"
                onClick={() => setShowPasswordConfirm(!showPasswordConfirm)}
                className="absolute left-3 top-3 text-gray-400 hover:text-gray-600"
              >
                {showPasswordConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {errors.owner_password_confirm && (
              <p className="text-sm text-red-600 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.owner_password_confirm}
              </p>
            )}
          </div>

          {/* Info Alert */}
          <Alert className="bg-purple-50 border-purple-200">
            <AlertDescription className="text-purple-900 text-sm" dir="rtl">
              <strong>הערה חשובה:</strong>
              <br />
              הפרטים האלה ישמשו ליצירת חשבון המנהל הראשי של המרפאה. 
              תוכל להזמין עובדים נוספים מאוחר יותר.
            </AlertDescription>
          </Alert>
        </CardContent>

        <CardFooter className="flex gap-3">
          <Button
            type="button"
            variant="outline"
            onClick={onBack}
            className="flex-1"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            חזור
          </Button>
          <Button
            type="submit"
            className="flex-1 bg-purple-600 hover:bg-purple-700"
          >
            המשך
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}

