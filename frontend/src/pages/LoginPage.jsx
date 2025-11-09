import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Sparkles } from 'lucide-react'
import MFAVerificationModal from '@/components/security/MFAVerificationModal'

export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [mfaRequired, setMfaRequired] = useState(false)
  const [tempToken, setTempToken] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        // Check if MFA is required
        if (response.status === 403 && data.detail?.includes('MFA')) {
          setMfaRequired(true)
          setTempToken(data.temp_token || null)
          return
        }
        throw new Error(data.detail || 'Login failed')
      }

      // Check if MFA is enabled for this user
      if (data.mfa_required) {
        setMfaRequired(true)
        setTempToken(data.temp_token || null)
        return
      }

      // No MFA required, proceed with login
      await completeLogin(data.access_token)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const completeLogin = async (accessToken) => {
    try {
      // Fetch user info
      const userResponse = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      })
      
      if (!userResponse.ok) {
        throw new Error('Failed to fetch user information')
      }

      const userData = await userResponse.json()
      onLogin(accessToken, userData)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleMFASuccess = async (data) => {
    // MFA verification successful, complete login
    await completeLogin(data.access_token)
    setMfaRequired(false)
    setTempToken(null)
  }

  const handleMFACancel = () => {
    setMfaRequired(false)
    setTempToken(null)
    setEmail('')
    setPassword('')
    setError('Login cancelled. Please try again.')
  }

  return (
    <>
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
        <Card className="w-full max-w-md shadow-xl">
          <CardHeader className="space-y-1 text-center">
            <div className="flex justify-center mb-4">
              <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-3 rounded-2xl">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
            </div>
            <CardTitle className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              DentalAI
            </CardTitle>
            <CardDescription className="text-base">
              Sign in to your account to continue
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col space-y-4">
              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
              <p className="text-sm text-center text-gray-600">
                Don't have an account?{' '}
                <Link to="/register" className="text-blue-600 hover:underline font-medium">
                  Sign up
                </Link>
              </p>
            </CardFooter>
          </form>
        </Card>
      </div>

      {/* MFA Verification Modal */}
      <MFAVerificationModal
        open={mfaRequired}
        onOpenChange={setMfaRequired}
        onSuccess={handleMFASuccess}
        onCancel={handleMFACancel}
        email={email}
      />
    </>
  )
}

