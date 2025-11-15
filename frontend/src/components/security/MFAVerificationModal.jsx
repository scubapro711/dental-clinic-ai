import React, { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Shield, AlertCircle } from 'lucide-react'
import API_CONFIG from '@/config/api';

/**
 * MFAVerificationModal - Component for verifying MFA code during login
 * 
 * Features:
 * - 6-digit code input
 * - Option to use backup code
 * - Error handling
 * - Auto-focus on code input
 * 
 * @param {boolean} open - Whether the modal is open
 * @param {function} onOpenChange - Callback when modal open state changes
 * @param {function} onSuccess - Callback when verification is successful
 * @param {function} onCancel - Callback when user cancels
 * @param {string} email - User's email for verification
 */
export default function MFAVerificationModal({ 
  open, 
  onOpenChange, 
  onSuccess, 
  onCancel,
  email 
}) {
  const [code, setCode] = useState('')
  const [useBackupCode, setUseBackupCode] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleVerify = async () => {
    if (!code || (useBackupCode ? code.length !== 8 : code.length !== 6)) {
      setError(useBackupCode ? 'Please enter a valid 8-character backup code' : 'Please enter a valid 6-digit code')
      return
    }

    setLoading(true)
    setError('')

    try {
      const endpoint = useBackupCode 
        ? API_CONFIG.endpoint('mfa/verify-backup')
        : API_CONFIG.endpoint('mfa/verify')

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          code: code,
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Invalid code')
      }

      const data = await response.json()
      onSuccess?.(data)
    } catch (err) {
      setError(err.message)
      setCode('')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setCode('')
    setError('')
    setUseBackupCode(false)
    onCancel?.()
    onOpenChange(false)
  }

  const toggleBackupCode = () => {
    setUseBackupCode(!useBackupCode)
    setCode('')
    setError('')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <div className="flex items-center gap-2 mb-2">
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <DialogTitle>Two-Factor Authentication</DialogTitle>
          </div>
          <DialogDescription>
            {useBackupCode 
              ? 'Enter one of your backup codes'
              : 'Enter the 6-digit code from your authenticator app'
            }
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="mfa-code">
              {useBackupCode ? 'Backup Code' : 'Verification Code'}
            </Label>
            <Input
              id="mfa-code"
              type="text"
              placeholder={useBackupCode ? 'XXXXXXXX' : '000000'}
              value={code}
              onChange={(e) => {
                const value = useBackupCode 
                  ? e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8)
                  : e.target.value.replace(/\D/g, '').slice(0, 6)
                setCode(value)
              }}
              maxLength={useBackupCode ? 8 : 6}
              className="text-center text-2xl font-mono tracking-widest"
              disabled={loading}
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter' && code.length === (useBackupCode ? 8 : 6)) {
                  handleVerify()
                }
              }}
            />
          </div>

          <div className="flex justify-center">
            <Button
              variant="link"
              size="sm"
              onClick={toggleBackupCode}
              className="text-blue-600"
              disabled={loading}
            >
              {useBackupCode 
                ? 'Use authenticator code instead'
                : 'Use backup code instead'
              }
            </Button>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleCancel} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleVerify}
            disabled={loading || code.length !== (useBackupCode ? 8 : 6)}
            className="bg-gradient-to-r from-blue-600 to-purple-600"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Verifying...
              </>
            ) : (
              'Verify'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

