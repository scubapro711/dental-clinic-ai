# 🚀 AWS Deployment Guide
## AI Dental Clinic Management System

**Version:** 2.2.0  
**Status:** Production Ready  
**Last Updated:** September 26, 2025

---

## 📋 Overview

This guide provides complete instructions for deploying the AI Dental Clinic Management System to Amazon Web Services (AWS) using Infrastructure as Code (Terraform) and containerized services (ECS Fargate).

### 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Application Load Balancer                    │
│                    (SSL Termination)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼────────┐         ┌────────▼────────┐
│  Gateway       │         │  AI Agents      │
│  Service       │         │  Service        │
│  (ECS Fargate) │         │  (ECS Fargate)  │
└───────┬────────┘         └────────┬────────┘
        │                           │
        └─────────────┬─────────────┘
                      │
        ┌─────────────▼─────────────┐
        │                           │
┌───────▼────────┐         ┌────────▼────────┐
│  RDS MySQL     │         │  ElastiCache    │
│  (Multi-AZ)    │         │  Redis          │
└────────────────┘         └─────────────────┘
```

---

## 🛠️ Prerequisites

### Required Tools
- **AWS CLI** (v2.0+) - [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- **Docker** (v20.0+) - [Installation Guide](https://docs.docker.com/get-docker/)
- **Terraform** (v1.0+) - [Installation Guide](https://learn.hashicorp.com/tutorials/terraform/install-cli)
- **Git** - For repository management

### AWS Requirements
- **AWS Account** with appropriate permissions
- **IAM User** with the following policies:
  - `AmazonECS_FullAccess`
  - `AmazonRDS_FullAccess`
  - `AmazonElastiCacheFullAccess`
  - `AmazonEC2FullAccess`
  - `AmazonRoute53FullAccess`
  - `AWSCertificateManagerFullAccess`
  - `SecretsManagerReadWrite`
  - `CloudWatchFullAccess`

### Environment Setup
```bash
# Configure AWS CLI
aws configure

# Verify access
aws sts get-caller-identity
```

---

## 🔐 Secrets Management

### Required Secrets
Before deployment, you need to provide the following secrets:

1. **OpenAI API Key** - For AI services
2. **Database Password** - For MySQL (auto-generated if not provided)
3. **WhatsApp Token** - For WhatsApp integration (optional)
4. **Telegram Token** - For Telegram integration (optional)

### Setting Secrets
```bash
# Set environment variables
export TF_VAR_openai_api_key="your_openai_api_key_here"
export TF_VAR_db_password="your_secure_database_password"
export TF_VAR_whatsapp_webhook_token="your_whatsapp_token"
export TF_VAR_telegram_bot_token="your_telegram_token"
```

---

## 🚀 Deployment Steps

### Step 1: Clone Repository
```bash
git clone https://github.com/scubapro711/dental-clinic-ai.git
cd dental-clinic-ai
```

### Step 2: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your configuration
nano .env
```

### Step 3: Run Deployment Script
```bash
# Make script executable
chmod +x scripts/deploy-to-aws.sh

# Deploy to production
./scripts/deploy-to-aws.sh

# Or deploy to specific environment
./scripts/deploy-to-aws.sh -e staging -r us-west-2
```

### Step 4: Manual Terraform Deployment (Alternative)
```bash
cd infrastructure/terraform/aws

# Initialize Terraform
terraform init

# Create workspace
terraform workspace new prod

# Plan deployment
terraform plan -var="openai_api_key=your_key_here"

# Apply deployment
terraform apply
```

---

## 📊 Infrastructure Components

### Networking
- **VPC** with public/private/database subnets
- **Multi-AZ** deployment across 2 availability zones
- **NAT Gateways** for private subnet internet access
- **Security Groups** with least privilege access

### Compute
- **ECS Fargate Cluster** for container orchestration
- **Application Load Balancer** with SSL termination
- **Auto Scaling** based on CPU, memory, and queue length
- **CloudWatch** monitoring and alerting

### Storage
- **RDS MySQL** with encryption and automated backups
- **ElastiCache Redis** for session and queue management
- **ECR** repositories for container images

### Security
- **AWS Secrets Manager** for secure credential storage
- **KMS** encryption for all sensitive data
- **IAM Roles** with minimal required permissions
- **VPC Security Groups** for network isolation

---

## 🔍 Monitoring & Observability

### CloudWatch Dashboards
- **Application Performance** metrics
- **Infrastructure Health** monitoring
- **Cost Optimization** insights

### Alerts
- **High CPU/Memory** utilization
- **Database Connection** issues
- **Queue Length** monitoring
- **Error Rate** tracking

### Logs
- **Application Logs** in CloudWatch
- **Access Logs** from Load Balancer
- **Database Logs** for performance tuning

---

## 🔧 Configuration Options

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `environment` | Deployment environment | `prod` |
| `aws_region` | AWS region | `us-east-1` |
| `db_instance_class` | RDS instance type | `db.t3.micro` |
| `gateway_cpu` | Gateway service CPU | `512` |
| `gateway_memory` | Gateway service memory | `1024` |
| `ai_agents_cpu` | AI Agents service CPU | `1024` |
| `ai_agents_memory` | AI Agents service memory | `2048` |

### Auto Scaling
- **Min Capacity:** 1 instance
- **Max Capacity:** 10 instances
- **Target CPU:** 70%
- **Target Memory:** 80%

---

## 🧪 Testing Deployment

### Health Checks
```bash
# Get load balancer URL
LB_URL=$(terraform output -raw application_url)

# Test Gateway service
curl $LB_URL/health

# Test AI Agents service
curl $LB_URL/ai/health

# Test API endpoints
curl -X POST $LB_URL/api/queue/process \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message", "type": "appointment"}'
```

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 $LB_URL/health
```

---

## 🔄 Updates & Maintenance

### Updating Application
```bash
# Rebuild and redeploy
./scripts/deploy-to-aws.sh

# Or update specific service
aws ecs update-service \
  --cluster dental-clinic-ai-prod-cluster \
  --service dental-clinic-ai-prod-gateway \
  --force-new-deployment
```

### Database Maintenance
- **Automated Backups:** Daily at 3:00 AM UTC
- **Maintenance Window:** Sunday 4:00-5:00 AM UTC
- **Monitoring:** CloudWatch alarms for performance

### Cost Optimization
- **Spot Instances:** Available for development environments
- **Reserved Instances:** Recommended for production
- **Auto Scaling:** Reduces costs during low usage

---

## 🛡️ Security Best Practices

### Data Protection
- **Encryption at Rest:** All data encrypted with KMS
- **Encryption in Transit:** TLS 1.2+ for all connections
- **Secrets Management:** No hardcoded credentials

### Access Control
- **IAM Roles:** Principle of least privilege
- **VPC Security:** Private subnets for databases
- **API Security:** Rate limiting and authentication

### Compliance
- **HIPAA Ready:** Encryption and audit logging
- **SOC 2:** Infrastructure controls
- **GDPR:** Data protection measures

---

## 🆘 Troubleshooting

### Common Issues

#### Deployment Fails
```bash
# Check Terraform logs
terraform plan -detailed-exitcode

# Check AWS CLI configuration
aws sts get-caller-identity

# Verify permissions
aws iam get-user
```

#### Services Not Starting
```bash
# Check ECS service status
aws ecs describe-services \
  --cluster dental-clinic-ai-prod-cluster \
  --services dental-clinic-ai-prod-gateway

# Check CloudWatch logs
aws logs describe-log-groups \
  --log-group-name-prefix "/ecs/dental-clinic-ai"
```

#### Database Connection Issues
```bash
# Check security groups
aws ec2 describe-security-groups \
  --group-names dental-clinic-ai-prod-rds-sg

# Test connectivity from ECS
aws ecs execute-command \
  --cluster dental-clinic-ai-prod-cluster \
  --task TASK_ID \
  --container gateway \
  --interactive \
  --command "/bin/bash"
```

### Support Resources
- **AWS Documentation:** [ECS](https://docs.aws.amazon.com/ecs/), [RDS](https://docs.aws.amazon.com/rds/), [ElastiCache](https://docs.aws.amazon.com/elasticache/)
- **Terraform Documentation:** [AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- **Project Repository:** [GitHub Issues](https://github.com/scubapro711/dental-clinic-ai/issues)

---

## 📈 Scaling Considerations

### Horizontal Scaling
- **ECS Services:** Auto-scaling based on metrics
- **Database:** Read replicas for read-heavy workloads
- **Cache:** Redis cluster mode for high availability

### Vertical Scaling
- **Instance Types:** Upgrade CPU/memory as needed
- **Storage:** Increase RDS storage automatically
- **Network:** Enhanced networking for high throughput

---

## 💰 Cost Estimation

### Monthly Costs (Production)
| Service | Instance Type | Estimated Cost |
|---------|---------------|----------------|
| ECS Fargate | 2 vCPU, 4GB RAM | $50-80 |
| RDS MySQL | db.t3.micro | $15-25 |
| ElastiCache | cache.t3.micro | $10-15 |
| Load Balancer | Application LB | $20-25 |
| Data Transfer | 100GB/month | $10-15 |
| **Total** | | **$105-160** |

### Cost Optimization Tips
- Use **Reserved Instances** for 40-60% savings
- Enable **Auto Scaling** to reduce idle costs
- Monitor with **AWS Cost Explorer**
- Set up **Billing Alerts**

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] AWS CLI configured and tested
- [ ] Docker installed and running
- [ ] Terraform installed
- [ ] Required secrets available
- [ ] Domain name configured (optional)
- [ ] SSL certificate ready (optional)

### Deployment
- [ ] Repository cloned
- [ ] Environment variables set
- [ ] Deployment script executed
- [ ] Infrastructure created successfully
- [ ] Services deployed and running

### Post-Deployment
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Backup verified
- [ ] Documentation updated
- [ ] Team notified

---

## 🎯 Next Steps

After successful deployment:

1. **Configure Domain:** Point your domain to the load balancer
2. **Set Up SSL:** Add SSL certificate for HTTPS
3. **Configure Monitoring:** Set up custom dashboards
4. **Load Testing:** Validate performance under load
5. **Backup Testing:** Verify backup and restore procedures
6. **Team Training:** Train team on AWS console and monitoring

---

**🎉 Congratulations! Your AI Dental Clinic Management System is now running on AWS!**

For support or questions, please refer to the project documentation or create an issue in the GitHub repository.
