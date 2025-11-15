import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { 
  Shield, 
  CheckCircle, 
  AlertCircle, 
  Key, 
  Smartphone,
  FileText,
  Loader2
} from 'lucide-react'
import MFASetupModal from '@/components/security/MFASetupModal'
import API_CONFIG from '@/config/api';

/**
 * SecuritySettings - Page for managing security settings
 * 
 * Features:
 * - MFA status display
 * - Enable/disable MFA
 * - View/regenerate backup codes
 * - Security recommendations
 * 
 * @param {string} token - Authentication token
 * @param {object} user - Current user object
 */
export default function SecuritySettings({ token, user }) {
  const [mfaEnabled, setMfaEnabled] = useState(false)
  const [loading, setLoading] = useState(true)
  const [setupModalOpen, setSetupModalOpen] = useState(false)
  const [backupCodesModalOpen, setBackupCodesModalOpen] = useState(false)
  const [disabling, setDisabling] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    fetchMFAStatus()
  }, [])

  const fetchMFAStatus = async () => {
    setLoading(true)
    try {
      const response = await fetch(API_CONFIG.endpoint('mfa/status'), {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setMfaEnabled(data.mfa_enabled)
      }
    } catch (err) {
      console.error('Failed to fetch MFA status:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDisableMFA = async () => {
    if (!confirm('Are you sure you want to disable two-factor authentication? This will make your account less secure.')) {
      return
    }

    setDisabling(true)
    setError('')

    try {
      const response = await fetch(API_CONFIG.endpoint('mfa/disable'), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to disable MFA')
      }

      setMfaEnabled(false)
      setSuccess('Two-factor authentication has been disabled')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.message)
    } finally {
      setDisabling(false)
    }
  }

  const handleSetupSuccess = () => {
    setMfaEnabled(true)
    setSuccess('Two-factor authentication has been enabled successfully!')
    setTimeout(() => setSuccess(''), 5000)
  }

  const handleRegenerateBackupCodes = async () => {
    if (!confirm('Regenerating backup codes will invalidate all existing codes. Continue?')) {
      return
    }

    try {
      const response = await fetch(API_CONFIG.endpoint('mfa/regenerate-backup-codes'), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to regenerate backup codes')
      }

      const data = await response.json()
      // Show backup codes modal with new codes
      setBackupCodesModalOpen(true)
      setSuccess('Backup codes have been regenerated')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="container max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Security Settings
        </h1>
        <p className="text-gray-600 mt-2">
          Manage your account security and authentication methods
        </p>
      </div>

      {/* Alerts */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* Two-Factor Authentication Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <CardTitle>Two-Factor Authentication</CardTitle>
                <CardDescription>
                  Add an extra layer of security to your account
                </CardDescription>
              </div>
            </div>
            <Badge 
              variant={mfaEnabled ? "success" : "secondary"}
              className={mfaEnabled ? "bg-green-100 text-green-800" : ""}
            >
              {mfaEnabled ? 'Enabled' : 'Disabled'}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-gray-600">
            Two-factor authentication (2FA) adds an additional layer of security to your account by requiring a verification code from your authenticator app when you sign in.
          </p>

          {!mfaEnabled ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 space-y-3">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
                <div>
                  <p className="font-medium text-yellow-900">Your account is not protected by 2FA</p>
                  <p className="text-sm text-yellow-800 mt-1">
                    We strongly recommend enabling two-factor authentication to protect your account from unauthorized access.
                  </p>
                </div>
              </div>
              <Button
                onClick={() => setSetupModalOpen(true)}
                className="bg-gradient-to-r from-blue-600 to-purple-600"
              >
                <Smartphone className="mr-2 h-4 w-4" />
                Enable Two-Factor Authentication
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-green-900">Your account is protected</p>
                    <p className="text-sm text-green-800 mt-1">
                      Two-factor authentication is active on your account.
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={handleRegenerateBackupCodes}
                >
                  <Key className="mr-2 h-4 w-4" />
                  Regenerate Backup Codes
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleDisableMFA}
                  disabled={disabling}
                >
                  {disabling ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Disabling...
                    </>
                  ) : (
                    'Disable 2FA'
                  )}
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Security Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>Security Recommendations</CardTitle>
          <CardDescription>
            Follow these best practices to keep your account secure
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className={`p-2 rounded-lg ${mfaEnabled ? 'bg-green-100' : 'bg-gray-100'}`}>
                <CheckCircle className={`h-4 w-4 ${mfaEnabled ? 'text-green-600' : 'text-gray-400'}`} />
              </div>
              <div className="flex-1">
                <p className="font-medium">Enable two-factor authentication</p>
                <p className="text-sm text-gray-600">
                  Protect your account with an additional verification step
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-gray-100">
                <Key className="h-4 w-4 text-gray-400" />
              </div>
              <div className="flex-1">
                <p className="font-medium">Use a strong, unique password</p>
                <p className="text-sm text-gray-600">
                  Choose a password that's at least 12 characters long and includes a mix of letters, numbers, and symbols
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-gray-100">
                <FileText className="h-4 w-4 text-gray-400" />
              </div>
              <div className="flex-1">
                <p className="font-medium">Save your backup codes</p>
                <p className="text-sm text-gray-600">
                  Store your backup codes in a secure location in case you lose access to your authenticator app
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* MFA Setup Modal */}
      <MFASetupModal
        open={setupModalOpen}
        onOpenChange={setSetupModalOpen}
        onSuccess={handleSetupSuccess}
        token={token}
      />
    </div>
  )
}

