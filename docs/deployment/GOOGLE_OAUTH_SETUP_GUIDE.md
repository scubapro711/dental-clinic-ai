# Google OAuth Setup Guide

This guide explains how to configure Google OAuth for DentaFlow.

## 📋 Prerequisites

- Google Account
- Access to [Google Cloud Console](https://console.cloud.google.com)

---

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **Select a project** → **New Project**
3. Enter project name: `DentaFlow` (or your preferred name)
4. Click **Create**

### Step 2: Enable Google+ API

1. In the left sidebar, go to **APIs & Services** → **Library**
2. Search for "Google+ API"
3. Click on it and click **Enable**

### Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** (for public access)
3. Click **Create**
4. Fill in the required fields:
   - **App name**: `DentaFlow`
   - **User support email**: Your email
   - **Developer contact email**: Your email
5. Click **Save and Continue**
6. **Scopes**: Click **Add or Remove Scopes**
   - Select: `email`, `profile`, `openid`
   - Click **Update**
7. Click **Save and Continue**
8. **Test users** (optional for development):
   - Add your test email addresses
9. Click **Save and Continue**

### Step 4: Create OAuth Client ID

1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth client ID**
3. Select **Application type**: `Web application`
4. **Name**: `DentaFlow Web Client`
5. **Authorized redirect URIs**:
   - For development: `http://localhost:8000/api/v1/auth/google/callback`
   - For production: `https://yourdomain.com/api/v1/auth/google/callback`
6. Click **Create**
7. **Save the credentials**:
   - Copy **Client ID**
   - Copy **Client Secret**

---

## 🔧 Configure DentaFlow

### Option 1: Environment Variables (Recommended)

Add to your `.env` file:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

### Option 2: AWS Secrets Manager (Production)

Store credentials in AWS Secrets Manager:

```json
{
  "GOOGLE_CLIENT_ID": "your-client-id-here.apps.googleusercontent.com",
  "GOOGLE_CLIENT_SECRET": "your-client-secret-here",
  "GOOGLE_REDIRECT_URI": "https://yourdomain.com/api/v1/auth/google/callback"
}
```

---

## 🧪 Test the Integration

### 1. Start the backend server

```bash
cd backend
python3.11 -m uvicorn app.main:app --reload
```

### 2. Test the Google OAuth flow

Open your browser and navigate to:

```
http://localhost:8000/api/v1/auth/google/login
```

You should be redirected to Google's consent screen.

### 3. After authorization

You'll be redirected back to the callback URL with:
- `access_token`: JWT token for API access
- `user_id`: User ID
- `email`: User email
- `is_new_user`: Whether this is a new registration

---

## 📝 API Endpoints

### 1. Initiate Google Login

```http
GET /api/v1/auth/google/login
```

Redirects user to Google's consent screen.

### 2. Google Callback (automatic)

```http
GET /api/v1/auth/google/callback?code=...&state=...
```

Handles the callback from Google and returns JWT token.

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "is_new_user": false,
  "message": "Successfully authenticated with Google"
}
```

### 3. Link Google Account (for existing users)

```http
POST /api/v1/auth/google/link
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "code": "authorization-code-from-google"
}
```

Allows users who registered with email/password to link their Google account.

---

## 🔒 Security Best Practices

### 1. HTTPS in Production

Always use HTTPS in production:
```
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/auth/google/callback
```

### 2. State Parameter (CSRF Protection)

The implementation includes state parameter for CSRF protection.

### 3. Verify Email

Google-verified emails are automatically trusted (`is_verified=True`).

### 4. Scope Limitation

We only request:
- `openid`: User ID
- `email`: Email address
- `profile`: Name and picture

No sensitive data is requested.

---

## 🌐 Frontend Integration

### React Example

```jsx
import React from 'react';

function GoogleLoginButton() {
  const handleGoogleLogin = () => {
    // Redirect to backend Google OAuth endpoint
    window.location.href = 'http://localhost:8000/api/v1/auth/google/login';
  };

  return (
    <button onClick={handleGoogleLogin}>
      <img src="/google-icon.svg" alt="Google" />
      Sign in with Google
    </button>
  );
}

export default GoogleLoginButton;
```

### Handle Callback

Create a callback page to handle the redirect:

```jsx
// pages/auth/google/callback.jsx
import { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

function GoogleCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const code = searchParams.get('code');
    
    if (code) {
      // Exchange code for token (handled by backend)
      fetch(`http://localhost:8000/api/v1/auth/google/callback?code=${code}`)
        .then(res => res.json())
        .then(data => {
          // Store token
          localStorage.setItem('access_token', data.access_token);
          
          // Redirect to dashboard
          navigate('/dashboard');
        })
        .catch(err => {
          console.error('Google OAuth error:', err);
          navigate('/login?error=google_oauth_failed');
        });
    }
  }, [searchParams, navigate]);

  return <div>Authenticating with Google...</div>;
}

export default GoogleCallback;
```

---

## 🐛 Troubleshooting

### Error: "redirect_uri_mismatch"

**Solution:** Make sure the redirect URI in your code matches exactly what you configured in Google Cloud Console.

### Error: "Google OAuth is not configured"

**Solution:** Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in your `.env` file.

### Error: "Email not provided by Google"

**Solution:** Make sure you requested the `email` scope in the OAuth consent screen.

### User created but not linked to organization

**Solution:** Check that a default organization exists in the database, or provide `organization_id` during registration.

---

## 📊 Database Schema

### User Model Updates

The `User` model now includes:

```python
google_id = Column(String(255), nullable=True, unique=True, index=True)
picture_url = Column(String(500), nullable=True)
```

### Migration Required

Run migrations to add these fields:

```bash
cd backend
alembic revision --autogenerate -m "Add Google OAuth fields to User"
alembic upgrade head
```

---

## ✅ Verification Checklist

- [ ] Google Cloud Project created
- [ ] OAuth consent screen configured
- [ ] OAuth Client ID created
- [ ] Credentials saved in `.env`
- [ ] Backend server running
- [ ] Can access `/api/v1/auth/google/login`
- [ ] Redirected to Google consent screen
- [ ] Successfully authenticated
- [ ] JWT token received
- [ ] User created/updated in database

---

## 🎉 Success!

You've successfully configured Google OAuth for DentaFlow!

Users can now sign in with their Google accounts in one click.

---

## 📚 Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com)
- [OAuth 2.0 Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)

---

## 🆘 Need Help?

If you encounter any issues:
1. Check the logs: `tail -f backend/logs/app.log`
2. Verify environment variables: `echo $GOOGLE_CLIENT_ID`
3. Test the Google OAuth service directly
4. Contact support

---

**Happy coding! 🚀**
