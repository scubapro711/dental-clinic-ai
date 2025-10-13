import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Sparkles, ChevronLeft, ChevronRight } from 'lucide-react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Textarea } from '@/components/ui/textarea'

export default function RegisterPage({ onRegister }) {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    // Account Info
    email: '',
    password: '',
    confirmPassword: '',
    
    // Personal Info
    full_name: '',
    phone: '',
    date_of_birth: '',
    gender: '',
    blood_type: '',
    
    // Address
    street: '',
    city: '',
    zip_code: '',
    country: '',
    
    // Medical Info
    has_allergies: false,
    allergy_notes: '',
    has_medications: false,
    medication_notes: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    })
  }

  const handleSelectChange = (name, value) => {
    setFormData({
      ...formData,
      [name]: value,
    })
  }

  const validateStep = () => {
    setError('')
    
    switch (step) {
      case 1: // Account Info
        if (!formData.email) {
          setError('Email is required')
          return false
        }
        if (!formData.password || formData.password.length < 8) {
          setError('Password must be at least 8 characters')
          return false
        }
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match')
          return false
        }
        break
        
      case 2: // Personal Info
        if (!formData.full_name) {
          setError('Full name is required')
          return false
        }
        if (!formData.phone) {
          setError('Phone number is required')
          return false
        }
        break
        
      case 3: // Address - all optional
        break
        
      case 4: // Medical Info - all optional
        break
    }
    
    return true
  }

  const nextStep = () => {
    if (validateStep()) {
      setStep(step + 1)
    }
  }

  const prevStep = () => {
    setError('')
    setStep(step - 1)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateStep()) {
      return
    }
    
    setLoading(true)
    setError('')

    try {
      // Remove confirmPassword before sending
      const { confirmPassword, ...submitData } = formData
      
      const response = await fetch('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Registration failed')
      }

      const data = await response.json()
      
      // Auto-login after registration
      const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: formData.email,
          password: formData.password,
        }),
      })

      const loginData = await loginResponse.json()
      onRegister(loginData.access_token, data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <>
            <div className="space-y-2">
              <Label htmlFor="email">Email *</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="you@example.com"
                value={formData.email}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password *</Label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
                required
                disabled={loading}
              />
              <p className="text-xs text-gray-500">Minimum 8 characters</p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password *</Label>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                placeholder="••••••••"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>
          </>
        )
        
      case 2:
        return (
          <>
            <div className="space-y-2">
              <Label htmlFor="full_name">Full Name *</Label>
              <Input
                id="full_name"
                name="full_name"
                type="text"
                placeholder="John Doe"
                value={formData.full_name}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone Number *</Label>
              <Input
                id="phone"
                name="phone"
                type="tel"
                placeholder="05X-XXXXXXX"
                value={formData.phone}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="date_of_birth">Date of Birth</Label>
              <Input
                id="date_of_birth"
                name="date_of_birth"
                type="date"
                value={formData.date_of_birth}
                onChange={handleChange}
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="gender">Gender</Label>
              <Select
                value={formData.gender}
                onValueChange={(value) => handleSelectChange('gender', value)}
                disabled={loading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="male">Male</SelectItem>
                  <SelectItem value="female">Female</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="blood_type">Blood Type</Label>
              <Select
                value={formData.blood_type}
                onValueChange={(value) => handleSelectChange('blood_type', value)}
                disabled={loading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select blood type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="a+">A+</SelectItem>
                  <SelectItem value="a-">A-</SelectItem>
                  <SelectItem value="b+">B+</SelectItem>
                  <SelectItem value="b-">B-</SelectItem>
                  <SelectItem value="ab+">AB+</SelectItem>
                  <SelectItem value="ab-">AB-</SelectItem>
                  <SelectItem value="o+">O+</SelectItem>
                  <SelectItem value="o-">O-</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </>
        )
        
      case 3:
        return (
          <>
            <div className="space-y-2">
              <Label htmlFor="street">Street Address</Label>
              <Input
                id="street"
                name="street"
                type="text"
                placeholder="123 Main St"
                value={formData.street}
                onChange={handleChange}
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="city">City</Label>
              <Input
                id="city"
                name="city"
                type="text"
                placeholder="Tel Aviv"
                value={formData.city}
                onChange={handleChange}
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="zip_code">Postal Code</Label>
              <Input
                id="zip_code"
                name="zip_code"
                type="text"
                placeholder="12345"
                value={formData.zip_code}
                onChange={handleChange}
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="country">Country</Label>
              <Input
                id="country"
                name="country"
                type="text"
                placeholder="Israel"
                value={formData.country}
                onChange={handleChange}
                disabled={loading}
              />
            </div>
          </>
        )
        
      case 4:
        return (
          <>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <Checkbox
                  id="has_allergies"
                  name="has_allergies"
                  checked={formData.has_allergies}
                  onCheckedChange={(checked) => handleSelectChange('has_allergies', checked)}
                  disabled={loading}
                />
                <div className="space-y-1">
                  <Label htmlFor="has_allergies" className="cursor-pointer">
                    I have allergies
                  </Label>
                </div>
              </div>
              
              {formData.has_allergies && (
                <div className="space-y-2 ml-7">
                  <Label htmlFor="allergy_notes">Please describe your allergies</Label>
                  <Textarea
                    id="allergy_notes"
                    name="allergy_notes"
                    placeholder="e.g., Penicillin, Peanuts, etc."
                    value={formData.allergy_notes}
                    onChange={handleChange}
                    disabled={loading}
                    rows={3}
                  />
                </div>
              )}
            </div>
            
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <Checkbox
                  id="has_medications"
                  name="has_medications"
                  checked={formData.has_medications}
                  onCheckedChange={(checked) => handleSelectChange('has_medications', checked)}
                  disabled={loading}
                />
                <div className="space-y-1">
                  <Label htmlFor="has_medications" className="cursor-pointer">
                    I am currently taking medications
                  </Label>
                </div>
              </div>
              
              {formData.has_medications && (
                <div className="space-y-2 ml-7">
                  <Label htmlFor="medication_notes">Please list your medications</Label>
                  <Textarea
                    id="medication_notes"
                    name="medication_notes"
                    placeholder="e.g., Aspirin 100mg daily, etc."
                    value={formData.medication_notes}
                    onChange={handleChange}
                    disabled={loading}
                    rows={3}
                  />
                </div>
              )}
            </div>
          </>
        )
    }
  }

  const stepTitles = [
    'Account Information',
    'Personal Information',
    'Address',
    'Medical Information'
  ]

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-3 rounded-2xl">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
          </div>
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Create Account
          </CardTitle>
          <CardDescription className="text-base">
            Step {step} of 4: {stepTitles[step - 1]}
          </CardDescription>
          
          {/* Progress bar */}
          <div className="flex gap-2 mt-4">
            {[1, 2, 3, 4].map((s) => (
              <div
                key={s}
                className={`h-2 flex-1 rounded-full transition-colors ${
                  s <= step ? 'bg-gradient-to-r from-blue-600 to-purple-600' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
        </CardHeader>
        
        <form onSubmit={step === 4 ? handleSubmit : (e) => { e.preventDefault(); nextStep(); }}>
          <CardContent className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            {renderStep()}
          </CardContent>
          
          <CardFooter className="flex flex-col space-y-4">
            <div className="flex gap-2 w-full">
              {step > 1 && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={prevStep}
                  disabled={loading}
                  className="flex-1"
                >
                  <ChevronLeft className="mr-2 h-4 w-4" />
                  Back
                </Button>
              )}
              
              <Button
                type="submit"
                className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {step === 4 ? 'Creating account...' : 'Processing...'}
                  </>
                ) : step === 4 ? (
                  'Create Account'
                ) : (
                  <>
                    Next
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
            
            <p className="text-sm text-center text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-600 hover:underline font-medium">
                Sign in
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}

