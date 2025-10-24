import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, Send, Phone, Sparkles } from 'lucide-react';
import TelegramInviteCodesWidget from '@/components/communications/TelegramInviteCodesWidget';
import TelegramUsersWidget from '@/components/communications/TelegramUsersWidget';
import TelegramConversationsWidget from '@/components/communications/TelegramConversationsWidget';
// import TelegramHub from '@/components/communications/TelegramHub'; // Temporarily disabled

/**
 * Communications Hub - Main Page
 * 
 * Centralized communication management for:
 * - Telegram (active)
 * - SMS (coming soon)
 * - WhatsApp (coming soon)
 */
export default function CommunicationsHub() {
  const [activeTab, setActiveTab] = useState('telegram');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  מרכז תקשורת
                </h1>
                <p className="text-sm text-gray-600 mt-1">
                  ניהול ערוצי תקשורת עם מטופלים
                </p>
              </div>
            </div>
            
            {/* Stats */}
            <div className="flex gap-4">
              <Card className="border-2 border-blue-200 bg-blue-50/50">
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-blue-600">12</div>
                  <p className="text-xs text-gray-600">משתמשים פעילים</p>
                </CardContent>
              </Card>
              <Card className="border-2 border-purple-200 bg-purple-50/50">
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-purple-600">8</div>
                  <p className="text-xs text-gray-600">שיחות פתוחות</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-[600px]">
            <TabsTrigger value="telegram" className="flex items-center gap-2">
              <Send className="w-4 h-4" />
              Telegram
              <Badge variant="secondary" className="ml-2">פעיל</Badge>
            </TabsTrigger>
            <TabsTrigger value="sms" disabled className="flex items-center gap-2">
              <Phone className="w-4 h-4" />
              SMS
              <Badge variant="outline" className="ml-2">בקרוב</Badge>
            </TabsTrigger>
            <TabsTrigger value="whatsapp" disabled className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              WhatsApp
              <Badge variant="outline" className="ml-2">בקרוב</Badge>
            </TabsTrigger>
          </TabsList>

          {/* Telegram Tab */}
          <TabsContent value="telegram" className="space-y-6">
            {/* Full Telegram Hub - Chat Interface */}
            {/* <TelegramHub /> */} {/* Temporarily disabled */}
            
            {/* Management Widgets */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
              {/* Invite Codes Widget */}
              <TelegramInviteCodesWidget />
              
              {/* Users Widget */}
              <TelegramUsersWidget />
            </div>
          </TabsContent>

          {/* SMS Tab (Coming Soon) */}
          <TabsContent value="sms">
            <Card className="border-2 border-dashed border-gray-300">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Phone className="w-16 h-16 text-gray-400 mb-4" />
                <h3 className="text-xl font-semibold text-gray-600 mb-2">
                  SMS Integration - בקרוב
                </h3>
                <p className="text-gray-500 text-center max-w-md">
                  שילוב SMS יאפשר לך לשלוח תזכורות והודעות למטופלים ישירות מהמערכת
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          {/* WhatsApp Tab (Coming Soon) */}
          <TabsContent value="whatsapp">
            <Card className="border-2 border-dashed border-gray-300">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <MessageSquare className="w-16 h-16 text-gray-400 mb-4" />
                <h3 className="text-xl font-semibold text-gray-600 mb-2">
                  WhatsApp Integration - בקרוב
                </h3>
                <p className="text-gray-500 text-center max-w-md">
                  שילוב WhatsApp יאפשר תקשורת דו-כיוונית עם מטופלים דרך הפלטפורמה הפופולרית ביותר
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

