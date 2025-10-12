# AWS Cognito Setup Guide

Complete guide for setting up AWS Cognito with Google OAuth for DentaFlow.

## 📋 Table of Contents

1. [Create Cognito User Pool](#1-create-cognito-user-pool)
2. [Configure Google OAuth](#2-configure-google-oauth)
3. [Set Up Identity Pool (Optional)](#3-set-up-identity-pool-optional)
4. [Configure Environment Variables](#4-configure-environment-variables)
5. [Test Authentication](#5-test-authentication)

---

## 1. Create Cognito User Pool

### Step 1.1: Create User Pool

1. Go to [AWS Cognito Console](https://console.aws.amazon.com/cognito/)
2. Click **"Create user pool"**
3. **Configure sign-in experience:**
   - Provider types: **Cognito user pool**
   - Cognito user pool sign-in options: ✅ **Email**
   - Click **Next**

### Step 1.2: Configure Security Requirements

1. **Password policy:**
   - Minimum length: **8 characters**
   - Password requirements: ✅ **Lowercase**, ✅ **Uppercase**, ✅ **Numbers**
   - ⬜ Special characters (optional)

2. **Multi-factor authentication:**
   - MFA enforcement: **Optional** (recommended for production)
   - MFA methods: ✅ **SMS** or ✅ **Authenticator app**

3. **User account recovery:**
   - Self-service account recovery: ✅ **Enable**
   - Delivery method: **Email only**

4. Click **Next**

### Step 1.3: Configure Sign-up Experience

1. **Self-registration:**
   - ✅ **Enable self-registration**

2. **Attribute verification and user account confirmation:**
   - Attributes to verify: ✅ **Email**
   - Verification message: **Code** (default)

3. **Required attributes:**
   - ✅ **email** (already required)
   - ✅ **given_name** (optional)
   - ✅ **family_name** (optional)
   - ✅ **phone_number** (optional)

4. Click **Next**

### Step 1.4: Configure Message Delivery

1. **Email:**
   - Email provider: **Send email with Cognito** (for testing)
   - For production: Use **Amazon SES** for higher limits

2. **SMS (if MFA enabled):**
   - Use **Amazon SNS** (default)

3. Click **Next**

### Step 1.5: Integrate Your App

1. **User pool name:** `dentaflow-users`

2. **Hosted authentication pages:**
   - ⬜ Use Cognito Hosted UI (we'll use custom UI)

3. **Initial app client:**
   - App type: **Public client**
   - App client name: `dentaflow-web`
   - Client secret: **Don't generate** (for public clients)

4. **Advanced app client settings:**
   - Authentication flows: ✅ **ALLOW_USER_PASSWORD_AUTH**, ✅ **ALLOW_REFRESH_TOKEN_AUTH**

5. Click **Next**

### Step 1.6: Review and Create

1. Review all settings
2. Click **Create user pool**
3. **Save these values:**
   - User Pool ID: `us-east-1_XXXXXXXXX`
   - Client ID: `XXXXXXXXXXXXXXXXXXXXXXXXXX`

---

## 2. Configure Google OAuth

### Step 2.1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing: **DentaFlow**
3. Go to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client ID**

5. **Configure OAuth consent screen** (if first time):
   - User Type: **External**
   - App name: **DentaFlow**
   - User support email: your email
   - Developer contact: your email
   - Scopes: **email**, **profile**, **openid**
   - Test users: Add your email

6. **Create OAuth Client ID:**
   - Application type: **Web application**
   - Name: **DentaFlow Web Client**
   - Authorized JavaScript origins:
     - `https://dentaflow.ai`
     - `http://localhost:3000` (for development)
   - Authorized redirect URIs:
     - `https://dentaflow-users.auth.us-east-1.amazoncognito.com/oauth2/idpresponse`
     - (Replace `dentaflow-users` and `us-east-1` with your values)

7. Click **Create**
8. **Save these values:**
   - Client ID: `XXXXXXXXX.apps.googleusercontent.com`
   - Client Secret: `XXXXXXXXXXXXXXXXXXXXXXXX`

### Step 2.2: Add Google as Identity Provider in Cognito

1. Go back to AWS Cognito Console
2. Select your user pool: **dentaflow-users**
3. Go to **Sign-in experience** tab
4. Under **Federated identity provider sign-in**, click **Add identity provider**

5. **Select provider:** Google

6. **Configure Google:**
   - Client ID: (paste from Google)
   - Client secret: (paste from Google)
   - Authorized scopes: `profile email openid`
   - Attribute mapping:
     - `email` → `email`
     - `given_name` → `given_name`
     - `family_name` → `family_name`
     - `picture` → `picture`

7. Click **Add identity provider**

### Step 2.3: Configure App Client for Google

1. Go to **App integration** tab
2. Select your app client: **dentaflow-web**
3. Click **Edit**

4. **Hosted UI settings:**
   - Allowed callback URLs:
     - `https://dentaflow.ai/auth/callback`
     - `http://localhost:3000/auth/callback`
   - Allowed sign-out URLs:
     - `https://dentaflow.ai`
     - `http://localhost:3000`

5. **Identity providers:**
   - ✅ **Google**
   - ✅ **Cognito user pool**

6. **OAuth 2.0 grant types:**
   - ✅ **Authorization code grant**
   - ✅ **Implicit grant**

7. **OpenID Connect scopes:**
   - ✅ **openid**
   - ✅ **email**
   - ✅ **profile**

8. Click **Save changes**

---

## 3. Set Up Identity Pool (Optional)

Identity pools are used for AWS resource access (S3, DynamoDB, etc.).

### Step 3.1: Create Identity Pool

1. Go to Cognito Console → **Identity pools**
2. Click **Create identity pool**
3. **Identity pool name:** `dentaflow-identity-pool`

4. **Authentication providers:**
   - **Cognito:**
     - User Pool ID: (your pool ID)
     - App Client ID: (your client ID)

5. **Unauthenticated access:** ⬜ Disable

6. Click **Create pool**

7. **Configure IAM roles:**
   - Authenticated role: **Create new role** → `dentaflow-auth-role`
   - Permissions: Add policies as needed (S3, DynamoDB, etc.)

8. **Save Identity Pool ID:** `us-east-1:XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

---

## 4. Configure Environment Variables

Add these to your `.env` file:

```bash
# AWS Cognito Configuration
AWS_COGNITO_REGION=us-east-1
AWS_COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
AWS_COGNITO_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXX
AWS_COGNITO_CLIENT_SECRET=  # Leave empty for public clients
AWS_COGNITO_IDENTITY_POOL_ID=us-east-1:XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX

# Google OAuth
GOOGLE_CLIENT_ID=XXXXXXXXX.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=XXXXXXXXXXXXXXXXXXXXXXXX

# AWS Credentials (for boto3)
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
AWS_DEFAULT_REGION=us-east-1
```

---

## 5. Test Authentication

### Test 1: Sign Up with Email/Password

```bash
curl -X POST http://localhost:8000/api/v1/auth/cognito/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "given_name": "Test",
    "family_name": "User"
  }'
```

**Expected Response:**
```json
{
  "user_sub": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "user_confirmed": false,
  "message": "User registered successfully. Please check your email for confirmation code.",
  "code_delivery_details": {
    "Destination": "t***@e***.com",
    "DeliveryMedium": "EMAIL"
  }
}
```

### Test 2: Confirm Sign Up

```bash
curl -X POST http://localhost:8000/api/v1/auth/cognito/confirm-signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "confirmation_code": "123456"
  }'
```

### Test 3: Sign In

```bash
curl -X POST http://localhost:8000/api/v1/auth/cognito/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJraWQiOiJ...",
  "id_token": "eyJraWQiOiJ...",
  "refresh_token": "eyJjdHkiOiJ...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### Test 4: Get User Info

```bash
curl -X GET http://localhost:8000/api/v1/auth/cognito/me \
  -H "Authorization: Bearer <id_token>"
```

### Test 5: Google OAuth (Browser)

1. Navigate to:
```
https://dentaflow-users.auth.us-east-1.amazoncognito.com/oauth2/authorize?
  client_id=<YOUR_CLIENT_ID>&
  response_type=code&
  scope=openid+email+profile&
  redirect_uri=http://localhost:3000/auth/callback&
  identity_provider=Google
```

2. Sign in with Google
3. Get authorization code from redirect
4. Exchange code for tokens (handled by frontend)

---

## 🔒 Security Best Practices

1. **Use HTTPS in production** - Never send tokens over HTTP
2. **Store tokens securely** - Use httpOnly cookies or secure storage
3. **Enable MFA** - Require MFA for sensitive operations
4. **Rotate secrets** - Regularly rotate client secrets
5. **Monitor logs** - Use CloudWatch to monitor authentication attempts
6. **Set token expiration** - Access tokens: 1 hour, Refresh tokens: 30 days
7. **Implement rate limiting** - Prevent brute force attacks
8. **Use AWS WAF** - Protect against common web exploits

---

## 📊 Cost Estimation

**AWS Cognito Pricing (as of 2024):**
- First 50,000 MAUs: **Free**
- 50,001 - 100,000 MAUs: **$0.0055 per MAU**
- 100,001+ MAUs: **$0.0046 per MAU**

**Example:**
- 1,000 active users/month: **$0** (free tier)
- 75,000 active users/month: **~$137.50/month**

---

## 🐛 Troubleshooting

### Issue: "Invalid client_id"
**Solution:** Verify `AWS_COGNITO_CLIENT_ID` in `.env`

### Issue: "User is not confirmed"
**Solution:** Check email for confirmation code or use `confirm-signup` endpoint

### Issue: "Invalid refresh token"
**Solution:** Refresh tokens expire after 30 days (configurable)

### Issue: "Google sign-in not working"
**Solution:** 
1. Verify redirect URI matches exactly in Google Console
2. Check that Google is enabled in Cognito app client
3. Verify scopes are correct

### Issue: "JWT validation failed"
**Solution:** 
1. Check token hasn't expired
2. Verify `AWS_COGNITO_USER_POOL_ID` is correct
3. Ensure JWKS keys are being fetched correctly

---

## 📚 Additional Resources

- [AWS Cognito Documentation](https://docs.aws.amazon.com/cognito/)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [JWT.io](https://jwt.io/) - Debug JWT tokens
- [Cognito Pricing](https://aws.amazon.com/cognito/pricing/)

---

## ✅ Checklist

- [ ] User pool created
- [ ] App client configured
- [ ] Google OAuth credentials created
- [ ] Google added as identity provider in Cognito
- [ ] Redirect URIs configured in both Google and Cognito
- [ ] Environment variables set
- [ ] Email/password sign up tested
- [ ] Email/password sign in tested
- [ ] Google OAuth tested
- [ ] Token refresh tested
- [ ] Password reset tested
- [ ] MFA configured (production)
- [ ] CloudWatch logging enabled
- [ ] Rate limiting implemented
