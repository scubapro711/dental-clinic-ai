# AWS Deployment Secrets

## ⚠️ Security Notice

This directory contains sensitive configuration information. **DO NOT commit actual secrets to Git.**

## AWS Credentials

**Account ID:** 488675216463  
**IAM User:** Scubapro711_Dev_API  
**Region:** us-east-1

### Access Keys
- Access keys are stored securely in AWS IAM
- For deployment, use GitHub Secrets or AWS Secrets Manager
- Never commit access keys to version control

## ECR Repository

**Backend Image Repository:**
```
488675216463.dkr.ecr.us-east-1.amazonaws.com/dentalai-backend
```

## Required Secrets for Deployment

### 1. AWS Credentials
```bash
AWS_ACCESS_KEY_ID=AKIAXDR2QBRHTS5MKE3K
AWS_SECRET_ACCESS_KEY=<stored-securely>
AWS_DEFAULT_REGION=us-east-1
```

### 2. Database Credentials
```bash
DB_PASSWORD=<strong-password>
```

### 3. OpenAI API Key
```bash
OPENAI_API_KEY=sk-CExcY56xFcv7rR43RkpeEP
```

### 4. Odoo Credentials
```bash
ODOO_PASSWORD=<secure-password>
```

## GitHub Secrets Configuration

Add these secrets to your GitHub repository:
1. Go to: `Settings > Secrets and variables > Actions`
2. Add the following secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `OPENAI_API_KEY`
   - `DB_PASSWORD`
   - `ODOO_PASSWORD`

## Terraform Variables

The actual values are stored in:
- `terraform/environments/production/terraform.tfvars` (gitignored)
- Use `terraform.tfvars.example` as template

## Local Development

For local development, copy `.env.example` to `.env` and fill in your values.

---

**Last Updated:** October 4, 2025  
**Maintained By:** DevOps Team
