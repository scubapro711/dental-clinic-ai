# 🚀 DentalAI Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying DentalAI to AWS production environment.

**Architecture:**
- Frontend: S3 + CloudFront CDN
- Backend: ECS Fargate + Application Load Balancer
- Database: RDS PostgreSQL (Multi-AZ)
- Cache: ElastiCache Redis
- Memory: Neo4j on EC2 (optional)
- Infrastructure: Terraform
- CI/CD: GitHub Actions

---

## Prerequisites

### Required Tools
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### AWS Account Setup
1. Create AWS account
2. Create IAM user with AdministratorAccess
3. Generate access keys
4. Configure AWS CLI:
```bash
aws configure
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: us-east-1
# Default output format: json
```

---

## Phase 1: Infrastructure Setup (30 minutes)

### Step 1.1: Create ECR Repositories
```bash
# Backend repository
aws ecr create-repository \
  --repository-name dentalai-backend \
  --region us-east-1

# Frontend repository (optional, we use S3)
aws ecr create-repository \
  --repository-name dentalai-frontend \
  --region us-east-1
```

### Step 1.2: Configure Terraform
```bash
cd terraform/environments/production

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
nano terraform.tfvars
```

**Required values:**
- `db_password`: Strong database password
- `odoo_password`: Odoo admin password
- `openai_api_key`: Your OpenAI API key
- `backend_image`: ECR repository URI

### Step 1.3: Deploy Infrastructure
```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan -out=tfplan

# Apply (create infrastructure)
terraform apply tfplan
```

**Expected time:** 15-20 minutes

**Outputs:**
- VPC ID
- RDS endpoint
- Redis endpoint
- Backend ALB DNS
- Frontend CloudFront domain
- S3 bucket name

---

## Phase 2: Build & Push Docker Images (15 minutes)

### Step 2.1: Build Backend Image
```bash
cd ../../backend

# Get ECR login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_ECR_REGISTRY

# Build image
docker build -t dentalai-backend:latest .

# Tag image
docker tag dentalai-backend:latest \
  YOUR_ECR_REGISTRY/dentalai-backend:latest

# Push image
docker push YOUR_ECR_REGISTRY/dentalai-backend:latest
```

### Step 2.2: Build Frontend
```bash
cd ../frontend

# Install dependencies
npm ci --legacy-peer-deps

# Build
VITE_API_URL=https://YOUR_BACKEND_URL npm run build

# Deploy to S3
aws s3 sync dist/ s3://YOUR_S3_BUCKET/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

---

## Phase 3: Database Setup (10 minutes)

### Step 3.1: Run Migrations
```bash
cd ../backend

# Connect to RDS via bastion (if needed)
# Or run migrations from ECS task

# Install alembic
pip install alembic

# Run migrations
alembic upgrade head
```

### Step 3.2: Seed Initial Data (Optional)
```bash
# Run seed script
python scripts/seed_data.py
```

---

## Phase 4: Configure GitHub Actions (10 minutes)

### Step 4.1: Add GitHub Secrets
Go to: `Settings > Secrets and variables > Actions`

Add the following secrets:
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `VITE_API_URL`: Backend API URL
- `VITE_WS_URL`: Backend WebSocket URL
- `S3_BUCKET`: Frontend S3 bucket name
- `CLOUDFRONT_DISTRIBUTION_ID`: CloudFront distribution ID

### Step 4.2: Test CI/CD
```bash
# Push to main branch
git add .
git commit -m "Deploy to production"
git push origin main
```

GitHub Actions will automatically:
1. Run tests
2. Build Docker images
3. Push to ECR
4. Deploy to ECS
5. Deploy frontend to S3
6. Invalidate CloudFront

---

## Phase 5: Verification (10 minutes)

### Step 5.1: Check Backend Health
```bash
curl https://YOUR_BACKEND_URL/health
# Expected: {"status":"healthy"}

curl https://YOUR_BACKEND_URL/api/v1/monitoring/agent-status
# Expected: {"status":"online",...}
```

### Step 5.2: Check Frontend
```bash
curl https://YOUR_CLOUDFRONT_DOMAIN/
# Expected: HTML content

# Open in browser
open https://YOUR_CLOUDFRONT_DOMAIN/
```

### Step 5.3: Test Dashboard
1. Navigate to: `https://YOUR_CLOUDFRONT_DOMAIN/dashboard`
2. Login (if authentication is enabled)
3. Verify all widgets load
4. Test language switcher (Hebrew ↔ English)
5. Test agent controls (Pause/Restart)

---

## Phase 6: Monitoring Setup (15 minutes)

### Step 6.1: CloudWatch Dashboards
```bash
# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name DentalAI-Production \
  --dashboard-body file://monitoring/cloudwatch-dashboard.json
```

### Step 6.2: Set Up Alarms
```bash
# CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name dentalai-backend-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# Memory alarm
aws cloudwatch put-metric-alarm \
  --alarm-name dentalai-backend-high-memory \
  --alarm-description "Alert when memory exceeds 80%" \
  --metric-name MemoryUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

---

## Phase 7: Security Hardening (15 minutes)

### Step 7.1: Enable WAF
```bash
# Create WAF web ACL
aws wafv2 create-web-acl \
  --name dentalai-waf \
  --scope CLOUDFRONT \
  --default-action Allow={} \
  --rules file://security/waf-rules.json
```

### Step 7.2: Enable Secrets Rotation
```bash
# Enable automatic rotation for RDS password
aws secretsmanager rotate-secret \
  --secret-id dentalai/rds/password \
  --rotation-lambda-arn YOUR_ROTATION_LAMBDA_ARN \
  --rotation-rules AutomaticallyAfterDays=30
```

### Step 7.3: Enable Backup
```bash
# Enable automated backups for RDS
aws rds modify-db-instance \
  --db-instance-identifier dentalai-production \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00"
```

---

## Troubleshooting

### Backend Not Starting
```bash
# Check ECS task logs
aws logs tail /ecs/dentalai-backend --follow

# Check task definition
aws ecs describe-tasks \
  --cluster dentalai-production \
  --tasks TASK_ID
```

### Frontend Not Loading
```bash
# Check S3 bucket
aws s3 ls s3://YOUR_S3_BUCKET/

# Check CloudFront distribution
aws cloudfront get-distribution \
  --id YOUR_DISTRIBUTION_ID
```

### Database Connection Issues
```bash
# Check security groups
aws ec2 describe-security-groups \
  --group-ids YOUR_SG_ID

# Test connection from ECS task
aws ecs execute-command \
  --cluster dentalai-production \
  --task TASK_ID \
  --container dentalai-backend \
  --interactive \
  --command "/bin/bash"
```

---

## Cost Optimization

### Estimated Monthly Costs
| Service | Configuration | Cost |
|---------|--------------|------|
| RDS PostgreSQL | db.t3.medium, 100GB | ~$70 |
| ElastiCache Redis | cache.t3.micro | ~$15 |
| ECS Fargate | 2 tasks, 1 vCPU, 2GB RAM | ~$30 |
| S3 + CloudFront | 100GB storage, 1TB transfer | ~$15 |
| ALB | 1 load balancer | ~$20 |
| Data Transfer | Varies | ~$10 |
| **Total** | | **~$160/month** |

### Cost Reduction Tips
1. Use Reserved Instances for RDS (save 40%)
2. Enable S3 Intelligent-Tiering
3. Use CloudFront caching aggressively
4. Schedule ECS tasks to scale down at night
5. Use Spot Instances for non-critical workloads

---

## Maintenance

### Daily
- Check CloudWatch dashboards
- Review error logs
- Monitor costs

### Weekly
- Review security alerts
- Check backup status
- Update dependencies

### Monthly
- Review and optimize costs
- Update Terraform modules
- Security audit
- Performance testing

---

## Rollback Procedure

### Quick Rollback
```bash
# Rollback backend to previous version
aws ecs update-service \
  --cluster dentalai-production \
  --service dentalai-backend-service \
  --task-definition dentalai-backend:PREVIOUS_REVISION

# Rollback frontend
aws s3 sync s3://YOUR_BACKUP_BUCKET/ s3://YOUR_S3_BUCKET/ --delete
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

### Full Rollback
```bash
# Rollback infrastructure
cd terraform/environments/production
terraform apply -var-file=previous.tfvars
```

---

## Support

### Documentation
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Terraform Documentation](https://www.terraform.io/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Contact
- **Email:** support@dentalai.com
- **Slack:** #dentalai-devops
- **On-call:** +1-XXX-XXX-XXXX

---

## Appendix

### A. Environment Variables Reference
See: `backend/.env.example`

### B. Terraform Modules Reference
See: `terraform/modules/README.md`

### C. API Documentation
See: `https://YOUR_BACKEND_URL/docs`

### D. Architecture Diagram
See: `docs/architecture.png`

---

**Last Updated:** October 4, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production-Ready
