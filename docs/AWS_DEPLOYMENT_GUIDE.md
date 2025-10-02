# DentalAI MVP - AWS Deployment Guide

**Date:** October 2, 2025  
**Version:** MVP 1.0  
**Status:** Ready for Deployment

---

## 📋 Prerequisites

### AWS Account Setup
1. AWS Account with appropriate permissions
2. AWS CLI installed and configured
3. Domain name (optional, can use AWS provided URLs)

### Required AWS Services
- **ECS (Elastic Container Service)** - Container orchestration
- **RDS (PostgreSQL)** - Primary database
- **ElastiCache (Redis)** - Caching layer
- **EC2** - Neo4j instance
- **S3** - Static assets and backups
- **CloudFront** - CDN for frontend
- **ALB (Application Load Balancer)** - Load balancing
- **ECR (Elastic Container Registry)** - Docker images
- **Secrets Manager** - Secure credentials storage
- **CloudWatch** - Monitoring and logs

---

## 🏗️ Architecture Overview

```
Internet
    ↓
CloudFront (CDN)
    ↓
Application Load Balancer
    ↓
┌─────────────────────────────────────┐
│  ECS Cluster                        │
│  ├── Backend Service (FastAPI)     │
│  │   - 2+ tasks for high availability
│  │   - Auto-scaling enabled        │
│  └── Frontend Service (React)      │
│      - Served via Nginx             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Data Layer                         │
│  ├── RDS PostgreSQL (Multi-AZ)     │
│  ├── ElastiCache Redis              │
│  └── EC2 Neo4j Instance             │
└─────────────────────────────────────┘
```

---

## 🚀 Step-by-Step Deployment

### Step 1: Set Up AWS Infrastructure

#### 1.1 Create VPC and Networking
```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=dentalai-vpc}]'

# Create subnets (public and private in 2 AZs)
aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.1.0/24 --availability-zone us-east-1a
aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.2.0/24 --availability-zone us-east-1b
aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.11.0/24 --availability-zone us-east-1a
aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.12.0/24 --availability-zone us-east-1b

# Create Internet Gateway
aws ec2 create-internet-gateway --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=dentalai-igw}]'
aws ec2 attach-internet-gateway --vpc-id <vpc-id> --internet-gateway-id <igw-id>
```

#### 1.2 Create RDS PostgreSQL
```bash
aws rds create-db-instance \
    --db-instance-identifier dentalai-db \
    --db-instance-class db.t3.medium \
    --engine postgres \
    --engine-version 15.4 \
    --master-username dentalai \
    --master-user-password <secure-password> \
    --allocated-storage 100 \
    --storage-type gp3 \
    --vpc-security-group-ids <sg-id> \
    --db-subnet-group-name dentalai-db-subnet \
    --multi-az \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --preferred-maintenance-window "sun:04:00-sun:05:00" \
    --tags Key=Name,Value=dentalai-db
```

#### 1.3 Create ElastiCache Redis
```bash
aws elasticache create-cache-cluster \
    --cache-cluster-id dentalai-redis \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --engine-version 7.0 \
    --num-cache-nodes 1 \
    --cache-subnet-group-name dentalai-redis-subnet \
    --security-group-ids <sg-id> \
    --tags Key=Name,Value=dentalai-redis
```

#### 1.4 Launch Neo4j EC2 Instance
```bash
# Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.medium \
    --key-name dentalai-key \
    --security-group-ids <sg-id> \
    --subnet-id <subnet-id> \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=dentalai-neo4j}]' \
    --user-data file://neo4j-user-data.sh
```

**neo4j-user-data.sh:**
```bash
#!/bin/bash
# Install Neo4j
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | tee /etc/apt/sources.list.d/neo4j.list
apt-get update
apt-get install -y neo4j

# Configure Neo4j
echo "dbms.default_listen_address=0.0.0.0" >> /etc/neo4j/neo4j.conf
systemctl enable neo4j
systemctl start neo4j
```

---

### Step 2: Build and Push Docker Images

#### 2.1 Create ECR Repositories
```bash
aws ecr create-repository --repository-name dentalai-backend
aws ecr create-repository --repository-name dentalai-frontend
```

#### 2.2 Build and Push Backend Image
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build backend image
cd backend
docker build -t dentalai-backend .

# Tag and push
docker tag dentalai-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/dentalai-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/dentalai-backend:latest
```

#### 2.3 Build and Push Frontend Image
```bash
# Build frontend image
cd frontend
docker build -t dentalai-frontend .

# Tag and push
docker tag dentalai-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/dentalai-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/dentalai-frontend:latest
```

---

### Step 3: Store Secrets in AWS Secrets Manager

```bash
# Create secret for database
aws secretsmanager create-secret \
    --name dentalai/database \
    --secret-string '{"username":"dentalai","password":"<db-password>","host":"<rds-endpoint>","port":"5432","database":"dentalai"}'

# Create secret for Redis
aws secretsmanager create-secret \
    --name dentalai/redis \
    --secret-string '{"host":"<redis-endpoint>","port":"6379"}'

# Create secret for Neo4j
aws secretsmanager create-secret \
    --name dentalai/neo4j \
    --secret-string '{"uri":"bolt://<neo4j-ip>:7687","username":"neo4j","password":"<neo4j-password>"}'

# Create secret for API keys
aws secretsmanager create-secret \
    --name dentalai/api-keys \
    --secret-string '{"openai_api_key":"<openai-key>","jwt_secret":"<jwt-secret>","secret_key":"<secret-key>"}'
```

---

### Step 4: Create ECS Cluster and Services

#### 4.1 Create ECS Cluster
```bash
aws ecs create-cluster --cluster-name dentalai-cluster
```

#### 4.2 Create Task Definitions

**Backend Task Definition (backend-task.json):**
```json
{
  "family": "dentalai-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/dentalai-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "APP_ENV", "value": "production"}
      ],
      "secrets": [
        {"name": "DATABASE_URL", "valueFrom": "dentalai/database:url"},
        {"name": "REDIS_URL", "valueFrom": "dentalai/redis:url"},
        {"name": "NEO4J_URI", "valueFrom": "dentalai/neo4j:uri"},
        {"name": "OPENAI_API_KEY", "valueFrom": "dentalai/api-keys:openai_api_key"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/dentalai-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 4.3 Create Services
```bash
# Register task definitions
aws ecs register-task-definition --cli-input-json file://backend-task.json

# Create backend service
aws ecs create-service \
    --cluster dentalai-cluster \
    --service-name dentalai-backend-service \
    --task-definition dentalai-backend \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[<subnet-1>,<subnet-2>],securityGroups=[<sg-id>],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=<tg-arn>,containerName=backend,containerPort=8000"
```

---

### Step 5: Set Up Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
    --name dentalai-alb \
    --subnets <subnet-1> <subnet-2> \
    --security-groups <sg-id> \
    --scheme internet-facing \
    --type application

# Create target groups
aws elbv2 create-target-group \
    --name dentalai-backend-tg \
    --protocol HTTP \
    --port 8000 \
    --vpc-id <vpc-id> \
    --target-type ip \
    --health-check-path /health

# Create listeners
aws elbv2 create-listener \
    --load-balancer-arn <alb-arn> \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=<tg-arn>
```

---

### Step 6: Set Up CloudFront for Frontend

```bash
# Create S3 bucket for frontend
aws s3 mb s3://dentalai-frontend

# Upload frontend build
cd frontend/dist
aws s3 sync . s3://dentalai-frontend --acl public-read

# Create CloudFront distribution
aws cloudfront create-distribution \
    --origin-domain-name dentalai-frontend.s3.amazonaws.com \
    --default-root-object index.html
```

---

### Step 7: Set Up Monitoring

#### 7.1 Create CloudWatch Log Groups
```bash
aws logs create-log-group --log-group-name /ecs/dentalai-backend
aws logs create-log-group --log-group-name /ecs/dentalai-frontend
```

#### 7.2 Create CloudWatch Alarms
```bash
# High CPU alarm
aws cloudwatch put-metric-alarm \
    --alarm-name dentalai-high-cpu \
    --alarm-description "Alert when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2

# Error rate alarm
aws cloudwatch put-metric-alarm \
    --alarm-name dentalai-high-error-rate \
    --alarm-description "Alert when error rate exceeds 5%" \
    --metric-name 5XXError \
    --namespace AWS/ApplicationELB \
    --statistic Sum \
    --period 300 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1
```

---

## 🔒 Security Checklist

- [ ] All secrets stored in AWS Secrets Manager
- [ ] RDS encryption at rest enabled
- [ ] RDS Multi-AZ enabled for high availability
- [ ] Security groups configured with least privilege
- [ ] HTTPS/TLS enabled on ALB
- [ ] CloudFront HTTPS only
- [ ] IAM roles follow least privilege principle
- [ ] VPC flow logs enabled
- [ ] CloudTrail logging enabled
- [ ] Backup strategy configured

---

## 📊 Monitoring and Alerts

### Key Metrics to Monitor
1. **Backend API**
   - Response time (p50, p95, p99)
   - Error rate (4xx, 5xx)
   - Request rate
   - CPU and memory utilization

2. **Database (RDS)**
   - Connection count
   - CPU utilization
   - Disk I/O
   - Replication lag (if using read replicas)

3. **Redis (ElastiCache)**
   - Hit rate
   - Memory usage
   - Evictions

4. **Neo4j**
   - Query performance
   - Memory usage
   - Transaction rate

---

## 💰 Cost Estimation (Monthly)

| Service | Configuration | Estimated Cost |
|---------|--------------|----------------|
| ECS Fargate | 2 tasks (1 vCPU, 2GB RAM) | ~$60 |
| RDS PostgreSQL | db.t3.medium, Multi-AZ | ~$150 |
| ElastiCache Redis | cache.t3.micro | ~$15 |
| EC2 (Neo4j) | t3.medium | ~$30 |
| ALB | Standard | ~$20 |
| CloudFront | 1TB data transfer | ~$85 |
| S3 | 100GB storage | ~$3 |
| **Total** | | **~$363/month** |

---

## 🔄 CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push backend
        run: |
          cd backend
          docker build -t dentalai-backend .
          docker tag dentalai-backend:latest ${{ steps.login-ecr.outputs.registry }}/dentalai-backend:latest
          docker push ${{ steps.login-ecr.outputs.registry }}/dentalai-backend:latest
      
      - name: Update ECS service
        run: |
          aws ecs update-service --cluster dentalai-cluster --service dentalai-backend-service --force-new-deployment
```

---

## 📝 Post-Deployment Checklist

- [ ] Verify all services are running
- [ ] Test API endpoints
- [ ] Test frontend access
- [ ] Verify database connectivity
- [ ] Test AI agents responses
- [ ] Check CloudWatch logs
- [ ] Verify monitoring and alerts
- [ ] Test backup and restore procedures
- [ ] Document all endpoints and credentials
- [ ] Update DNS records (if using custom domain)

---

## 🆘 Troubleshooting

### Common Issues

**1. ECS tasks failing to start**
- Check CloudWatch logs: `/ecs/dentalai-backend`
- Verify secrets are accessible
- Check security group rules

**2. Database connection errors**
- Verify RDS security group allows ECS tasks
- Check database credentials in Secrets Manager
- Verify RDS endpoint is correct

**3. High latency**
- Check RDS performance insights
- Review Redis hit rate
- Check ECS task CPU/memory usage
- Consider scaling up or out

---

## 📞 Support

For deployment issues, contact:
- Email: support@dentalai.com
- GitHub Issues: https://github.com/scubapro711/dental-clinic-ai/issues

---

**Last Updated:** October 2, 2025  
**Document Version:** 1.0
