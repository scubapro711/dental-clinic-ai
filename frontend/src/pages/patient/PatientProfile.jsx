import React, { useState } from 'react';
import { 
  User, Mail, Phone, MapPin, Calendar, Shield,
  Bell, MessageSquare, Edit2, Save, X, ChevronRight,
  MessageCircle, Check, Smartphone, Send
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

/**
 * Patient Profile Page - Hebrew version
 * 
 * Features:
 * - Personal information (edit mode)
 * - Kupat Cholim (Israeli health insurance)
 * - Communication preferences (SMS, Telegram, Email)
 * - Notification settings
 * - Security settings
 * - Account management
 */
export default function PatientProfile() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [editMode, setEditMode] = useState(false);
  const [activeTab, setActiveTab] = useState('personal');

  // Mock user data
  const [userData, setUserData] = useState({
    firstName: 'שרה',
    lastName: 'כהן',
    idNumber: '123456789',
    email: 'sarah.cohen@example.com',
    phone: '+972-50-123-4567',
    dateOfBirth: '1990-05-15',
    address: 'רחוב הרצל 123, תל אביב',
    city: 'תל אביב',
    zipCode: '6473301',
    kupat: 'מכבי',
    kupatNumber: '12345678',
    insurance: 'מכבי שלי זהב',
    allergies: 'פניצילין',
    medicalConditions: 'אין',
    emergencyContact: 'יוסי כהן',
    emergencyPhone: '+972-50-987-6543',
  });

  const [notifications, setNotifications] = useState({
    smsReminders: true,
    smsPayments: true,
    smsResults: false,
    emailReminders: true,
    emailPayments: true,
    emailResults: true,
    telegramReminders: false,
    telegramPayments: false,
    telegramResults: false,
    telegramLinked: false,
    telegramUsername: '',
  });

  const handleSave = () => {
    // Save user data
    console.log('Saving user data:', userData);
    setEditMode(false);
  };

  const handleCancel = () => {
    // Reset to original data
    setEditMode(false);
  };

  const linkTelegram = () => {
    // Generate linking code and redirect to Telegram
    const linkingCode = 'ABC123XYZ';
    window.open(`https://t.me/DentaFlowBot?start=${linkingCode}`, '_blank');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50" dir="rtl">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate('/patient/dashboard')}>
                <ChevronRight className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">הפרופיל שלי</h1>
                <p className="text-sm text-gray-500">נהל את הפרטים והגדרות החשבון שלך</p>
              </div>
            </div>
            
            {!editMode && activeTab === 'personal' && (
              <Button onClick={() => setEditMode(true)}>
                <Edit2 className="h-4 w-4 ml-1" />
                ערוך פרופיל
              </Button>
            )}
            
            {editMode && (
              <div className="flex gap-2">
                <Button variant="outline" onClick={handleCancel}>
                  <X className="h-4 w-4 ml-1" />
                  ביטול
                </Button>
                <Button onClick={handleSave} className="bg-gradient-to-r from-blue-600 to-purple-600">
                  <Save className="h-4 w-4 ml-1" />
                  שמור
                </Button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Header */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <div className="flex items-center gap-6">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-white text-3xl font-bold flex-shrink-0">
                {userData.firstName.charAt(0)}{userData.lastName.charAt(0)}
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-gray-900">
                  {userData.firstName} {userData.lastName}
                </h2>
                <p className="text-gray-600">{userData.email}</p>
                <div className="flex gap-2 mt-2">
                  <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100">
                    מטופל פעיל
                  </Badge>
                  <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
                    {userData.kupat}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="personal">פרטים אישיים</TabsTrigger>
            <TabsTrigger value="medical">מידע רפואי</TabsTrigger>
            <TabsTrigger value="notifications">התראות</TabsTrigger>
            <TabsTrigger value="security">אבטחה</TabsTrigger>
          </TabsList>

          {/* Personal Info Tab */}
          <TabsContent value="personal" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>פרטים אישיים</CardTitle>
                <CardDescription>המידע הבסיסי שלך</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="firstName">שם פרטי</Label>
                    <Input
                      id="firstName"
                      value={userData.firstName}
                      onChange={(e) => setUserData({...userData, firstName: e.target.value})}
                      disabled={!editMode}
                    />
                  </div>
                  <div>
                    <Label htmlFor="lastName">שם משפחה</Label>
                    <Input
                      id="lastName"
                      value={userData.lastName}
                      onChange={(e) => setUserData({...userData, lastName: e.target.value})}
                      disabled={!editMode}
                    />
                  </div>
                  <div>
                    <Label htmlFor="idNumber">תעודת זהות</Label>
                    <Input
                      id="idNumber"
                      value={userData.idNumber}
                      disabled
                    />
                  </div>
                  <div>
                    <Label htmlFor="dateOfBirth">תאריך לידה</Label>
                    <Input
                      id="dateOfBirth"
                      type="date"
                      value={userData.dateOfBirth}
                      onChange={(e) => setUserData({...userData, dateOfBirth: e.target.value})}
                      disabled={!editMode}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>פרטי קשר</CardTitle>
                <CardDescription>איך ליצור איתך קשר</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="email">אימייל</Label>
                    <Input
                      id="email"
                      type="email"
                      value={userData.email}
                      onChange={(e) => setUserData({...userData, email: e.target.value})}
                      disabled={!editMode}
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone">טלפון</Label>
                    <Input
                      id="phone"
                      type="tel"
                      value={userData.phone}
                      onChange={(e) => setUserData({...userData, phone: e.target.value})}
                      disabled={!editMode}
                    />
                  </div>
                  <div className="md:col-span-2">
                    <Label htmlFor="address">כתובת</Label>
                    <Input
                      id="address"
                      value={userData.address}
                      onChange={(e) => setUserData({...userData, address: e.target.value})}
                      disabled={!editMode}
                    />
                  </div>
                  <div>
                    <Label htmlFor="city">עיר</Label>
                    <Input
                      id="city"
                      value={userData.city}
                      onChange={(e) => setUserData({...userData, city: e.target.value})}
                      disabled={!editMode}
                    />
                  </div>
                  <div>
                    <Label htmlFor="zipCode">מיקוד</Label>
                    <Input
                      id="zipCode"
                      value={userData.zipCode}
                      onChange={(e) => setUserData({...userData, zipCode: e.target.value})}
                      disabled={!editMode}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>איש קשר לחירום</CardTitle>
                <CardDescription>מי ליצור קשר במקרה חירום</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="emergencyContact">שם</Label>
                    <Input
                      id="emergencyContact"
                      value={userData.emergencyContact}
                      onChange={(e) => setUserData({...userData, emergencyContact: e.target.value})}
                      disabled={!editMode}
                    />
                  </div>
                  <div>
                    <Label htmlFor="emergencyPhone">טלפון</Label>
                    <Input
                      id="emergencyPhone"
                      type="tel"
                      value={userData.emergencyPhone}
                      onChange={(e) => setUserData({...userData, emergencyPhone: e.target.value})}
                      disabled={!editMode}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Medical Info Tab */}
          <TabsContent value="medical" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>קופת חולים</CardTitle>
                <CardDescription>מידע על קופת החולים והביטוח המשלים</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="kupat">קופת חולים</Label>
                    <Select value={userData.kupat} onValueChange={(value) => setUserData({...userData, kupat: value})} disabled={!editMode}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="מכבי">מכבי</SelectItem>
                        <SelectItem value="כללית">כללית</SelectItem>
                        <SelectItem value="מאוחדת">מאוחדת</SelectItem>
                        <SelectItem value="לאומית">לאומית</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="kupatNumber">מספר חבר</Label>
                    <Input
                      id="kupatNumber"
                      value={userData.kupatNumber}
                      onChange={(e) => setUserData({...userData, kupatNumber: e.target.value})}
                      disabled={!editMode}
                    />
                  </div>
                  <div className="md:col-span-2">
                    <Label htmlFor="insurance">ביטוח משלים</Label>
                    <Input
                      id="insurance"
                      value={userData.insurance}
                      onChange={(e) => setUserData({...userData, insurance: e.target.value})}
                      disabled={!editMode}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>מידע רפואי</CardTitle>
                <CardDescription>אלרגיות ומצבים רפואיים</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="allergies">אלרגיות</Label>
                  <Input
                    id="allergies"
                    value={userData.allergies}
                    onChange={(e) => setUserData({...userData, allergies: e.target.value})}
                    disabled={!editMode}
                    placeholder="פניצילין, אספירין, וכו'"
                  />
                </div>
                <div>
                  <Label htmlFor="medicalConditions">מצבים רפואיים</Label>
                  <Input
                    id="medicalConditions"
                    value={userData.medicalConditions}
                    onChange={(e) => setUserData({...userData, medicalConditions: e.target.value})}
                    disabled={!editMode}
                    placeholder="סוכרת, לחץ דם, וכו'"
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Notifications Tab */}
          <TabsContent value="notifications" className="space-y-6">
            {/* SMS Notifications */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Smartphone className="h-5 w-5" />
                  הודעות SMS (Twilio)
                </CardTitle>
                <CardDescription>
                  קבל הודעות SMS לטלפון שלך: {userData.phone}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">תזכורות לתורים</p>
                    <p className="text-sm text-gray-500">קבל תזכורת יום לפני התור</p>
                  </div>
                  <Switch
                    checked={notifications.smsReminders}
                    onCheckedChange={(checked) => setNotifications({...notifications, smsReminders: checked})}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">תזכורות תשלום</p>
                    <p className="text-sm text-gray-500">קבל תזכורת על חשבוניות פתוחות</p>
                  </div>
                  <Switch
                    checked={notifications.smsPayments}
                    onCheckedChange={(checked) => setNotifications({...notifications, smsPayments: checked})}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">תוצאות בדיקות</p>
                    <p className="text-sm text-gray-500">קבל הודעה כשתוצאות מוכנות</p>
                  </div>
                  <Switch
                    checked={notifications.smsResults}
                    onCheckedChange={(checked) => setNotifications({...notifications, smsResults: checked})}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Telegram Notifications */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Send className="h-5 w-5" />
                  הודעות Telegram
                </CardTitle>
                <CardDescription>
                  {notifications.telegramLinked 
                    ? `מקושר ל-@${notifications.telegramUsername}`
                    : 'קשר את חשבון הטלגרם שלך לקבלת הודעות'}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {!notifications.telegramLinked ? (
                  <div className="p-6 border-2 border-dashed border-gray-300 rounded-lg text-center">
                    <Send className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="font-semibold mb-2">קשר את Telegram</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      קשר את חשבון הטלגרם שלך כדי לקבל הודעות ולשוחח עם Alex
                    </p>
                    <Button onClick={linkTelegram} className="bg-blue-600 hover:bg-blue-700">
                      <Send className="h-4 w-4 ml-1" />
                      קשר Telegram
                    </Button>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">תזכורות לתורים</p>
                        <p className="text-sm text-gray-500">קבל תזכורת דרך Telegram</p>
                      </div>
                      <Switch
                        checked={notifications.telegramReminders}
                        onCheckedChange={(checked) => setNotifications({...notifications, telegramReminders: checked})}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">תזכורות תשלום</p>
                        <p className="text-sm text-gray-500">קבל תזכורת על חשבוניות</p>
                      </div>
                      <Switch
                        checked={notifications.telegramPayments}
                        onCheckedChange={(checked) => setNotifications({...notifications, telegramPayments: checked})}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">תוצאות בדיקות</p>
                        <p className="text-sm text-gray-500">קבל הודעה כשתוצאות מוכנות</p>
                      </div>
                      <Switch
                        checked={notifications.telegramResults}
                        onCheckedChange={(checked) => setNotifications({...notifications, telegramResults: checked})}
                      />
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Email Notifications */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mail className="h-5 w-5" />
                  הודעות אימייל
                </CardTitle>
                <CardDescription>
                  קבל הודעות לאימייל: {userData.email}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">תזכורות לתורים</p>
                    <p className="text-sm text-gray-500">קבל תזכורת באימייל</p>
                  </div>
                  <Switch
                    checked={notifications.emailReminders}
                    onCheckedChange={(checked) => setNotifications({...notifications, emailReminders: checked})}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">חשבוניות ותשלומים</p>
                    <p className="text-sm text-gray-500">קבל חשבוניות באימייל</p>
                  </div>
                  <Switch
                    checked={notifications.emailPayments}
                    onCheckedChange={(checked) => setNotifications({...notifications, emailPayments: checked})}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">תוצאות בדיקות</p>
                    <p className="text-sm text-gray-500">קבל תוצאות באימייל</p>
                  </div>
                  <Switch
                    checked={notifications.emailResults}
                    onCheckedChange={(checked) => setNotifications({...notifications, emailResults: checked})}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>סיסמה</CardTitle>
                <CardDescription>שנה את הסיסמה שלך</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="currentPassword">סיסמה נוכחית</Label>
                  <Input id="currentPassword" type="password" />
                </div>
                <div>
                  <Label htmlFor="newPassword">סיסמה חדשה</Label>
                  <Input id="newPassword" type="password" />
                </div>
                <div>
                  <Label htmlFor="confirmPassword">אימות סיסמה</Label>
                  <Input id="confirmPassword" type="password" />
                </div>
                <Button>שנה סיסמה</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>אימות דו-שלבי (2FA)</CardTitle>
                <CardDescription>הגן על החשבון שלך עם אימות נוסף</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">אימות דו-שלבי</p>
                    <p className="text-sm text-gray-500">קבל קוד SMS בכל כניסה</p>
                  </div>
                  <Switch />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>מחיקת חשבון</CardTitle>
                <CardDescription>מחק את החשבון והנתונים שלך לצמיתות</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  פעולה זו תמחק את כל הנתונים שלך ולא ניתן לבטל אותה.
                </p>
                <Button variant="destructive">מחק חשבון</Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      {/* Floating Chat Button */}
      <Button
        size="lg"
        className="fixed bottom-6 left-6 w-16 h-16 rounded-full shadow-2xl bg-gradient-to-br from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 z-50"
        onClick={() => navigate('/patient/dashboard')}
      >
        <MessageCircle className="h-6 w-6" />
      </Button>
    </div>
  );
}

