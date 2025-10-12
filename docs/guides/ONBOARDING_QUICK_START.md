# Clinic Onboarding - Quick Start Guide

**Version:** 21.0.0  
**Last Updated:** October 11, 2025

---

## 🚀 For Users: How to Register Your Clinic

### Step 1: Access the Registration Page
Navigate to: `https://your-domain.com/onboarding`

### Step 2: Fill Clinic Details
- **Clinic Name:** Your dental clinic's name
- **Email:** Official clinic email (for patient communication)
- **Phone:** Clinic phone number (format: 03-1234567 or 050-1234567)
- **Address:** Full clinic address

Click **Continue** →

### Step 3: Fill Owner Details
- **Full Name:** Your full name (e.g., Dr. John Smith)
- **Email:** Your personal email (for login)
- **Phone:** Your mobile number (optional)
- **Password:** Create a strong password (min 8 characters, with uppercase, lowercase, and numbers)
- **Confirm Password:** Re-enter your password

Click **Continue** →

### Step 4: Sign BAA Agreement
- Read the HIPAA Business Associate Agreement
- Scroll to the bottom
- Fill in:
  - **Signatory Name:** Your full name
  - **Signatory Title:** Your role (e.g., Owner, CEO, Practice Manager)
- Check the consent box
- Click **Sign Agreement** →

### Step 5: Complete!
You'll be redirected to your clinic dashboard. Welcome to DentaFlow! 🎉

### Optional: Complete Onboarding
Visit the **Onboarding Dashboard** to:
- ✅ Verify your email
- ✅ Invite team members
- ✅ Add your first patient

---

## 🔧 For Developers: Setup Instructions

### Prerequisites
- Node.js 22.x
- Python 3.11
- PostgreSQL
- Backend running on port 8000
- Frontend running on port 5173

### Installation

1. **Install Frontend Dependencies**
```bash
cd frontend
npm install
```

2. **Install Backend Dependencies**
```bash
cd backend
pip3 install -r requirements.txt
```

### Configuration

1. **Environment Variables**
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:password@localhost/dentaflow
ENCRYPTION_MASTER_KEY=your-32-byte-key-here
JWT_SECRET_KEY=your-jwt-secret-here
SENDGRID_API_KEY=your-sendgrid-key-here  # For email verification
```

2. **Database Migration**
```bash
cd backend
alembic upgrade head
```

### Running

1. **Start Backend**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

2. **Start Frontend**
```bash
cd frontend
npm run dev
```

3. **Access Application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📋 API Endpoints

### Registration
```
POST /api/v1/organizations/register
```
**Request:**
```json
{
  "clinic_name": "Dr. Smith Dental Clinic",
  "clinic_email": "info@smithdental.com",
  "clinic_phone": "03-1234567",
  "clinic_address": "123 Main St, Tel Aviv",
  "owner_full_name": "Dr. John Smith",
  "owner_email": "john@example.com",
  "owner_phone": "050-1234567",
  "owner_password": "SecurePass123"
}
```

**Response:**
```json
{
  "organization_id": "uuid",
  "user_id": "uuid",
  "access_token": "jwt-token",
  "message": "Organization registered successfully"
}
```

### BAA Signature
```
GET  /api/v1/baa/document/{organization_id}
POST /api/v1/baa/sign
GET  /api/v1/baa/status/{organization_id}
```

### Email Verification
```
POST /api/v1/auth/resend-verification
POST /api/v1/auth/verify-email
GET  /api/v1/auth/verification-status
```

---

## 🧪 Testing

### Manual Testing Checklist

#### Registration Flow
- [ ] Navigate to /onboarding
- [ ] Fill Step 1 (Clinic Details)
- [ ] Validate all fields
- [ ] Click Continue
- [ ] Fill Step 2 (Owner Details)
- [ ] Check password strength indicator
- [ ] Click Continue
- [ ] Verify organization created in database
- [ ] Verify user created with owner role

#### BAA Signature
- [ ] BAA document loads
- [ ] Scroll tracking works
- [ ] Can't submit without scrolling to bottom
- [ ] Fill signature form
- [ ] Submit signature
- [ ] Verify signature saved in database
- [ ] Check IP address and timestamp recorded

#### Email Verification
- [ ] Verification code sent (check console if email not configured)
- [ ] Enter 6-digit code
- [ ] Auto-advance between inputs
- [ ] Paste support works
- [ ] Resend code works
- [ ] Cooldown timer works
- [ ] Verify email marked as verified in database

#### Onboarding Dashboard
- [ ] Progress bar shows correct percentage
- [ ] Completed steps marked with checkmark
- [ ] Pending steps show action buttons
- [ ] Next step suggestion works
- [ ] Quick actions navigate correctly
- [ ] Skip option works

### Automated Testing
```bash
cd frontend
npm test
```

---

## 🐛 Troubleshooting

### Issue: Email verification codes not received
**Cause:** Email service not configured  
**Solution:** 
1. Configure SendGrid API key in backend/.env
2. Or check console logs for verification code
3. Temporarily use console code for testing

### Issue: BAA document not loading
**Cause:** Backend API not running or CORS issue  
**Solution:**
1. Ensure backend is running on port 8000
2. Check CORS settings in backend/app/main.py
3. Check browser console for errors

### Issue: Registration fails with 500 error
**Cause:** Database connection or missing environment variables  
**Solution:**
1. Check DATABASE_URL in .env
2. Ensure PostgreSQL is running
3. Run database migrations
4. Check backend logs for details

### Issue: Password strength indicator not working
**Cause:** JavaScript error  
**Solution:**
1. Check browser console for errors
2. Ensure all dependencies installed
3. Clear browser cache

---

## 📊 Monitoring

### Key Metrics to Track

1. **Completion Rate**
   - % of users who complete full onboarding
   - Target: > 80%

2. **Drop-off Points**
   - Which step users abandon most
   - Optimize based on data

3. **Time to Complete**
   - Average time from start to finish
   - Target: < 5 minutes

4. **BAA Signature Rate**
   - % of users who sign BAA
   - Target: 100% (required)

5. **Email Verification Rate**
   - % of users who verify email
   - Target: > 90%

### Analytics Events to Track
```javascript
// Step completion
analytics.track('Onboarding Step Completed', {
  step: 1,
  step_name: 'Clinic Details'
});

// Registration success
analytics.track('Clinic Registered', {
  organization_id: 'uuid',
  has_phone: true
});

// BAA signed
analytics.track('BAA Signed', {
  organization_id: 'uuid',
  signatory_title: 'Owner'
});

// Email verified
analytics.track('Email Verified', {
  user_id: 'uuid'
});

// Onboarding completed
analytics.track('Onboarding Completed', {
  organization_id: 'uuid',
  completion_percentage: 100
});
```

---

## 🔐 Security Considerations

### Data Protection
- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens for authentication
- ✅ HTTPS required in production
- ✅ CORS configured properly
- ✅ SQL injection prevention
- ✅ XSS protection

### HIPAA Compliance
- ✅ BAA signature required
- ✅ Audit logging enabled
- ✅ Encrypted data at rest (with ENCRYPTION_MASTER_KEY)
- ✅ IP address tracking
- ✅ Timestamp tracking
- ⚠️ Email encryption pending (configure email service)

### Best Practices
1. Always use HTTPS in production
2. Set strong JWT_SECRET_KEY
3. Rotate ENCRYPTION_MASTER_KEY periodically
4. Monitor failed login attempts
5. Implement rate limiting
6. Regular security audits

---

## 📚 Additional Resources

### Documentation
- [CLINIC_ONBOARDING_COMPLETE_V21.0.0.md](./CLINIC_ONBOARDING_COMPLETE_V21.0.0.md) - Full implementation details
- [HIPAA_COMPLIANCE.md](./HIPAA_COMPLIANCE.md) - HIPAA compliance guide
- [API Documentation](http://localhost:8000/docs) - Interactive API docs

### Support
- Email: support@dentaflow.co.il
- Documentation: https://docs.dentaflow.co.il
- GitHub Issues: https://github.com/your-org/dental-clinic-ai/issues

---

## ✅ Production Deployment Checklist

### Pre-deployment
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Email service configured (SendGrid/AWS SES)
- [ ] HTTPS certificate installed
- [ ] CORS configured for production domain
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Monitoring setup (Sentry, Datadog, etc.)

### Deployment
- [ ] Deploy backend to production server
- [ ] Deploy frontend to CDN/hosting
- [ ] Update DNS records
- [ ] Test full registration flow
- [ ] Test BAA signature
- [ ] Test email verification
- [ ] Monitor error logs

### Post-deployment
- [ ] Announce to users
- [ ] Monitor completion rates
- [ ] Gather user feedback
- [ ] Fix any issues
- [ ] Iterate and improve

---

**Need help?** Contact support@dentaflow.co.il

**Version:** 21.0.0  
**Last Updated:** October 11, 2025

