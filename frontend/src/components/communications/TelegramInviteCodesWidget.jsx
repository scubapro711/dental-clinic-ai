import React, { useState, useEffect } from 'react';
import BaseWidget from '../widgets/BaseWidget';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Plus, Copy, Check, Ticket, Clock, Users } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Telegram Invite Codes Widget
 * 
 * Manage Telegram invitation codes for patient onboarding
 */
export default function TelegramInviteCodesWidget() {
  const [codes, setCodes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [copiedCode, setCopiedCode] = useState(null);
  const [newCodeData, setNewCodeData] = useState({
    max_uses: '',
    expires_in_days: 7,
    notes: ''
  });

  useEffect(() => {
    fetchInviteCodes();
  }, []);

  const fetchInviteCodes = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/telegram-admin/invite-codes', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id')
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCodes(data);
      }
    } catch (error) {
      console.error('Error fetching invite codes:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createInviteCode = async () => {
    try {
      const response = await fetch('/api/v1/telegram-admin/invite-codes', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id'),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          max_uses: newCodeData.max_uses ? parseInt(newCodeData.max_uses) : null,
          expires_in_days: parseInt(newCodeData.expires_in_days),
          notes: newCodeData.notes || null
        })
      });
      
      if (response.ok) {
        const newCode = await response.json();
        setCodes([newCode, ...codes]);
        setIsDialogOpen(false);
        setNewCodeData({ max_uses: '', expires_in_days: 7, notes: '' });
        
        // Auto-copy the new code
        copyToClipboard(newCode.code);
      }
    } catch (error) {
      console.error('Error creating invite code:', error);
    }
  };

  const copyToClipboard = (code) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const getStatusBadge = (code) => {
    if (code.status === 'ACTIVE') {
      return <Badge className="bg-green-500">פעיל</Badge>;
    } else if (code.status === 'EXPIRED') {
      return <Badge variant="secondary">פג תוקף</Badge>;
    } else if (code.status === 'EXHAUSTED') {
      return <Badge variant="secondary">מוצה</Badge>;
    }
    return <Badge variant="outline">{code.status}</Badge>;
  };

  return (
    <BaseWidget
      title="קודי הזמנה"
      icon={<Ticket />}
      agent="alex"
      badge={`${codes.filter(c => c.status === 'ACTIVE').length} פעילים`}
      isLoading={isLoading}
      headerAction={
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
              <Plus className="w-4 h-4 mr-2" />
              קוד חדש
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>יצירת קוד הזמנה חדש</DialogTitle>
              <DialogDescription>
                צור קוד הזמנה למטופלים חדשים להתחבר לבוט הטלגרם
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="max_uses">מספר שימושים מקסימלי (אופציונלי)</Label>
                <Input
                  id="max_uses"
                  type="number"
                  placeholder="ללא הגבלה"
                  value={newCodeData.max_uses}
                  onChange={(e) => setNewCodeData({...newCodeData, max_uses: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="expires_in_days">תוקף (ימים)</Label>
                <Input
                  id="expires_in_days"
                  type="number"
                  value={newCodeData.expires_in_days}
                  onChange={(e) => setNewCodeData({...newCodeData, expires_in_days: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="notes">הערות (אופציונלי)</Label>
                <Input
                  id="notes"
                  placeholder="למשל: קבוצת מטופלים חדשים"
                  value={newCodeData.notes}
                  onChange={(e) => setNewCodeData({...newCodeData, notes: e.target.value})}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                ביטול
              </Button>
              <Button onClick={createInviteCode} className="bg-gradient-to-r from-blue-500 to-purple-600">
                צור קוד
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      }
    >
      <div className="space-y-3">
        {codes.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Ticket className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p>אין קודי הזמנה עדיין</p>
            <p className="text-sm">צור קוד ראשון כדי להתחיל</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {codes.map((code) => (
              <div
                key={code.id}
                className="p-3 border-2 rounded-lg hover:shadow-md transition-all duration-200 bg-white"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <code className="px-3 py-1 bg-blue-50 text-blue-600 rounded font-mono text-sm font-bold">
                      {code.code}
                    </code>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(code.code)}
                      className="h-7 w-7 p-0"
                    >
                      {copiedCode === code.code ? (
                        <Check className="w-4 h-4 text-green-500" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                  {getStatusBadge(code)}
                </div>
                
                <div className="flex items-center gap-4 text-xs text-gray-600">
                  <div className="flex items-center gap-1">
                    <Users className="w-3 h-3" />
                    <span>{code.used_count}/{code.max_uses || '∞'}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>
                      {code.expires_at 
                        ? new Date(code.expires_at).toLocaleDateString('he-IL')
                        : 'ללא תפוגה'}
                    </span>
                  </div>
                </div>
                
                {code.notes && (
                  <p className="text-xs text-gray-500 mt-2 italic">{code.notes}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </BaseWidget>
  );
}

