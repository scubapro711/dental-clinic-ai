# Environment Variables Management

Complete guide to managing environment variables and secrets in DentaFlow.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Environment Files](#environment-files)
3. [AWS Secrets Manager](#aws-secrets-manager)
4. [Feature Flags](#feature-flags)
5. [Security Best Practices](#security-best-practices)

---

## 🎯 Overview

DentaFlow supports two methods for managing configuration:

1. **Environment Variables** (`.env` file) - Development
2. **AWS Secrets Manager** - Production

---

## 📁 Environment Files

### Development (.env)

```bash
# Application
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
APP_HOST=0.0.0.0
APP_PORT=8000

# AWS
AWS_REGION=us-east-1
USE_SECRETS_MANAGER=false  # false in development

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dentalai

# Redis
REDIS_URL=redis://localhost:6379/0

# Odoo
ODOO_URL=https://dentaflow.ai
ODOO_DB=dental_prod
ODOO_USERNAME=admin
ODOO_PASSWORD=your-password

# LLM
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...

# AWS Cognito
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
COGNITO_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxx
COGNITO_REGION=us-east-1

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Feature Flags
FEATURE_PROACTIVE_SUGGESTIONS=true
FEATURE_WHATSAPP=false
FEATURE_ANALYTICS=true
FEATURE_MFA=false
```

### Production (.env)

```bash
# Application
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING
APP_HOST=0.0.0.0
APP_PORT=8000

# AWS
AWS_REGION=us-east-1
USE_SECRETS_MANAGER=true  # true in production!

# Security (fallback only)
SECRET_KEY=fallback-secret-key
JWT_SECRET=fallback-jwt-secret

# Database (fallback only)
DATABASE_URL=postgresql://localhost/dentalai

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=https://dentaflow.ai

# Feature Flags
FEATURE_PROACTIVE_SUGGESTIONS=true
FEATURE_WHATSAPP=true
FEATURE_ANALYTICS=true
FEATURE_MFA=true
```

---

## 🔐 AWS Secrets Manager

### Setup

1. **Install AWS CLI:**
```bash
pip install boto3
```

2. **Configure AWS credentials:**
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter region: us-east-1
```

3. **Enable Secrets Manager in production:**
```bash
# In .env
USE_SECRETS_MANAGER=true
```

### Secret Structure

Secrets are organized by environment:

```
dentaflow/
├── development/
│   ├── database
│   ├── openai
│   ├── telegram
│   ├── odoo
│   ├── cognito
│   ├── encryption
│   └── jwt
├── staging/
│   └── (same structure)
└── production/
    └── (same structure)
```

### Creating Secrets

#### Database Credentials

```bash
aws secretsmanager create-secret \
    --name dentaflow/production/database \
    --description "DentaFlow production database credentials" \
    --secret-string '{
        "host": "dentaflow-prod.xxxxxxxx.us-east-1.rds.amazonaws.com",
        "port": "5432",
        "database": "dentalai",
        "username": "dentalai_user",
        "password": "super-secure-password"
    }'
```

#### OpenAI API Key

```bash
aws secretsmanager create-secret \
    --name dentaflow/production/openai \
    --description "DentaFlow OpenAI API key" \
    --secret-string '{
        "api_key": "sk-proj-..."
    }'
```

#### Telegram Bot Token

```bash
aws secretsmanager create-secret \
    --name dentaflow/production/telegram \
    --description "DentaFlow Telegram bot token" \
    --secret-string '{
        "bot_token": "123456:ABC-DEF..."
    }'
```

#### Odoo Credentials

```bash
aws secretsmanager create-secret \
    --name dentaflow/production/odoo \
    --description "DentaFlow Odoo credentials" \
    --secret-string '{
        "url": "https://dentaflow.ai",
        "db": "dental_prod",
        "username": "admin",
        "password": "odoo-password"
    }'
```

#### AWS Cognito Config

```bash
aws secretsmanager create-secret \
    --name dentaflow/production/cognito \
    --description "DentaFlow AWS Cognito configuration" \
    --secret-string '{
        "user_pool_id": "us-east-1_XXXXXXXXX",
        "client_id": "xxxxxxxxxxxxxxxxxxxxxxxxxx",
        "client_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxx",
        "region": "us-east-1"
    }'
```

#### Encryption Key

```bash
aws secretsmanager create-secret \
    --name dentaflow/production/encryption \
    --description "DentaFlow database encryption key" \
    --secret-string '{
        "key": "your-fernet-key-here"
    }'
```

#### JWT Secret

```bash
aws secretsmanager create-secret \
    --name dentaflow/production/jwt \
    --description "DentaFlow JWT secret key" \
    --secret-string '{
        "secret_key": "your-jwt-secret-here"
    }'
```

### Updating Secrets

```bash
aws secretsmanager update-secret \
    --secret-id dentaflow/production/database \
    --secret-string '{
        "host": "new-host.rds.amazonaws.com",
        "port": "5432",
        "database": "dentalai",
        "username": "dentalai_user",
        "password": "new-password"
    }'
```

### Secret Rotation

Enable automatic rotation for database credentials:

```bash
aws secretsmanager rotate-secret \
    --secret-id dentaflow/production/database \
    --rotation-lambda-arn arn:aws:lambda:us-east-1:ACCOUNT_ID:function:dentaflow-secret-rotation \
    --rotation-rules AutomaticallyAfterDays=30
```

### Using Secrets in Code

```python
from app.core.config import settings

# Automatically uses Secrets Manager if USE_SECRETS_MANAGER=true
database_url = settings.get_database_url()
openai_key = settings.get_openai_key()
telegram_token = settings.get_telegram_token()
odoo_creds = settings.get_odoo_credentials()
```

---

## 🚩 Feature Flags

Feature flags allow gradual rollout and A/B testing.

### Available Flags

| Flag | Default | Description |
|------|---------|-------------|
| `FEATURE_PROACTIVE_SUGGESTIONS` | `true` | Enable proactive AI suggestions |
| `FEATURE_WHATSAPP` | `false` | Enable WhatsApp integration |
| `FEATURE_ANALYTICS` | `true` | Enable analytics dashboard |
| `FEATURE_MFA` | `false` | Enable multi-factor authentication |
| `FEATURE_FINE_TUNING` | `false` | Enable LLM fine-tuning |
| `FEATURE_EXECUTIVE_AGENTS` | `false` | Enable executive AI agents |
| `FEATURE_SELF_HEALING` | `false` | Enable self-healing system |

### Using Feature Flags

```python
from app.core.feature_flags import feature_flags, FeatureFlag

# Check if feature is enabled
if feature_flags.is_enabled(FeatureFlag.PROACTIVE_SUGGESTIONS):
    # Show proactive suggestions
    pass

# Check for specific organization
if feature_flags.is_enabled_for_organization(FeatureFlag.WHATSAPP, org_id):
    # Enable WhatsApp for this organization
    pass

# Check for specific user
if feature_flags.is_enabled_for_user(FeatureFlag.MFA, user_id):
    # Require MFA for this user
    pass
```

### Feature Flag Decorator

```python
from app.core.feature_flags import require_feature, FeatureFlag

@router.get("/proactive-suggestions")
@require_feature(FeatureFlag.PROACTIVE_SUGGESTIONS)
async def get_suggestions():
    # This endpoint only works if feature is enabled
    pass
```

---

## 🔒 Security Best Practices

### 1. Never Commit Secrets

Add to `.gitignore`:
```
.env
.env.*
!.env.example
```

### 2. Use Strong Secrets

Generate secure secrets:
```bash
# Secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# JWT secret
python -c "import secrets; print(secrets.token_hex(32))"

# Encryption key (Fernet)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Rotate Secrets Regularly

- Database passwords: Every 90 days
- API keys: Every 180 days
- JWT secrets: Every 365 days
- Encryption keys: Never (or migrate data)

### 4. Use IAM Roles

In production, use IAM roles instead of access keys:

```bash
# EC2 instance role
aws iam create-role --role-name DentaFlowEC2Role --assume-role-policy-document file://trust-policy.json

# Attach Secrets Manager policy
aws iam attach-role-policy \
    --role-name DentaFlowEC2Role \
    --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
```

### 5. Audit Access

Enable CloudTrail for Secrets Manager:

```bash
aws cloudtrail create-trail \
    --name dentaflow-secrets-audit \
    --s3-bucket-name dentaflow-audit-logs
```

### 6. Encrypt at Rest

Secrets Manager encrypts at rest by default using AWS KMS.

### 7. Least Privilege

Grant minimal permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:dentaflow/production/*"
    }
  ]
}
```

---

## 🧪 Testing

### Local Testing with Secrets Manager

```bash
# Set environment
export USE_SECRETS_MANAGER=true
export AWS_PROFILE=dentaflow-dev

# Run application
python -m uvicorn app.main:app --reload
```

### Testing Fallback

```bash
# Disable Secrets Manager
export USE_SECRETS_MANAGER=false

# Application falls back to .env
python -m uvicorn app.main:app --reload
```

---

## 📚 References

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [12-Factor App Config](https://12factor.net/config)
