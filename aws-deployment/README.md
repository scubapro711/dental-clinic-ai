# 🚀 DentalAI AWS Deployment

Complete AWS production deployment configuration for the DentalAI system.

## 📁 Directory Structure

```
aws-deployment/
├── terraform/              # Infrastructure as Code
│   ├── modules/           # Reusable Terraform modules
│   │   ├── vpc/          # VPC, subnets, NAT gateway
│   │   ├── rds/          # PostgreSQL database
│   │   ├── redis/        # ElastiCache Redis
│   │   ├── ecs/          # ECS Fargate cluster
│   │   └── s3-cloudfront/ # Frontend hosting
│   └── environments/
│       └── production/    # Production environment config
├── docs/                  # Deployment documentation
│   ├── PRODUCTION_DEPLOYMENT_GUIDE.md
│   └── COMPLETE_ARCHITECTURE_ANALYSIS.md
└── secrets/              # Secrets documentation (no actual secrets)
    └── README.md
```

## 🏗️ Architecture Overview

### Infrastructure Components

1. **Frontend**
   - S3 bucket for static hosting
   - CloudFront CDN for global distribution
   - Automatic cache invalidation

2. **Backend**
   - ECS Fargate cluster (serverless containers)
   - Application Load Balancer
   - Auto-scaling based on CPU/memory
   - Multi-AZ deployment

3. **Database**
   - RDS PostgreSQL (Multi-AZ)
   - Automated backups
   - Encryption at rest

4. **Cache**
   - ElastiCache Redis
   - Session management
   - API response caching

5. **Networking**
   - VPC with public/private subnets
   - NAT Gateway for private subnet internet access
   - Security groups for network isolation

## 🚀 Quick Start

### Prerequisites

1. **AWS Account**
   - Account ID: 488675216463
   - IAM User: Scubapro711_Dev_API
   - Region: us-east-1

2. **Tools Required**
   ```bash
   # AWS CLI
   aws --version  # v2.x

   # Terraform
   terraform version  # v1.0+

   # Docker
   docker --version  # v20.x+
   ```

3. **Credentials**
   - AWS access keys configured
   - OpenAI API key
   - Database passwords

### Step 1: Configure Terraform

```bash
cd terraform/environments/production

# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

### Step 2: Initialize Terraform

```bash
terraform init
```

### Step 3: Plan Deployment

```bash
terraform plan -out=tfplan
```

### Step 4: Deploy Infrastructure

```bash
terraform apply tfplan
```

**Expected time:** 15-20 minutes

### Step 5: Deploy Application

See `docs/PRODUCTION_DEPLOYMENT_GUIDE.md` for detailed steps.

## 📊 Cost Estimation

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| RDS PostgreSQL | db.t3.medium, 100GB | ~$70 |
| ElastiCache Redis | cache.t3.micro | ~$15 |
| ECS Fargate | 2 tasks, 1 vCPU, 2GB | ~$30 |
| S3 + CloudFront | 100GB + 1TB transfer | ~$15 |
| ALB | 1 load balancer | ~$20 |
| Data Transfer | Varies | ~$10 |
| **Total** | | **~$160/month** |

## 🔒 Security

- All secrets stored in AWS Secrets Manager
- Encryption at rest and in transit
- VPC isolation with security groups
- WAF for CloudFront (optional)
- Automated security scanning

## 📈 Monitoring

- CloudWatch dashboards
- Custom metrics for agent status
- Automated alarms for:
  - High CPU/Memory
  - Database connections
  - Error rates
  - Response times

## 🔄 CI/CD

GitHub Actions workflow included:
- Automated testing
- Docker image building
- ECR push
- ECS deployment
- Frontend deployment to S3

## 📚 Documentation

- **[Production Deployment Guide](docs/PRODUCTION_DEPLOYMENT_GUIDE.md)** - Step-by-step deployment instructions
- **[Architecture Analysis](docs/COMPLETE_ARCHITECTURE_ANALYSIS.md)** - Detailed system architecture
- **[Secrets Management](secrets/README.md)** - Security and secrets documentation

## 🛠️ Maintenance

### Daily
- Monitor CloudWatch dashboards
- Review error logs
- Check cost reports

### Weekly
- Security alerts review
- Backup verification
- Dependency updates

### Monthly
- Cost optimization
- Performance testing
- Security audit

## 🆘 Troubleshooting

### Backend Not Starting
```bash
# Check ECS logs
aws logs tail /ecs/dentalai-backend --follow
```

### Frontend Not Loading
```bash
# Verify S3 sync
aws s3 ls s3://dentalai-frontend-production/

# Check CloudFront
aws cloudfront get-distribution --id <DISTRIBUTION_ID>
```

### Database Connection Issues
```bash
# Test from ECS task
aws ecs execute-command \
  --cluster dentalai-production \
  --task <TASK_ID> \
  --container dentalai-backend \
  --interactive \
  --command "/bin/bash"
```

## 🔙 Rollback

```bash
# Rollback to previous version
aws ecs update-service \
  --cluster dentalai-production \
  --service dentalai-backend-service \
  --task-definition dentalai-backend:<PREVIOUS_REVISION>
```

## 📞 Support

- **Repository:** https://github.com/scubapro711/dental-clinic-ai
- **Issues:** https://github.com/scubapro711/dental-clinic-ai/issues
- **Documentation:** See `docs/` directory

## 📝 License

See main repository LICENSE file.

---

**Status:** ✅ Ready for Production Deployment  
**Last Updated:** October 4, 2025  
**Version:** 1.0.0
