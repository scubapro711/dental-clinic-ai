import React, { useState, useEffect } from 'react'
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
import { Loader2, Shield, CheckCircle, AlertCircle, Copy, Check } from 'lucide-react'

/**
 * MFASetupModal - Component for setting up Multi-Factor Authentication
 * 
 * Features:
 * - QR code display for authenticator apps
 * - Manual secret key entry option
 * - Verification code input
 * - Backup codes display after successful setup
 * 
 * @param {boolean} open - Whether the modal is open
 * @param {function} onOpenChange - Callback when modal open state changes
 * @param {function} onSuccess - Callback when MFA setup is successful
 * @param {string} token - Authentication token
 */
export default function MFASetupModal({ open, onOpenChange, onSuccess, token }) {
  const [step, setStep] = useState('setup') // 'setup' | 'verify' | 'backup-codes'
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [qrCode, setQrCode] = useState('')
  const [secret, setSecret] = useState('')
  const [verificationCode, setVerificationCode] = useState('')
  const [backupCodes, setBackupCodes] = useState([])
  const [copiedSecret, setCopiedSecret] = useState(false)
  const [copiedBackupCodes, setCopiedBackupCodes] = useState(false)

  // Fetch QR code and secret when modal opens
  useEffect(() => {
    if (open && step === 'setup') {
      fetchMFASetup()
    }
  }, [open, step])

  const fetchMFASetup = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await fetch('http://localhost:8000/api/v1/mfa/setup', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to setup MFA')
      }

      const data = await response.json()
      setQrCode(data.qr_code)
      setSecret(data.secret)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleVerify = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setError('Please enter a valid 6-digit code')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch('http://localhost:8000/api/v1/mfa/verify-setup', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: verificationCode,
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Invalid verification code')
      }

      const data = await response.json()
      setBackupCodes(data.backup_codes)
      setStep('backup-codes')
    } catch (err) {
      setError(err.message)
      setVerificationCode('')
    } finally {
      setLoading(false)
    }
  }

  const handleComplete = () => {
    onSuccess?.()
    onOpenChange(false)
    // Reset state
    setTimeout(() => {
      setStep('setup')
      setQrCode('')
      setSecret('')
      setVerificationCode('')
      setBackupCodes([])
      setError('')
    }, 300)
  }

  const copyToClipboard = (text, type) => {
    navigator.clipboard.writeText(text)
    if (type === 'secret') {
      setCopiedSecret(true)
      setTimeout(() => setCopiedSecret(false), 2000)
    } else if (type === 'backup') {
      setCopiedBackupCodes(true)
      setTimeout(() => setCopiedBackupCodes(false), 2000)
    }
  }

  const downloadBackupCodes = () => {
    const text = backupCodes.join('\n')
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'dentaflow-backup-codes.txt'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <div className="flex items-center gap-2 mb-2">
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <DialogTitle>
              {step === 'setup' && 'Setup Two-Factor Authentication'}
              {step === 'verify' && 'Verify Your Setup'}
              {step === 'backup-codes' && 'Save Your Backup Codes'}
            </DialogTitle>
          </div>
          <DialogDescription>
            {step === 'setup' && 'Scan the QR code with your authenticator app'}
            {step === 'verify' && 'Enter the 6-digit code from your authenticator app'}
            {step === 'backup-codes' && 'Store these codes in a safe place'}
          </DialogDescription>
        </DialogHeader>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Setup Step */}
        {step === 'setup' && (
          <div className="space-y-4">
            {loading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
              </div>
            ) : (
              <>
                {/* QR Code */}
                <div className="flex justify-center p-4 bg-white rounded-lg border-2 border-gray-200">
                  {qrCode ? (
                    <img src={qrCode} alt="MFA QR Code" className="w-48 h-48" />
                  ) : (
                    <div className="w-48 h-48 flex items-center justify-center text-gray-400">
                      No QR code available
                    </div>
                  )}
                </div>

                {/* Manual Entry */}
                <div className="space-y-2">
                  <Label className="text-sm font-medium">Or enter this code manually:</Label>
                  <div className="flex gap-2">
                    <Input
                      value={secret}
                      readOnly
                      className="font-mono text-sm"
                    />
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => copyToClipboard(secret, 'secret')}
                    >
                      {copiedSecret ? (
                        <Check className="h-4 w-4 text-green-600" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>

                {/* Instructions */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-2">
                  <p className="text-sm font-medium text-blue-900">Setup Instructions:</p>
                  <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                    <li>Install an authenticator app (Google Authenticator, Authy, etc.)</li>
                    <li>Scan the QR code or enter the secret key manually</li>
                    <li>Click "Next" to verify your setup</li>
                  </ol>
                </div>
              </>
            )}
          </div>
        )}

        {/* Verify Step */}
        {step === 'verify' && (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="verification-code">Verification Code</Label>
              <Input
                id="verification-code"
                type="text"
                placeholder="000000"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                maxLength={6}
                className="text-center text-2xl font-mono tracking-widest"
                disabled={loading}
                autoFocus
              />
              <p className="text-sm text-gray-600">
                Enter the 6-digit code from your authenticator app
              </p>
            </div>
          </div>
        )}

        {/* Backup Codes Step */}
        {step === 'backup-codes' && (
          <div className="space-y-4">
            <Alert>
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                Two-factor authentication has been successfully enabled!
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <Label className="text-sm font-medium">Your Backup Codes:</Label>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-2 font-mono text-sm">
                  {backupCodes.map((code, index) => (
                    <div key={index} className="text-center py-1">
                      {code}
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => copyToClipboard(backupCodes.join('\n'), 'backup')}
                  className="flex-1"
                >
                  {copiedBackupCodes ? (
                    <>
                      <Check className="mr-2 h-4 w-4 text-green-600" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="mr-2 h-4 w-4" />
                      Copy All
                    </>
                  )}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={downloadBackupCodes}
                  className="flex-1"
                >
                  Download
                </Button>
              </div>
            </div>

            <Alert variant="warning" className="bg-yellow-50 border-yellow-200">
              <AlertCircle className="h-4 w-4 text-yellow-800" />
              <AlertDescription className="text-yellow-800">
                <strong>Important:</strong> Save these codes in a secure location. Each code can only be used once if you lose access to your authenticator app.
              </AlertDescription>
            </Alert>
          </div>
        )}

        <DialogFooter>
          {step === 'setup' && (
            <>
              <Button variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
                Cancel
              </Button>
              <Button
                onClick={() => setStep('verify')}
                disabled={loading || !qrCode}
                className="bg-gradient-to-r from-blue-600 to-purple-600"
              >
                Next
              </Button>
            </>
          )}

          {step === 'verify' && (
            <>
              <Button variant="outline" onClick={() => setStep('setup')} disabled={loading}>
                Back
              </Button>
              <Button
                onClick={handleVerify}
                disabled={loading || verificationCode.length !== 6}
                className="bg-gradient-to-r from-blue-600 to-purple-600"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  'Verify & Enable'
                )}
              </Button>
            </>
          )}

          {step === 'backup-codes' && (
            <Button
              onClick={handleComplete}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600"
            >
              Done
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

