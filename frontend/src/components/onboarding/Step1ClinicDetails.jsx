import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Building2, Mail, Phone, MapPin, ArrowRight, AlertCircle } from 'lucide-react';

/**
 * Step 1: Clinic Details
 * 
 * Collects basic clinic information:
 * - Clinic name
 * - Email
 * - Phone
 * - Address
 * 
 * Props:
 * - initialData: Object with initial form values
 * - onNext: Callback with form data when user proceeds
 * - onBack: Optional callback to go back
 */
export default function Step1ClinicDetails({ initialData = {}, onNext, onBack }) {
  const [formData, setFormData] = useState({
    clinic_name: initialData.clinic_name || '',
    clinic_email: initialData.clinic_email || '',
    clinic_phone: initialData.clinic_phone || '',
    clinic_address: initialData.clinic_address || ''
  });

  const [errors, setErrors] = useState({});

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

    // Clinic name
    if (!formData.clinic_name.trim()) {
      newErrors.clinic_name = 'שם המרפאה הוא שדה חובה';
    } else if (formData.clinic_name.trim().length < 2) {
      newErrors.clinic_name = 'שם המרפאה חייב להכיל לפחות 2 תווים';
    }

    // Email
    if (!formData.clinic_email.trim()) {
      newErrors.clinic_email = 'אימייל הוא שדה חובה';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.clinic_email)) {
      newErrors.clinic_email = 'אימייל לא תקין';
    }

    // Phone (Israeli format)
    if (!formData.clinic_phone.trim()) {
      newErrors.clinic_phone = 'טלפון הוא שדה חובה';
    } else if (!/^0\d{1,2}-?\d{7}$/.test(formData.clinic_phone.replace(/\s/g, ''))) {
      newErrors.clinic_phone = 'מספר טלפון לא תקין (לדוגמה: 03-1234567 או 050-1234567)';
    }

    // Address
    if (!formData.clinic_address.trim()) {
      newErrors.clinic_address = 'כתובת היא שדה חובה';
    } else if (formData.clinic_address.trim().length < 10) {
      newErrors.clinic_address = 'כתובת חייבת להכיל לפחות 10 תווים';
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

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="bg-blue-100 p-3 rounded-lg">
            <Building2 className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <CardTitle>פרטי המרפאה</CardTitle>
            <CardDescription>
              שלב 1 מתוך 4 - נתחיל בפרטים הבסיסיים של המרפאה
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          {/* Clinic Name */}
          <div className="space-y-2">
            <Label htmlFor="clinic_name">
              שם המרפאה <span className="text-red-600">*</span>
            </Label>
            <div className="relative">
              <Building2 className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                id="clinic_name"
                name="clinic_name"
                type="text"
                placeholder="מרפאת שיניים ד״ר כהן"
                value={formData.clinic_name}
                onChange={handleChange}
                className={`pr-10 text-right ${errors.clinic_name ? 'border-red-500' : ''}`}
                dir="rtl"
              />
            </div>
            {errors.clinic_name && (
              <p className="text-sm text-red-600 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.clinic_name}
              </p>
            )}
          </div>

          {/* Clinic Email */}
          <div className="space-y-2">
            <Label htmlFor="clinic_email">
              אימייל <span className="text-red-600">*</span>
            </Label>
            <div className="relative">
              <Mail className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                id="clinic_email"
                name="clinic_email"
                type="email"
                placeholder="info@clinic.co.il"
                value={formData.clinic_email}
                onChange={handleChange}
                className={`pr-10 text-right ${errors.clinic_email ? 'border-red-500' : ''}`}
                dir="rtl"
              />
            </div>
            {errors.clinic_email && (
              <p className="text-sm text-red-600 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.clinic_email}
              </p>
            )}
            <p className="text-xs text-gray-500">
              האימייל הרשמי של המרפאה (ישמש לתקשורת עם מטופלים)
            </p>
          </div>

          {/* Clinic Phone */}
          <div className="space-y-2">
            <Label htmlFor="clinic_phone">
              טלפון <span className="text-red-600">*</span>
            </Label>
            <div className="relative">
              <Phone className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                id="clinic_phone"
                name="clinic_phone"
                type="tel"
                placeholder="03-1234567"
                value={formData.clinic_phone}
                onChange={handleChange}
                className={`pr-10 text-right ${errors.clinic_phone ? 'border-red-500' : ''}`}
                dir="rtl"
              />
            </div>
            {errors.clinic_phone && (
              <p className="text-sm text-red-600 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.clinic_phone}
              </p>
            )}
            <p className="text-xs text-gray-500">
              מספר טלפון קווי או נייד (לדוגמה: 03-1234567 או 050-1234567)
            </p>
          </div>

          {/* Clinic Address */}
          <div className="space-y-2">
            <Label htmlFor="clinic_address">
              כתובת <span className="text-red-600">*</span>
            </Label>
            <div className="relative">
              <MapPin className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
              <Textarea
                id="clinic_address"
                name="clinic_address"
                placeholder="רחוב הרצל 123, תל אביב"
                value={formData.clinic_address}
                onChange={handleChange}
                className={`pr-10 text-right min-h-[80px] ${errors.clinic_address ? 'border-red-500' : ''}`}
                dir="rtl"
              />
            </div>
            {errors.clinic_address && (
              <p className="text-sm text-red-600 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.clinic_address}
              </p>
            )}
            <p className="text-xs text-gray-500">
              הכתובת המלאה של המרפאה (רחוב, מספר בית, עיר)
            </p>
          </div>

          {/* Info Alert */}
          <Alert className="bg-blue-50 border-blue-200">
            <AlertDescription className="text-blue-900 text-sm" dir="rtl">
              <strong>למה אנחנו צריכים את המידע הזה?</strong>
              <br />
              הפרטים האלה ישמשו ליצירת פרופיל המרפאה שלך, לתקשורת עם מטופלים, 
              ולהצגה בפורטל המטופלים.
            </AlertDescription>
          </Alert>
        </CardContent>

        <CardFooter className="flex gap-3">
          {onBack && (
            <Button
              type="button"
              variant="outline"
              onClick={onBack}
              className="flex-1"
            >
              חזור
            </Button>
          )}
          <Button
            type="submit"
            className="flex-1 bg-blue-600 hover:bg-blue-700"
          >
            המשך
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}

